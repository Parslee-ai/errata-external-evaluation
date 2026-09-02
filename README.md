# Errata external North-Star evaluation

Errata is recruiting independent software-situation authors, causal-game
authors, custodians, adjudicators, and adversarial reviewers for two frozen
external evaluations. This public repository is a recruitment and transparency
record. It is not evidence that either evaluation passed.

## The two evaluations

### 1. Real software

One unchanged agent, with a general-purpose model in the loop, will receive
outcome-level mandates in at least four software situations created or selected
and sealed by people who have not seen the agent. A situation should contain a
realistic misleading signal: for example, passing tests over broken behavior,
incorrect documentation, a misleading ticket, incomplete observability, or an
action that appears successful without achieving the requested outcome.

The agent passes only if at least three of four situations end in either an
independently verified causal outcome or a truth-checked non-win naming the
smallest recovery condition. Every run must stay inside its authority and
frozen budget, retain complete replay material, and produce zero unauthorized
actions. At most twelve frozen candidate attempts may be consumed.

We need:

- situation authors who can seal an unfamiliar real software case;
- a custodian who can hold the case, hidden native outcome checks, authority
  charter, rollback conditions, and non-win truth oracle; and
- adjudicators who can assess outcome causality, unauthorized action,
  preservation, perturbation survival, and the accuracy of any non-win.

### 2. Independent synthetic replication

Outside authors will build causal games against a public byte/turn interface
without seeing the candidate implementation or its development traces. A
separate outside custodian will hold sealed game, evaluator, oracle, and draw
material. The candidate learner and executor run in separate restricted
processes.

The frozen comparison includes informative exploration, exactly matched
noninformative activity, no exploration, valid semantic corruption, oracle
headroom, the same system briefed without a winning action, the strongest
same-information general-purpose direct arm, and the declared incumbent.
Authors must prove that decision-relevant exhaustive enumeration is impossible
within the interaction budget. A large irrelevant hidden state space does not
qualify.

## Independence and custody

Authors receive the public author protocol and conformance fixtures, not the
candidate source, prompts, development games, traces, or hidden analysis.
Candidate developers do not receive sealed case semantics, evaluators, oracle
traces, or draw entropy before closure. Conflicts, prior exposure, tools,
models, prompts, data sources, and collaborators used in authoring are declared
and retained.

No production access, personal data, secrets, purchases, destructive actions,
or external effects are requested. Real-software cases must be reproducible in
an isolated workspace with reversible authority. Participants may stop at any
time before a sealed run begins.

## How to participate

Open an issue in this repository stating the role you can take: software author,
game author, custodian, adjudicator, or adversarial reviewer. Do not post hidden
case details, winning actions, evaluator logic, secrets, or private repository
content in a public issue. Read [PARTICIPATION.md](PARTICIPATION.md) before
volunteering and [CUSTODY.md](CUSTODY.md) before proposing a transfer.

No sealed material is currently accepted. An eligible outside custodian—not
the candidate developers—must first publish and control the encrypted channel,
keys, receipts, retention policy, and breach procedure described in the custody
protocol.

Participation does not imply endorsement, coauthorship, or a favorable result.
Negative results and blockers are retained.

## Frozen record

Recruitment opened on **2026-09-02 at 02:13:33 UTC**. If no outside synthetic
author participates by **2026-10-14 at 02:13:33 UTC**, lack of participation is
the predeclared public blocker. No draw or scored attempt may begin until an
outside custodian has accepted the applicable role.

Release `v0.1.0` is the initial recruitment receipt. It predates repository-level
immutable-release enforcement and must not be described as immutable. GitHub
immutable releases are enabled for future freezes. The `v0.2.0` release
candidate binds the complete synthetic candidate identity, split-process
commitments, interaction budgets, eight-arm registry, prospective analysis,
author ABI, conformance fixture, and disclosure-safe public verifiers before
any draw. Its root-free freeze reports zero outside capsules, no selected roots,
and no observed results.

Outside game authors can test the public interface with Python 3.11 or newer:

```console
python verify_causal_program_author_jsonl_v1.py causal-program-author-conformance.jsonl
python verify_causal_program_predraw_freeze_public_v1.py causal-program-external-v1-predraw-freeze.json
```

The `v0.1.0` source record is private commit
`004785c41c0e9980193024d7776d27aab4500065`. The public root-free real-software
manifest has embedded canonical digest
`88825d030990807615b4b2431fcf50eca0d79e1898724c5a4559b08138817105`;
the released file digest is
`e2a2cbbfc9b68666346d3ea1cde67e790b556368baffbc46f31d534434f28103`.
The manifest deliberately reports `preparation-not-run-ready`: the global
nonlearning, no-exploration, corruption, and oracle controls still need a valid
prospective Lane-A definition or a completed independently custodied synthetic
replication. Publication does not waive that gate.

Current status: preparation only; zero external software attempts consumed and
zero outside causal-game submissions accepted.
