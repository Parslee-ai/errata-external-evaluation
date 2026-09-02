"""Preparation boundary for an externally authored causal-program replication.

This module deliberately contains no game generator, candidate implementation,
case root, model response, or experimental result.  It defines the public byte
ABI, the frozen arm registry, and a fail-closed signed intake envelope that an
outside author and custodian can prepare without seeing candidate internals.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Literal, Mapping, Sequence


ABI_SCHEMA = "errata.causal-program-external.author-jsonl.v1"
TURN_SCHEMA = "errata.causal-program-external.turn.v1"
CAPSULE_SCHEMA = "errata.causal-program-external.capsule.v1"
INTAKE_SCHEMA = "errata.causal-program-external.intake-receipt.v1"
NONENUMERATION_SCHEMA = "errata.causal-program-external.nonenumeration.v1"
ARM_REGISTRY_SCHEMA = "errata.causal-program-external.arm-registry.v1"
PREDRAW_FREEZE_SCHEMA = "errata.causal-program-external.predraw-freeze.v1"
ATTESTATION_NAMESPACE = "errata-causal-program-external-v1"
CUSTODIAN_ATTESTATION_NAMESPACE = "errata-causal-program-external-v1-custodian"
FROZEN_CANDIDATE_IDENTITY = "semantic-set-valued-causal-program-agent-v0"
FROZEN_CANDIDATE_ACTION_BUDGET = 20_000
FROZEN_CANDIDATE_INTERACTION_BUDGET = 20_000
ZERO_SHA256 = "0" * 64

_IDENTITY_PATTERN = re.compile(r"[A-Za-z0-9._:@+-]{1,128}")
_HEX_32_PATTERN = re.compile(r"[0-9a-f]{32}")
_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
_AUTHOR_OPERATIONS = {
    "metadata", "reset_practice", "practice_step", "start_scored", "scored_step",
}


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_value(value: object) -> str:
    return sha256_bytes(canonical_bytes(value))


def _identity(value: object, label: str) -> str:
    if type(value) is not str or not _IDENTITY_PATTERN.fullmatch(value):
        raise ValueError(f"causal-program external {label} identity is invalid")
    return value


def _sha256(value: object, label: str, *, allow_zero: bool = False) -> str:
    if type(value) is not str or not _SHA256_PATTERN.fullmatch(value):
        raise ValueError(f"causal-program external {label} digest is invalid")
    if not allow_zero and value == ZERO_SHA256:
        raise ValueError(f"causal-program external {label} digest is empty")
    return value


@dataclass(frozen=True, slots=True)
class AuthorTurnV1:
    """The complete candidate-visible turn; field names carry no game semantics."""

    observation: tuple[str, str, str]
    mandate: tuple[str, str, str]
    resource: str
    actions: tuple[str, ...]
    terminal: bool
    outcome: Literal["win", "timeout"] | None
    steps_remaining: int
    receipt_sha256: str

    def verify(self) -> None:
        for label, values in (("observation", self.observation), ("mandate", self.mandate)):
            if len(values) != 3 or any(type(value) is not str or not value for value in values):
                raise ValueError(f"causal-program external turn {label} differs")
        if type(self.resource) is not str or not self.resource:
            raise ValueError("causal-program external turn resource differs")
        if (
            len(self.actions) != 5
            or len(set(self.actions)) != 5
            or any(type(action) is not str or not action for action in self.actions)
        ):
            raise ValueError("causal-program external turn action presentation differs")
        if type(self.terminal) is not bool:
            raise ValueError("causal-program external turn terminal differs")
        if self.outcome not in {None, "win", "timeout"}:
            raise ValueError("causal-program external turn outcome differs")
        if self.terminal != (self.outcome is not None):
            raise ValueError("causal-program external turn terminal outcome differs")
        if type(self.steps_remaining) is not int or self.steps_remaining < 0:
            raise ValueError("causal-program external turn horizon differs")
        _sha256(self.receipt_sha256, "turn receipt")

    def payload(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": TURN_SCHEMA,
            "observation": list(self.observation),
            "mandate": list(self.mandate),
            "resource": self.resource,
            "actions": list(self.actions),
            "terminal": self.terminal,
            "outcome": self.outcome,
            "steps_remaining": self.steps_remaining,
            "receipt_sha256": self.receipt_sha256,
        }

    @classmethod
    def from_payload(cls, value: Mapping[str, object]) -> "AuthorTurnV1":
        required = {
            "schema", "observation", "mandate", "resource", "actions",
            "terminal", "outcome", "steps_remaining", "receipt_sha256",
        }
        if set(value) != required or value.get("schema") != TURN_SCHEMA:
            raise ValueError("causal-program external turn schema differs")
        observation = value["observation"]
        mandate = value["mandate"]
        actions = value["actions"]
        if not isinstance(observation, list) or not isinstance(mandate, list) or not isinstance(actions, list):
            raise ValueError("causal-program external turn arrays differ")
        result = cls(
            tuple(observation),  # type: ignore[arg-type]
            tuple(mandate),  # type: ignore[arg-type]
            value["resource"],  # type: ignore[arg-type]
            tuple(actions),  # type: ignore[arg-type]
            value["terminal"],  # type: ignore[arg-type]
            value["outcome"],  # type: ignore[arg-type]
            value["steps_remaining"],  # type: ignore[arg-type]
            value["receipt_sha256"],  # type: ignore[arg-type]
        )
        result.verify()
        return result


def author_request(
    sequence: int,
    operation: Literal["metadata", "reset_practice", "practice_step", "start_scored", "scored_step"],
    *,
    episode_index: int | None = None,
    action: str | None = None,
) -> dict[str, object]:
    if type(sequence) is not int or sequence < 0:
        raise ValueError("causal-program external request sequence differs")
    if operation not in _AUTHOR_OPERATIONS:
        raise ValueError("causal-program external request operation differs")
    if operation == "reset_practice":
        if type(episode_index) is not int or episode_index < 0 or action is not None:
            raise ValueError("causal-program external reset request differs")
    elif operation in {"practice_step", "scored_step"}:
        if type(action) is not str or not action or episode_index is not None:
            raise ValueError("causal-program external step request differs")
    elif episode_index is not None or action is not None:
        raise ValueError("causal-program external request has unexpected arguments")
    return {
        "schema": ABI_SCHEMA,
        "sequence": sequence,
        "kind": "request",
        "operation": operation,
        "episode_index": episode_index,
        "action": action,
    }


def author_response(
    sequence: int,
    operation: str,
    *,
    turn: AuthorTurnV1 | None = None,
    practice_count: int | None = None,
    failure_code: str | None = None,
) -> dict[str, object]:
    if type(sequence) is not int or sequence < 0 or type(operation) is not str:
        raise ValueError("causal-program external response header differs")
    populated = sum(value is not None for value in (turn, practice_count, failure_code))
    if populated != 1:
        raise ValueError("causal-program external response must have one payload")
    if practice_count is not None and (type(practice_count) is not int or practice_count < 1):
        raise ValueError("causal-program external practice count differs")
    if failure_code is not None and (type(failure_code) is not str or not failure_code):
        raise ValueError("causal-program external failure code differs")
    return {
        "schema": ABI_SCHEMA,
        "sequence": sequence,
        "kind": "response",
        "operation": operation,
        "turn": None if turn is None else turn.payload(),
        "practice_count": practice_count,
        "failure_code": failure_code,
    }


def verify_author_jsonl(lines: Sequence[bytes]) -> dict[str, object]:
    """Verify a disclosure-safe conformance transcript, not a candidate trace."""

    if not lines or len(lines) % 2:
        raise ValueError("causal-program external JSONL must contain request/response pairs")
    operations: list[str] = []
    for pair_index in range(0, len(lines), 2):
        try:
            request = json.loads(lines[pair_index])
            response = json.loads(lines[pair_index + 1])
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError("causal-program external JSONL is not canonical JSON") from exc
        if canonical_bytes(request) != lines[pair_index] or canonical_bytes(response) != lines[pair_index + 1]:
            raise ValueError("causal-program external JSONL bytes are not canonical")
        expected_sequence = pair_index // 2
        if (
            request.get("schema") != ABI_SCHEMA
            or request.get("kind") != "request"
            or request.get("sequence") != expected_sequence
            or set(request) != {"schema", "sequence", "kind", "operation", "episode_index", "action"}
        ):
            raise ValueError("causal-program external request envelope differs")
        canonical_request = author_request(
            expected_sequence,
            request["operation"],
            episode_index=request["episode_index"],
            action=request["action"],
        )
        if request != canonical_request:
            raise ValueError("causal-program external request differs")
        if (
            response.get("schema") != ABI_SCHEMA
            or response.get("kind") != "response"
            or response.get("sequence") != expected_sequence
            or response.get("operation") != request["operation"]
            or set(response) != {"schema", "sequence", "kind", "operation", "turn", "practice_count", "failure_code"}
        ):
            raise ValueError("causal-program external response envelope differs")
        payloads = [response["turn"], response["practice_count"], response["failure_code"]]
        if sum(value is not None for value in payloads) != 1:
            raise ValueError("causal-program external response payload differs")
        if response["turn"] is not None:
            AuthorTurnV1.from_payload(response["turn"])
        elif response["practice_count"] is not None:
            if request["operation"] != "metadata" or type(response["practice_count"]) is not int or response["practice_count"] < 1:
                raise ValueError("causal-program external metadata differs")
        elif type(response["failure_code"]) is not str or not response["failure_code"]:
            raise ValueError("causal-program external failure differs")
        operations.append(request["operation"])
    return {
        "schema": "errata.causal-program-external.author-conformance.v1",
        "pairs": len(lines) // 2,
        "operations": operations,
        "jsonl_sha256": sha256_bytes(b"".join(lines)),
        "contains_candidate_source_or_trace": False,
    }


@dataclass(frozen=True, slots=True)
class ArmDefinitionV1:
    arm_id: str
    label: str
    input_rule: str
    executor_rule: str
    implementation_status: Literal["deterministic-reference", "external-required"]


ARM_REGISTRY: tuple[ArmDefinitionV1, ...] = (
    ArmDefinitionV1("informative", "Informative exploration", "Frozen learner receives informative public practice.", "Fresh common executor receives the admitted learned artifact.", "deterministic-reference"),
    ArmDefinitionV1("matched-noninformative", "Exactly matched noninformative activity", "Same learner receives chronology-, event-, motor-, reset-, byte-, and budget-matched activity with decision-relevant evidence removed.", "Fresh common executor receives the resulting admitted artifact or typed absence.", "external-required"),
    ArmDefinitionV1("zero", "No exploration", "No practice calls and canonical artifact absence.", "Fresh common executor receives no learned artifact.", "deterministic-reference"),
    ArmDefinitionV1("semantic-corruption", "Valid semantic corruption", "A prospectively selected, parser-valid, provenance-preserving decision-relevant semantic intervention is applied without scored-behavior access.", "The exact common parser and executor used by informative receive the corrupted artifact.", "external-required"),
    ArmDefinitionV1("oracle", "Oracle headroom", "Custodian-private truth is encoded through the same admitted artifact interface.", "The exact common parser and executor receive no extra actuation budget.", "external-required"),
    ArmDefinitionV1("same-information-gp-direct", "Strongest same-information general-purpose direct", "A frozen general-purpose policy receives the complete informative public transcript, no learned artifact, and equal-or-better resources.", "Its own fresh process acts through the same scored capability.", "external-required"),
    ArmDefinitionV1("briefed-no-winning-action", "Briefed without winning action", "The unchanged agent receives a truthful task explanation that contains no winning action, plan, or hidden truth.", "Its learner and executor retain the same process and authority boundary.", "external-required"),
    ArmDefinitionV1("incumbent", "Incumbent", "The outside author prospectively declares the ordinary existing way this game would be solved.", "The incumbent runs under its native declared budget and is reported without weakening.", "external-required"),
)


def arm_registry_payload() -> dict[str, object]:
    payload = {
        "schema": ARM_REGISTRY_SCHEMA,
        "candidate_identity": FROZEN_CANDIDATE_IDENTITY,
        "execution_status": "registry-only-no-model-arm-execution",
        "arms": [
            {
                "arm_id": arm.arm_id,
                "label": arm.label,
                "input_rule": arm.input_rule,
                "executor_rule": arm.executor_rule,
                "implementation_status": arm.implementation_status,
            }
            for arm in ARM_REGISTRY
        ],
    }
    return {**payload, "canonical_sha256": _sha256_value(payload)}


ARM_REGISTRY_SHA256 = arm_registry_payload()["canonical_sha256"]


AUTHOR_NON_EXPOSURE_ATTESTATIONS = (
    "author_did_not_receive_candidate_source",
    "author_did_not_receive_candidate_prompt_or_model_configuration",
    "author_did_not_receive_candidate_development_or_evaluation_traces",
    "author_did_not_receive_arm_outcomes_or_scored_behavior",
    "author_package_was_sealed_before_candidate_access",
)

EVIDENCE_FIELDS = (
    "sealed_source_sha256",
    "runtime_image_sha256",
    "evaluator_sha256",
    "oracle_sha256",
    "arm_implementations_sha256",
    "draw_protocol_sha256",
    "analysis_plan_sha256",
    "confinement_policy_sha256",
    "shutdown_rollback_policy_sha256",
    "primary_renderer_sha256",
    "independent_renderer_sha256",
    "nonenumeration_certificate_sha256",
    "nonenumeration_proof_sha256",
    "nonenumeration_verifier_sha256",
    "transparency_log_entry_sha256",
    "custodian_attestation_sha256",
    "author_signing_key_sha256",
    "custodian_signing_key_sha256",
    "signed_attestation_sha256",
    "custodian_signed_attestation_sha256",
)

SIGNATURE_EVIDENCE_FIELDS = (
    "signed_attestation_sha256",
    "custodian_signed_attestation_sha256",
)

PREDRAW_SOURCE_PATHS = (
    "src/errata/north_star/causal_program_semantic_agent_v0.py",
    "src/errata/north_star/causal_program_external_v1.py",
    "src/errata/north_star/causal_program_external_v1_host.py",
    "docs/causal_program_external_v1.md",
    "tests/fixtures/causal_program_external_v1_author_conformance.jsonl",
)


def predraw_analysis_plan_payload() -> dict[str, object]:
    """Return the prospective, result-independent admission rules.

    Four ordered retained cases preserve the already frozen base-case sample
    size while requiring an outside-authored generator/capsule.  Pairwise
    discordances are evaluated on those same case identities; no marginal-only
    substitution or post-draw case replacement is admissible.
    """

    payload = {
        "schema": "errata.causal-program-external.analysis-plan.v1",
        "retained_case_count": 4,
        "outcome_metric": "binary independently-rendered native win",
        "required_gates": {
            "informative_wins_at_least": 3,
            "matched_noninformative_wins_at_most": 1,
            "zero_exploration_wins_at_most": 1,
            "semantic_corruption_wins_at_most": 1,
            "oracle_wins_exactly": 4,
            "informative_only_vs_matched_noninformative_at_least": 2,
            "matched_noninformative_only_vs_informative_exactly": 0,
            "informative_only_vs_zero_exploration_at_least": 2,
            "zero_exploration_only_vs_informative_exactly": 0,
            "informative_only_vs_semantic_corruption_at_least": 2,
            "semantic_corruption_only_vs_informative_exactly": 0,
            "all_oracle_proofs_verify": True,
            "all_cases_have_oracle_success_on_unseen_decision_relevant_edge": True,
            "all_nonenumeration_verifiers_accept": True,
            "primary_and_independent_renderers_agree_exactly": True,
            "complete_deterministic_replay": True,
            "restricted_process_policy_violations_exactly": 0,
            "post_draw_case_replacements_exactly": 0,
        },
        "mandatory_report_only_comparisons": [
            "same-information-gp-direct",
            "briefed-no-winning-action",
            "incumbent",
        ],
        "classification_rules": {
            "retire_specialized_architecture_if": (
                "same-information-gp-direct wins are greater than or equal to "
                "informative wins on the same retained cases"
            ),
            "classify_executor_not_discovery_if": (
                "informative wins are below three and briefed-no-winning-action "
                "wins are at least three on the same retained cases"
            ),
            "retire_discovery_claim_if": (
                "either informative-vs-matched-noninformative or "
                "informative-vs-zero required paired gate fails"
            ),
        },
        "exclusions": (
            "No post-draw exclusion, threshold change, arm repair, case repair, "
            "or renderer substitution is admissible. Infrastructure failure is "
            "reported and the frozen evaluation does not pass."
        ),
    }
    return {**payload, "canonical_sha256": _sha256_value(payload)}


def predraw_analysis_plan_file_sha256() -> str:
    """Digest of the exact canonical analysis-plan evidence file."""

    return sha256_bytes(canonical_bytes(predraw_analysis_plan_payload()))


def build_predraw_freeze(
    *,
    source_commit: str,
    source_sha256: Mapping[str, str],
    split_process_commitment: Mapping[str, str],
    recruitment_release_notes_sha256: str,
) -> dict[str, object]:
    """Build a root-free public freeze; publication supplies the timestamp."""

    if type(source_commit) is not str or not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ValueError("causal-program external source commit differs")
    if set(source_sha256) != set(PREDRAW_SOURCE_PATHS):
        raise ValueError("causal-program external predraw source closure differs")
    for path, digest in source_sha256.items():
        if type(path) is not str or path.startswith("/") or ".." in Path(path).parts:
            raise ValueError("causal-program external predraw source path differs")
        _sha256(digest, f"predraw source {path}")
    if set(split_process_commitment) != {"candidate_sha256", "bootstrap_sha256", "host_sha256"}:
        raise ValueError("causal-program external split-process commitment differs")
    for label, digest in split_process_commitment.items():
        _sha256(digest, f"split-process {label}")
    if split_process_commitment["candidate_sha256"] != source_sha256[PREDRAW_SOURCE_PATHS[0]]:
        raise ValueError("causal-program external candidate commitment differs")
    if split_process_commitment["host_sha256"] != source_sha256[PREDRAW_SOURCE_PATHS[2]]:
        raise ValueError("causal-program external host commitment differs")
    _sha256(recruitment_release_notes_sha256, "recruitment release notes")
    analysis = predraw_analysis_plan_payload()
    payload = {
        "schema": PREDRAW_FREEZE_SCHEMA,
        "status": "root-free-pre-draw-pre-candidate-transfer",
        "candidate_identity": FROZEN_CANDIDATE_IDENTITY,
        "candidate_action_budget": FROZEN_CANDIDATE_ACTION_BUDGET,
        "candidate_interaction_budget": FROZEN_CANDIDATE_INTERACTION_BUDGET,
        "source_commit": source_commit,
        "source_sha256": dict(sorted(source_sha256.items())),
        "split_process_commitment": dict(sorted(split_process_commitment.items())),
        "arm_registry": arm_registry_payload(),
        "analysis_plan": analysis,
        "recruitment_release_notes_sha256": recruitment_release_notes_sha256,
        "roots_selected": False,
        "outside_capsules_accepted": 0,
        "model_arms_executed": [],
        "results_observed": False,
        "public_timestamp_required_before_draw": True,
    }
    return {**payload, "canonical_sha256": _sha256_value(payload)}


def verify_predraw_freeze(value: Mapping[str, object]) -> None:
    expected = {
        "schema", "status", "candidate_identity", "candidate_action_budget",
        "candidate_interaction_budget",
        "source_commit", "source_sha256", "split_process_commitment", "arm_registry", "analysis_plan",
        "recruitment_release_notes_sha256", "roots_selected", "outside_capsules_accepted",
        "model_arms_executed", "results_observed", "public_timestamp_required_before_draw",
        "canonical_sha256",
    }
    if set(value) != expected or value.get("schema") != PREDRAW_FREEZE_SCHEMA:
        raise ValueError("causal-program external predraw freeze schema differs")
    source = value.get("source_sha256")
    split_process = value.get("split_process_commitment")
    if not isinstance(source, dict) or not isinstance(split_process, dict):
        raise ValueError("causal-program external predraw source closure differs")
    rebuilt = build_predraw_freeze(
        source_commit=value["source_commit"],  # type: ignore[arg-type]
        source_sha256=source,  # type: ignore[arg-type]
        split_process_commitment=split_process,  # type: ignore[arg-type]
        recruitment_release_notes_sha256=value["recruitment_release_notes_sha256"],  # type: ignore[arg-type]
    )
    if value != rebuilt:
        raise ValueError("causal-program external predraw freeze differs")


def identity_commitment(identity: str, public_key: bytes, *, role: str) -> str:
    normalized = _identity(identity, role)
    return _sha256_value({
        "schema": "errata.causal-program-external.identity.v1",
        "role": role,
        "identity": normalized,
        "public_key_sha256": sha256_bytes(public_key),
    })


def build_nonenumeration_certificate(
    *,
    certificate_id: str,
    method: str,
    decision_relevant_state_lower_bound: int,
    decision_relevant_transition_lower_bound: int,
    exhaustive_interaction_lower_bound: int,
    proof_sha256: str,
    verifier_sha256: str,
) -> dict[str, object]:
    if not _HEX_32_PATTERN.fullmatch(certificate_id):
        raise ValueError("causal-program external nonenumeration certificate id differs")
    if type(method) is not str or not method.strip():
        raise ValueError("causal-program external nonenumeration method differs")
    for label, value in (
        ("state", decision_relevant_state_lower_bound),
        ("transition", decision_relevant_transition_lower_bound),
        ("interaction", exhaustive_interaction_lower_bound),
    ):
        if type(value) is not int or value < 1:
            raise ValueError(f"causal-program external nonenumeration {label} bound differs")
    if exhaustive_interaction_lower_bound <= FROZEN_CANDIDATE_INTERACTION_BUDGET:
        raise ValueError("causal-program external world is enumerable within the candidate budget")
    _sha256(proof_sha256, "nonenumeration proof")
    _sha256(verifier_sha256, "nonenumeration verifier")
    payload = {
        "schema": NONENUMERATION_SCHEMA,
        "certificate_id": certificate_id,
        "method": method.strip(),
        "candidate_identity": FROZEN_CANDIDATE_IDENTITY,
        "candidate_action_budget": FROZEN_CANDIDATE_ACTION_BUDGET,
        "candidate_interaction_budget": FROZEN_CANDIDATE_INTERACTION_BUDGET,
        "decision_relevant_state_lower_bound": decision_relevant_state_lower_bound,
        "decision_relevant_transition_lower_bound": decision_relevant_transition_lower_bound,
        "exhaustive_interaction_lower_bound": exhaustive_interaction_lower_bound,
        "decision_relevant_only": True,
        "irrelevant_state_padding_excluded": True,
        "exhaustive_enumeration_possible_within_budget": False,
        "proof_sha256": proof_sha256,
        "verifier_sha256": verifier_sha256,
    }
    return {**payload, "canonical_sha256": _sha256_value(payload)}


def verify_nonenumeration_certificate(value: Mapping[str, object]) -> None:
    if set(value) != {
        "schema", "certificate_id", "method", "candidate_identity",
        "candidate_action_budget", "candidate_interaction_budget",
        "decision_relevant_state_lower_bound",
        "decision_relevant_transition_lower_bound", "exhaustive_interaction_lower_bound",
        "decision_relevant_only", "irrelevant_state_padding_excluded",
        "exhaustive_enumeration_possible_within_budget", "proof_sha256",
        "verifier_sha256", "canonical_sha256",
    }:
        raise ValueError("causal-program external nonenumeration schema differs")
    rebuilt = build_nonenumeration_certificate(
        certificate_id=value["certificate_id"],  # type: ignore[arg-type]
        method=value["method"],  # type: ignore[arg-type]
        decision_relevant_state_lower_bound=value["decision_relevant_state_lower_bound"],  # type: ignore[arg-type]
        decision_relevant_transition_lower_bound=value["decision_relevant_transition_lower_bound"],  # type: ignore[arg-type]
        exhaustive_interaction_lower_bound=value["exhaustive_interaction_lower_bound"],  # type: ignore[arg-type]
        proof_sha256=value["proof_sha256"],  # type: ignore[arg-type]
        verifier_sha256=value["verifier_sha256"],  # type: ignore[arg-type]
    )
    if value != rebuilt:
        raise ValueError("causal-program external nonenumeration certificate differs")


def build_capsule_manifest(
    *,
    capsule_id: str,
    author_identity: str,
    author_public_key: bytes,
    custodian_identity: str,
    custodian_public_key: bytes,
    custody_commitment_sha256: str,
    predraw_freeze_sha256: str,
    evidence_sha256: Mapping[str, str],
    non_exposure_attestations: Mapping[str, bool],
) -> dict[str, object]:
    if not _HEX_32_PATTERN.fullmatch(capsule_id):
        raise ValueError("causal-program external capsule id differs")
    author = _identity(author_identity, "author")
    custodian = _identity(custodian_identity, "custodian")
    if set(evidence_sha256) != set(EVIDENCE_FIELDS):
        raise ValueError("causal-program external capsule evidence commitments are incomplete")
    for field, digest in evidence_sha256.items():
        _sha256(digest, field, allow_zero=field in SIGNATURE_EVIDENCE_FIELDS)
    if evidence_sha256["analysis_plan_sha256"] != predraw_analysis_plan_file_sha256():
        raise ValueError("causal-program external capsule analysis plan differs from predraw freeze")
    if set(non_exposure_attestations) != set(AUTHOR_NON_EXPOSURE_ATTESTATIONS) or not all(
        type(value) is bool and value for value in non_exposure_attestations.values()
    ):
        raise ValueError("causal-program external author non-exposure attestation differs")
    _sha256(custody_commitment_sha256, "custody commitment")
    _sha256(predraw_freeze_sha256, "predraw freeze")
    author_commitment = identity_commitment(author, author_public_key, role="author")
    custodian_key_commitment = identity_commitment(
        custodian, custodian_public_key, role="custodian"
    )
    custodian_commitment = _sha256_value({
        "schema": "errata.causal-program-external.custodian.v1",
        "custodian_identity": custodian,
        "custodian_key_commitment_sha256": custodian_key_commitment,
        "custody_commitment_sha256": custody_commitment_sha256,
        "custodian_attestation_sha256": evidence_sha256["custodian_attestation_sha256"],
    })
    payload = {
        "schema": CAPSULE_SCHEMA,
        "capsule_id": capsule_id,
        "candidate_identity": FROZEN_CANDIDATE_IDENTITY,
        "candidate_action_budget": FROZEN_CANDIDATE_ACTION_BUDGET,
        "candidate_interaction_budget": FROZEN_CANDIDATE_INTERACTION_BUDGET,
        "author_identity_commitment_sha256": author_commitment,
        "custodian_identity_commitment_sha256": custodian_commitment,
        "custodian_key_commitment_sha256": custodian_key_commitment,
        "custody_commitment_sha256": custody_commitment_sha256,
        "predraw_freeze_sha256": predraw_freeze_sha256,
        "arm_registry_sha256": ARM_REGISTRY_SHA256,
        "author_non_exposure_attestations": dict(sorted(non_exposure_attestations.items())),
        **dict(evidence_sha256),
        "status": "sealed-pre-candidate-intake-only",
    }
    return {**payload, "canonical_sha256": _sha256_value(payload)}


def verify_capsule_manifest(value: Mapping[str, object]) -> None:
    expected = {
        "schema", "capsule_id", "candidate_identity", "candidate_action_budget",
        "candidate_interaction_budget",
        "author_identity_commitment_sha256", "custodian_identity_commitment_sha256",
        "custodian_key_commitment_sha256", "custody_commitment_sha256",
        "predraw_freeze_sha256", "arm_registry_sha256",
        "author_non_exposure_attestations", "status", "canonical_sha256",
        *EVIDENCE_FIELDS,
    }
    if set(value) != expected or value.get("schema") != CAPSULE_SCHEMA:
        raise ValueError("causal-program external capsule schema differs")
    if (
        value.get("candidate_identity") != FROZEN_CANDIDATE_IDENTITY
        or value.get("candidate_action_budget") != FROZEN_CANDIDATE_ACTION_BUDGET
        or value.get("candidate_interaction_budget") != FROZEN_CANDIDATE_INTERACTION_BUDGET
    ):
        raise ValueError("causal-program external capsule candidate boundary differs")
    if value.get("arm_registry_sha256") != ARM_REGISTRY_SHA256:
        raise ValueError("causal-program external arm registry differs")
    if value.get("status") != "sealed-pre-candidate-intake-only":
        raise ValueError("causal-program external capsule status differs")
    if not _HEX_32_PATTERN.fullmatch(value["capsule_id"]):  # type: ignore[arg-type]
        raise ValueError("causal-program external capsule id differs")
    for field in (
        "author_identity_commitment_sha256", "custodian_identity_commitment_sha256",
        "custodian_key_commitment_sha256", "custody_commitment_sha256",
        "predraw_freeze_sha256", "arm_registry_sha256", *EVIDENCE_FIELDS,
    ):
        _sha256(value[field], field, allow_zero=field in SIGNATURE_EVIDENCE_FIELDS)
    attestations = value["author_non_exposure_attestations"]
    if not isinstance(attestations, dict) or set(attestations) != set(AUTHOR_NON_EXPOSURE_ATTESTATIONS) or not all(type(item) is bool and item for item in attestations.values()):
        raise ValueError("causal-program external author non-exposure attestation differs")
    payload = {key: item for key, item in value.items() if key != "canonical_sha256"}
    if value["canonical_sha256"] != _sha256_value(payload):
        raise ValueError("causal-program external capsule canonical digest differs")


def capsule_attestation_bytes(manifest: Mapping[str, object]) -> bytes:
    verify_capsule_manifest(manifest)
    return canonical_bytes({
        key: value
        for key, value in manifest.items()
        if key not in {"canonical_sha256", *SIGNATURE_EVIDENCE_FIELDS}
    })


def _allowed_signer_line(identity: str, public_key: bytes) -> bytes:
    try:
        tokens = public_key.decode().strip().split()
    except UnicodeDecodeError as exc:
        raise ValueError("causal-program external author public key is not UTF-8") from exc
    if len(tokens) < 2 or not tokens[0].startswith("ssh-"):
        raise ValueError("causal-program external author public key is not OpenSSH format")
    return f"{identity} {tokens[0]} {tokens[1]}\n".encode()


def _verify_sshsig(
    identity: str,
    public_key: bytes,
    signature_path: Path,
    message: bytes,
    *,
    namespace: str = ATTESTATION_NAMESPACE,
) -> None:
    with tempfile.TemporaryDirectory(prefix="errata-causal-external-v1-") as temporary:
        allowed = Path(temporary) / "allowed_signers"
        allowed.write_bytes(_allowed_signer_line(identity, public_key))
        result = subprocess.run(
            ("ssh-keygen", "-Y", "verify", "-f", str(allowed), "-I", identity,
             "-n", namespace, "-s", str(signature_path)),
            input=message,
            capture_output=True,
        )
    if result.returncode != 0:
        detail = result.stderr.decode(errors="replace").strip()
        raise ValueError(f"causal-program external signer signature verification failed: {detail}")


def verify_outside_capsule_intake(
    manifest: Mapping[str, object],
    *,
    author_identity: str,
    custodian_identity: str,
    expected_predraw_freeze_sha256: str,
    evidence_paths: Mapping[str, Path],
) -> dict[str, object]:
    verify_capsule_manifest(manifest)
    author = _identity(author_identity, "author")
    custodian = _identity(custodian_identity, "custodian")
    _sha256(expected_predraw_freeze_sha256, "expected predraw freeze")
    if manifest["predraw_freeze_sha256"] != expected_predraw_freeze_sha256:
        raise ValueError("causal-program external capsule binds another predraw freeze")
    if set(evidence_paths) != set(EVIDENCE_FIELDS):
        raise ValueError("causal-program external evidence paths are incomplete")
    bodies: dict[str, bytes] = {}
    evidence_rows = []
    for field in EVIDENCE_FIELDS:
        body = Path(evidence_paths[field]).read_bytes()
        if not body:
            raise ValueError(f"causal-program external evidence is empty: {field}")
        digest = sha256_bytes(body)
        if digest != manifest[field]:
            raise ValueError(f"causal-program external evidence digest mismatch: {field}")
        bodies[field] = body
        evidence_rows.append({"field": field, "sha256": digest, "bytes": len(body)})
    if len({row["sha256"] for row in evidence_rows}) != len(evidence_rows):
        raise ValueError("causal-program external evidence files must be distinct")
    author_key = bodies["author_signing_key_sha256"]
    custodian_key = bodies["custodian_signing_key_sha256"]
    if identity_commitment(author, author_key, role="author") != manifest["author_identity_commitment_sha256"]:
        raise ValueError("causal-program external author identity commitment mismatch")
    custodian_key_commitment = identity_commitment(
        custodian, custodian_key, role="custodian"
    )
    if custodian_key_commitment != manifest["custodian_key_commitment_sha256"]:
        raise ValueError("causal-program external custodian key commitment mismatch")
    expected_custodian = _sha256_value({
        "schema": "errata.causal-program-external.custodian.v1",
        "custodian_identity": custodian,
        "custodian_key_commitment_sha256": custodian_key_commitment,
        "custody_commitment_sha256": manifest["custody_commitment_sha256"],
        "custodian_attestation_sha256": manifest["custodian_attestation_sha256"],
    })
    if expected_custodian != manifest["custodian_identity_commitment_sha256"]:
        raise ValueError("causal-program external custodian identity commitment mismatch")
    try:
        certificate = json.loads(bodies["nonenumeration_certificate_sha256"])
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("causal-program external nonenumeration certificate is not JSON") from exc
    if canonical_bytes(certificate) != bodies["nonenumeration_certificate_sha256"]:
        raise ValueError("causal-program external nonenumeration certificate is not canonical")
    verify_nonenumeration_certificate(certificate)
    if certificate["proof_sha256"] != manifest["nonenumeration_proof_sha256"] or certificate["verifier_sha256"] != manifest["nonenumeration_verifier_sha256"]:
        raise ValueError("causal-program external nonenumeration evidence binding differs")
    _verify_sshsig(
        author,
        author_key,
        Path(evidence_paths["signed_attestation_sha256"]),
        capsule_attestation_bytes(manifest),
    )
    _verify_sshsig(
        custodian,
        custodian_key,
        Path(evidence_paths["custodian_signed_attestation_sha256"]),
        capsule_attestation_bytes(manifest),
        namespace=CUSTODIAN_ATTESTATION_NAMESPACE,
    )
    payload = {
        "schema": INTAKE_SCHEMA,
        "capsule_id": manifest["capsule_id"],
        "capsule_canonical_sha256": manifest["canonical_sha256"],
        "author_identity_commitment_sha256": manifest["author_identity_commitment_sha256"],
        "custodian_identity_commitment_sha256": manifest["custodian_identity_commitment_sha256"],
        "predraw_freeze_sha256": manifest["predraw_freeze_sha256"],
        "arm_registry_sha256": ARM_REGISTRY_SHA256,
        "nonenumeration_certificate_sha256": manifest["nonenumeration_certificate_sha256"],
        "evidence": evidence_rows,
        "acceptance_checks": {
            "manifest_is_canonical": True,
            "all_committed_evidence_bytes_match": True,
            "author_identity_is_key_bound": True,
            "author_signature_is_valid": True,
            "all_non_exposure_attestations_are_true": True,
            "custodian_identity_and_commitment_are_bound": True,
            "custodian_signature_is_valid": True,
            "capsule_binds_expected_public_predraw_freeze": True,
            "oracle_and_evaluator_bytes_are_committed": True,
            "arms_draw_analysis_confinement_and_renderers_are_committed": True,
            "decision_relevant_nonenumeration_certificate_is_bound": True,
            "no_root_or_result_is_admitted": True,
        },
        "status": "intake-accepted-pre-candidate-only",
        "claim_boundary": (
            "This receipt verifies canonical bytes, declared author non-exposure, "
            "identity and custody commitments, author and custodian signatures, and a syntactically "
            "valid decision-relevant non-enumeration certificate. It does not establish "
            "independent authorship, custodian honesty, proof correctness, oracle or "
            "evaluator correctness, public chronology, root selection, or agent performance."
        ),
    }
    return {**payload, "canonical_sha256": _sha256_value(payload)}


__all__ = [
    "ABI_SCHEMA", "ARM_REGISTRY", "ARM_REGISTRY_SHA256", "ATTESTATION_NAMESPACE",
    "AUTHOR_NON_EXPOSURE_ATTESTATIONS", "AuthorTurnV1",
    "CUSTODIAN_ATTESTATION_NAMESPACE", "EVIDENCE_FIELDS",
    "FROZEN_CANDIDATE_ACTION_BUDGET", "FROZEN_CANDIDATE_IDENTITY",
    "FROZEN_CANDIDATE_INTERACTION_BUDGET",
    "PREDRAW_FREEZE_SCHEMA", "PREDRAW_SOURCE_PATHS", "SIGNATURE_EVIDENCE_FIELDS",
    "arm_registry_payload", "author_request", "author_response",
    "build_capsule_manifest", "build_nonenumeration_certificate",
    "build_predraw_freeze", "predraw_analysis_plan_payload",
    "predraw_analysis_plan_file_sha256",
    "canonical_bytes", "capsule_attestation_bytes", "identity_commitment",
    "sha256_bytes", "verify_author_jsonl", "verify_capsule_manifest",
    "verify_nonenumeration_certificate", "verify_outside_capsule_intake",
    "verify_predraw_freeze",
]
