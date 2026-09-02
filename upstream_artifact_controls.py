"""Deterministic controls for the upstream-artifact software cohort.

The candidate event stream is untrusted input.  These transforms retain either
resource shape without semantic content or a shape-identical substitution of
semantic text.  They never execute an action or decide an outcome.
"""

from __future__ import annotations

from hashlib import sha256
import json
import re
import subprocess
import time
from typing import Any, Iterable, Mapping, Protocol

from .protocol import ProposedAction


MATCHED_SCHEMA = "errata.rung1-upstream-matched-activity.v1"
CORRUPTED_SCHEMA = "errata.rung1-upstream-corrupted-information.v1"
MATCHED_EXECUTION_SCHEMA = "errata.rung1-upstream-matched-execution.v1"

_SEMANTIC_FIELDS = frozenset(
    {
        "aggregated_output",
        "command",
        "content",
        "message",
        "output",
        "path",
        "text",
    }
)
_STRUCTURAL_FIELDS = frozenset(
    {
        "id",
        "type",
        "status",
        "exit_code",
        "duration_ms",
        "wall_time_ms",
    }
)
_WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_MUTATION_TOOLS = frozenset(
    {
        "write_file",
        "replace_text",
        "remove_file",
        "remove_tree",
        "restore_file",
    }
)
_SAFETY_TOOLS = frozenset({"stop_process", "remove_prepared_environment"})
_PRESERVED_WORDS = frozenset(
    {
        "and",
        "as",
        "assert",
        "async",
        "await",
        "break",
        "case",
        "class",
        "continue",
        "def",
        "del",
        "elif",
        "else",
        "except",
        "False",
        "finally",
        "for",
        "from",
        "global",
        "if",
        "import",
        "in",
        "is",
        "lambda",
        "match",
        "None",
        "nonlocal",
        "not",
        "or",
        "pass",
        "raise",
        "return",
        "True",
        "try",
        "while",
        "with",
        "yield",
    }
)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _digest(value: object) -> str:
    return sha256(canonical_bytes(value)).hexdigest()


def parse_codex_jsonl(raw: bytes) -> list[dict[str, Any]]:
    """Parse a bounded Codex JSONL transcript without accepting partial lines."""

    if len(raw) > 100_000_000:
        raise ValueError("Codex transcript exceeds the frozen 100 MB limit")
    rows: list[dict[str, Any]] = []
    for line in raw.splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError("Codex transcript is not JSONL") from exc
        if not isinstance(row, dict) or not isinstance(
            row.get("type", row.get("kind")), str
        ):
            raise ValueError("Codex transcript event shape differs")
        rows.append(row)
    if not rows:
        raise ValueError("Codex transcript is empty")
    return rows


def _item(row: Mapping[str, Any]) -> Mapping[str, Any] | None:
    if row.get("kind") == "tool_result" and isinstance(row.get("payload"), Mapping):
        return row["payload"]
    value = row.get("item")
    return value if isinstance(value, Mapping) else None


def _activity_rows(events: Iterable[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    selected: list[Mapping[str, Any]] = []
    for row in events:
        item = _item(row)
        if item is None:
            continue
        item_type = item.get("type")
        if item.get("tool") or item_type in {
            "command_execution",
            "file_read",
            "mcp_tool_call",
            "web_search",
        }:
            selected.append(row)
    return selected


def _semantic_byte_count(value: object) -> int:
    if isinstance(value, str):
        return len(value.encode("utf-8"))
    if isinstance(value, list):
        return sum(_semantic_byte_count(item) for item in value)
    if isinstance(value, Mapping):
        return sum(
            _semantic_byte_count(item)
            for key, item in value.items()
            if key in _SEMANTIC_FIELDS or isinstance(item, (list, Mapping))
        )
    return 0


def matched_activity_packet(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Retain activity/cost shape while withholding commands and observations."""

    activities = []
    for ordinal, row in enumerate(_activity_rows(events), start=1):
        item = _item(row)
        assert item is not None
        activities.append(
            {
                "ordinal": ordinal,
                "event_type": row.get("type", row.get("kind")),
                "activity_type": item.get("type", item.get("tool")),
                "status": item.get("status"),
                "exit_code": item.get("exit_code"),
                "duration_ms": item.get("duration_ms", item.get("wall_time_ms")),
                "semantic_output_bytes": _semantic_byte_count(item),
            }
        )
    body = {
        "schema": MATCHED_SCHEMA,
        "source_event_count": len(events),
        "activity_count": len(activities),
        "activities": activities,
        "semantic_outputs_withheld": True,
    }
    return {**body, "sha256": _digest(body)}


def _substitution(word: str, salt: bytes) -> str:
    if word in _PRESERVED_WORDS:
        return word
    stream = sha256(salt + b"\x00" + word.encode("utf-8")).digest()
    output: list[str] = []
    for index, character in enumerate(word):
        shift = 1 + stream[index % len(stream)] % 25
        if "a" <= character <= "z":
            output.append(chr(ord("a") + (ord(character) - ord("a") + shift) % 26))
        elif "A" <= character <= "Z":
            output.append(chr(ord("A") + (ord(character) - ord("A") + shift) % 26))
        elif character.isdigit():
            output.append(
                str((int(character) + 1 + stream[index % len(stream)] % 9) % 10)
            )
        else:
            output.append(character)
    replacement = "".join(output)
    if replacement == word:
        # ``_WORD`` deliberately admits underscore-only Python identifiers.
        # They contain no character handled by the shifts above, so map the
        # first byte to a deterministic letter while preserving byte length.
        replacement = chr(ord("a") + stream[0] % 26) + word[1:]
    return replacement


def corrupt_text(text: str, *, salt: bytes) -> str:
    """Consistently replace non-keyword identifiers without changing byte length."""

    return _WORD.sub(lambda match: _substitution(match.group(0), salt), text)


def _corrupt(value: object, *, salt: bytes, field: str | None = None) -> object:
    if isinstance(value, list):
        return [_corrupt(item, salt=salt) for item in value]
    if isinstance(value, Mapping):
        return {
            str(key): (
                item
                if key in _STRUCTURAL_FIELDS
                else _corrupt(item, salt=salt, field=str(key))
            )
            for key, item in value.items()
        }
    if isinstance(value, str) and field in _SEMANTIC_FIELDS:
        return corrupt_text(value, salt=salt)
    return value


def corrupted_information_packet(
    events: list[dict[str, Any]], *, case_sha256: str
) -> dict[str, Any]:
    """Build a record-shape-preserving semantic corruption of activity events."""

    if not re.fullmatch(r"[0-9a-f]{64}", case_sha256):
        raise ValueError("case digest differs")
    source = [dict(row) for row in _activity_rows(events)]
    corrupted = [_corrupt(row, salt=bytes.fromhex(case_sha256)) for row in source]
    source_bytes = canonical_bytes(source)
    corrupted_bytes = canonical_bytes(corrupted)
    body = {
        "schema": CORRUPTED_SCHEMA,
        "case_sha256": case_sha256,
        "source_event_count": len(events),
        "activity_count": len(source),
        "source_activity_sha256": sha256(source_bytes).hexdigest(),
        "corrupted_activity_sha256": sha256(corrupted_bytes).hexdigest(),
        "source_activity_bytes": len(source_bytes),
        "corrupted_activity_bytes": len(corrupted_bytes),
        "activities": corrupted,
    }
    result = {**body, "sha256": _digest(body)}
    validate_corruption(source, result)
    return result


def validate_matched(packet: Mapping[str, Any]) -> None:
    body = {key: value for key, value in packet.items() if key != "sha256"}
    if packet.get("schema") != MATCHED_SCHEMA or packet.get("sha256") != _digest(body):
        raise ValueError("matched-activity packet identity differs")
    activities = packet.get("activities")
    if not isinstance(activities, list) or packet.get("activity_count") != len(
        activities
    ):
        raise ValueError("matched-activity count differs")
    forbidden = _SEMANTIC_FIELDS | {"argv", "arguments"}
    if any(forbidden.intersection(activity) for activity in activities):
        raise ValueError("matched-activity packet leaked semantic content")


def execute_matched_noninformative(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Perform one inert activity per retained raw activity and retain costs.

    Command-class events execute ``/usr/bin/true``. Other activity classes hash
    a zero buffer whose length equals the withheld semantic byte count. Nothing
    from the case workspace is read and no semantic output is produced.
    """

    validate_matched(packet)
    rows = []
    for activity in packet["activities"]:
        started = time.perf_counter_ns()
        activity_type = str(activity.get("activity_type", ""))
        byte_count = int(activity.get("semantic_output_bytes", 0))
        if activity_type in {"command_execution", "run_command", "start_process"}:
            completed = subprocess.run(
                ["/usr/bin/true"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=5,
                check=False,
            )
            action_class = "process"
            returncode = completed.returncode
        else:
            digest = sha256()
            remaining = byte_count
            block = b"\x00" * min(65_536, max(1, remaining))
            while remaining:
                selected = block[: min(len(block), remaining)]
                digest.update(selected)
                remaining -= len(selected)
            action_class = "bounded-read"
            returncode = 0
        rows.append(
            {
                "ordinal": activity["ordinal"],
                "activity_type": activity_type,
                "action_class": action_class,
                "matched_semantic_byte_allowance": byte_count,
                "returncode": returncode,
                "elapsed_ns": time.perf_counter_ns() - started,
                "semantic_output_bytes": 0,
            }
        )
    body = {
        "schema": MATCHED_EXECUTION_SCHEMA,
        "packet_sha256": packet["sha256"],
        "activity_count": len(rows),
        "activities": rows,
        "case_workspace_reads": 0,
        "semantic_output_bytes": 0,
    }
    return {**body, "sha256": _digest(body)}


def validate_corruption(
    source: list[dict[str, Any]], packet: Mapping[str, Any]
) -> None:
    body = {key: value for key, value in packet.items() if key != "sha256"}
    if packet.get("schema") != CORRUPTED_SCHEMA or packet.get("sha256") != _digest(
        body
    ):
        raise ValueError("corrupted packet identity differs")
    corrupted = packet.get("activities")
    if not isinstance(corrupted, list) or len(corrupted) != len(source):
        raise ValueError("corruption changed activity count")
    if [row.get("type", row.get("kind")) for row in corrupted] != [
        row.get("type", row.get("kind")) for row in source
    ]:
        raise ValueError("corruption changed event types")
    source_bytes = canonical_bytes(source)
    corrupted_bytes = canonical_bytes(corrupted)
    if source_bytes == corrupted_bytes:
        raise ValueError("semantic corruption was inert")
    if len(source_bytes) != len(corrupted_bytes):
        raise ValueError("semantic corruption changed canonical byte length")
    if packet.get("source_activity_sha256") != sha256(source_bytes).hexdigest():
        raise ValueError("corruption source binding differs")
    if packet.get("corrupted_activity_sha256") != sha256(corrupted_bytes).hexdigest():
        raise ValueError("corrupted activity binding differs")


class _Executor(Protocol):
    def execute(self, action: ProposedAction) -> dict[str, Any]: ...


class NoExplorationExecutor:
    """Deny information acquisition while retaining mutation and fixed checks.

    A control may act from its initial packet, but it cannot inspect the case.
    After its first mutation it may run only evaluator-predeclared commands.
    Shutdown and rollback remain available throughout.
    """

    def __init__(
        self,
        inner: _Executor,
        *,
        validation_argv: Iterable[Iterable[str]] = (),
    ) -> None:
        self.inner = inner
        self.validation_argv = frozenset(tuple(argv) for argv in validation_argv)
        self.mutation_seen = False
        self.denials = 0

    @property
    def authority(self) -> Any:
        return self.inner.authority

    @authority.setter
    def authority(self, value: Any) -> None:
        self.inner.authority = value

    @property
    def removable_paths(self) -> Any:
        return self.inner.removable_paths

    @removable_paths.setter
    def removable_paths(self, value: Any) -> None:
        self.inner.removable_paths = value

    @property
    def restorable_entries(self) -> Any:
        return self.inner.restorable_entries

    @restorable_entries.setter
    def restorable_entries(self, value: Any) -> None:
        self.inner.restorable_entries = value

    def execute(self, action: ProposedAction) -> dict[str, Any]:
        if action.tool in _MUTATION_TOOLS:
            result = self.inner.execute(action)
            if result.get("mutated"):
                self.mutation_seen = True
            return result
        if action.tool in _SAFETY_TOOLS:
            return self.inner.execute(action)
        if action.tool == "run_command" and self.mutation_seen:
            argv = action.arguments.get("argv")
            if isinstance(argv, list) and tuple(argv) in self.validation_argv:
                return self.inner.execute(action)
        self.denials += 1
        return {
            "ok": False,
            "tool": action.tool,
            "error": "frozen no-exploration policy denied information acquisition",
            "mutated": False,
            "control_denial": True,
        }


__all__ = [
    "CORRUPTED_SCHEMA",
    "MATCHED_SCHEMA",
    "MATCHED_EXECUTION_SCHEMA",
    "NoExplorationExecutor",
    "canonical_bytes",
    "corrupt_text",
    "corrupted_information_packet",
    "execute_matched_noninformative",
    "matched_activity_packet",
    "parse_codex_jsonl",
    "validate_corruption",
    "validate_matched",
]
