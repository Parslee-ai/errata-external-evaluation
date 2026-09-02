#!/usr/bin/env python3
"""Run the exact official evaluator for one private v1.0 task."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import sys


def canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def write_once(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def adjudicate(status: dict[str, str], row: dict[str, object]) -> dict[str, object]:
    passed = {name for name, value in status.items() if "pass" in value.lower()}
    failed = {name for name, value in status.items() if "fail" in value.lower()}
    f2p = set(row["FAIL_TO_PASS"])
    p2p = set(row["PASS_TO_PASS"])
    return {
        "resolved": f2p.issubset(passed) and not (p2p & failed),
        "fail_to_pass_success": sorted(f2p & passed),
        "fail_to_pass_failure": sorted(f2p & failed),
        "pass_to_pass_failure": sorted(p2p & failed),
        "parsed_status_count": len(status),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evaluator", type=Path, required=True)
    parser.add_argument("--case", type=Path, required=True)
    parser.add_argument("--mode", choices=("gold", "empty"), required=True)
    parser.add_argument("--repetition", type=int, required=True)
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--mirror", type=Path, required=True)
    args = parser.parse_args()
    row = json.loads(args.case.read_text(encoding="utf-8"))
    evaluator = args.evaluator.resolve(strict=True)
    sys.path.insert(0, str(evaluator))
    sys.path.insert(0, str(evaluator / "launch"))
    from evaluation.evaluation import evaluate_instance

    relative = Path("preflight") / row["instance_id"] / (
        f"{args.mode}-{args.repetition}"
    )
    outputs = [args.primary / relative, args.mirror / relative]
    if any((root / "result.json").exists() for root in outputs):
        raise FileExistsError("preflight output already exists")
    run_dir = args.primary / "staging" / relative
    run_dir.mkdir(parents=True, exist_ok=False)
    solution_patch = row["patch"] if args.mode == "gold" else ""
    status = evaluate_instance(
        row["instance_id"],
        row["docker_image"],
        " ; ".join(row.get("rebuild_cmds", [])),
        " ; ".join(row.get("test_cmds", [])),
        " ; ".join(row.get("print_cmds", [])),
        row["test_patch"],
        solution_patch,
        row["log_parser"],
        "linux",
        str(run_dir),
    )
    decision = adjudicate(status, row)
    if args.mode == "empty":
        decision["empty_patch_gate"] = (
            not decision["resolved"]
            and bool(decision["fail_to_pass_failure"])
            and not decision["pass_to_pass_failure"]
        )
    body = {
        "schema": "errata.swebench-live-v100-case-preflight.v1",
        "instance_id": row["instance_id"],
        "mode": args.mode,
        "repetition": args.repetition,
        "case_file_sha256": digest(args.case.read_bytes()),
        "evaluator_commit": "3225e471b7540a2c2b703c7bfbed80571f653f3b",
        "decision": decision,
        "status_sha256": digest(canonical(status)),
        "log_sha256": digest((run_dir / "post_patch_log.txt").read_bytes()),
    }
    result = {**body, "sha256": digest(canonical(body))}
    artifacts = {
        "result.json": canonical(result) + b"\n",
        "post_patch_log.txt": (run_dir / "post_patch_log.txt").read_bytes(),
        "status.json": (run_dir / "status.json").read_bytes(),
    }
    for root in outputs:
        for name, raw in artifacts.items():
            write_once(root / name, raw)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
