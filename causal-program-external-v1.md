# Causal-program external replication v1 preparation

Status: **preparation only; no outside capsule, Lane-B pre-draw public freeze,
case root, model arm, external run, or readiness decision exists**.

This protocol and its public author conformance fixture were timestamped in the
external-evaluation
[`v0.1.0` release](https://github.com/Parslee-ai/errata-external-evaluation/releases/tag/v0.1.0).
Outside-author recruitment closes with a documented blocker if no author
participates by `2026-10-14T02:13:33Z`.

This package makes the existing
`semantic-set-valued-causal-program-agent-v0` transferable to an outside author
and custodian without exposing its source or development traces to the author.
It does not change that agent. It supplies an author-facing byte protocol,
dual-signed author/custodian intake, a root-free pre-draw freeze builder, a
split learner/executor host, a frozen arm registry and analysis plan, and a
clean normalized replay command for the internal base case.

The public `v0.1.0` recruitment release timestamps this protocol and fixture,
but it does **not** contain the complete Lane-B pre-draw freeze. In particular,
it does not bind the candidate bytes, embedded child bootstrap, controls,
thresholds, and analysis in one canonical artifact. No draw is admissible under
`v0.1.0`; a later public release of the freeze produced below is required.

## Root-free pre-draw freeze

`scripts/freeze_causal_program_external_v1.py` creates a canonical freeze that
binds all of the following before any case root is selected or candidate bytes
are transferred:

- the exact unchanged candidate, public ABI, split host, child bootstrap,
  public protocol, and conformance fixture bytes;
- the private source commit and the SHA-256 of the exact `RELEASE-NOTES.md`
  bytes at public tag `v0.1.0` (not an invented release-envelope digest);
- the eight-arm registry, unchanged 20,000-practice-action candidate ceiling,
  and host-enforced 20,000 total game-call ceiling;
- four retained same-case comparisons, exact win and paired-discordance
  thresholds, oracle 4/4 plus verified success across an unseen
  decision-relevant scored edge in every case, proof/confinement/replay/renderer
  gates, and the ban on post-draw replacement or repair; and
- prospective retirement/classification rules for the general-purpose direct,
  briefed, and discovery comparisons.

The output states `roots_selected=false`, `outside_capsules_accepted=0`,
`model_arms_executed=[]`, and `results_observed=false`. Its publication time is
supplied by an independently timestamped public release, not a self-asserted
field inside the JSON. After the preparation source is committed, the candidate
custodian creates it inside the frozen private source checkout with:

```bash
PYTHONPATH=src python3 scripts/freeze_causal_program_external_v1.py \
  --source-commit <40-hex-commit> \
  --recruitment-release-notes-sha256 <64-hex-v0.1.0-RELEASE-NOTES.md-digest> \
  --output <outside-public-repository>/causal-program-external-v1-predraw-freeze.json
```

Then publish those exact bytes together with the disclosure-safe module and the
standalone public verifier. Anyone can verify the canonical schema, controls,
thresholds, and root-free status without candidate access:

```bash
python3 verify_causal_program_predraw_freeze_public_v1.py \
  causal-program-external-v1-predraw-freeze.json
```

The custodian additionally runs the private source-closure verifier before the
draw. Public verification proves the published commitment and frozen rules;
custodian verification proves the held candidate bytes match that commitment.

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

The next public release must include that disclosure-safe module and
`scripts/verify_causal_program_author_jsonl_v1.py`, not only this prose and the
fixture. An author can then run:

```bash
python3 verify_causal_program_author_jsonl_v1.py \
  causal-program-author-conformance.jsonl
```

Neither public file contains the candidate implementation or a candidate
trace. The standalone tools require Python 3.11 or newer and only the standard
library plus an OpenSSH `ssh-keygen` executable for signature verification.

This narrow ABI is the unchanged candidate's compatibility boundary, not a
claim of general game discovery. An outside game that cannot honestly expose
this boundary is an incompatible case, not a reason to add a post-hoc adapter.

## Signed outside-capsule intake

An author package commits the sealed source, deterministic runtime image,
evaluator, oracle, concrete arm implementations, draw protocol, analysis plan,
OS confinement policy, shutdown/rollback policy, two renderer implementations,
non-enumeration certificate/proof/verifier, transparency-log entry, custodian
attestation, both public keys, and both signatures. The manifest also binds:

- the frozen candidate identity, its unchanged 20,000-practice-action ceiling,
  and the host-enforced 20,000 total game-call ceiling;
- the exact arm-registry digest;
- an author identity tied to the signing key;
- a named custodian, custody-root commitment, and custodian-attestation digest;
- the exact public Lane-B pre-draw freeze digest;
- five mandatory author non-exposure attestations; and
- status `sealed-pre-candidate-intake-only`.

The author and custodian sign the same canonical manifest, excluding only its
final digest and the two signature digests, with separate OpenSSH Ed25519
namespaces `errata-causal-program-external-v1` and
`errata-causal-program-external-v1-custodian`.
`verify_outside_capsule_intake` checks all bytes, both identity/key bindings and
signatures, the expected public-freeze digest, evaluator and oracle commitments,
the exact frozen analysis-plan bytes, and the non-enumeration binding.
It emits an intake-only receipt. Dual signatures establish that the holders of
the declared keys signed the same byte commitments; they do not authenticate
authorship history, independence, custodian honesty, semantic correctness,
transparency chronology, correct confinement, renderer independence, or the
mathematical proof. Those remain external review and execution obligations.

## Non-enumeration gate

Every capsule must include a canonical certificate tied to separate proof and
verifier bytes. It must state a lower bound on decision-relevant native states,
transitions, and interactions, exclude irrelevant state padding, and establish
that exhaustive enumeration requires more than the frozen 20,000
candidate-visible game calls. The host counts practice resets, practice
actions, scored start, and scored actions against that ceiling; the unchanged
learner separately retains its 20,000-practice-action cap. Equality with the
interaction budget fails intake construction.

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

The registry says which components still require external implementation. The
capsule must commit their exact bytes before candidate transfer, but intake
does not establish that those bytes correctly implement the declared arms.
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

The host fail-closes before the 20,001st game call. This closes a preparation
gap in which reset observations were not counted against the non-enumeration
interaction ceiling.

This is source and process separation, **not an operating-system sandbox**.
`-I`, `-S`, an empty environment, and a temporary working directory do not by
themselves block arbitrary filesystem paths, syscalls, process inspection, or
network access. A claim-bearing custodian must additionally provide independent
OS confinement and receipts for filesystem, network, process, resource,
shutdown, and cleanup controls. The present host must not be described as
satisfying the restricted-process admission rule on its own.

The host runs only the deterministic informative reference path. It selects no
root and executes no model arm.

## Verification boundary

The public author-conformance and pre-draw-freeze commands above are standalone
and require only the files released beside them. Internal base-case replay and
preparation tests remain developer regressions; they are not author tooling and
do not establish external readiness.

The next admissible sequence is: commit this preparation; generate and
independently publish the root-free Lane-B freeze; then accept a dual-signed,
outside-authored, custodian-held capsule bound to that exact freeze; and publicly
timestamp the disclosure-safe capsule commitments plus intake receipt. Only
after those events may the outside custodian draw case roots. Sealed source,
evaluator, oracle, and winning semantics remain private with the custodian.
More internal cases, conformance passes, or this document do not count as
external progress.
