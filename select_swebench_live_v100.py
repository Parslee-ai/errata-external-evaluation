#!/usr/bin/env python3
"""Create or verify the redacted deterministic Lane-A v1.0 task ranking."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from typing import Any

import pyarrow.parquet as parquet


SCHEMA = "errata.swebench-live-v100-ranking.v1"
DATASET_REVISION = "dc443bc2574733152ba51b4d4457ccd38921613b"
MAXIMUM_SCAN = 64
CUTOFF = datetime(2026, 2, 17, tzinfo=timezone.utc)
EXCLUDED_REPOSITORIES = {
    "aio-libs/aiohttp",
    "aio-libs/multidict",
    "aio-libs/yarl",
    "astral-sh/ruff",
    "celery/celery",
    "encode/httpx",
    "encode/starlette",
    "fastapi/fastapi",
    "pallets/click",
    "pallets/flask",
    "pallets/itsdangerous",
    "pallets/jinja",
    "pallets/werkzeug",
    "psf/black",
    "pycqa/flake8",
    "pycqa/isort",
    "pydantic/pydantic",
    "pypa/packaging",
    "pypa/pip",
    "pytest-dev/pluggy",
    "pytest-dev/pytest",
    "python-attrs/attrs",
    "python-trio/trio",
    "sqlalchemy/sqlalchemy",
    "sqlfluff/sqlfluff",
    "textualize/rich",
    "tox-dev/tox",
    "urllib3/urllib3",
}
REQUIRED = (
    "instance_id",
    "repo",
    "base_commit",
    "patch",
    "test_patch",
    "problem_statement",
    "FAIL_TO_PASS",
    "PASS_TO_PASS",
    "docker_image",
)


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


def parse_created_at(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def git_head(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def read_pulse(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    value = json.loads(raw)
    body = {key: item for key, item in value.items() if key != "sha256"}
    if (
        raw != canonical(value) + b"\n"
        or value.get("sha256") != digest(canonical(body))
        or value.get("pulse", {}).get("chainIndex") != 2
        or value.get("pulse", {}).get("pulseIndex") != 1924372
    ):
        raise ValueError("draw receipt identity differs")
    return value, bytes.fromhex(value["pulse"]["outputValue"])


def create(dataset: Path, pulse_path: Path, output: Path) -> dict[str, Any]:
    if output.exists():
        raise FileExistsError("ranking output already exists")
    dataset = dataset.resolve(strict=True)
    if git_head(dataset) != DATASET_REVISION:
        raise ValueError("dataset revision differs from freeze")
    pulse, entropy = read_pulse(pulse_path.resolve(strict=True))
    rows: list[tuple[str, str, dict[str, Any]]] = []
    parquet_files: list[dict[str, object]] = []
    for path in sorted((dataset / "data").glob("*.parquet")):
        raw_hash = digest(path.read_bytes())
        parquet_files.append(
            {"path": path.name, "bytes": path.stat().st_size, "sha256": raw_hash}
        )
        language = path.name.split("-", 1)[0]
        table = parquet.read_table(path)
        for row in table.to_pylist():
            instance_id = row.get("instance_id")
            if not isinstance(instance_id, str) or not instance_id:
                continue
            rank_digest = digest(entropy + b"\0" + instance_id.encode("utf-8"))
            rows.append((rank_digest, instance_id, {**row, "language": language}))
    rows.sort(key=lambda item: (item[0], item[1].encode("utf-8")))
    ranked: list[dict[str, object]] = []
    for rank, (rank_digest, instance_id, row) in enumerate(
        rows[:MAXIMUM_SCAN], start=1
    ):
        reasons: list[str] = []
        for field in REQUIRED:
            value = row.get(field)
            if value is None or value == "" or value == []:
                reasons.append(f"missing-{field}")
        created_at = row.get("created_at")
        try:
            created = parse_created_at(str(created_at))
        except ValueError:
            reasons.append("invalid-created-at")
            created = None
        if created is not None and created < CUTOFF:
            reasons.append("before-cutoff")
        repo = str(row.get("repo", ""))
        if repo.casefold() in EXCLUDED_REPOSITORIES:
            reasons.append("prior-errata-repository")
        ranked.append(
            {
                "rank": rank,
                "rank_sha256": rank_digest,
                "language": row["language"],
                "instance_id": instance_id,
                "repository": repo,
                "created_at": created_at,
                "base_commit": row.get("base_commit"),
                "docker_image": row.get("docker_image"),
                "problem_statement_sha256": digest(
                    str(row.get("problem_statement", "")).encode("utf-8")
                ),
                "accepted_patch_sha256": digest(
                    str(row.get("patch", "")).encode("utf-8")
                ),
                "test_patch_sha256": digest(
                    str(row.get("test_patch", "")).encode("utf-8")
                ),
                "fail_to_pass_count": len(row.get("FAIL_TO_PASS") or []),
                "pass_to_pass_count": len(row.get("PASS_TO_PASS") or []),
                "static_eligible": not reasons,
                "static_rejection_reasons": reasons,
            }
        )
    body = {
        "schema": SCHEMA,
        "dataset_revision": DATASET_REVISION,
        "dataset_row_count": len(rows),
        "dataset_files": parquet_files,
        "pulse_receipt_sha256": digest(pulse_path.read_bytes()),
        "pulse_index": pulse["pulse"]["pulseIndex"],
        "ranking_rule": "SHA256(pulse_output || 0x00 || UTF8(instance_id))",
        "maximum_scan": MAXIMUM_SCAN,
        "ranked_rows": ranked,
        "task_content_disclosed": False,
    }
    result = {**body, "sha256": digest(canonical(body))}
    output.write_bytes(canonical(result) + b"\n")
    return result


def verify(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    body = {key: item for key, item in value.items() if key != "sha256"}
    if (
        raw != canonical(value) + b"\n"
        or value.get("schema") != SCHEMA
        or value.get("sha256") != digest(canonical(body))
        or len(value.get("ranked_rows", [])) != MAXIMUM_SCAN
    ):
        raise ValueError("ranking receipt verification failed")
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    create_parser = commands.add_parser("create")
    create_parser.add_argument("--dataset", type=Path, required=True)
    create_parser.add_argument("--pulse", type=Path, required=True)
    create_parser.add_argument("--output", type=Path, required=True)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "create":
        result = create(args.dataset, args.pulse, args.output)
    else:
        result = verify(args.receipt)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
