#!/usr/bin/env python3
"""Fetch and verify the predeclared NIST Beacon pulse for the Lane-A draw."""

from __future__ import annotations

import argparse
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import re
from urllib.request import urlopen


SCHEMA = "errata.rung1-nist-beacon-receipt.v1"
BASE = "https://beacon.nist.gov/beacon/2.0"


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


def _timestamp_ms(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() * 1000)


def _validate_pulse(pulse: object, *, strictly_after_ms: int) -> dict[str, object]:
    if not isinstance(pulse, dict):
        raise ValueError("NIST response lacks a pulse object")
    timestamp = pulse.get("timeStamp")
    output = pulse.get("outputValue")
    uri = pulse.get("uri")
    if (
        pulse.get("version") != "2.0"
        or pulse.get("statusCode") != 0
        or pulse.get("period") != 60_000
        or not isinstance(timestamp, str)
        or _timestamp_ms(timestamp) <= strictly_after_ms
        or not isinstance(output, str)
        or not re.fullmatch(r"[0-9A-F]{128}", output)
        or not isinstance(uri, str)
        or not uri.startswith(f"{BASE}/chain/")
        or not isinstance(pulse.get("signatureValue"), str)
        or not isinstance(pulse.get("certificateId"), str)
    ):
        raise ValueError("NIST pulse fails the frozen v2 shape or time boundary")
    return pulse


def fetch(
    *, strictly_after_ms: int, release_url: str, output: Path
) -> dict[str, object]:
    if output.exists():
        raise ValueError("beacon receipt already exists")
    request_url = f"{BASE}/pulse/time/next/{strictly_after_ms}"
    with urlopen(request_url, timeout=30) as response:  # noqa: S310 - exact frozen HTTPS host
        raw = response.read(1_000_001)
    if len(raw) > 1_000_000:
        raise ValueError("NIST beacon response exceeds one megabyte")
    response_value = json.loads(raw)
    pulse = _validate_pulse(
        response_value.get("pulse") if isinstance(response_value, dict) else None,
        strictly_after_ms=strictly_after_ms,
    )
    entropy = bytes.fromhex(str(pulse["outputValue"]))
    body = {
        "schema": SCHEMA,
        "rule": "first NIST Beacon 2.0 pulse strictly after the immutable v0.4.1 release publishedAt",
        "release_url": release_url,
        "strictly_after_unix_ms": strictly_after_ms,
        "request_url": request_url,
        "raw_response_bytes": len(raw),
        "raw_response_sha256": sha256(raw).hexdigest(),
        "beacon_entropy_sha256": sha256(entropy).hexdigest(),
        "pulse": pulse,
    }
    result = {**body, "sha256": _digest(body)}
    output.write_bytes(canonical_bytes(result) + b"\n")
    return result


def verify(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if raw != canonical_bytes(value) + b"\n":
        raise ValueError("NIST beacon receipt bytes are not canonical")
    body = {key: item for key, item in value.items() if key != "sha256"}
    if value.get("schema") != SCHEMA or value.get("sha256") != _digest(body):
        raise ValueError("NIST beacon receipt identity differs")
    _validate_pulse(
        value.get("pulse"), strictly_after_ms=value["strictly_after_unix_ms"]
    )
    entropy = bytes.fromhex(value["pulse"]["outputValue"])
    if value.get("beacon_entropy_sha256") != sha256(entropy).hexdigest():
        raise ValueError("NIST beacon entropy digest differs")
    expected_url = f"{BASE}/pulse/time/next/{value['strictly_after_unix_ms']}"
    if value.get("request_url") != expected_url:
        raise ValueError("NIST beacon request URL differs")
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    fetch_parser = commands.add_parser("fetch")
    fetch_parser.add_argument("--strictly-after-unix-ms", type=int, required=True)
    fetch_parser.add_argument("--release-url", required=True)
    fetch_parser.add_argument("--output", type=Path, required=True)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "fetch":
        result = fetch(
            strictly_after_ms=args.strictly_after_unix_ms,
            release_url=args.release_url,
            output=args.output,
        )
    else:
        result = verify(args.receipt)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
