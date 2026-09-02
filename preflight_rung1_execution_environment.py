#!/usr/bin/env python3
"""Fail before reservation unless cognition and contained Python both execute."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import tempfile

from errata.pursue.authority import AuthorityPolicy
from errata.pursue.lane_a_freeze import canonical_bytes
from errata.pursue.model import CodexExecModel
from errata.pursue.protocol import ProposedAction
from errata.pursue.tools import ToolExecutor


SCHEMA = "errata.rung1-execution-environment-preflight.v1"


def _digest(value: object) -> str:
    return sha256(canonical_bytes(value)).hexdigest()


def run(output: Path) -> dict[str, object]:
    if output.exists():
        raise ValueError("execution preflight output already exists")
    launcher_dir = str(Path(sys.executable).absolute().parent)
    current_path = os.environ.get("PATH", "/usr/bin:/bin").split(os.pathsep)
    os.environ["PATH"] = os.pathsep.join(
        [launcher_dir, *(entry for entry in current_path if entry != launcher_dir)]
    )
    with tempfile.TemporaryDirectory(prefix="errata-rung1-runtime-preflight-") as raw:
        root = Path(raw)
        workspace = root / "workspace"
        runtime = root / "runtime"
        workspace.mkdir()
        (workspace / "test_preflight.py").write_text(
            "import unittest\n\n"
            "class TestRuntime(unittest.TestCase):\n"
            "    def test_runtime(self):\n"
            "        self.assertEqual(2 + 2, 4)\n",
            encoding="utf-8",
        )
        executor = ToolExecutor(
            AuthorityPolicy(workspace, allow_local_writes=True),
            runtime_dir=runtime,
        )
        command = executor.execute(
            ProposedAction(
                tool="run_command",
                arguments={
                    "argv": ["python", "-m", "unittest", "-q", "test_preflight.py"],
                    "cwd": ".",
                    "effect": "local_write",
                    "network": "none",
                    "environment": {"PYTHONDONTWRITEBYTECODE": "1"},
                    "timeout_seconds": 60,
                },
            )
        )
        if not command.get("ok") or command.get("exit_code") != 0:
            raise RuntimeError(f"contained Python preflight failed: {command}")
        response = CodexExecModel().complete(
            'Return exactly this JSON object and nothing else: {"status":"ready-v1"}'
        )
        try:
            cognition = json.loads(response)
        except json.JSONDecodeError as exc:
            raise RuntimeError("cognition preflight did not return JSON") from exc
        if cognition != {"status": "ready-v1"}:
            raise RuntimeError("cognition preflight response differs")
        body: dict[str, object] = {
            "schema": SCHEMA,
            "python_launcher": sys.executable,
            "python_version": sys.version,
            "contained_command": {
                "argv": command["argv"],
                "containment": command["containment"],
                "exit_code": command["exit_code"],
                "network": command["network"],
                "output_sha256": sha256(command["output"].encode()).hexdigest(),
            },
            "cognition": {
                "model_identity": "codex-exec:gpt-5.6-sol",
                "response_sha256": sha256(response.encode()).hexdigest(),
                "status": cognition["status"],
            },
            "retained_secrets": False,
            "case_information_supplied": False,
        }
        result = {**body, "sha256": _digest(body)}
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(canonical_bytes(result) + b"\n")
        return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.output), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
