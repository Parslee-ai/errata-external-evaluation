# Causal-program independent-replication blocker v0

## Decision

The unchanged `semantic-set-valued-causal-program-agent-v0` is ineligible for
the North-Star independent synthetic discovery claim. This is a structural
blocker, not a failed game result and not a request for a live third party.

The fixed admission rule forbids a discovery claim when success depends on
enumerating the reachable state space. The candidate source deterministically:

1. iterates every opaque action sequence in `itertools.product(vocabulary,
   repeat=depth)` for every practice episode and every depth through its frozen
   practice limit;
2. enumerates five Cartesian-product layers spanning symbol polarity, guarded
   drive mechanisms, delayed pulse mechanisms, consumable mechanisms, and their
   joint causal hypotheses; and
3. breadth-first searches joint hypothesis states during execution with a
   queue and visited-state set.

Changing game authorship, custody, rendering, or draw procedure cannot remove
that algorithmic dependency while keeping the agent unchanged. A large native
state space also does not cure the issue: the supported abstraction is the
candidate's explicitly enumerated bounded causal-program hypothesis and joint
state space.

## Independently checkable evidence

The canonical receipt is
[`evidence/causal-program-nonenumeration-blocker-v0.json`](evidence/causal-program-nonenumeration-blocker-v0.json).
It binds source commit `f015e117f92f2ffc50b3c2792ff5b8f5a0c134c6`, candidate
source SHA-256
`24d177a6a004b5cb2f61e4c84263fc19f1932258462bef6a5b59e2d416a64bf1`,
the exact AST findings, and receipt digest
`a8ac84fb8b0014fe3432bbf1f3650643e3a5cc7a5fb81ba931628ff28defe1b3`.
Its file SHA-256 is
`66ac164d28575fd18010e37e9883b7f9c0f902bd948feb1d886efc39d2c454f6`.

Run the independent check from the bound source checkout:

```bash
PYTHONPATH=src python3 scripts/audit_causal_program_nonenumeration_blocker.py \
  --verify docs/evidence/causal-program-nonenumeration-blocker-v0.json
```

The verifier reparses the candidate source, re-establishes each enumerative
structure, recomputes the candidate hash and canonical receipt, and fails
closed on source or structural drift. The public blocker package includes the
candidate source, standalone audit, receipt, and this adjudication so the check
does not depend on private custody.

## Smallest recovery condition

Replace the learner's complete practice-sequence and causal-hypothesis
enumeration, and the executor's breadth-first joint-state search, with a
non-enumerative learning and control process; then freeze a new candidate
identity before any new game material is selected.

That recovery is incompatible with the current requirement to replicate the
unchanged causal-program agent. Therefore the independent synthetic lane ends
in a correct, publicly checkable non-win under the current objective. No game
family, author model, or external participant should be recruited to answer
this blocker. The internal positive base case remains valid only as finite
procedural-symbolic engineering evidence, not a discovery capability claim.
