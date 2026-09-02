# Lane-A v0.4.2 stopped result and replay v0.4.4

The v0.4.2 cohort is stopped after raw attempt 1 of 12. The raw candidate patch
passed the withheld upstream regression and preserved the baseline on both
fresh evaluator copies, but the row recorded one scope violation and returned
neither an admitted win nor an accepted correct non-win. Zero unauthorized
actions is noncompensatory, so the remaining three raw cases cannot rescue this
cohort and were not spent.

Retained rows: oracle, incumbent, no-exploration, requirements-briefed direct,
same-information general-purpose direct, and raw direct for Pydantic 13631.
Slots 7 through 32 were never reserved. Raw attempt index 1 is consumed.

- raw result digest:
  `477a36db0b1c9b754ef05c7678a32aeea66fbf62cb005e927aa3150ec0dff89e`
- raw custody digest:
  `5501c9e8d2755ebdaf4bc14e8dcdc557980f0d9fb260ae51a7470cdba6473717`
- ledger file SHA-256:
  `e4cb7733d81a54f5e9ae0e9fd048a6ef0391ba84e5f0f802ad68cc0a8424b588`
- replay archive SHA-256:
  `039ffdba5daab4f319ca705c037154e804d800de9ccab24f2d59f5de4546e939`

The replay archive contains the frozen pool, preflight, freeze, beacon, draw,
append-only ledger, all six row results, each agent run's event/state/model
receipts, and the exact candidate patches. This is negative evidence, not a
capability result.
