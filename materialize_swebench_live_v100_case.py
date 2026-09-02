#!/usr/bin/env python3
"""Materialize one frozen task into private evaluator custody without printing it."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess

import pyarrow.parquet as parquet


DATASET_REVISION = "dc443bc2574733152ba51b4d4457ccd38921613b"


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--ranking", type=Path, required=True)
    parser.add_argument("--instance-id", required=True)
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--mirror", type=Path, required=True)
    args = parser.parse_args()
    relative = Path("private/cases") / f"{args.instance_id}.jsonl"
    outputs = (args.primary / relative, args.mirror / relative)
    if any(path.exists() for path in outputs):
        raise FileExistsError("private case output already exists")
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=args.dataset,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout.strip()
    if head != DATASET_REVISION:
        raise ValueError("dataset revision differs")
    ranking = json.loads(args.ranking.read_bytes())
    ranked = next(
        row
        for row in ranking["ranked_rows"]
        if row["instance_id"] == args.instance_id
    )
    if not ranked["static_eligible"]:
        raise ValueError("requested task is not statically eligible")
    found = None
    for path in sorted((args.dataset / "data").glob("*.parquet")):
        table = parquet.read_table(path)
        for row in table.to_pylist():
            if row.get("instance_id") == args.instance_id:
                if found is not None:
                    raise ValueError("instance ID repeats in frozen dataset")
                found = row
    if found is None:
        raise ValueError("instance ID absent from frozen dataset")
    checks = {
        "base_commit": found["base_commit"] == ranked["base_commit"],
        "problem_statement_sha256": digest(
            found["problem_statement"].encode("utf-8")
        )
        == ranked["problem_statement_sha256"],
        "accepted_patch_sha256": digest(found["patch"].encode("utf-8"))
        == ranked["accepted_patch_sha256"],
        "test_patch_sha256": digest(found["test_patch"].encode("utf-8"))
        == ranked["test_patch_sha256"],
    }
    if not all(checks.values()):
        raise ValueError("private task differs from redacted ranking")
    raw = canonical(found) + b"\n"
    for path in outputs:
        write_once(path, raw)
    print(
        json.dumps(
            {
                "instance_id": args.instance_id,
                "private_case_bytes": len(raw),
                "private_case_sha256": digest(raw),
                "dual_root_paths_sha256": [
                    digest(str(path.resolve()).encode("utf-8")) for path in outputs
                ],
                "checks": checks,
                "task_content_printed": False,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
