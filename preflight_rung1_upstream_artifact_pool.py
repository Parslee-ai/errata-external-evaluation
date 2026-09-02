#!/usr/bin/env python3
"""Run source/test split preflight for the external-artifact case pool."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
from typing import Any

from rung1_upstream_artifact_pool import canonical_bytes, verify


SCHEMA = "errata.rung1-upstream-artifact-preflight.v1"


@dataclass(frozen=True, slots=True)
class Plan:
    baseline: tuple[str, ...]
    regression: tuple[str, ...]


PLANS = {
    "pallets--click--issue-3802": Plan(
        ("tests/test_commands.py::test_other_command_invoke",),
        (
            "tests/test_abort_interrupt.py::test_interrupt_while_reporting_abort",
            "tests/test_abort_interrupt.py::test_interrupt_while_reporting_error",
            "tests/test_abort_interrupt.py::test_interrupt_while_exiting_after_success",
        ),
    ),
    "pallets--click--issue-3572": Plan(
        ("tests/test_termui.py::test_confirmation_prompt",),
        ("tests/test_termui.py::test_prompt_and_confirm_ansi_respects_color",),
    ),
    "pallets--click--issue-3571": Plan(
        ("tests/test_termui.py::test_progressbar_time_per_iteration",),
        ("tests/test_termui.py::test_progressbar_lands_on_final_position",),
    ),
    "pytest-dev--pytest--issue-14864": Plan(
        ("testing/test_pathlib.py::test_samefile_false_negatives",),
        ("testing/test_pathlib.py::test_samefile_nofollow_zero_file_id",),
    ),
    "pydantic--pydantic--issue-13664": Plan(
        ("tests/test_json_schema.py::test_by_alias",),
        (
            "tests/test_json_schema.py::test_date_types_ser_json_temporal",
            "tests/test_json_schema.py::test_date_types_ser_json_temporal_matches_serialized_output",
            "tests/test_json_schema.py::test_timedelta_ser_json_temporal_takes_precedence",
        ),
    ),
    "pydantic--pydantic--issue-13692": Plan(
        ("tests/test_types.py::test_custom_serializer_override_secret_str",),
        ("tests/test_types.py::test_secret_str_none",),
    ),
    "pydantic--pydantic--issue-13687": Plan(
        ("tests/test_validate_call.py::test_validate_by_name",),
        (
            "tests/test_validate_call.py::test_populate_by_name",
            "tests/test_experimental_arguments_schema.py::test_populate_by_name",
        ),
    ),
    "pydantic--pydantic--issue-13645": Plan(
        (
            "tests/test_edge_cases.py::test_interconnected_models_build_in_linear_time",
        ),
        ("tests/test_edge_cases.py::test_unhasbable_generic_alias",),
    ),
}


def _run(
    argv: list[str], *, cwd: Path, env: dict[str, str] | None = None
) -> dict[str, Any]:
    completed = subprocess.run(
        argv,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=300,
    )
    return {
        "argv": argv,
        "returncode": completed.returncode,
        "output_bytes": len(completed.stdout),
        "output_sha256": sha256(completed.stdout).hexdigest(),
        "output": completed.stdout.decode("utf-8", errors="replace"),
    }


def _patch(repo: Path, base: str, merge: str, paths: list[str]) -> bytes:
    completed = subprocess.run(
        ["git", "diff", base, merge, "--", *paths],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
    )
    if not completed.stdout:
        raise ValueError("preflight patch is empty")
    return completed.stdout


def _apply(workspace: Path, patch: bytes) -> None:
    subprocess.run(
        ["git", "apply", "-"],
        cwd=workspace,
        input=patch,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
    )


def _extract(repo: Path, revision: str, destination: Path) -> None:
    archive = subprocess.run(
        ["git", "archive", revision],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=120,
    ).stdout
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as bundle:
        bundle.extractall(destination, filter="data")


def _pytest_version_shim(workspace: Path, case_id: str) -> dict[str, Any] | None:
    if not case_id.startswith("pytest-dev--pytest--"):
        return None
    content = (
        "version = __version__ = '9.2.0.dev0'\n"
        "version_tuple = __version_tuple__ = (9, 2, 0, 'dev0')\n"
        "commit_id = __commit_id__ = None\n"
    ).encode("ascii")
    path = workspace / "src/_pytest/_version.py"
    path.write_bytes(content)
    return {
        "path": "src/_pytest/_version.py",
        "bytes": len(content),
        "sha256": sha256(content).hexdigest(),
    }


def preflight(
    pool_path: Path, repos: dict[str, Path], python: Path, output: Path
) -> dict[str, Any]:
    if output.exists():
        raise ValueError("preflight output already exists")
    pool = verify(pool_path)
    if set(PLANS) != {case["case_id"] for case in pool["cases"]}:
        raise ValueError("preflight plan and pool differ")
    rows = []
    for case in pool["cases"]:
        case_id = case["case_id"]
        repo = repos.get(case["repository"])
        if repo is None:
            raise ValueError(f"repository root missing for {case['repository']}")
        plan = PLANS[case_id]
        with tempfile.TemporaryDirectory(prefix="errata-upstream-preflight-") as tmp:
            workspace = Path(tmp) / "workspace"
            workspace.mkdir()
            _extract(repo, case["gold"]["base_sha"], workspace)
            shim = _pytest_version_shim(workspace, case_id)
            env = dict(os.environ)
            env["PYTHONPATH"] = os.pathsep.join(
                (str(workspace / "src"), str(workspace))
            )
            prefix = [str(python), "-m", "pytest", "-q"]
            baseline_before = _run(prefix + list(plan.baseline), cwd=workspace, env=env)
            test_patch = _patch(
                repo,
                case["gold"]["base_sha"],
                case["gold"]["merge_sha"],
                case["gold"]["test_paths"],
            )
            implementation_patch = _patch(
                repo,
                case["gold"]["base_sha"],
                case["gold"]["merge_sha"],
                case["gold"]["implementation_paths"],
            )
            _apply(workspace, test_patch)
            regression_at_base = _run(
                prefix + list(plan.regression), cwd=workspace, env=env
            )
            _apply(workspace, implementation_patch)
            regression_at_gold = _run(
                prefix + list(plan.regression), cwd=workspace, env=env
            )
            baseline_at_gold = _run(
                prefix + list(plan.baseline), cwd=workspace, env=env
            )
        qualified = (
            baseline_before["returncode"] == 0
            and regression_at_base["returncode"] != 0
            and regression_at_gold["returncode"] == 0
            and baseline_at_gold["returncode"] == 0
        )
        rows.append(
            {
                "case_id": case_id,
                "case_sha256": case["sha256"],
                "qualified": qualified,
                "test_patch_bytes": len(test_patch),
                "test_patch_sha256": sha256(test_patch).hexdigest(),
                "implementation_patch_bytes": len(implementation_patch),
                "implementation_patch_sha256": sha256(implementation_patch).hexdigest(),
                "environment_shim": shim,
                "baseline_before": baseline_before,
                "regression_at_base": regression_at_base,
                "regression_at_gold": regression_at_gold,
                "baseline_at_gold": baseline_at_gold,
            }
        )
    body = {
        "schema": SCHEMA,
        "pool_sha256": pool["sha256"],
        "python": {
            "launcher_path": str(python),
            "binary_path": str(python.resolve()),
            "binary_sha256": sha256(python.resolve().read_bytes()).hexdigest(),
        },
        "all_qualified": all(row["qualified"] for row in rows),
        "rows": rows,
    }
    result = {**body, "sha256": sha256(canonical_bytes(body)).hexdigest()}
    output.write_bytes(canonical_bytes(result) + b"\n")
    return result


def verify_result(pool_path: Path, result_path: Path) -> dict[str, Any]:
    pool = verify(pool_path)
    raw = result_path.read_bytes()
    result = json.loads(raw)
    if raw != canonical_bytes(result) + b"\n":
        raise ValueError("preflight bytes are not canonical")
    if result.get("schema") != SCHEMA or result.get("pool_sha256") != pool["sha256"]:
        raise ValueError("preflight schema or pool binding differs")
    body = {key: value for key, value in result.items() if key != "sha256"}
    if result.get("sha256") != sha256(canonical_bytes(body)).hexdigest():
        raise ValueError("preflight digest differs")
    if {row.get("case_id") for row in result.get("rows", [])} != set(PLANS):
        raise ValueError("preflight denominator differs")
    for row in result["rows"]:
        checks = [
            row["baseline_before"]["returncode"] == 0,
            row["regression_at_base"]["returncode"] != 0,
            row["regression_at_gold"]["returncode"] == 0,
            row["baseline_at_gold"]["returncode"] == 0,
        ]
        if row.get("qualified") is not all(checks):
            raise ValueError("preflight qualification derivation differs")
        for key in (
            "baseline_before",
            "regression_at_base",
            "regression_at_gold",
            "baseline_at_gold",
        ):
            output_bytes = row[key]["output"].encode("utf-8")
            if (
                row[key]["output_bytes"] != len(output_bytes)
                or row[key]["output_sha256"] != sha256(output_bytes).hexdigest()
            ):
                raise ValueError("preflight retained output differs")
    if result.get("all_qualified") is not all(
        row["qualified"] for row in result["rows"]
    ):
        raise ValueError("preflight aggregate differs")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pool", type=Path, required=True)
    parser.add_argument("--python", type=Path)
    parser.add_argument("--repo", action="append", help="OWNER/REPO=/path")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify-result", type=Path)
    args = parser.parse_args()
    if args.verify_result is not None:
        if any(value is not None for value in (args.python, args.repo, args.output)):
            raise SystemExit(
                "--verify-result cannot be combined with execution arguments"
            )
        result = verify_result(args.pool, args.verify_result)
        print(
            json.dumps(
                {"all_qualified": result["all_qualified"], "sha256": result["sha256"]},
                indent=2,
                sort_keys=True,
            )
        )
        return
    if args.python is None or args.repo is None or args.output is None:
        raise SystemExit("execution requires --python, --repo, and --output")
    repos = {}
    for item in args.repo:
        name, separator, path = item.partition("=")
        if not separator or name in repos:
            raise SystemExit("--repo must be a unique OWNER/REPO=/path mapping")
        repos[name] = Path(path).resolve(strict=True)
    python = Path(os.path.abspath(args.python))
    if not python.exists():
        raise SystemExit("--python does not exist")
    result = preflight(args.pool, repos, python, args.output)
    print(
        json.dumps(
            {"all_qualified": result["all_qualified"], "sha256": result["sha256"]},
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
