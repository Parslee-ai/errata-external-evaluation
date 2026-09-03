#!/usr/bin/env python3
"""Record a frozen image-registration failure without rerunning the case."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess


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


def run(command: list[str]) -> dict[str, object]:
    completed = subprocess.run(command, capture_output=True, text=True)
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=Path, required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--mode", choices=("gold", "empty"), required=True)
    parser.add_argument("--repetition", type=int, required=True)
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--mirror", type=Path, required=True)
    args = parser.parse_args()

    row = json.loads(args.case.read_text(encoding="utf-8"))
    if row["docker_image"] != args.image:
        raise ValueError("image does not match the private case")
    local = run(["docker", "image", "inspect", args.image])
    registry = run(["docker", "manifest", "inspect", "--verbose", args.image])
    if local["returncode"] == 0:
        raise ValueError("image is registered locally; terminal state is invalid")
    if registry["returncode"] != 0:
        raise ValueError("registry manifest is unavailable; wrong terminal class")
    manifest = json.loads(str(registry["stdout"]))

    relative = Path("preflight") / row["instance_id"] / (
        f"{args.mode}-{args.repetition}"
    )
    result_paths = [args.primary / relative / "result.json", args.mirror / relative / "result.json"]
    if any(path.exists() for path in result_paths):
        raise FileExistsError("a scored preflight result already exists")

    descriptor = manifest["Descriptor"]
    layer_sizes = [item["size"] for item in manifest["SchemaV2Manifest"]["layers"]]
    body = {
        "schema": "errata.swebench-live-v100-preflight-image-registration-failure.v1",
        "instance_id": row["instance_id"],
        "mode": args.mode,
        "repetition": args.repetition,
        "case_file_sha256": digest(args.case.read_bytes()),
        "image": args.image,
        "observed_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "local_inspection": local,
        "registry_manifest": {
            "digest": descriptor["digest"],
            "media_type": descriptor["mediaType"],
            "platform": descriptor["platform"],
            "compressed_layer_bytes": sum(layer_sizes),
            "layer_count": len(layer_sizes),
        },
        "scored_result_absent_in_both_roots": True,
        "retry_or_replacement": False,
        "decision": "ineligible_image_registration_failure",
    }
    receipt = {**body, "sha256": digest(canonical(body))}
    raw = canonical(receipt) + b"\n"
    for root in (args.primary, args.mirror):
        write_once(root / relative / "image-registration-failure.json", raw)
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
