#!/usr/bin/env python3
"""Deterministically audit the frozen causal-program agent's enumeration boundary."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path


SCHEMA = "errata.causal-program-nonenumeration-blocker.v0"
ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = Path("src/errata/north_star/causal_program_semantic_agent_v0.py")
EXPECTED_IDENTITY = "semantic-set-valued-causal-program-agent-v0"


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _qualified_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _qualified_name(node.value)
        return None if parent is None else f"{parent}.{node.attr}"
    return None


def _function(tree: ast.Module, name: str) -> ast.FunctionDef:
    matches = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name]
    if len(matches) != 1:
        raise ValueError(f"candidate must contain exactly one {name} function")
    return matches[0]


def _product_loops(function: ast.FunctionDef) -> list[ast.For]:
    return [
        node
        for node in ast.walk(function)
        if isinstance(node, ast.For)
        and isinstance(node.iter, ast.Call)
        and _qualified_name(node.iter.func) == "itertools.product"
    ]


def _has_call(function: ast.FunctionDef, qualified_name: str) -> bool:
    return any(
        isinstance(node, ast.Call) and _qualified_name(node.func) == qualified_name
        for node in ast.walk(function)
    )


def audit_source(raw: bytes, *, source_commit: str) -> dict[str, object]:
    if len(source_commit) != 40 or any(character not in "0123456789abcdef" for character in source_commit):
        raise ValueError("source commit must be 40 lowercase hexadecimal characters")
    try:
        text = raw.decode("utf-8")
        tree = ast.parse(text)
    except (UnicodeDecodeError, SyntaxError) as exc:
        raise ValueError("candidate source is not valid UTF-8 Python") from exc

    identity_found = any(
        isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "identity" for target in node.targets)
        and isinstance(node.value, ast.Constant)
        and node.value.value == EXPECTED_IDENTITY
        for node in ast.walk(tree)
    )
    if not identity_found:
        raise ValueError("frozen candidate identity is absent")

    discover = _function(tree, "discover")
    hypothesis = _function(tree, "_enumerate_hypotheses")
    planner = _function(tree, "robust_plan")

    practice_loops = _product_loops(discover)
    if len(practice_loops) != 1:
        raise ValueError("practice trajectory enumeration structure differs")
    practice_call = practice_loops[0].iter
    assert isinstance(practice_call, ast.Call)
    if (
        len(practice_call.args) != 1
        or not isinstance(practice_call.args[0], ast.Name)
        or practice_call.args[0].id != "vocabulary"
        or len(practice_call.keywords) != 1
        or practice_call.keywords[0].arg != "repeat"
        or not isinstance(practice_call.keywords[0].value, ast.Name)
        or practice_call.keywords[0].value.id != "depth"
    ):
        raise ValueError("practice Cartesian product no longer covers vocabulary by depth")

    hypothesis_loops = _product_loops(hypothesis)
    if len(hypothesis_loops) != 5:
        raise ValueError("causal hypothesis Cartesian-product enumeration structure differs")

    has_queue_loop = any(
        isinstance(node, ast.While) and isinstance(node.test, ast.Name) and node.test.id == "queue"
        for node in ast.walk(planner)
    )
    if not has_queue_loop or not _has_call(planner, "queue.popleft") or not _has_call(planner, "seen.add"):
        raise ValueError("executor breadth-first state enumeration structure differs")

    findings = {
        "candidate_identity": EXPECTED_IDENTITY,
        "candidate_path": CANDIDATE.as_posix(),
        "candidate_sha256": hashlib.sha256(raw).hexdigest(),
        "discovery_enumerates_all_action_sequences_through_practice_depth": True,
        "discovery_product_loop_lines": [node.lineno for node in practice_loops],
        "hypothesis_cartesian_product_loop_count": len(hypothesis_loops),
        "hypothesis_product_loop_lines": sorted(node.lineno for node in hypothesis_loops),
        "executor_breadth_first_joint_state_enumeration": True,
        "executor_queue_loop_line": next(
            node.lineno
            for node in ast.walk(planner)
            if isinstance(node, ast.While) and isinstance(node.test, ast.Name) and node.test.id == "queue"
        ),
    }
    unsigned = {
        "schema": SCHEMA,
        "source_commit": source_commit,
        "audit_kind": "static-structural-exhaustive-enumeration-dependency",
        "findings": findings,
        "admission": {
            "independent_synthetic_replication_admissible": False,
            "non_enumeration_gate_satisfied": False,
            "reason": (
                "The unchanged candidate exhaustively enumerates bounded practice action sequences, "
                "causal-program hypotheses, and joint executor states. Any win on its supported substrate "
                "therefore depends on enumeration forbidden by the North-Star admission rule."
            ),
        },
        "smallest_recovery_condition": (
            "Replace the candidate with a non-enumerative learner and executor, then freeze a new identity; "
            "this cannot be done while preserving the required unchanged causal-program agent."
        ),
        "claim_boundary": (
            "This source audit proves an algorithmic admission blocker. It does not measure performance, "
            "semantic independence, custody, or any game outcome."
        ),
    }
    return {**unsigned, "sha256": hashlib.sha256(canonical_bytes(unsigned)).hexdigest()}


def verify_receipt(value: object, raw: bytes) -> dict[str, object]:
    if not isinstance(value, dict) or canonical_bytes(value) != raw:
        raise ValueError("blocker receipt is not canonical")
    digest = value.get("sha256")
    unsigned = {key: item for key, item in value.items() if key != "sha256"}
    if digest != hashlib.sha256(canonical_bytes(unsigned)).hexdigest():
        raise ValueError("blocker receipt digest differs")
    if value.get("schema") != SCHEMA:
        raise ValueError("blocker receipt schema differs")
    return value


def _write_once(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        os.write(descriptor, raw)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-commit")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    if args.verify is not None:
        if args.source_commit is not None or args.output is not None:
            parser.error("--verify cannot be combined with creation arguments")
        raw = args.verify.read_bytes()
        value = verify_receipt(json.loads(raw), raw)
        candidate_raw = (ROOT / value["findings"]["candidate_path"]).read_bytes()
        expected = audit_source(candidate_raw, source_commit=value["source_commit"])
        if value != expected:
            raise ValueError("blocker receipt differs from current frozen candidate source")
        print(canonical_bytes(value).decode(), end="")
        return
    if args.source_commit is None or args.output is None:
        parser.error("creation requires --source-commit and --output")
    value = audit_source((ROOT / CANDIDATE).read_bytes(), source_commit=args.source_commit)
    _write_once(args.output, canonical_bytes(value))
    print(canonical_bytes(value).decode(), end="")


if __name__ == "__main__":
    main()
