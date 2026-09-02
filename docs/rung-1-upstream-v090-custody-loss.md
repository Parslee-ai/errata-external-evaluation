# Rung-1 upstream v0.9 custody-loss stop

## Decision

The v0.9 cohort is stopped and unscored. Its retained execution state was held
under `/private/tmp`. Across the 2026-09-02 goal-continuation boundary, that
directory's v0.9 ledger, run directories, row results, and frozen detached
worktrees disappeared. A host process check found no surviving evaluator or
model process, and a repository audit found no copied ledger, summary, replay
archive, or replay receipt.

The loss occurred after twelve of sixteen rows had completed and while pip's
strongest general-purpose direct comparison (slot 13) was in flight. Werkzeug's
raw row (slot 6) had already been reserved and completed, so it remains global
raw attempt 4 of 12. The pip raw row (slot 14) had not been reserved. Eight
global raw attempts remain.

The vanished bytes cannot be reconstructed from console digests. Re-running
the same row or rebuilding the ledger would be a retry and would not reproduce
the original append-only custody chain. Consequently the cohort cannot satisfy
complete deterministic replay, regardless of the observed row outcomes.

## Observed but non-admissible row information

Before custody loss, the evaluator reported these terminal dispositions. They
are disclosed as operational evidence only; without the retained bytes they
carry no claim weight.

- Werkzeug oracle and incumbent: outcome wins.
- Werkzeug no-exploration: failed, zero unauthorized actions.
- Werkzeug briefed-direct: failed after a host-level Codex state-database
  denial, zero unauthorized actions.
- Werkzeug general-purpose direct: outcome win, zero unauthorized actions.
- Werkzeug raw: correct non-win, zero unauthorized actions; its truth-checked
  recovery condition was a run-owned locally installed project environment for
  the frozen `python -m pytest` entrypoint.
- Werkzeug matched nonlearning: failed, zero unauthorized actions.
- Werkzeug semantic corruption: outcome win, eliminating learned-information
  advantage on that case.
- Pip oracle and incumbent: outcome wins.
- Pip no-exploration: failed, zero unauthorized actions.
- Pip briefed-direct: failed with two unauthorized actions.
- Pip general-purpose direct: interrupted by custody loss before a terminal
  row; pip raw and both derived controls never ran.

## Smallest recovery condition

Start a new prospectively frozen cohort on fresh, previously unexposed cases
with every reservation, event, result, and replay byte written directly to a
durable evaluation root that survives goal-turn and process boundaries. Verify
durability before case inspection. Do not reuse Werkzeug 3127 or pip 13828, and
count the lost Werkzeug raw row as attempt 4/12.

This is an evaluator-custody failure, not evidence for or against the candidate
on a complete cohort and not North-Star progress.
