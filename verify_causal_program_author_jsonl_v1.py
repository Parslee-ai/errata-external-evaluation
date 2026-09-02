#!/usr/bin/env python3
"""Disclosure-safe conformance verifier for an outside author's JSONL ABI."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from errata.north_star.causal_program_external_v1 import canonical_bytes, verify_author_jsonl
except ModuleNotFoundError:  # public kit places the disclosure-safe module beside this script
    from causal_program_external_v1 import canonical_bytes, verify_author_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("jsonl", type=Path)
    args = parser.parse_args()
    receipt = verify_author_jsonl(args.jsonl.read_bytes().splitlines(keepends=True))
    print(canonical_bytes(receipt).decode(), end="")


if __name__ == "__main__":
    main()
