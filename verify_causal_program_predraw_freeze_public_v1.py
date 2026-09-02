#!/usr/bin/env python3
"""Standalone semantic verifier for the public Lane-B root-free freeze."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from errata.north_star.causal_program_external_v1 import (
        canonical_bytes,
        verify_predraw_freeze,
    )
except ModuleNotFoundError:  # public kit places the disclosure-safe module beside this script
    from causal_program_external_v1 import canonical_bytes, verify_predraw_freeze


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("freeze", type=Path)
    args = parser.parse_args()
    raw = args.freeze.read_bytes()
    try:
        value = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("causal-program external predraw freeze is not JSON") from exc
    if not isinstance(value, dict) or canonical_bytes(value) != raw:
        raise ValueError("causal-program external predraw freeze bytes are not canonical")
    verify_predraw_freeze(value)
    print(canonical_bytes(value).decode(), end="")


if __name__ == "__main__":
    main()
