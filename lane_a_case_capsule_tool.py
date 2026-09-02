#!/usr/bin/env python3
"""Build and verify opaque Lane-A case capsules without importing Errata.

This disclosure-safe utility uses only the Python standard library.  It emits
commitments (digest, byte count, and media type), never artifact paths or
artifact contents.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Any, Mapping


SCHEMA = "errata.lane-a-case-capsule.v1"
ARTIFACT_SCHEMA = "errata.lane-a-opaque-artifact.v1"

REQUIRED_ARTIFACT_ROLES = (
    "initial-workspace",
    "raw-mandate",
    "briefed-requirements",
    "authority-policy",
    "shutdown-procedure",
    "rollback-procedure",
    "human-escalation-procedure",
    "common-preflight",
    "native-outcome-verifier",
    "nonwin-truth-verifier",
    "trap-commitment",
    "exploration-event-classifier",
    "matched-nonlearning-transform",
    "matched-nonlearning-validator",
    "no-exploration-policy",
    "corruption-transform",
    "semantic-corruption-validator",
    "oracle-procedure",
    "incumbent-procedure",
    "case-author-declaration",
    "custodian-declaration",
    "adjudicator-declaration",
)

# This is the exact v1 protocol value bound by lane_a_case_capsule.py.  Keeping
# it here, instead of importing the package, makes this file independently
# distributable to an outside author or custodian.
CONTROL_PROTOCOL: dict[str, Any] = json.loads(
    r'''{"admission_contrasts":{"current_practice":["raw-pursuit","incumbent"],"discovery":["raw-pursuit","no-exploration"],"general_purpose_direct":["raw-pursuit","gp-direct"],"headroom":["raw-pursuit","oracle"],"learning":["raw-pursuit","matched-nonlearning"],"requirements":["raw-pursuit","briefed-pursuit"],"semantic_information":["raw-pursuit","corrupted-information"]},"briefed-pursuit":{"estimand_role":"requirement-information sensitivity","information":"truthful requirements, never a winning action or solution artifact"},"case_material_hidden_until_its_frozen_release_stage":true,"corrupted-information":{"estimand_role":"semantic learned-information necessity rather than activity or format","information":"the frozen transform changes task-relevant relations in the retained raw learned packet while preserving event order, record types, authority labels, and declared size tolerance","intervention":"an independent frozen validator must reject identity transforms, preserved winning relations, unsafe instructions, and corruption that makes the packet unparsable; the executor cannot acquire uncorrupted case information afterward"},"dependency_order":{"independent_arms_precede_raw":["oracle","incumbent","no-exploration","briefed-pursuit","gp-direct"],"raw_precedes_derived_controls":["matched-nonlearning","corrupted-information"]},"fresh_clone_per_arm":true,"gp-direct":{"estimand_role":"strongest frozen general-purpose direct policy on the same substrate","information":"same raw mandate and initial observation as raw-pursuit"},"incumbent":{"estimand_role":"current-practice outcome, cost, assistance, and authority comparator","information":"actual current workflow predeclared before candidate release"},"invalid_pair_policy":"a missing, failed, unmatched, semantically invalid, leaked, or post-hoc redefined control invalidates that case for the affected contrast and cannot be scored as favorable","matched-nonlearning":{"estimand_role":"learning value beyond matched noninformative activity","information":"a deterministic transform frozen before release maps each raw exploration event to a case-author equivalence-class activity with matched permission, action class, maximum duration, and output-byte allowance","intervention":"semantic outputs are withheld; the execution agent receives only counts, costs, statuses, and the original initial information, then commits one terminal plan without further information acquisition"},"no-exploration":{"estimand_role":"value of safe participation beyond acting from initial information","information":"raw mandate and initial observation only","intervention":"the frozen policy denies every event classified as information acquisition; the complete terminal plan is committed before outcome feedback, and only that plan, outcome checks, shutdown, rollback, and escalation remain"},"oracle":{"estimand_role":"case and substrate headroom","information":"outside author's sealed winning procedure","intervention":"custodian executes it on a fresh clone under the same authority and outer budgets; the native outcome verifier must pass without unauthorized action"},"raw-pursuit":{"estimand_role":"candidate discovery plus execution","information":"raw mandate and ordinary access only"},"same_agent_model_tools_and_limits_for_agent_arms":true,"same_initial_workspace_authority_and_outcome_verifier":true}'''
)

BUILD_SPEC_FIELDS = {
    "candidate_freeze_sha256",
    "case_id",
    "principals",
    "declarations",
    "artifacts",
}
PRINCIPAL_FIELDS = {"author_id", "custodian_id", "adjudicator_id"}
DECLARATIONS = {
    "author_non_exposure": True,
    "author_independent_of_candidate_team": True,
    "custodian_independent_of_candidate_team": True,
    "adjudicator_independent_of_candidate_team": True,
}


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("ascii")


def _digest(value: object) -> str:
    return sha256(canonical_bytes(value)).hexdigest()


def _sha256_file(path: Path) -> tuple[str, int]:
    digest = sha256()
    byte_count = 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
            byte_count += len(block)
    return digest.hexdigest(), byte_count


def opaque_artifact(*, sha256_hex: str, byte_count: int, media_type: str) -> dict[str, Any]:
    artifact = {
        "schema": ARTIFACT_SCHEMA,
        "sha256": sha256_hex,
        "bytes": byte_count,
        "media_type": media_type,
    }
    _validate_artifact(artifact)
    return artifact


def _validate_artifact(value: object) -> None:
    if not isinstance(value, dict) or set(value) != {
        "schema",
        "sha256",
        "bytes",
        "media_type",
    }:
        raise ValueError("case capsule artifact envelope differs")
    if value.get("schema") != ARTIFACT_SCHEMA:
        raise ValueError("case capsule artifact schema differs")
    digest = value.get("sha256")
    if (
        not isinstance(digest, str)
        or len(digest) != 64
        or any(character not in "0123456789abcdef" for character in digest)
    ):
        raise ValueError("case capsule artifact digest differs")
    if type(value.get("bytes")) is not int or value["bytes"] < 1:
        raise ValueError("case capsule artifact byte count differs")
    media_type = value.get("media_type")
    if not isinstance(media_type, str) or not media_type.strip() or len(media_type) > 160:
        raise ValueError("case capsule artifact media type differs")


def build_case_capsule(
    *,
    candidate_freeze_sha256: str,
    case_id: str,
    artifacts: Mapping[str, Mapping[str, Any]],
    author_id: str,
    custodian_id: str,
    adjudicator_id: str,
    author_non_exposure: bool,
    author_independent_of_candidate_team: bool,
    custodian_independent_of_candidate_team: bool,
    adjudicator_independent_of_candidate_team: bool,
) -> dict[str, Any]:
    if (
        not isinstance(candidate_freeze_sha256, str)
        or len(candidate_freeze_sha256) != 64
        or any(character not in "0123456789abcdef" for character in candidate_freeze_sha256)
    ):
        raise ValueError("case capsule candidate freeze digest differs")
    if not isinstance(case_id, str) or not case_id.strip() or len(case_id) > 160:
        raise ValueError("case capsule identifier differs")
    principals = (author_id, custodian_id, adjudicator_id)
    if any(not isinstance(item, str) or not item.strip() or len(item) > 160 for item in principals):
        raise ValueError("case capsule principal identity differs")
    if len(set(principals)) != 3:
        raise ValueError("case author, custodian, and adjudicator must be distinct")
    declarations = (
        author_non_exposure,
        author_independent_of_candidate_team,
        custodian_independent_of_candidate_team,
        adjudicator_independent_of_candidate_team,
    )
    if any(value is not True for value in declarations):
        raise ValueError("case capsule independence declarations are incomplete")
    if not isinstance(artifacts, Mapping) or set(artifacts) != set(REQUIRED_ARTIFACT_ROLES):
        raise ValueError("case capsule artifact roles differ")
    normalized: dict[str, dict[str, Any]] = {}
    for role in REQUIRED_ARTIFACT_ROLES:
        value = dict(artifacts[role])
        _validate_artifact(value)
        normalized[role] = value
    digests = [value["sha256"] for value in normalized.values()]
    if len(digests) != len(set(digests)):
        raise ValueError("case capsule reuses bytes across distinct semantic roles")
    body = {
        "schema": SCHEMA,
        "candidate_freeze_sha256": candidate_freeze_sha256,
        "case_id": case_id.strip(),
        "principals": {
            "author_id": author_id.strip(),
            "custodian_id": custodian_id.strip(),
            "adjudicator_id": adjudicator_id.strip(),
        },
        "declarations": dict(DECLARATIONS),
        "artifacts": normalized,
        "control_protocol": json.loads(json.dumps(CONTROL_PROTOCOL)),
    }
    return {**body, "sha256": _digest(body)}


def verify_case_capsule(value: object, *, candidate_freeze_sha256: str) -> str:
    if not isinstance(value, dict) or value.get("schema") != SCHEMA:
        raise ValueError("case capsule schema differs")
    claimed = value.get("sha256")
    body = {key: item for key, item in value.items() if key != "sha256"}
    if not isinstance(claimed, str) or claimed != _digest(body):
        raise ValueError("case capsule digest differs")
    if value.get("candidate_freeze_sha256") != candidate_freeze_sha256:
        raise ValueError("case capsule candidate freeze differs")
    if value.get("control_protocol") != CONTROL_PROTOCOL:
        raise ValueError("case capsule control protocol differs")
    principals = value.get("principals")
    declarations = value.get("declarations")
    artifacts = value.get("artifacts")
    if not isinstance(principals, dict) or set(principals) != PRINCIPAL_FIELDS:
        raise ValueError("case capsule principals differ")
    if len(set(principals.values())) != 3 or any(
        not isinstance(item, str) or not item.strip() or len(item) > 160
        for item in principals.values()
    ):
        raise ValueError("case capsule principal identity differs")
    if declarations != DECLARATIONS:
        raise ValueError("case capsule independence declarations differ")
    if not isinstance(artifacts, dict) or set(artifacts) != set(REQUIRED_ARTIFACT_ROLES):
        raise ValueError("case capsule artifact roles differ")
    digests: list[str] = []
    for role in REQUIRED_ARTIFACT_ROLES:
        _validate_artifact(artifacts[role])
        digests.append(artifacts[role]["sha256"])
    if len(digests) != len(set(digests)):
        raise ValueError("case capsule reuses bytes across distinct semantic roles")
    return claimed


def _load_canonical_json(path: Path, *, label: str) -> dict[str, Any]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} is not JSON") from exc
    if not isinstance(value, dict) or raw != canonical_bytes(value) + b"\n":
        raise ValueError(f"{label} is not canonical")
    return value


def _write_once(path: Path, value: object, *, label: str) -> None:
    payload = canonical_bytes(value) + b"\n"
    if path.exists():
        if path.read_bytes() != payload:
            raise ValueError(f"{label} path already has different bytes")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def _build_from_spec(spec: object) -> dict[str, Any]:
    if not isinstance(spec, dict) or set(spec) != BUILD_SPEC_FIELDS:
        raise ValueError("case capsule build specification fields differ")
    principals = spec.get("principals")
    declarations = spec.get("declarations")
    if not isinstance(principals, dict) or set(principals) != PRINCIPAL_FIELDS:
        raise ValueError("case capsule principals differ")
    if not isinstance(declarations, dict) or set(declarations) != set(DECLARATIONS):
        raise ValueError("case capsule independence declarations differ")
    artifacts = spec.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ValueError("case capsule artifact roles differ")
    return build_case_capsule(
        candidate_freeze_sha256=spec.get("candidate_freeze_sha256"),
        case_id=spec.get("case_id"),
        artifacts=artifacts,
        author_id=principals["author_id"],
        custodian_id=principals["custodian_id"],
        adjudicator_id=principals["adjudicator_id"],
        author_non_exposure=declarations["author_non_exposure"],
        author_independent_of_candidate_team=declarations[
            "author_independent_of_candidate_team"
        ],
        custodian_independent_of_candidate_team=declarations[
            "custodian_independent_of_candidate_team"
        ],
        adjudicator_independent_of_candidate_team=declarations[
            "adjudicator_independent_of_candidate_team"
        ],
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    artifact = subparsers.add_parser(
        "artifact", help="print a canonical opaque commitment for one local file"
    )
    artifact.add_argument("path", type=Path)
    artifact.add_argument("--media-type", required=True)

    build = subparsers.add_parser("build", help="build a write-once canonical capsule")
    build.add_argument("--spec", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)

    verify = subparsers.add_parser("verify", help="verify a canonical capsule")
    verify.add_argument("--capsule", type=Path, required=True)
    verify.add_argument("--candidate-freeze-sha256", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "artifact":
            digest, byte_count = _sha256_file(args.path)
            value = opaque_artifact(
                sha256_hex=digest, byte_count=byte_count, media_type=args.media_type
            )
            sys.stdout.buffer.write(canonical_bytes(value) + b"\n")
            return 0
        if args.command == "build":
            spec = _load_canonical_json(args.spec, label="case capsule build specification")
            capsule = _build_from_spec(spec)
            verify_case_capsule(
                capsule, candidate_freeze_sha256=capsule["candidate_freeze_sha256"]
            )
            _write_once(args.output, capsule, label="case capsule")
            print(capsule["sha256"])
            return 0
        capsule = _load_canonical_json(args.capsule, label="case capsule")
        print(
            verify_case_capsule(
                capsule, candidate_freeze_sha256=args.candidate_freeze_sha256
            )
        )
        return 0
    except (OSError, TypeError, ValueError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
