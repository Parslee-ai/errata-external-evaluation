# Lane-A first external attempt admission substrate

Status: **implementation substrate only; no external case is recruited, frozen,
run, adjudicated, or admitted by this document**.

The root-free source commitment and this protocol were publicly timestamped in
the external-evaluation
[`v0.1.0` release](https://github.com/Parslee-ai/errata-external-evaluation/releases/tag/v0.1.0).
That release opened recruitment; it did not make this substrate run-ready or
consume an attempt.

This protocol prepares one unchanged `errata pursue` candidate for the first
outside-authored real-software attempt. It does not relax the North-Star rule:
the attempt counts only after an author who has not seen the candidate supplies
a fresh situation and an independent custodian seals the initial case, native
outcome test, authority boundary, rollback condition, and non-win truth test.
It includes the raw, briefed, strongest general-purpose direct, incumbent,
matched-nonlearning, no-exploration, corrupted-information, and oracle
comparison boundaries required for external admission.

## Prospective freeze and budget

From a clean committed checkout, run:

```text
errata lane-a-freeze --output /custody/candidate-freeze.json
errata lane-a-ledger-create \
  --freeze /custody/candidate-freeze.json \
  --output /custody/attempts.jsonl \
  --case-capsule /custody/case-1-capsule.json \
  --case-capsule /custody/case-2-capsule.json \
  --case-capsule /custody/case-3-capsule.json \
  --case-capsule /custody/case-4-capsule.json
```

The freeze content-addresses the complete `src/errata/pursue` Python source
closure, CLI entry point, package metadata, prompt source, proposal and tool
schemas, exact Git commit, configured model identity, and the Python and Codex
executable bytes and reported versions. The configured provider model identity
is frozen. OpenAI's official
[GPT-5.6 Sol model page](https://developers.openai.com/api/docs/models/gpt-5.6-sol)
lists `gpt-5.6-sol` as the snapshot and `gpt-5.6` as the routing alias. The local
manifest still cannot hash remote weight bytes, and the Codex CLI does not
return a provider attestation in-run; that narrower custody boundary must remain
disclosed in every result.

The attempt-wide limits are prospective and identical for any matched direct
arm: 320 cumulative model steps, 10,800 cumulative active execution seconds,
50 changed files, 5,000 added lines, and 5,000 deleted lines. The 320-step
ceiling is just above the longest exposed successful development trace
(StateBench, 299 steps); 10,800 seconds is above that trace's approximately
8,254-second duration. The first two limits are mechanically accumulated by
the pursuit runtime across resumes. File and line limits are frozen outer
admission limits; existing per-action scope measurement supplies the evidence,
but this substrate does not yet claim pre-actuation enforcement of an aggregate
file/line ceiling. An independent adjudicator must fail an attempt that exceeds
either aggregate.

Before each model call and blocking tool action, the runtime compares the
declared call timeout with the remaining active-time budget and stops instead
of starting a call that cannot fit. It checks again immediately after every
model return and before executing the proposed action. A non-cooperative child
may still overrun its declared timeout by process-termination latency; that
bounded host-runtime latency is recorded and the attempt becomes
`budget_exhausted`, with no later action admitted.

One append-only ledger freezes four to twelve canonical outside-case capsule
digests and a fixed eight-row order. Each case appears once in each row:
`oracle`, `incumbent`, `no-exploration`, `briefed-pursuit`, `gp-direct`,
`raw-pursuit`, `matched-nonlearning`, and `corrupted-information`. The five
raw-independent rows are rotated prospectively across case ordinals, followed
by raw and then the two controls that mechanically depend on its retained
discovery trace. Every row uses a fresh clone and a custodian information
firewall. The incumbent and oracle rows are registry commitments to outside
executions and evidence, not simulated pursuit-agent runs. The first four cases
form the required primary matrix. Control rows are mandatory and retained but
do not consume the raw-candidate stopping counter. Raw reservations
receive a separate monotonically increasing attempt index capped at twelve.
Creating any arm run reserves and permanently consumes its next frozen run key
before the first model call. Failures,
timeouts, invalid model output, interrupted runs, and non-wins do not restore a
run key or raw-attempt index. A new Lane-A run requires the freeze, ledger, arm,
and a custodian-supplied case digest. Every resume must present the same freeze
and ledger and rejects source, runtime, model-identity, case, or budget drift.

No later row can be reserved until the immediately preceding row has a typed,
hash-chained completion receipt. Agent-run receipts bind the exact offline
custody report, independent semantic-adjudication evidence, terminal
disposition, unauthorized-action count, frozen budget state, and adjudicator
identity. External-control receipts bind their evidence, rollback receipt,
fresh-clone check, semantic-control validity, authority count, budget result,
and adjudicator identity. A reservation is therefore never treated as an
execution or result. The derived matched-nonlearning and corrupted-information
plans additionally bind the exact raw agent completion-event hash and embedded
agent-receipt hash; a plan referencing any other trace is rejected.

The `gp-direct` arm automatically uses the frozen general-purpose direct prompt
instead of the pursuit prompt while retaining the same model, tool, authority,
budget, and terminal protocol. The `briefed-pursuit` arm uses the unchanged
pursuit agent with a custodian-sealed truthful requirements briefing included in
that arm's mandate; the briefing may identify requirements but must not reveal
the winning action. The raw arm receives only the original outcome mandate.

## Opaque outside-case capsule and causal controls

Before any case material is released, the outside author, custodian, and
adjudicator must be three distinct people and sign independent commitments.
The author must also attest that they created the situation without seeing the
candidate. The canonical capsule contains only SHA-256, byte-count, and media-
type commitments to custodian-held bytes; it does not reveal the workspace,
mandates, solution, traps, or evaluators to this repository. Its digest is the
`CASE_SHA256` entered into the ledger.

Every capsule binds distinct bytes for the initial workspace; raw mandate;
briefed requirements; authority, shutdown, rollback, and escalation policies;
common preflight; native outcome and non-win truth verifiers; trap commitment;
exploration-event classifier; matched-activity transform and validator;
no-exploration policy; semantic-corruption transform and validator; oracle and
incumbent procedures; and the three principal declarations. Reusing the same
bytes for semantically distinct roles fails closed. This is a custody check,
not proof that the committed definitions are valid: the outside adjudicator
must execute and semantically validate each one before release.

The paired estimands are fixed prospectively:

- `raw-pursuit` versus `no-exploration` estimates the value of safe
  participation beyond acting from initial information. The frozen policy
  denies information-acquisition events while preserving terminal work,
  outcome checks, shutdown, rollback, and escalation.
- `raw-pursuit` versus `matched-nonlearning` estimates learning beyond matched
  noninformative activity. A precommitted deterministic transform maps every
  raw exploration event to an author-defined equivalence-class action matched
  on permission, action class, maximum duration, and output allowance. Semantic
  outputs are withheld; the executor sees only counts, costs, and statuses.
- `raw-pursuit` versus `corrupted-information` tests semantic necessity. A
  precommitted transform changes task-relevant relations in the retained raw
  packet while preserving order, record types, authority labels, and declared
  size tolerance. A separate frozen validator rejects identity corruption,
  preserved winning relations, unsafe instructions, and unparsable output.
- `raw-pursuit` versus `oracle` establishes headroom. The custodian executes the
  sealed outside-author solution on a fresh clone under the same authority and
  outer budget, and the native verifier must pass with no unauthorized action.
- `briefed-pursuit`, `gp-direct`, and `incumbent` retain the requirement-
  information, strongest-direct-policy, and current-practice contrasts.

A missing, unmatched, leaked, invalid, or post-hoc redefined control cannot be
counted as favorable evidence; it invalidates the affected case/contrast. The
ordinary pursuit engine supports only raw, briefed, and GP-direct arms. It
rejects all five externally executed control arms so their runner semantics
cannot silently degrade to the ordinary pursuit prompt.

### Standalone outside-custody capsule tool

Outside authors and custodians can build and check the capsule with
`scripts/lane_a_case_capsule_tool.py`. The file is independently distributable,
uses only the Python standard library, and does not import Errata. Copy that
single file into the custodian environment; do not copy hidden case material
into this repository.

First produce one opaque descriptor for each required role. This command reads
the local file but writes only its SHA-256 digest, byte count, schema, and the
media type supplied by the custodian:

```text
python3 lane_a_case_capsule_tool.py artifact \
  /outside-custody/oracle-procedure \
  --media-type application/octet-stream \
  > /outside-custody/oracle-procedure.commitment.json
```

Assemble a JSON build specification with exactly these top-level fields:
`candidate_freeze_sha256`, `case_id`, `principals`, `declarations`, and
`artifacts`. `principals` contains exactly `author_id`, `custodian_id`, and
`adjudicator_id`. `declarations` contains the four keys below, each literally
`true`. `artifacts` maps every role named earlier in this section to the
corresponding four-field opaque descriptor; paths and artifact contents are
not accepted in this map.

```json
{
  "artifacts": {
    "ROLE": {
      "bytes": 1,
      "media_type": "application/octet-stream",
      "schema": "errata.lane-a-opaque-artifact.v1",
      "sha256": "64 lowercase hexadecimal characters"
    }
  },
  "candidate_freeze_sha256": "64 lowercase hexadecimal characters",
  "case_id": "outside-defined identifier",
  "declarations": {
    "adjudicator_independent_of_candidate_team": true,
    "author_independent_of_candidate_team": true,
    "author_non_exposure": true,
    "custodian_independent_of_candidate_team": true
  },
  "principals": {
    "adjudicator_id": "outside-defined identity",
    "author_id": "outside-defined identity",
    "custodian_id": "outside-defined identity"
  }
}
```

`ROLE` is illustrative and must be replaced by all 22 exact roles. The build
specification itself must use canonical JSON: sorted keys, no insignificant
whitespace, ASCII escapes, and one trailing newline. Building is write-once:
an existing output is accepted only when its bytes are identical.
`candidate_freeze_sha256` is the candidate-freeze manifest's internal
`sha256` value, not a new digest of the newline-terminated manifest file.

```text
python3 lane_a_case_capsule_tool.py build \
  --spec /outside-custody/case-build-spec.json \
  --output /outside-custody/case-capsule.json

python3 lane_a_case_capsule_tool.py verify \
  --capsule /outside-custody/case-capsule.json \
  --candidate-freeze-sha256 CANDIDATE_FREEZE_SHA256
```

Both successful commands print only the capsule digest. Verification rejects
noncanonical bytes, a wrong candidate-freeze binding, a redigested control-
protocol change, missing or extra roles, malformed descriptors, repeated
artifact digests, non-distinct principals, and any false or incomplete
independence declaration. It verifies commitments and custody shape only; it
does not establish that hidden bytes satisfy their semantic roles.

```text
errata pursue \
  --workspace /sealed/case-copy \
  --mandate "the outside author's outcome mandate" \
  --allow-external-model-context \
  --lane-a-freeze /custody/candidate-freeze.json \
  --lane-a-ledger /custody/attempts.jsonl \
  --lane-a-case-sha256 CASE_SHA256 \
  --lane-a-arm raw-pursuit
```

## Offline custody verification

```text
errata lane-a-verify \
  --run-dir /sealed/run \
  --freeze /custody/candidate-freeze.json \
  --ledger /custody/attempts.jsonl
```

Lane-A events form a SHA-256 chain. Successful model returns have retained
request and response byte digests. The offline verifier checks the event chain,
state cursors and freeze bindings, attempt reservation, cumulative model-step
and active-time accounting, retained request/response bytes, contract parent
chain, contract evidence digests, latest contract, notebook, and snapshot.

The verifier deliberately does **not** call the model, regenerate probabilistic
answers, re-execute tools or external effects, prove that a retained tool result
was truthful, or decide whether the native outcome or smallest recovery
condition was correct. Those semantic and causal decisions remain with the
independent custodian and outcome adjudicator. A passing custody report is
preparation, not an agent win.

## First-attempt admission

Attempt 1 is admissible only if all of the following were sealed before release:

1. the publicly timestamped candidate freeze, four canonical outside-case
   capsules, and one empty arm-tagged ledger with the complete frozen case/arm
   order;
2. author non-exposure and independent-custody declarations;
3. the complete initial case bytes and fresh case digest;
4. ordinary access, explicit authority, shutdown, rollback, and escalation;
5. at least one realistic misleading signal or incomplete-observability trap;
6. an independently executable native outcome test and a separately checkable
   non-win recovery condition; and
7. the same frozen limits for raw, briefed, and general-purpose direct arms,
   plus a predeclared incumbent evidence/cost/authority boundary.

The custodian counts the reserved slot regardless of disposition, audits every
action for authority, runs the native outcome or non-win truth check, and runs
the offline custody verifier. Passing tests, a patch, a server start, or agent
confidence alone cannot earn credit.

The manifest deliberately remains `preparation-not-run-ready`. The four
previously missing causal controls now have prospective definitions and
content-addressed capsule roles, but no outside-authored capsule or executable
control adapter has been accepted or semantically validated. Readiness requires
four such capsules, custodian-verified adapters for every role, and completion
of the full eight-arm matrix. This substrate does not convert definitions or
hashes into external evidence.
