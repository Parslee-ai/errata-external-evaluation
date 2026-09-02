# Lane-A first external attempt admission substrate

Status: **implementation substrate only; no external case is recruited, frozen,
run, adjudicated, or admitted by this document**.

This protocol prepares one unchanged `errata pursue` candidate for the first
outside-authored real-software attempt. It does not relax the North-Star rule:
the attempt counts only after an author who has not seen the candidate supplies
a fresh situation and an independent custodian seals the initial case, native
outcome test, authority boundary, rollback condition, and non-win truth test.
It includes the raw, briefed, general-purpose direct, and incumbent comparison
boundaries required for external admission.

## Prospective freeze and budget

From a clean committed checkout, run:

```text
errata lane-a-freeze --output /custody/candidate-freeze.json
errata lane-a-ledger-create \
  --freeze /custody/candidate-freeze.json \
  --output /custody/attempts.jsonl \
  --case-sha256 CASE_1_SHA256 \
  --case-sha256 CASE_2_SHA256 \
  --case-sha256 CASE_3_SHA256 \
  --case-sha256 CASE_4_SHA256
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

One append-only ledger freezes four to twelve outside case digests and a fixed
four-row order. Each case appears once in each row: `raw-pursuit`, the same
agent truthfully briefed about requirements but not given the winning action,
the strongest same-substrate `gp-direct` agent, and the outside author/custodian's
predeclared `incumbent` workflow. The incumbent row is a registry commitment to
real current-practice evidence, not a simulated agent execution. The first four
cases form the required primary matrix. Briefed, direct, and incumbent rows are
mandatory and retained but do not consume the raw-candidate stopping counter. Raw reservations
receive a separate monotonically increasing attempt index capped at twelve.
Creating any arm run reserves and permanently consumes its next frozen run key
before the first model call. Failures,
timeouts, invalid model output, interrupted runs, and non-wins do not restore a
run key or raw-attempt index. A new Lane-A run requires the freeze, ledger, arm,
and a custodian-supplied case digest. Every resume must present the same freeze
and ledger and rejects source, runtime, model-identity, case, or budget drift.

The `gp-direct` arm automatically uses the frozen general-purpose direct prompt
instead of the pursuit prompt while retaining the same model, tool, authority,
budget, and terminal protocol. The `briefed-pursuit` arm uses the unchanged
pursuit agent with a custodian-sealed truthful requirements briefing included in
that arm's mandate; the briefing may identify requirements but must not reveal
the winning action. The raw arm receives only the original outcome mandate.

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

1. the publicly timestamped candidate freeze and one empty arm-tagged ledger
   with the complete frozen case/arm order;
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

The manifest deliberately remains `preparation-not-run-ready`. Matched
nonlearning, no-exploration, corrupted-information, and oracle controls still
need prospective valid Lane-A definitions or a bound completed independent
synthetic replication that supplies them. This substrate does not silently
convert their absence into external-admission readiness.
