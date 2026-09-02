#!/usr/bin/env python3
"""Build and verify deterministic controls from a retained Codex transcript."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from errata.pursue.upstream_artifact_controls import (
    CORRUPTED_SCHEMA,
    MATCHED_SCHEMA,
    canonical_bytes,
    corrupted_information_packet,
    matched_activity_packet,
    parse_codex_jsonl,
    validate_corruption,
    validate_matched,
)


def _write_once(path: Path, value: object) -> None:
    raw = canonical_bytes(value) + b"\n"
    if path.exists():
        if path.read_bytes() != raw:
            raise ValueError(
                "control packet output already exists with different bytes"
            )
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def main() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build")
    build.add_argument(
        "--arm", choices=("matched-activity", "corrupted-information"), required=True
    )
    build.add_argument("--transcript", type=Path, required=True)
    build.add_argument("--case-sha256")
    build.add_argument("--output", type=Path, required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--packet", type=Path, required=True)
    verify.add_argument("--transcript", type=Path)
    args = parser.parse_args()

    if args.command == "build":
        events = parse_codex_jsonl(args.transcript.read_bytes())
        if args.arm == "matched-activity":
            if args.case_sha256 is not None:
                raise SystemExit("matched activity does not accept --case-sha256")
            packet = matched_activity_packet(events)
        else:
            if args.case_sha256 is None:
                raise SystemExit("corrupted information requires --case-sha256")
            packet = corrupted_information_packet(events, case_sha256=args.case_sha256)
        _write_once(args.output, packet)
        print(packet["sha256"])
        return

    raw = args.packet.read_bytes()
    packet = json.loads(raw)
    if raw != canonical_bytes(packet) + b"\n":
        raise ValueError("control packet bytes are not canonical")
    if packet.get("schema") == MATCHED_SCHEMA:
        if args.transcript is not None:
            raise SystemExit("matched packet verification does not accept --transcript")
        validate_matched(packet)
    elif packet.get("schema") == CORRUPTED_SCHEMA:
        if args.transcript is None:
            raise SystemExit("corruption verification requires --transcript")
        events = parse_codex_jsonl(args.transcript.read_bytes())
        source = [
            row
            for row in events
            if (
                isinstance(row.get("payload"), dict)
                and row.get("kind") == "tool_result"
            )
            or (
                isinstance(row.get("item"), dict)
                and row["item"].get("type")
                in {"command_execution", "file_read", "mcp_tool_call", "web_search"}
            )
        ]
        validate_corruption(source, packet)
    else:
        raise ValueError("control packet schema differs")
    print(packet["sha256"])


if __name__ == "__main__":
    main()
