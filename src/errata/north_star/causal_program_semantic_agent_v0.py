"""Public-only semantic discovery for opaque causal-program games.

The learner knows only a bounded *language* of possible causal programs.  It
does not import the evaluator, receive a generated program, or inspect native
state.  It enumerates public practice trajectories, identifies opaque action
roles from consequences, fits every program consistent with those receipts,
and closes a canonical set-valued contract.  A fresh executor then searches
for one opaque action sequence that wins under every admitted hypothesis.
"""

from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
import hashlib
import itertools
import json
from typing import Final, Literal, Protocol


Effect = Literal["toggle", "set-0", "set-1"]
Outcome = Literal["win", "timeout"]
SEMANTIC_ROLES: Final = ("drive", "pulse", "consume", "wait", "commit")


class OpaqueTurn(Protocol):
    observation: tuple[str, str, str]
    mandate: tuple[str, str, str]
    resource: str
    legal_actions: tuple[str, ...]
    terminal: bool
    outcome: Outcome | None
    steps_remaining: int
    receipt_sha256: str


class PracticePort(Protocol):
    @property
    def practice_count(self) -> int: ...

    def reset_practice(self, index: int) -> OpaqueTurn: ...

    def step(self, opaque_action: str) -> OpaqueTurn: ...


def _canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _sha(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


@dataclass(frozen=True)
class PublicStep:
    action: str
    observation: tuple[str, str, str]
    resource: str
    terminal: bool
    outcome: Outcome | None
    receipt_sha256: str


@dataclass(frozen=True)
class PublicTrace:
    episode_index: int
    initial_observation: tuple[str, str, str]
    mandate: tuple[str, str, str]
    initial_resource: str
    horizon: int
    actions: tuple[str, ...]
    steps: tuple[PublicStep, ...]


@dataclass(frozen=True)
class ProgramHypothesis:
    false_symbols: tuple[str, str, str]
    action_roles: tuple[tuple[str, str], ...]
    drive_source: int
    drive_target: int
    drive_guard: int
    drive_guard_value: bool
    drive_effect: Effect
    pulse_guard: int
    pulse_guard_value: bool
    pulse_target: int
    pulse_effect: Effect
    pulse_delay: int
    consume_guard: int
    consume_guard_value: bool
    consume_target: int
    consume_effect: Effect


@dataclass(frozen=True)
class SemanticGameContract:
    schema: str
    actions: tuple[str, ...]
    full_resource_symbol: str
    hypotheses: tuple[ProgramHypothesis, ...]
    evidence_sha256: tuple[str, ...]
    practice_actions: int
    contract_sha256: str

    def payload(self, *, digest: bool = True) -> dict[str, object]:
        value: dict[str, object] = {
            "schema": self.schema,
            "actions": self.actions,
            "full_resource_symbol": self.full_resource_symbol,
            "hypotheses": [asdict(hypothesis) for hypothesis in self.hypotheses],
            "evidence_sha256": self.evidence_sha256,
            "practice_actions": self.practice_actions,
        }
        if digest:
            value["contract_sha256"] = self.contract_sha256
        return value

    def verify(self) -> None:
        if self.schema != "errata.semantic-causal-game-contract.v0":
            raise ValueError("semantic contract schema differs")
        if not self.hypotheses:
            raise ValueError("semantic contract has no admitted hypothesis")
        if tuple(sorted(self.hypotheses, key=_hypothesis_key)) != self.hypotheses:
            raise ValueError("semantic contract hypotheses are not canonical")
        if self.contract_sha256 != _sha(self.payload(digest=False)):
            raise ValueError("semantic contract digest differs")


def build_contract(
    actions: tuple[str, ...],
    full_resource_symbol: str,
    hypotheses: tuple[ProgramHypothesis, ...],
    evidence_sha256: tuple[str, ...],
    practice_actions: int,
) -> SemanticGameContract:
    """Canonical constructor shared by learner, controls, and oracle adapter."""

    ordered = tuple(sorted(set(hypotheses), key=_hypothesis_key))
    base = SemanticGameContract(
        "errata.semantic-causal-game-contract.v0",
        actions,
        full_resource_symbol,
        ordered,
        tuple(sorted(evidence_sha256)),
        practice_actions,
        "",
    )
    result = SemanticGameContract(
        base.schema,
        base.actions,
        base.full_resource_symbol,
        base.hypotheses,
        base.evidence_sha256,
        base.practice_actions,
        _sha(base.payload(digest=False)),
    )
    result.verify()
    return result


@dataclass(frozen=True)
class DiscoveryReceipt:
    contract: SemanticGameContract | None
    disposition: Literal["act", "not-identifiable", "budget-exhausted"]
    reason: str
    practice_resets: int
    practice_actions: int


@dataclass(frozen=True)
class _Pending:
    target: int
    effect: Effect
    ticks: int


@dataclass(frozen=True)
class _State:
    bits: tuple[bool, bool, bool]
    consumable: bool
    pending: _Pending | None = None
    steps: int = 0
    terminal: bool = False
    outcome: Outcome | None = None


def _hypothesis_key(hypothesis: ProgramHypothesis) -> bytes:
    return _canonical(asdict(hypothesis))


def _apply(bits: tuple[bool, bool, bool], target: int, effect: Effect):
    result = list(bits)
    if effect == "toggle":
        result[target] = not result[target]
    elif effect == "set-0":
        result[target] = False
    else:
        result[target] = True
    return tuple(result)


def _advance(
    hypothesis: ProgramHypothesis,
    state: _State,
    semantic_action: str,
    goal: tuple[bool, bool, bool],
    horizon: int,
) -> _State:
    pending = state.pending
    bits = state.bits
    if pending is not None:
        if pending.ticks > 1:
            pending = _Pending(pending.target, pending.effect, pending.ticks - 1)
        else:
            bits = _apply(bits, pending.target, pending.effect)
            pending = None
    consumable = state.consumable
    if semantic_action == "drive":
        bits = _apply(bits, hypothesis.drive_source, "toggle")
        if bits[hypothesis.drive_guard] == hypothesis.drive_guard_value:
            bits = _apply(bits, hypothesis.drive_target, hypothesis.drive_effect)
    elif semantic_action == "pulse":
        if pending is None and bits[hypothesis.pulse_guard] == hypothesis.pulse_guard_value:
            pending = _Pending(
                hypothesis.pulse_target,
                hypothesis.pulse_effect,
                hypothesis.pulse_delay,
            )
    elif semantic_action == "consume":
        if (
            consumable
            and bits[hypothesis.consume_guard] == hypothesis.consume_guard_value
        ):
            consumable = False
            bits = _apply(bits, hypothesis.consume_target, hypothesis.consume_effect)
    elif semantic_action == "commit" and bits == goal and pending is None:
        return _State(bits, consumable, pending, state.steps + 1, True, "win")
    steps = state.steps + 1
    terminal = steps >= horizon
    return _State(
        bits,
        consumable,
        pending,
        steps,
        terminal,
        "timeout" if terminal else None,
    )


def _symbol_pairs(traces: tuple[PublicTrace, ...]) -> tuple[tuple[str, ...], ...]:
    values = [set() for _ in range(3)]
    for trace in traces:
        for index, value in enumerate(trace.initial_observation):
            values[index].add(value)
        for index, value in enumerate(trace.mandate):
            values[index].add(value)
        for step in trace.steps:
            for index, value in enumerate(step.observation):
                values[index].add(value)
    return tuple(tuple(sorted(row)) for row in values)


def _decode(
    symbols: tuple[str, str, str], false_symbols: tuple[str, str, str]
) -> tuple[bool, bool, bool]:
    return tuple(value != false_symbols[index] for index, value in enumerate(symbols))


def _roles(hypothesis: ProgramHypothesis) -> dict[str, str]:
    return dict(hypothesis.action_roles)


def _trace_matches(hypothesis: ProgramHypothesis, trace: PublicTrace) -> bool:
    role_map = _roles(hypothesis)
    horizon = trace.horizon
    state = _State(
        _decode(trace.initial_observation, hypothesis.false_symbols),
        True,
    )
    goal = _decode(trace.mandate, hypothesis.false_symbols)
    for action, public in zip(trace.actions, trace.steps):
        state = _advance(hypothesis, state, role_map[action], goal, horizon)
        if _decode(public.observation, hypothesis.false_symbols) != state.bits:
            return False
        expected_full = public.resource == trace.initial_resource
        if expected_full != state.consumable:
            return False
        if public.terminal != state.terminal or public.outcome != state.outcome:
            return False
    return True


def _role_maps(traces: tuple[PublicTrace, ...], actions: tuple[str, ...]):
    win_actions = {
        step.action
        for trace in traces
        for step in trace.steps
        if step.outcome == "win"
    }
    resource_actions: set[str] = set()
    for trace in traces:
        previous = trace.initial_resource
        for step in trace.steps:
            if step.resource != previous:
                resource_actions.add(step.action)
            previous = step.resource
    if len(win_actions) != 1 or len(resource_actions) != 1:
        return ()
    commit = next(iter(win_actions))
    consume = next(iter(resource_actions))
    remaining = tuple(action for action in actions if action not in {commit, consume})
    if len(remaining) != 3:
        return ()
    result = []
    for assignment in itertools.permutations(("drive", "pulse", "wait")):
        mapping = {commit: "commit", consume: "consume"}
        mapping.update(zip(remaining, assignment))
        result.append(tuple(sorted(mapping.items())))
    return tuple(result)


def _enumerate_hypotheses(
    traces: tuple[PublicTrace, ...], actions: tuple[str, ...]
) -> tuple[ProgramHypothesis, ...]:
    pairs = _symbol_pairs(traces)
    if any(len(pair) != 2 for pair in pairs):
        return ()
    effects: tuple[Effect, ...] = ("toggle", "set-0", "set-1")
    admitted: list[ProgramHypothesis] = []
    for false_symbols in itertools.product(*pairs):
        false_symbols = tuple(false_symbols)
        for action_roles in _role_maps(traces, actions):
            role_map = dict(action_roles)
            drive_action = next(action for action, role in role_map.items() if role == "drive")
            pulse_action = next(action for action, role in role_map.items() if role == "pulse")
            consume_action = next(action for action, role in role_map.items() if role == "consume")
            neutral = {role_map[action] for action in actions} - {"drive", "pulse", "consume"}

            def subset(allowed: set[str]) -> tuple[PublicTrace, ...]:
                return tuple(
                    trace
                    for trace in traces
                    if set(trace.actions) <= allowed
                )

            drive_traces = subset({drive_action, *[a for a in actions if role_map[a] in neutral]})
            pulse_traces = subset({pulse_action, *[a for a in actions if role_map[a] in neutral]})
            consume_traces = subset({consume_action, *[a for a in actions if role_map[a] in neutral]})

            base = dict(
                false_symbols=false_symbols,
                action_roles=action_roles,
                drive_source=0, drive_target=1, drive_guard=0,
                drive_guard_value=False, drive_effect="toggle",
                pulse_guard=0, pulse_guard_value=False, pulse_target=1,
                pulse_effect="toggle", pulse_delay=1,
                consume_guard=0, consume_guard_value=False, consume_target=1,
                consume_effect="toggle",
            )
            drive_candidates = []
            for source, target, guard, guard_value, effect in itertools.product(
                range(3), range(3), range(3), (False, True), effects
            ):
                if source == target:
                    continue
                hypothesis = ProgramHypothesis(
                    **(base | dict(
                        drive_source=source, drive_target=target, drive_guard=guard,
                        drive_guard_value=guard_value, drive_effect=effect,
                    ))
                )
                if all(_trace_matches(hypothesis, trace) for trace in drive_traces):
                    drive_candidates.append((source, target, guard, guard_value, effect))
            pulse_candidates = []
            for guard, guard_value, target, effect, delay in itertools.product(
                range(3), (False, True), range(3), effects, (1, 2)
            ):
                hypothesis = ProgramHypothesis(
                    **(base | dict(
                        pulse_guard=guard, pulse_guard_value=guard_value,
                        pulse_target=target, pulse_effect=effect, pulse_delay=delay,
                    ))
                )
                if all(_trace_matches(hypothesis, trace) for trace in pulse_traces):
                    pulse_candidates.append((guard, guard_value, target, effect, delay))
            consume_candidates = []
            for guard, guard_value, target, effect in itertools.product(
                range(3), (False, True), range(3), effects
            ):
                hypothesis = ProgramHypothesis(
                    **(base | dict(
                        consume_guard=guard, consume_guard_value=guard_value,
                        consume_target=target, consume_effect=effect,
                    ))
                )
                if all(_trace_matches(hypothesis, trace) for trace in consume_traces):
                    consume_candidates.append((guard, guard_value, target, effect))
            for drive, pulse, consume in itertools.product(
                drive_candidates, pulse_candidates, consume_candidates
            ):
                hypothesis = ProgramHypothesis(
                    false_symbols=false_symbols,
                    action_roles=action_roles,
                    drive_source=drive[0], drive_target=drive[1], drive_guard=drive[2],
                    drive_guard_value=drive[3], drive_effect=drive[4],
                    pulse_guard=pulse[0], pulse_guard_value=pulse[1],
                    pulse_target=pulse[2], pulse_effect=pulse[3], pulse_delay=pulse[4],
                    consume_guard=consume[0], consume_guard_value=consume[1],
                    consume_target=consume[2], consume_effect=consume[3],
                )
                if all(_trace_matches(hypothesis, trace) for trace in traces):
                    admitted.append(hypothesis)
    return tuple(sorted(set(admitted), key=_hypothesis_key))


class SemanticCausalProgramAgent:
    identity = "semantic-set-valued-causal-program-agent-v0"

    def __init__(self, *, practice_depth: int = 3, max_actions: int = 20_000):
        self.practice_depth = practice_depth
        self.max_actions = max_actions

    def discover(self, port: PracticePort) -> DiscoveryReceipt:
        traces: list[PublicTrace] = []
        actions_used = 0
        resets = 0
        vocabulary: tuple[str, ...] | None = None
        for episode_index in range(port.practice_count):
            first = port.reset_practice(episode_index)
            resets += 1
            if vocabulary is None:
                vocabulary = first.legal_actions
            elif first.legal_actions != vocabulary:
                return DiscoveryReceipt(None, "not-identifiable", "action presentation changed", resets, actions_used)
            for depth in range(1, min(self.practice_depth, first.steps_remaining) + 1):
                for actions in itertools.product(vocabulary, repeat=depth):
                    turn = port.reset_practice(episode_index)
                    resets += 1
                    steps = []
                    for action in actions:
                        if actions_used >= self.max_actions:
                            return DiscoveryReceipt(None, "budget-exhausted", "practice action budget exhausted", resets, actions_used)
                        turn = port.step(action)
                        actions_used += 1
                        steps.append(PublicStep(action, turn.observation, turn.resource, turn.terminal, turn.outcome, turn.receipt_sha256))
                        if turn.terminal:
                            break
                    traces.append(PublicTrace(
                        episode_index,
                        first.observation,
                        first.mandate,
                        first.resource,
                        first.steps_remaining,
                        tuple(step.action for step in steps),
                        tuple(steps),
                    ))
        assert vocabulary is not None
        hypotheses = _enumerate_hypotheses(tuple(traces), vocabulary)
        if not hypotheses:
            return DiscoveryReceipt(None, "not-identifiable", "no causal program fits public practice", resets, actions_used)
        evidence = tuple(sorted(_sha(asdict(trace)) for trace in traces))
        contract = build_contract(
            vocabulary,
            traces[0].initial_resource,
            hypotheses,
            evidence,
            actions_used,
        )
        contract.verify()
        return DiscoveryReceipt(contract, "act", "set-valued causal program compiled", resets, actions_used)


def robust_plan(
    contract: SemanticGameContract, turn: OpaqueTurn
) -> tuple[str, ...] | None:
    contract.verify()
    if turn.legal_actions != contract.actions:
        raise ValueError("scored action presentation differs from contract")
    joint = []
    for hypothesis in contract.hypotheses:
        joint.append(
            _State(
                _decode(turn.observation, hypothesis.false_symbols),
                turn.resource == contract.full_resource_symbol,
            )
        )
    goals = tuple(
        _decode(turn.mandate, hypothesis.false_symbols)
        for hypothesis in contract.hypotheses
    )
    initial = tuple(joint)
    queue = deque([(initial, tuple())])
    seen = {initial}
    while queue:
        states, path = queue.popleft()
        if len(path) >= turn.steps_remaining:
            continue
        for action in contract.actions:
            next_states = tuple(
                _advance(
                    hypothesis,
                    state,
                    dict(hypothesis.action_roles)[action],
                    goal,
                    turn.steps_remaining,
                )
                for hypothesis, state, goal in zip(contract.hypotheses, states, goals)
            )
            candidate = (*path, action)
            if all(state.outcome == "win" for state in next_states):
                return candidate
            if any(state.terminal for state in next_states):
                continue
            if next_states not in seen:
                seen.add(next_states)
                queue.append((next_states, candidate))
    return None


__all__ = [
    "DiscoveryReceipt",
    "ProgramHypothesis",
    "SemanticCausalProgramAgent",
    "SemanticGameContract",
    "build_contract",
    "robust_plan",
]
