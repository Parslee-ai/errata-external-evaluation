# Rung-1 external-artifact cohort

Status: **prospective route; pool capture and native preflight are preparation,
not a result**.

This cohort removes the dependency on recruiting a live third party without
removing external authorship. Each situation is an issue and merged fix created
in a public upstream repository by people with no Errata role. Both the report
and fix postdate the frozen model's documented 2026-02-16 knowledge cutoff. Errata
may operate the harness, but it cannot author the defect, choose the winning
patch after seeing a run, expose the later pull request to the agent, or award
credit from an agent-written test.

This is a successor to the failed rung-1 prequalification, not a reinterpretation
of it. The failed four cases remain failed and are never reused. The specialized
pursuit architecture remains retired. The candidate is the strongest frozen
general-purpose direct agent inside the thin deterministic authority, custody,
and replay substrate that survived that falsification.

## Externality and information firewall

The public pool contains eight issue/fix pairs. The agent receives only the
exact issue snapshot, repository identity, and pre-fix base commit. It runs on
a fresh base-commit worktree with network disabled. It cannot read the later
pull request, merge commit, upstream diff, regression additions, pool ranking,
other cases, evaluator scripts, or gold results.

The evaluator process separately retains the upstream merge commit and diff,
the paths of upstream-added regression tests, and the GitHub authorship and
merge record. Git object identity plus the public host supply independently
checkable provenance; no contemporaneous volunteer declaration is needed.
The upstream issue author need not equal the fix author. The situation is
external when both the defect report and accepted fix history pre-exist Errata's
selection and at least the accepted fix author is outside Errata.

## Pool, preflight, and draw

`scripts/rung1_upstream_artifact_pool.py capture` records canonical issue bytes,
base and merge SHAs, human fix authorship, changed paths, and the complete
upstream-diff digest. Capture rejects pre-cutoff reports or fixes, bots, Errata
principals, pulls without both implementation and regression-test changes,
truncated file lists, and a pool with fewer than four distinct external authors.

Before the public freeze, evaluator-only native preflight must establish for
every retained case:

1. the project installs and its pre-existing focused tests pass at the base SHA;
2. applying only the upstream-added or changed regression material makes at
   least one requirement-level check fail at base;
3. the same check passes at the upstream merge SHA;
4. a clean rebuild or restart reproduces the distinction; and
5. the check exercises observable behavior, not source text or patch identity.

Cases that fail preflight remain in a rejection ledger and cannot enter the
draw. Preflight does not consume an agent attempt. A public freeze binds the
candidate, protocol, complete qualified pool, rejected candidates, evaluator
commands and digests, budgets, and scoring before a beacon round is known.
Exactly four cases are then selected without replacement by ascending
`SHA-256(beacon_digest || 0x00 || case_sha256)`, using the first predeclared
public beacon strictly after the freeze. The initial immutable `v0.4.0`
publication left the beacon provider and canonical pulse bytes unspecified and
is therefore ineligible for a draw. Its successor predeclares the NIST
Randomness Beacon 2.0: request
`/pulse/time/next/<v0.4.2-publishedAt-unix-milliseconds>`, require the returned
pulse timestamp to be strictly later, interpret the 128-hex-character
`outputValue` as 64 entropy bytes, and set `beacon_digest` to the SHA-256 of
those bytes. The canonical receipt retains the pulse, signature, certificate
identifier, request URL, raw-response digest, and immutable-release URL. There
is no redraw.

Errata selected the repositories and eight-case sampling frame before the
beacon. The draw prevents discretionary choice among those eight, but it does
not make the cohort independently designed or representative of software work
in general. This is a four-case externally authored challenge cohort, not a
population estimate. Public adversarial review of the frozen frame and
information firewall remains required before any capability claim.

## Outcome admission

A credited win must satisfy all of the following on a clean evaluator copy:

- upstream regression behavior passes without importing the gold implementation;
- the ordinary focused suite still passes;
- a predeclared behavior perturbation or clean restart passes;
- the delta is causally necessary relative to the unchanged base;
- only intended reconciled changes remain;
- no unauthorized action occurred; and
- custody and replay validate byte-for-byte.

The upstream gold patch is the oracle and the accepted upstream workflow is the
incumbent. Neither automatically grants candidate credit. If the upstream gold
does not pass its own frozen checks, the case is invalid rather than a candidate
loss. Passing ordinary tests, an agent-authored regression, textual similarity
to the gold patch, or a confident terminal report is never sufficient.

A non-win earns credit only when evaluator-held base/gold evidence confirms the
failed condition and the stated smallest recovery condition. The evaluator
must reject broader, merely convenient, or already-disproved blockers.

## Agent and comparisons

One `gpt-5.6-sol` direct agent, prompt, tool schema, authority policy, and budget
is content-addressed before the draw and unchanged across all four raw rows.
Each raw row receives only the original issue snapshot. Required comparisons
are retained on fresh clones:

- the same agent with a truthful requirements briefing but no winning action;
- a duplicate strongest-general-purpose direct row, expected prospectively to
  match because the raw candidate is itself that policy;
- no exploration;
- matched noninformative activity;
- semantic corruption of the retained learned observations;
- the upstream gold oracle; and
- the upstream accepted patching workflow as incumbent.

The no-exploration, matched-activity, and corruption transformations must be
frozen and validated before the draw; invalid matching or corruption invalidates
the contrast. The raw candidate passes only with at least three correct
dispositions in four cases, zero unauthorized actions, frozen-budget compliance,
and complete deterministic replay. All rows and failures remain in the record.
No more than twelve raw attempts may ever be consumed.

This route can establish externally authored software evidence because the
situations and their accepted truth material were created outside Errata. It
does not by itself satisfy the independent synthetic lane, and it does not turn
GitHub provenance, a freeze, or a harness into a result.

## Current blocker

Recruitment is not the Lane-A blocker. Generic fail-closed implementations now
exist for the no-exploration tool boundary, matched-activity projection, and
case-keyed shape-preserving semantic corruption. Unit tests establish their
mechanical invariants, not their semantic validity on a selected case. A
failure-inclusive 32-row runner now pre-reserves every row, uses fresh
workspaces, binds derived controls to the raw trace, runs the hidden regression
and baseline twice on clean evaluator copies, checks aggregate budgets and
unauthorized actions, verifies retained custody, and applies the noncompensatory
3/4 summary. Eight requirements-only briefings are frozen separately from the
winning patches. The runner has not yet executed a model row. Immutable
`v0.4.1` is invalidated before the draw because its evaluator resolved the
Python launcher symlink, discarding the virtual-environment context required by
the frozen checks. Its intended first NIST pulse became observable, but no
canonical receipt, case ranking, or model attempt was created. `v0.4.2`
preserves the invoked launcher path and requires a new future pulse after its
own immutable publication. No beacon may be requested and no raw attempt may
be consumed until that corrected closure and the analysis rule are in one
public content-addressed freeze.

The immutable `v0.4.2` release was published at
`2026-09-02T11:40:21Z`. Its first strictly later NIST pulse was chain 2 pulse
`1923737` at `2026-09-02T11:41:00Z`. The canonical ranking selected Pydantic
13631, then Click 3458, 3360, and 3449. Receipt digest
`f4912ee6e6d1f29c0816013b370f95e837c5921751e4185e71f095ee5ebde5cc`
and draw digest
`fd241b9910fc1f1883d042ac744645fde4f086385d746010407a224420d1bf27`
bind the selection. No replacement or redraw is permitted.

## Deterministic-complement successor

The v0.4.2 cohort stopped after its first raw row made the zero-unauthorized
gate impossible. Its remaining selected cases are not reused. The only eligible
successor cohort is the entire unexposed complement of the original pool:
Flask 6093, pytest 14828, Pydantic 13716, and Pydantic 13713. Canonical
selection digest
`a533e9b234219d5661e17ce2ea5aea4e57e7c414c07724b51be268243ce31dde`
binds that complement. There is no second random draw and no discretionary
subsampling after observing v0.4.2.

Before its freeze, the successor must pass a case-free environment preflight
that sends one fixed readiness request to the frozen cognition model and runs
one credential-free Python unittest through the same deny-default command
containment. The receipt must retain no secret and disclose that no case
information was supplied. This prevents provider state, launcher PATH, dynamic
library, or nested-sandbox failures from consuming a row. The candidate must
also treat allowed paths and line/file budgets as cumulative: it may not commit
a test-only delta and then edit source without first expanding the bounded
source-and-test scope.

## Fresh successor after v0.5.0

The immutable v0.5.0 complement cohort is permanently stopped, unscored, after
seven Flask rows. Its raw row failed the hidden outcome without an accepted
non-win, and the next corruption row stopped before reservation because the
frozen semantic substitution was inert on an underscore-only identifier. The
failure consumed global raw attempt 2; it is not rerun.

The smallest recovery makes semantic corruption total by deterministically
replacing an otherwise unchanged underscore-only token with a case-keyed ASCII
letter. A regression exercises that exact boundary. A fresh eight-case pool,
with no case exposed to either prior candidate run, is qualified from Click,
pytest, and Pydantic issues and accepted fixes created after the model cutoff.
Its canonical pool digest is
`e9c602da8f700dabf25bcfceac5d03034bc5e89ac2d9520798ad3676dd809618`;
the all-qualified preflight digest is
`4fb1f81a947eb1b37f8eedcb98cd6befa46e264745c8ed6439c2284d34fad586`.
The successor retains the unchanged candidate cognition and all gates, records
two prior global raw attempts and ten remaining, and requires a new immutable
freeze followed by a strictly later public beacon pulse. Preparation is not a
result.
