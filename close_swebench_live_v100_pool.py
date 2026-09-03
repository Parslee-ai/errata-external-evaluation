#!/usr/bin/env python3
"""Close the frozen SWE-bench-Live v1.0 pool from dual custody."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path


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


def verify_internal_digest(value: dict[str, object]) -> None:
    claimed = value.get("sha256")
    body = {key: item for key, item in value.items() if key != "sha256"}
    if claimed != digest(canonical(body)):
        raise ValueError("internal digest differs")


def load_equal(primary: Path, mirror: Path, relative: Path) -> tuple[dict[str, object], str]:
    primary_raw = (primary / relative).read_bytes()
    mirror_raw = (mirror / relative).read_bytes()
    if primary_raw != mirror_raw:
        raise ValueError(f"custody roots differ at {relative}")
    value = json.loads(primary_raw)
    verify_internal_digest(value)
    return value, digest(primary_raw)


def result_summary(value: dict[str, object], file_sha256: str) -> dict[str, object]:
    decision = value["decision"]
    assert isinstance(decision, dict)
    return {
        "mode": value["mode"],
        "repetition": value["repetition"],
        "result_file_sha256": file_sha256,
        "result_internal_sha256": value["sha256"],
        "status_sha256": value["status_sha256"],
        "log_sha256": value["log_sha256"],
        "resolved": decision["resolved"],
        "empty_patch_gate": decision.get("empty_patch_gate"),
        "fail_to_pass_success_count": len(decision["fail_to_pass_success"]),
        "fail_to_pass_failure_count": len(decision["fail_to_pass_failure"]),
        "pass_to_pass_failure_count": len(decision["pass_to_pass_failure"]),
        "parsed_status_count": decision["parsed_status_count"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ranking", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--mirror", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    ranking_raw = args.ranking.read_bytes()
    ranking = json.loads(ranking_raw)
    verify_internal_digest(ranking)
    freeze_raw = args.freeze.read_bytes()
    freeze = json.loads(freeze_raw)
    verify_internal_digest(freeze)

    retained: list[dict[str, object]] = []
    scan: list[dict[str, object]] = []
    custody_files: dict[str, str] = {}

    for ranked in ranking["ranked_rows"]:
        if len(retained) == 4:
            break
        row = {
            "rank": ranked["rank"],
            "instance_id": ranked["instance_id"],
            "repository": ranked["repository"],
        }
        if not ranked["static_eligible"]:
            row["disposition"] = "static-ineligible"
            row["reasons"] = ranked["static_rejection_reasons"]
            scan.append(row)
            continue

        case_relative = Path("private/cases") / f"{ranked['instance_id']}.jsonl"
        primary_case = (args.primary / case_relative).read_bytes()
        mirror_case = (args.mirror / case_relative).read_bytes()
        if primary_case != mirror_case:
            raise ValueError(f"private case custody differs for {ranked['instance_id']}")
        case_sha256 = digest(primary_case)
        row["private_case_sha256"] = case_sha256

        run_summaries: list[dict[str, object]] = []
        gold_failed = False
        terminal_failure: dict[str, object] | None = None
        for repetition in (1, 2, 3):
            base = Path("preflight") / ranked["instance_id"] / f"gold-{repetition}"
            result_relative = base / "result.json"
            if (args.primary / result_relative).exists():
                result, file_sha = load_equal(args.primary, args.mirror, result_relative)
                custody_files[str(result_relative)] = file_sha
                for artifact in ("post_patch_log.txt", "status.json"):
                    relative = base / artifact
                    primary_raw = (args.primary / relative).read_bytes()
                    mirror_raw = (args.mirror / relative).read_bytes()
                    if primary_raw != mirror_raw:
                        raise ValueError(f"custody roots differ at {relative}")
                    custody_files[str(relative)] = digest(primary_raw)
                summary = result_summary(result, file_sha)
                run_summaries.append(summary)
                if not summary["resolved"]:
                    gold_failed = True
                    break
                continue

            for failure_name in ("timeout.json", "image-registration-failure.json"):
                failure_relative = base / failure_name
                if (args.primary / failure_relative).exists():
                    failure, file_sha = load_equal(args.primary, args.mirror, failure_relative)
                    custody_files[str(failure_relative)] = file_sha
                    terminal_failure = {
                        "mode": failure["mode"],
                        "repetition": failure["repetition"],
                        "decision": failure["decision"],
                        "receipt_file_sha256": file_sha,
                        "receipt_internal_sha256": failure["sha256"],
                        "retry_or_replacement": failure["retry_or_replacement"],
                    }
                    break
            if terminal_failure is None:
                raise FileNotFoundError(f"missing terminal gold receipt for {ranked['instance_id']}")
            break

        row["gold_runs"] = run_summaries
        if terminal_failure is not None:
            row["terminal_failure"] = terminal_failure
            row["disposition"] = "dynamic-ineligible"
            scan.append(row)
            continue
        if gold_failed:
            row["disposition"] = "gold-ineligible"
            scan.append(row)
            continue
        if len(run_summaries) != 3:
            raise ValueError(f"three gold repetitions absent for {ranked['instance_id']}")

        empty_base = Path("preflight") / ranked["instance_id"] / "empty-1"
        empty_relative = empty_base / "result.json"
        empty_result, empty_file_sha = load_equal(args.primary, args.mirror, empty_relative)
        custody_files[str(empty_relative)] = empty_file_sha
        for artifact in ("post_patch_log.txt", "status.json"):
            relative = empty_base / artifact
            primary_raw = (args.primary / relative).read_bytes()
            mirror_raw = (args.mirror / relative).read_bytes()
            if primary_raw != mirror_raw:
                raise ValueError(f"custody roots differ at {relative}")
            custody_files[str(relative)] = digest(primary_raw)
        empty_summary = result_summary(empty_result, empty_file_sha)
        row["empty_run"] = empty_summary
        if empty_summary["empty_patch_gate"] is not True:
            row["disposition"] = "empty-gate-ineligible"
            scan.append(row)
            continue

        if any(item["repository"] == ranked["repository"] for item in retained):
            row["disposition"] = "duplicate-repository-ineligible"
            scan.append(row)
            continue
        row["disposition"] = "retained-eligible"
        scan.append(row)
        retained.append(
            {
                "pool_index": len(retained) + 1,
                "rank": ranked["rank"],
                "instance_id": ranked["instance_id"],
                "repository": ranked["repository"],
                "private_case_sha256": case_sha256,
            }
        )

    if len(retained) != 4:
        raise ValueError("frozen scan did not produce four eligible cases")
    manifest = [
        {"path": path, "sha256": sha}
        for path, sha in sorted(custody_files.items())
    ]
    body = {
        "schema": "errata.swebench-live-v100-pool-closure.v1",
        "status": "pool-closed-before-cognition",
        "freeze_file_sha256": digest(freeze_raw),
        "freeze_internal_sha256": freeze["sha256"],
        "ranking_file_sha256": digest(ranking_raw),
        "ranking_internal_sha256": ranking["sha256"],
        "dataset_revision": ranking["dataset_revision"],
        "evaluator_revision": freeze["external_inputs"]["evaluator_git_revision"],
        "scan_stop_rank": scan[-1]["rank"],
        "scan_rows": scan,
        "retained_cases": retained,
        "dual_custody_equal": True,
        "preflight_artifact_count": len(manifest),
        "preflight_manifest": manifest,
        "preflight_manifest_sha256": digest(canonical(manifest)),
        "candidate_invocations": 0,
        "raw_attempts_reserved": [],
        "task_content_disclosed": False,
    }
    closure = {**body, "sha256": digest(canonical(body))}
    raw = canonical(closure) + b"\n"
    descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    print(json.dumps(closure, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
