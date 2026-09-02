from __future__ import annotations

import json
from typing import Any

from .authority import AuthorityPolicy
from .redaction import redact_text
from .state import PursuitState
from .tools import tool_descriptions


_PUBLIC_EVENT_KINDS = {
    "tool_result",
    "user_answer",
    "capability_granted",
    "capability_requested",
    "capability_consequence",
    "terminal_rejected",
    "action_rejected",
    "environment_changed",
    "interrupted_action_recovered",
    "provider_error",
    "run_resumed",
    "scope_violation",
    "scope_violation_resolved",
    "strategy_stalled",
    "tool_interrupted",
    "workspace_change",
}


def build_direct_prompt(
    state: PursuitState,
    events: list[dict[str, Any]],
    authority: AuthorityPolicy,
    *,
    limits: dict[str, int] | None = None,
) -> str:
    """Build the matched direct-arm prompt without pursuit working memory.

    The direct arm sees its own public observations and mechanical action schema,
    but never receives the pursuit arm's notebook, contract, hypotheses, or run.
    """

    selected = [event for event in events if event.get("kind") in _PUBLIC_EVENT_KINDS]
    compacted: list[dict[str, Any]] = []
    for event in selected:
        payload, _ = redact_text(json.dumps(event.get("payload", {}), sort_keys=True))
        if len(payload) > 8_000:
            payload = payload[:8_000] + "...[truncated]"
        compacted.append(
            {
                "event_id": event["event_id"],
                "step": event["step"],
                "kind": event["kind"],
                "payload_json": payload,
            }
        )
    # Retain the full bounded direct trajectory instead of importing Errata's
    # selected-memory policy. The total is capped deterministically from the tail.
    while len(json.dumps(compacted, sort_keys=True)) > 80_000 and compacted:
        compacted.pop(0)

    mandate, _ = redact_text(state.mandate)
    direct_scratch, _ = redact_text(state.notebook)
    matched_limits = limits or {
        "maximum_changed_files": 50,
        "maximum_added_lines": 5_000,
        "maximum_deleted_lines": 5_000,
    }
    return f"""SOLVE THE USER'S OUTCOME DIRECTLY IN THE SELECTED WORKSPACE.

Mandate:
{mandate}

Selected workspace:
{state.workspace}

Authority boundary:
{json.dumps(authority.summary(), indent=2, sort_keys=True)}

You are a strong general-purpose Codex agent. Work from the mandate and the
workspace evidence available to you. Inspect the actual situation, decide what
would distinguish the mandate-level outcome from misleading partial success,
take one bounded next action, inspect its consequence, and continue until the
outcome is directly verified or a checkable blocker is established. Preserve
unrelated state. Do not treat a patch, passing partial test, ticket state,
generated file, process launch, or confidence as the outcome. After a mutation,
verify project-native behavior and a clean rerun, restart, regeneration, or
equivalent durability boundary available in the project.

You have the same mechanical action and terminal-admission protocol as the
other arm. The protocol fields are audit records, not a suggested decomposition
or strategy. Decide the work yourself. `notebook` is your own ordinary concise
scratch summary, up to 1,200 characters; it is never shared with or imported
from another arm. No pursuit-arm notebook, snapshot, predecessor contract, or
discovered answer is available. Do not refer to another arm.

Choose exactly one decision. `continue` and `change_strategy` execute one tool.
`request_user` asks only for decision-relevant missing information or exact
authority. `stop_success` cites successful tool-result events that directly
verify the mandate. `stop_blocked` cites tool-result evidence for a necessary
failed condition and names the smallest accurate recovery condition.

Before any mutation, snapshot must include nonempty `causal_situation`,
`inferred_game`, `win_condition`, `boundary`, `preservation_invariants`,
`allowed_changes`, `change_budget`, `expected_consequence`, and `falsifiers`.
The fixed cohort ceiling is {matched_limits['maximum_changed_files']} changed
files, {matched_limits['maximum_added_lines']} added lines, and
{matched_limits['maximum_deleted_lines']} deleted lines; choose no broader
allowed paths or budget than the next action requires.
`allowed_changes` and `change_budget` are enforced against the cumulative
workspace delta, not only the next write. Before every later mutation, retain
every already changed path that is still intended, add every path the next
action may change, and set the budget at least as large as the resulting
cumulative delta. Never make a source edit while the committed scope names
only a test file; revise the scope first.
If environment change or repeated-action evidence requires a new approach, use
`change_strategy` and set `snapshot.strategy_revision`.

For `request_user`, snapshot.capability_request must contain exactly `kind`,
`blocked_path`, `minimum_scope`, `evidence_event_ids`, `unlock_test`, and
`requested_names`. Allowed kinds are information, secret_input,
workspace_environment, workspace_dependency, host_runtime, external_service,
and external_effect. Secret inputs name exact uppercase environment variables;
other kinds use an empty requested_names list.

For `stop_success`, snapshot.outcome_verification must contain `result`,
`causal_link`, `evidence_event_ids`, `evidence_class` equal to `direct`,
`usage_path`, and `evidence_limitations`. snapshot.invariant_verification must
contain one preserved entry with post-mutation evidence ids for every invariant
previously committed by this run. For `stop_blocked`,
snapshot.non_win_certificate must contain `failed_condition`,
`evidence_event_ids`, `uncertainty`, `attempted_strategies`,
`exhaustion_reason`, and `recovery_condition`. Every terminal snapshot retains
nonempty causal_situation, inferred_game, win_condition, and boundary.

Available tools:
{json.dumps(tool_descriptions(), indent=2, sort_keys=True)}

Initial protected dirty paths:
{json.dumps(list(state.initial_dirty_paths), indent=2)}

Authoritative accumulated preservation invariants:
{json.dumps(list(state.preservation_invariants), indent=2)}

Your own direct-arm scratch summary:
{direct_scratch or "(empty)"}

Your public tool and authority transcript:
{json.dumps(compacted, indent=2)}

Return exactly one JSON object with only these fields:
{{
  "decision": "continue | change_strategy | request_user | stop_success | stop_blocked",
  "rationale": "short explanation",
  "notebook": "your concise direct-arm scratch summary, maximum 1200 characters",
  "snapshot": {{"concise audit fields for this decision": true}},
  "action": {{"tool": "one available tool", "arguments": {{}}}} or null,
  "evidence_event_ids": [integer event ids],
  "user_question": "question or empty string",
  "terminal_summary": "verified result or blocker, or empty string"
}}
"""
