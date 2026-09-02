# v0.9.2 — Lane-A v0.9 custody-loss adjudication

This immutable release records a terminal evaluator-custody failure. It is not
a capability result, and it does not reconstruct missing evidence.

The v0.9 execution root under `/private/tmp` disappeared after twelve completed
rows and during slot 13, before a replay package was written. No ledger, row
result, run directory, summary, replay archive, or receipt survived. Therefore
all console-observed row dispositions are excluded and the cohort is stopped
unscored.

Werkzeug raw had completed and remains global frozen attempt 4 of 12. Pip raw
was not reserved. Eight attempts remain. Re-running or reconstructing any v0.9
row is forbidden. The smallest recovery condition is a newly frozen cohort of
fresh cases whose durable custody root is verified before case inspection.

Bound private source commit:
`07db4b7c11aaa40702f22f63d049b0f7cddcf1eb`.

Released adjudication digest:

- `rung-1-upstream-v090-custody-loss.md`:
  `3a260d134baa1690ecfebfb2a2c8d02f35da350fa704fe1430ebe0c3b2f0a802`

There are deliberately no ledger, result, summary, replay, or receipt assets in
this release because none survived custody loss.
