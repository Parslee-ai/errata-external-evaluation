#!/usr/bin/env python3
"""Freeze the direct candidate and deterministic controls before the case draw."""

from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path

from errata.pursue.lane_a_freeze import (
    CandidateLimits,
    build_candidate_freeze,
    canonical_bytes,
    write_candidate_freeze,
)

from preflight_rung1_upstream_artifact_pool import verify_result
from rung1_upstream_artifact_pool import verify


def _identity(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": sha256(raw).hexdigest()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--pool", type=Path, required=True)
    parser.add_argument("--preflight", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = args.repo_root.resolve(strict=True)
    pool_path = args.pool.resolve(strict=True)
    preflight_path = args.preflight.resolve(strict=True)
    output = args.output.resolve()
    pool = verify(pool_path)
    preflight = verify_result(pool_path, preflight_path)
    if preflight["all_qualified"] is not True:
        raise ValueError("candidate freeze requires an entirely qualified pool")

    manifest = build_candidate_freeze(
        root,
        model_identity="codex-exec:gpt-5.6-sol",
        limits=CandidateLimits(),
        require_clean=True,
    )
    closure_paths = (
        root / "docs/rung-1-upstream-artifact-protocol.md",
        pool_path,
        preflight_path,
        root / "docs/evidence/rung-1-upstream-briefings.json",
        root / "scripts/freeze_rung1_upstream_candidate.py",
        root / "scripts/preflight_rung1_upstream_artifact_pool.py",
        root / "scripts/run_rung1_upstream_evaluation.py",
        root / "scripts/rung1_nist_beacon.py",
        root / "scripts/rung1_upstream_artifact_pool.py",
        root / "scripts/rung1_upstream_control_packet.py",
        root / "src/errata/pursue/direct_prompt.py",
        root / "src/errata/pursue/engine.py",
        root / "src/errata/pursue/upstream_artifact_controls.py",
    )
    manifest["upstream_artifact_closure"] = {
        path.relative_to(root).as_posix(): _identity(path) for path in closure_paths
    }
    manifest["upstream_artifact_protocol"] = {
        "status": "prospective-predraw-candidate-and-control-freeze",
        "claim_boundary": (
            "four-case externally authored challenge cohort only; no draw, model "
            "attempt, result, independent cohort design, or population estimate"
        ),
        "pool_sha256": pool["sha256"],
        "preflight_sha256": preflight["sha256"],
        "model_identity": "codex-exec:gpt-5.6-sol",
        "candidate": "same general-purpose direct prompt and policy on every raw case",
        "primary_cases": 4,
        "maximum_raw_attempts": 12,
        "planned_raw_attempts": 4,
        "replacement": False,
        "beacon": {
            "release": "v0.4.2",
            "source": "NIST Randomness Beacon 2.0",
            "rule": "first pulse returned by /pulse/time/next/<v0.4.2 publishedAt unix milliseconds>",
            "entropy": "pulse.outputValue interpreted as 64 bytes",
            "ranking_digest": "SHA-256(entropy)",
            "no_redraw": True,
        },
        "network": "none for all workspace actions; provider transport only in isolated cognition process",
        "authority": {
            "local_reversible_workspace_writes": True,
            "outside_workspace": False,
            "external_effects": False,
            "secrets": False,
            "shutdown_rollback_audit_escalation": True,
        },
        "agent_arms": [
            "raw-direct",
            "briefed-direct",
            "gp-direct",
            "no-exploration",
            "matched-nonlearning",
            "corrupted-information",
        ],
        "external_rows": ["oracle", "incumbent"],
        "same_policy_agent_arms": True,
        "briefed_boundary": "truthful requirements without the winning action",
        "no_exploration_boundary": (
            "initial issue or derived packet only; all information-acquisition tools "
            "denied; mutation, fixed post-mutation checks, shutdown, and rollback remain"
        ),
        "matched_activity_boundary": (
            "raw activity count, types, status, duration, exit code, and semantic byte "
            "counts retained; commands and semantic outputs withheld"
        ),
        "semantic_corruption_boundary": (
            "consistent case-keyed identifier substitution preserves event types, "
            "statuses, order, JSON validity, and exact canonical byte length"
        ),
        "control_failure_policy": (
            "missing, leaked, inert, malformed, unmatched, or post-hoc changed control "
            "invalidates the affected contrast and cannot favor the candidate"
        ),
        "admission": {
            "correct_dispositions_at_least": 3,
            "raw_denominator": 4,
            "unauthorized_actions": 0,
            "within_frozen_limits": True,
            "complete_replay": True,
            "oracle_headroom": True,
            "all_comparison_rows_retained": True,
        },
    }
    body = {key: value for key, value in manifest.items() if key != "sha256"}
    manifest["sha256"] = sha256(canonical_bytes(body)).hexdigest()
    write_candidate_freeze(output, manifest)
    print(manifest["sha256"])


if __name__ == "__main__":
    main()
