#!/usr/bin/env python3
"""Capture, verify, and draw a post-cutoff upstream software case pool.

The capture command talks only to public GitHub APIs.  The resulting canonical
JSON is self-contained: candidate-visible issue bytes are retained verbatim,
while evaluator-only PR identity and patch digests are committed without being
placed in an agent workspace.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from typing import Any


SCHEMA = "errata.rung1-upstream-artifact-pool.v1"
DRAW_SCHEMA = "errata.rung1-upstream-artifact-draw.v1"
MODEL_KNOWLEDGE_CUTOFF = "2026-02-16T23:59:59Z"
EXCLUDED_LOGINS = frozenset({"mliotta", "parslee-ai"})
CASES = (
    ("pallets/click", 3802, 3818),
    ("pallets/click", 3572, 3653),
    ("pallets/click", 3571, 3769),
    ("pytest-dev/pytest", 14864, 14865),
    ("pydantic/pydantic", 13664, 13665),
    ("pydantic/pydantic", 13692, 13699),
    ("pydantic/pydantic", 13687, 13691),
    ("pydantic/pydantic", 13645, 13648),
)


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


def _gh_json(endpoint: str) -> Any:
    completed = subprocess.run(
        ["gh", "api", endpoint],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
    )
    return json.loads(completed.stdout)


def _gh_diff(repo: str, pull: int) -> bytes:
    completed = subprocess.run(
        [
            "gh",
            "api",
            f"repos/{repo}/pulls/{pull}",
            "-H",
            "Accept: application/vnd.github.v3.diff",
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
    )
    return completed.stdout


def _is_test(path: str) -> bool:
    return path.startswith(("tests/", "testing/")) or "/tests/" in path


def _is_implementation(path: str) -> bool:
    return path.endswith(
        (".py", ".c", ".cc", ".cpp", ".go", ".js", ".rs")
    ) and not _is_test(path)


def _capture_case(repo: str, issue_number: int, pull_number: int) -> dict[str, Any]:
    issue = _gh_json(f"repos/{repo}/issues/{issue_number}")
    pull = _gh_json(f"repos/{repo}/pulls/{pull_number}")
    files = _gh_json(f"repos/{repo}/pulls/{pull_number}/files?per_page=100")
    if not isinstance(files, list) or not files or len(files) >= 100:
        raise ValueError(
            f"{repo}#{pull_number}: changed-file page is empty or truncated"
        )
    if pull.get("merged_at") is None or pull["merged_at"] <= MODEL_KNOWLEDGE_CUTOFF:
        raise ValueError(f"{repo}#{pull_number}: fix does not postdate model cutoff")
    if issue.get("created_at") is None or issue["created_at"] <= MODEL_KNOWLEDGE_CUTOFF:
        raise ValueError(
            f"{repo}#{issue_number}: report does not postdate model cutoff"
        )
    author = pull.get("user") or {}
    login = str(author.get("login", "")).lower()
    if not login or login in EXCLUDED_LOGINS or author.get("type") != "User":
        raise ValueError(f"{repo}#{pull_number}: external human author is unavailable")
    paths = sorted(str(item["filename"]) for item in files)
    test_paths = [path for path in paths if _is_test(path)]
    implementation_paths = [path for path in paths if _is_implementation(path)]
    if not test_paths or not implementation_paths:
        raise ValueError(
            f"{repo}#{pull_number}: source-plus-regression shape is absent"
        )
    diff = _gh_diff(repo, pull_number)
    issue_snapshot = {
        "body": issue.get("body") or "",
        "created_at": issue["created_at"],
        "number": issue_number,
        "title": issue["title"],
        "url": issue["html_url"],
    }
    body: dict[str, Any] = {
        "case_id": f"{repo.replace('/', '--')}--issue-{issue_number}",
        "repository": repo,
        "issue": issue_snapshot,
        "issue_snapshot_sha256": _digest(issue_snapshot),
        "external_author": {
            "login": author["login"],
            "profile_url": author["html_url"],
            "type": author["type"],
        },
        "gold": {
            "base_sha": pull["base"]["sha"],
            "merge_sha": pull["merge_commit_sha"],
            "merged_at": pull["merged_at"],
            "pull_number": pull_number,
            "pull_url": pull["html_url"],
            "upstream_diff_bytes": len(diff),
            "upstream_diff_sha256": sha256(diff).hexdigest(),
            "implementation_paths": implementation_paths,
            "test_paths": test_paths,
        },
        "eligibility": {
            "agent_network_disabled": True,
            "author_outside_errata": True,
            "fix_postdates_model_cutoff": True,
            "issue_postdates_model_cutoff": True,
            "gold_and_regression_withheld_from_agent": True,
            "source_and_regression_changed": True,
        },
    }
    return {**body, "sha256": _digest(body)}


def capture(output: Path) -> dict[str, Any]:
    if output.exists():
        raise ValueError("pool output already exists")
    cases = [_capture_case(*spec) for spec in CASES]
    if len({case["external_author"]["login"] for case in cases}) < 4:
        raise ValueError("pool requires at least four distinct external authors")
    body: dict[str, Any] = {
        "schema": SCHEMA,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "model_identity": "codex-exec:gpt-5.6-sol",
        "model_knowledge_cutoff": MODEL_KNOWLEDGE_CUTOFF,
        "candidate_visible_fields": ["repository", "issue", "gold.base_sha"],
        "evaluator_only_fields": ["external_author", "gold", "eligibility"],
        "selection": {
            "beacon_rule": "first predeclared public beacon strictly after public freeze",
            "method": "ascending SHA-256(beacon_digest || 0x00 || case_sha256)",
            "primary_cases": 4,
            "replacement": False,
        },
        "cases": cases,
    }
    result = {**body, "sha256": _digest(body)}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(canonical_bytes(result) + b"\n")
    return result


def verify(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if raw != canonical_bytes(value) + b"\n":
        raise ValueError("pool bytes are not canonical")
    if value.get("schema") != SCHEMA:
        raise ValueError("pool schema differs")
    claimed = value.get("sha256")
    body = {key: item for key, item in value.items() if key != "sha256"}
    if claimed != _digest(body):
        raise ValueError("pool digest differs")
    if [
        (case["repository"], case["issue"]["number"], case["gold"]["pull_number"])
        for case in value["cases"]
    ] != list(CASES):
        raise ValueError("pool case roster differs")
    for case in value["cases"]:
        case_claimed = case.get("sha256")
        case_body = {key: item for key, item in case.items() if key != "sha256"}
        if case_claimed != _digest(case_body):
            raise ValueError("case digest differs")
        if case["issue_snapshot_sha256"] != _digest(case["issue"]):
            raise ValueError("issue snapshot digest differs")
        if case["gold"]["merged_at"] <= MODEL_KNOWLEDGE_CUTOFF:
            raise ValueError("case no longer satisfies post-cutoff rule")
        if case["issue"]["created_at"] <= MODEL_KNOWLEDGE_CUTOFF:
            raise ValueError("issue no longer satisfies post-cutoff rule")
    return value


def draw(pool_path: Path, beacon_path: Path, output: Path) -> dict[str, Any]:
    if output.exists():
        raise ValueError("draw output already exists")
    pool = verify(pool_path)
    beacon = beacon_path.read_bytes()
    beacon_value = json.loads(beacon)
    if beacon_value.get("schema") != "errata.rung1-nist-beacon-receipt.v1":
        raise ValueError("draw requires the frozen NIST beacon receipt schema")
    beacon_body = {key: value for key, value in beacon_value.items() if key != "sha256"}
    if beacon_value.get("sha256") != _digest(beacon_body):
        raise ValueError("draw beacon receipt digest differs")
    if (
        beacon_value.get("rule")
        != "first NIST Beacon 2.0 pulse strictly after the immutable v0.4.2 release publishedAt"
        or beacon_value.get("release_url")
        != "https://github.com/Parslee-ai/errata-external-evaluation/releases/tag/v0.4.2"
        or beacon_value.get("request_url")
        != "https://beacon.nist.gov/beacon/2.0/pulse/time/next/"
        + str(beacon_value.get("strictly_after_unix_ms"))
    ):
        raise ValueError("draw beacon precommitment differs")
    pulse = beacon_value.get("pulse")
    if not isinstance(pulse, dict) or not isinstance(pulse.get("outputValue"), str):
        raise ValueError("draw beacon pulse differs")
    beacon_entropy = bytes.fromhex(pulse["outputValue"])
    if len(beacon_entropy) != 64:
        raise ValueError("draw beacon entropy must contain 512 bits")
    pulse_ms = int(
        datetime.fromisoformat(pulse["timeStamp"].replace("Z", "+00:00")).timestamp()
        * 1000
    )
    if pulse_ms <= beacon_value.get("strictly_after_unix_ms", pulse_ms):
        raise ValueError("draw beacon pulse does not postdate the release")
    beacon_digest = sha256(beacon_entropy).hexdigest()
    ranked = sorted(
        pool["cases"],
        key=lambda case: sha256(
            bytes.fromhex(beacon_digest) + b"\x00" + bytes.fromhex(case["sha256"])
        ).hexdigest(),
    )
    selected = [case["case_id"] for case in ranked[:4]]
    body = {
        "schema": DRAW_SCHEMA,
        "pool_sha256": pool["sha256"],
        "beacon_receipt_bytes": len(beacon),
        "beacon_receipt_sha256": sha256(beacon).hexdigest(),
        "beacon_receipt_canonical_sha256": beacon_value["sha256"],
        "beacon_sha256": beacon_digest,
        "selected_case_ids": selected,
    }
    result = {**body, "sha256": _digest(body)}
    output.write_bytes(canonical_bytes(result) + b"\n")
    return result


def complement(pool_path: Path, prior_draw_path: Path, output: Path) -> dict[str, Any]:
    """Select the entire unexposed complement of a completed four-case draw."""
    if output.exists():
        raise ValueError("complement output already exists")
    pool = verify(pool_path)
    raw = prior_draw_path.read_bytes()
    prior = json.loads(raw)
    prior_body = {key: value for key, value in prior.items() if key != "sha256"}
    if (
        raw != canonical_bytes(prior) + b"\n"
        or prior.get("schema") != DRAW_SCHEMA
        or prior.get("pool_sha256") != pool["sha256"]
        or prior.get("sha256") != _digest(prior_body)
        or not isinstance(prior.get("selected_case_ids"), list)
        or len(prior["selected_case_ids"]) != 4
    ):
        raise ValueError("prior draw identity differs")
    exposed = set(prior["selected_case_ids"])
    selected = [
        case["case_id"] for case in pool["cases"] if case["case_id"] not in exposed
    ]
    if len(selected) != 4:
        raise ValueError("prior draw does not leave a four-case complement")
    body = {
        "schema": DRAW_SCHEMA,
        "pool_sha256": pool["sha256"],
        "selection_rule": "entire deterministic complement of the v0.4.2 draw",
        "prior_draw_sha256": prior["sha256"],
        "selected_case_ids": selected,
    }
    result = {**body, "sha256": _digest(body)}
    output.write_bytes(canonical_bytes(result) + b"\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    capture_parser = commands.add_parser("capture")
    capture_parser.add_argument("--output", type=Path, required=True)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--pool", type=Path, required=True)
    draw_parser = commands.add_parser("draw")
    draw_parser.add_argument("--pool", type=Path, required=True)
    draw_parser.add_argument("--beacon", type=Path, required=True)
    draw_parser.add_argument("--output", type=Path, required=True)
    complement_parser = commands.add_parser("complement")
    complement_parser.add_argument("--pool", type=Path, required=True)
    complement_parser.add_argument("--prior-draw", type=Path, required=True)
    complement_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "capture":
        result = capture(args.output)
    elif args.command == "verify":
        result = verify(args.pool)
    elif args.command == "draw":
        result = draw(args.pool, args.beacon, args.output)
    else:
        result = complement(args.pool, args.prior_draw, args.output)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
