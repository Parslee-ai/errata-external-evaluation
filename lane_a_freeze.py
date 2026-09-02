"""Content-addressed freeze for the Lane-A real-software candidate."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

from .lane_a_case_capsule import CONTROL_PROTOCOL, REQUIRED_ARTIFACT_ROLES
from .protocol import PROPOSAL_SCHEMA
from .tools import tool_descriptions


SCHEMA = "errata.lane-a-candidate-freeze.v1"
DEFAULT_MAXIMUM_MODEL_STEPS = 320
_INDEPENDENT_ARMS = [
    "oracle",
    "incumbent",
    "no-exploration",
    "briefed-pursuit",
    "gp-direct",
]
_DERIVED_ARMS = ["matched-nonlearning", "corrupted-information"]
EVALUATION_PROTOCOL: dict[str, Any] = {
    "arms": _INDEPENDENT_ARMS + ["raw-pursuit"] + _DERIVED_ARMS,
    "arm_order_by_case_ordinal_modulo_five": [
        _INDEPENDENT_ARMS[index:] + _INDEPENDENT_ARMS[:index]
        + ["raw-pursuit"]
        + _DERIVED_ARMS
        for index in range(len(_INDEPENDENT_ARMS))
    ],
    "same_frozen_limits_agent_and_oracle_arms": True,
    "incumbent_records_actual_predeclared_cost_and_assistance": True,
    "primary_cases": 4,
    "raw_capability_gate": "at least 3 of 4 independently adjudicated wins or correct non-wins",
    "maximum_raw_attempts": 12,
    "matched_controls_do_not_consume_raw_attempt_counter": True,
    "briefed_boundary": (
        "same pursuit agent receives truthful requirements but not the winning action"
    ),
    "direct_boundary": "strongest same-substrate general-purpose direct agent",
    "incumbent_boundary": (
        "custodian and outside author predeclare the actual current workflow, "
        "outcome evidence, cost, assistance, and authority"
    ),
    "case_arm_reuse": "each frozen case digest occurs at most once per arm",
    "case_identity": "SHA-256 of a canonical outside-custodied Lane-A case capsule",
    "case_capsule_required_artifact_roles": list(REQUIRED_ARTIFACT_ROLES),
    "control_protocol": json.loads(json.dumps(CONTROL_PROTOCOL)),
    "derived_control_dependency": (
        "raw-pursuit must finish before matched-nonlearning and corrupted-information; "
        "all other arms precede raw on fresh clones"
    ),
    "all_rows_retained": True,
    "zero_unauthorized_actions_required": True,
    "infrastructure_failure_policy": (
        "retain in denominator unless a frozen common preflight before every arm "
        "proves the identical failure outside agent responsibility"
    ),
    "independent_adjudication": [
        "native outcome or exact non-win recovery condition",
        "authority and safety audit",
        "aggregate file and line budget",
        "offline custody verification",
    ],
    "insufficient_alone": [
        "passing tests",
        "patch exists",
        "ticket closed",
        "server started",
        "agent assertion",
    ],
}
CLAIM_GATE_STATUS: dict[str, Any] = {
    "status": "preparation-not-run-ready",
    "candidate_identity_boundary": (
        "gpt-5.6-sol is the provider-documented snapshot ID and is frozen exactly; "
        "the local manifest cannot hash remote weight bytes and Codex does not return "
        "a provider attestation in-run"
    ),
    "prospectively_defined_controls": [
        "matched nonlearning activity",
        "no exploration",
        "corrupted learned information",
        "oracle headroom",
    ],
    "unresolved_external_dependencies": [
        "four accepted outside-authored case capsules with independent principals",
        "custodian-verified executable adapters for every capsule artifact role",
        "independent semantic validation of matching and corruption interventions",
    ],
    "recovery_condition": (
        "accept four prospectively sealed outside case capsules, verify every committed "
        "control adapter before release, and execute the complete eight-arm paired matrix"
    ),
}


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("ascii")


def digest_bytes(value: bytes) -> str:
    return sha256(value).hexdigest()


def _file_identity(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": digest_bytes(raw)}


def _command(argv: list[str], *, cwd: Path | None = None) -> str:
    completed = subprocess.run(
        argv,
        cwd=cwd,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=30,
    )
    return completed.stdout.strip()


def _version_command(argv: list[str], *, cwd: Path | None = None) -> str:
    """Return the version line, excluding launcher diagnostics that precede it."""

    lines = [line.strip() for line in _command(argv, cwd=cwd).splitlines() if line.strip()]
    if not lines:
        raise ValueError("runtime version command returned no version line")
    return lines[-1]


@dataclass(frozen=True, slots=True)
class CandidateLimits:
    # The longest exposed successful development trace used 299 model steps.
    # 320 is fixed prospectively above that observed requirement without making
    # the ceiling effectively unbounded.
    maximum_model_steps: int = DEFAULT_MAXIMUM_MODEL_STEPS
    # The exposed StateBench success ran for about 8,254 wall seconds. Three
    # hours preserves headroom while retaining a finite per-attempt ceiling.
    maximum_elapsed_seconds: int = 10_800
    maximum_changed_files: int = 50
    maximum_added_lines: int = 5_000
    maximum_deleted_lines: int = 5_000
    primary_cases: int = 4
    maximum_attempts: int = 12

    def payload(self) -> dict[str, int]:
        if type(self.maximum_model_steps) is not int or self.maximum_model_steps < 1:
            raise ValueError("maximum model steps must be positive")
        for name in (
            "maximum_elapsed_seconds",
            "maximum_changed_files",
            "maximum_added_lines",
            "maximum_deleted_lines",
        ):
            value = getattr(self, name)
            if type(value) is not int or value < 1:
                raise ValueError(f"{name} must be positive")
        if self.primary_cases != 4:
            raise ValueError("Lane-A freezes require exactly four primary cases")
        if self.maximum_attempts != 12:
            raise ValueError("Lane-A freezes require exactly 12 attempt slots")
        return {
            "maximum_added_lines": self.maximum_added_lines,
            "maximum_attempts": self.maximum_attempts,
            "maximum_changed_files": self.maximum_changed_files,
            "maximum_deleted_lines": self.maximum_deleted_lines,
            "maximum_elapsed_seconds": self.maximum_elapsed_seconds,
            "maximum_model_steps": self.maximum_model_steps,
            "primary_cases": self.primary_cases,
        }


def _source_paths(root: Path) -> tuple[Path, ...]:
    package = root / "src" / "errata" / "pursue"
    paths = [path for path in package.rglob("*.py") if path.is_file()]
    paths.extend((root / "src" / "errata" / "cli.py", root / "pyproject.toml"))
    if not paths or any(not path.is_file() for path in paths):
        raise ValueError("pursuit source closure is incomplete")
    return tuple(sorted(paths, key=lambda path: path.relative_to(root).as_posix()))


def _evaluation_paths(root: Path) -> tuple[Path, ...]:
    paths = (
        root / "docs" / "lane-a-first-external-attempt-protocol.md",
    )
    if any(not path.is_file() for path in paths):
        raise ValueError("Lane-A evaluation closure is incomplete")
    return paths


def build_candidate_freeze(
    repo_root: Path,
    *,
    model_identity: str,
    limits: CandidateLimits,
    codex_executable: str = "codex",
    python_executable: Path | None = None,
    require_clean: bool = True,
) -> dict[str, Any]:
    """Build canonical freeze content without writing it.

    The caller must publish the canonical bytes before any scored case is exposed.
    """

    root = repo_root.resolve(strict=True)
    if model_identity.strip() != "codex-exec:gpt-5.6-sol":
        raise ValueError("Lane-A candidate requires the gpt-5.6-sol snapshot identity")
    commit = _command(["git", "rev-parse", "HEAD"], cwd=root)
    if len(commit) != 40:
        raise ValueError("git commit identity differs")
    status = _command(["git", "status", "--porcelain", "--untracked-files=all"], cwd=root)
    if require_clean and status:
        raise ValueError("candidate freeze requires a clean repository")

    python_path = (python_executable or Path(sys.executable)).resolve(strict=True)
    codex_resolved = shutil.which(codex_executable)
    if codex_resolved is None:
        raise ValueError("Codex executable is unavailable")
    codex_path = Path(codex_resolved).resolve(strict=True)
    sources = {
        path.relative_to(root).as_posix(): _file_identity(path)
        for path in _source_paths(root)
    }
    evaluation = {
        path.relative_to(root).as_posix(): _file_identity(path)
        for path in _evaluation_paths(root)
    }
    body: dict[str, Any] = {
        "schema": SCHEMA,
        "git_commit": commit,
        "model_identity": model_identity.strip(),
        "limits": limits.payload(),
        "source_closure": sources,
        "evaluation_closure": evaluation,
        "prompt_source_sha256": sources["src/errata/pursue/prompt.py"]["sha256"],
        "direct_prompt_source_sha256": sources[
            "src/errata/pursue/direct_prompt.py"
        ]["sha256"],
        "proposal_schema_sha256": digest_bytes(canonical_bytes(PROPOSAL_SCHEMA)),
        "tool_schema_sha256": digest_bytes(canonical_bytes(tool_descriptions())),
        "case_capsule_control_protocol_sha256": digest_bytes(
            canonical_bytes(CONTROL_PROTOCOL)
        ),
        "evaluation_protocol": json.loads(json.dumps(EVALUATION_PROTOCOL)),
        "claim_gate_status": json.loads(json.dumps(CLAIM_GATE_STATUS)),
        "python": {
            "path": str(python_path),
            "version": _version_command([str(python_path), "--version"]),
            **_file_identity(python_path),
        },
        "codex": {
            "path": str(codex_path),
            "version": _version_command([str(codex_path), "--version"]),
            **_file_identity(codex_path),
        },
    }
    return {**body, "sha256": digest_bytes(canonical_bytes(body))}


def write_candidate_freeze(path: Path, manifest: dict[str, Any]) -> None:
    verify_manifest_envelope(manifest)
    if path.exists():
        if path.read_bytes() != canonical_bytes(manifest) + b"\n":
            raise ValueError("candidate freeze path already has different bytes")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(manifest) + b"\n")


def verify_manifest_envelope(manifest: dict[str, Any]) -> str:
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA:
        raise ValueError("candidate freeze schema differs")
    claimed = manifest.get("sha256")
    body = {key: value for key, value in manifest.items() if key != "sha256"}
    actual = digest_bytes(canonical_bytes(body))
    if not isinstance(claimed, str) or claimed != actual:
        raise ValueError("candidate freeze digest differs")
    limits = manifest.get("limits")
    if not isinstance(limits, dict):
        raise ValueError("candidate freeze limits differ")
    CandidateLimits(
        maximum_model_steps=limits.get("maximum_model_steps"),
        maximum_elapsed_seconds=limits.get("maximum_elapsed_seconds"),
        maximum_changed_files=limits.get("maximum_changed_files"),
        maximum_added_lines=limits.get("maximum_added_lines"),
        maximum_deleted_lines=limits.get("maximum_deleted_lines"),
        primary_cases=limits.get("primary_cases"),
        maximum_attempts=limits.get("maximum_attempts"),
    ).payload()
    if manifest.get("evaluation_protocol") != EVALUATION_PROTOCOL:
        raise ValueError("candidate freeze evaluation protocol differs")
    if manifest.get("claim_gate_status") != CLAIM_GATE_STATUS:
        raise ValueError("candidate freeze claim gate differs")
    if manifest.get("case_capsule_control_protocol_sha256") != digest_bytes(
        canonical_bytes(CONTROL_PROTOCOL)
    ):
        raise ValueError("candidate freeze case capsule control protocol differs")
    return actual


def load_candidate_freeze(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("candidate freeze is not JSON") from exc
    if not isinstance(value, dict) or raw != canonical_bytes(value) + b"\n":
        raise ValueError("candidate freeze is not canonical")
    verify_manifest_envelope(value)
    return value


def verify_candidate_freeze(
    path: Path, *, repo_root: Path, model_identity: str
) -> dict[str, Any]:
    """Fail closed if committed candidate, source, schemas, or runtimes drift."""

    frozen = load_candidate_freeze(path)
    if frozen["model_identity"] != model_identity:
        raise ValueError("candidate freeze model identity differs")
    root = repo_root.resolve(strict=True)
    if _command(["git", "rev-parse", "HEAD"], cwd=root) != frozen["git_commit"]:
        raise ValueError("candidate freeze git commit drifted")
    current_paths = _source_paths(root)
    current = {
        item.relative_to(root).as_posix(): _file_identity(item) for item in current_paths
    }
    if current != frozen["source_closure"]:
        raise ValueError("candidate freeze source closure drifted")
    current_evaluation = {
        item.relative_to(root).as_posix(): _file_identity(item)
        for item in _evaluation_paths(root)
    }
    if current_evaluation != frozen.get("evaluation_closure"):
        raise ValueError("candidate freeze evaluation closure drifted")
    if digest_bytes(canonical_bytes(PROPOSAL_SCHEMA)) != frozen["proposal_schema_sha256"]:
        raise ValueError("candidate freeze proposal schema drifted")
    if digest_bytes(canonical_bytes(tool_descriptions())) != frozen["tool_schema_sha256"]:
        raise ValueError("candidate freeze tool schema drifted")
    if digest_bytes(canonical_bytes(CONTROL_PROTOCOL)) != frozen[
        "case_capsule_control_protocol_sha256"
    ]:
        raise ValueError("candidate freeze case capsule control protocol drifted")
    for name in ("python", "codex"):
        identity = frozen.get(name)
        if not isinstance(identity, dict):
            raise ValueError(f"candidate freeze {name} identity differs")
        executable = Path(identity["path"]).resolve(strict=True)
        if _file_identity(executable) != {
            "bytes": identity["bytes"],
            "sha256": identity["sha256"],
        }:
            raise ValueError(f"candidate freeze {name} executable drifted")
        if _version_command([str(executable), "--version"]) != identity["version"]:
            raise ValueError(f"candidate freeze {name} version drifted")
    return frozen


__all__ = [
    "CandidateLimits",
    "CLAIM_GATE_STATUS",
    "DEFAULT_MAXIMUM_MODEL_STEPS",
    "EVALUATION_PROTOCOL",
    "build_candidate_freeze",
    "canonical_bytes",
    "digest_bytes",
    "load_candidate_freeze",
    "verify_candidate_freeze",
    "verify_manifest_envelope",
    "write_candidate_freeze",
]
