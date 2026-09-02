# Causal-program external replication v1 preparation

Status: **preparation only; no outside capsule, public freeze, case root, model
arm, external run, or readiness decision exists**.

This package makes the existing
`semantic-set-valued-causal-program-agent-v0` transferable to an outside author
and custodian without exposing its source or development traces to the author.
It does not change that agent. It supplies an author-facing byte protocol,
signed intake, a split learner/executor host, a frozen arm registry, and a clean
normalized replay command for the internal base case.

## Author-facing boundary

The public ABI is canonical JSON Lines with alternating request and response
records. Its schema is
`errata.causal-program-external.author-jsonl.v1`. The allowed operations are:

| Operation | Request argument | Response |
|---|---|---|
| `metadata` | none | positive `practice_count` |
| `reset_practice` | nonnegative episode index | one public turn |
| `practice_step` | one opaque action token | one public turn |
| `start_scored` | none | one public turn |
| `scored_step` | one opaque action token | one public turn |

A public turn contains only three opaque observation symbols, three opaque
mandate symbols, one opaque resource symbol, five opaque action tokens,
terminal/outcome state, remaining steps, and a receipt digest. The ABI carries
no semantic action roles, mechanism, generator root, evaluator state, oracle
plan, reward, arm label, candidate hypothesis, or winning action.

The canonical non-scoring fixture is
`tests/fixtures/causal_program_external_v1_author_conformance.jsonl`. It tests
transport shape only and contains no candidate source or candidate trace.
`verify_author_jsonl` in
`src/errata/north_star/causal_program_external_v1.py` verifies exact canonical
bytes, sequence, request/response pairing, and turn shape.

This narrow ABI is the unchanged candidate's compatibility boundary, not a
claim of general game discovery. An outside game that cannot honestly expose
this boundary is an incompatible case, not a reason to add a post-hoc adapter.

## Signed outside-capsule intake

An author package commits the sealed source, deterministic runtime image,
evaluator, oracle, non-enumeration certificate/proof/verifier, transparency-log
entry, custodian attestation, author public key, and author signature. The
manifest also binds:

- the frozen candidate identity and 20,000-action ceiling;
- the exact arm-registry digest;
- an author identity tied to the signing key;
- a named custodian, custody-root commitment, and custodian-attestation digest;
- five mandatory author non-exposure attestations; and
- status `sealed-pre-candidate-intake-only`.

The author signs the canonical manifest, excluding only its final digest and
signature digest, with OpenSSH Ed25519 namespace
`errata-causal-program-external-v1`. `verify_outside_capsule_intake` checks all
bytes, the author identity/key binding, signature, custodian identity
commitment, evaluator and oracle commitments, and the non-enumeration binding.
It emits an intake-only receipt. It cannot authenticate authorship history,
custodian honesty, semantic correctness, transparency chronology, or the
mathematical proof merely from those bytes; those require independent review.

## Non-enumeration gate

Every capsule must include a canonical certificate tied to separate proof and
verifier bytes. It must state a lower bound on decision-relevant native states,
transitions, and interactions, exclude irrelevant state padding, and establish
that exhaustive enumeration requires more than the frozen 20,000 candidate
actions. Equality with the budget fails intake construction.

This is intentionally stronger than adding decorative hidden state. Before a
capsule can enter a public experiment freeze, the custodian must execute the
committed verifier in its independently confined environment and an outside
reviewer must confirm that the proof concerns decision-relevant behavior. The
current validator establishes the certificate's canonical binding, not its
truth.

## Frozen arm registry

The registry fixes eight required arms before any outside draw:

1. informative exploration;
2. exactly chronology/event/motor/reset/byte/budget-matched noninformative
   activity;
3. zero exploration;
4. parser-valid, provenance-preserving semantic corruption;
5. oracle headroom through the common artifact interface;
6. strongest same-information general-purpose direct;
7. the unchanged agent truthfully briefed without a winning action; and
8. the author-declared incumbent.

The registry says which components still require external implementation.
Registration is not execution. In particular, this package contains no model
response and does not pretend to implement or run the general-purpose direct,
briefed, or incumbent arms.

## Split learner and executor host

`causal_program_external_v1_host.py` copies the unchanged candidate source
byte-for-byte into two fresh temporary workspaces. Each child starts under a
fresh Python interpreter with `-I -S`, an empty environment, canonical JSONL
RPC, and a hard read deadline. The learner receives only practice calls, closes
its artifact, and exits. Only after that exit does the host create the scored
turn and start a distinct executor process. The receipt binds the candidate,
bootstrap and host sources, ordered hash-chained calls, distinct process IDs,
phase ordering, terminal result, and a deterministic semantic replay digest.

This is source and process separation, **not an operating-system sandbox**.
`-I`, `-S`, an empty environment, and a temporary working directory do not by
themselves block arbitrary filesystem paths, syscalls, process inspection, or
network access. A claim-bearing custodian must additionally provide independent
OS confinement and receipts for filesystem, network, process, resource,
shutdown, and cleanup controls. The present host must not be described as
satisfying the restricted-process admission rule on its own.

The host runs only the deterministic informative reference path. It selects no
root and executes no model arm.

## Reproduction

Run the inherited internal base-case normalized replay with one command:

```bash
PYTHONPATH=src python3 scripts/verify_causal_program_external_v1.py
```

The output must say `internal-base-replay-only`,
`normalized_exact_replay=true`, `roots_selected_by_external_v1=false`,
`model_arms_executed_by_external_v1=[]`, and
`external_readiness_admitted=false`.

Run the focused preparation tests with:

```bash
PYTHONPATH=src python3 -m pytest -q \
  tests/test_causal_program_external_v1.py \
  tests/test_causal_program_external_v1_host.py
```

The next admissible event is an outside-authored, custodian-held capsule and
independently posted freeze receipt. More internal cases, conformance passes,
or this document do not count as external progress.
