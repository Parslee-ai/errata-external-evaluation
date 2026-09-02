#!/usr/bin/env python3
"""Initialize and independently verify the Lane-A v1.0 custody roots."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile


SCHEMA = "errata.swebench-live-v100-custody-root.v1"
RECEIPT_SCHEMA = "errata.swebench-live-v100-custody-preflight.v1"


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


def fsync_dir(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def write_once(path: Path, raw: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    fsync_dir(path.parent)


def is_temporary(path: Path) -> bool:
    resolved = path.resolve()
    candidates = {Path("/tmp").resolve(), Path("/private/tmp").resolve()}
    candidate = Path(tempfile.gettempdir()).resolve()
    candidates.add(candidate)
    return any(resolved == root or root in resolved.parents for root in candidates)


def checked_roots(primary: Path, mirror: Path) -> tuple[Path, Path]:
    roots = (primary.expanduser().resolve(), mirror.expanduser().resolve())
    if (
        roots[0] == roots[1]
        or roots[0] in roots[1].parents
        or roots[1] in roots[0].parents
    ):
        raise ValueError("custody roots must be distinct and non-nested")
    if any(is_temporary(root) for root in roots):
        raise ValueError("custody roots must not use temporary storage")
    return roots


def initialize(primary: Path, mirror: Path, freeze: Path) -> dict[str, object]:
    roots = checked_roots(primary, mirror)
    freeze_raw = freeze.resolve(strict=True).read_bytes()
    freeze_sha = digest(freeze_raw)
    manifests: list[dict[str, object]] = []
    for role, root in zip(("primary", "mirror"), roots, strict=True):
        if root.exists():
            raise FileExistsError(f"custody root already exists: {root}")
        root.mkdir(parents=True, mode=0o700)
        fsync_dir(root.parent)
        root_hash = digest(str(root).encode("utf-8"))
        canary = canonical(
            {"freeze_sha256": freeze_sha, "role": role, "root_sha256": root_hash}
        ) + b"\n"
        canary_path = root / ".durability-canary"
        write_once(canary_path, canary)
        if canary_path.read_bytes() != canary:
            raise ValueError("durability canary readback differs")
        canary_path.unlink()
        fsync_dir(root)
        body = {
            "schema": SCHEMA,
            "freeze_sha256": freeze_sha,
            "role": role,
            "root_sha256": root_hash,
            "device": root.stat().st_dev,
            "initializer_pid": os.getpid(),
            "canary_sha256": digest(canary),
            "canary_fsynced_read_back_and_removed": True,
        }
        manifest = {**body, "sha256": digest(canonical(body))}
        write_once(root / "custody-manifest.json", canonical(manifest) + b"\n")
        manifests.append(manifest)
    return {"initialized": True, "manifests": manifests}


def read_manifest(
    root: Path, role: str, freeze_sha: str
) -> tuple[dict[str, object], str]:
    path = root / "custody-manifest.json"
    raw = path.read_bytes()
    value = json.loads(raw)
    if raw != canonical(value) + b"\n" or not isinstance(value, dict):
        raise ValueError("custody manifest is not canonical")
    body = {key: item for key, item in value.items() if key != "sha256"}
    if (
        value.get("schema") != SCHEMA
        or value.get("sha256") != digest(canonical(body))
        or value.get("role") != role
        or value.get("freeze_sha256") != freeze_sha
        or value.get("root_sha256") != digest(str(root).encode("utf-8"))
        or value.get("device") != root.stat().st_dev
        or (root / ".durability-canary").exists()
    ):
        raise ValueError("custody manifest verification failed")
    return value, digest(raw)


def verify(
    primary: Path, mirror: Path, freeze: Path, output: Path
) -> dict[str, object]:
    if output.exists():
        raise FileExistsError("custody receipt already exists")
    roots = checked_roots(primary, mirror)
    freeze_sha = digest(freeze.resolve(strict=True).read_bytes())
    rows = [
        read_manifest(root, role, freeze_sha)
        for role, root in zip(("primary", "mirror"), roots, strict=True)
    ]
    initializer_pids = {int(row[0]["initializer_pid"]) for row in rows}
    if len(initializer_pids) != 1 or os.getpid() in initializer_pids:
        raise ValueError("custody roots were not reopened in a separate process")
    body = {
        "schema": RECEIPT_SCHEMA,
        "verified_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "freeze_sha256": freeze_sha,
        "root_count": 2,
        "distinct_non_nested": True,
        "non_temporary": True,
        "cross_process_reopen": True,
        "initializer_pid": initializer_pids.pop(),
        "verifier_pid": os.getpid(),
        "roots": [
            {
                "role": row[0]["role"],
                "root_sha256": row[0]["root_sha256"],
                "device": row[0]["device"],
                "manifest_file_sha256": row[1],
                "canary_sha256": row[0]["canary_sha256"],
            }
            for row in rows
        ],
    }
    receipt = {**body, "sha256": digest(canonical(body))}
    write_once(output, canonical(receipt) + b"\n")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--mirror", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("initialize")
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "initialize":
        result = initialize(args.primary, args.mirror, args.freeze)
    else:
        result = verify(args.primary, args.mirror, args.freeze, args.output)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
