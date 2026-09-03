#!/usr/bin/env python3
"""Record an over-limit SWE-bench-Live preflight without rerunning it."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess


LIMIT_SECONDS = 3 * 60 * 60


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


def parse_utc(value: str) -> datetime:
    normalized = value.strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


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
    parser.add_argument("--instance-id", required=True)
    parser.add_argument("--mode", choices=("gold", "empty"), required=True)
    parser.add_argument("--repetition", type=int, required=True)
    parser.add_argument("--container", required=True)
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--mirror", type=Path, required=True)
    args = parser.parse_args()

    raw_inspect = subprocess.run(
        ["docker", "inspect", args.container],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    inspected = json.loads(raw_inspect)
    if len(inspected) != 1:
        raise ValueError("expected exactly one container")
    container = inspected[0]
    started_at = parse_utc(container["State"]["StartedAt"])
    observed_at = datetime.now(timezone.utc)
    elapsed_seconds = int((observed_at - started_at).total_seconds())
    if elapsed_seconds < LIMIT_SECONDS:
        raise ValueError("container has not exceeded the frozen host limit")

    relative = Path("preflight") / args.instance_id / (
        f"{args.mode}-{args.repetition}"
    )
    result_paths = [args.primary / relative / "result.json", args.mirror / relative / "result.json"]
    if any(path.exists() for path in result_paths):
        raise FileExistsError("a scored preflight result already exists")

    body = {
        "schema": "errata.swebench-live-v100-preflight-timeout.v1",
        "instance_id": args.instance_id,
        "mode": args.mode,
        "repetition": args.repetition,
        "terminal": "host_timeout",
        "frozen_limit_seconds": LIMIT_SECONDS,
        "observed_elapsed_seconds_from_container_start": elapsed_seconds,
        "observed_at": observed_at.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "container": {
            "name": args.container,
            "image": container["Config"]["Image"],
            "image_id": container["Image"],
            "started_at": container["State"]["StartedAt"],
            "state": container["State"]["Status"],
            "running": container["State"]["Running"],
            "oom_killed": container["State"]["OOMKilled"],
        },
        "scored_result_absent_in_both_roots": True,
        "retry_or_replacement": False,
        "decision": "ineligible_host_timeout",
    }
    receipt = {**body, "sha256": digest(canonical(body))}
    raw_receipt = canonical(receipt) + b"\n"
    for root in (args.primary, args.mirror):
        write_once(root / relative / "timeout.json", raw_receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
