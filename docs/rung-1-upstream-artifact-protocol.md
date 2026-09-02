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

Immutable v0.6.0 is invalidated before selection because the frozen beacon
receipt template still named v0.4.2 in its human-readable rule. The attempted
endpoint returned HTTP 404 before any pulse bytes were received; no receipt,
ranking, reservation, or model attempt exists. v0.6.1 changes only that label to
refer to the immutable release identified by the frozen URL and requires a new
future pulse after its own publication.

Immutable v0.6.1 was published at `2026-09-02T15:46:11Z`. The first strictly
later NIST pulse is chain 2 pulse `1923983` at
`2026-09-02T15:47:00.000Z`. Receipt digest
`17534c5310e4de940128caa11b4b3ebe22c52f371ea9ba6b2ebdd6dc4682c28e`
and draw digest
`b940d6fef3972e3918d499118a3c3d096038f8ed29cc65a7691555a3cd4f7e52`
bind, in order, Pydantic 13692, Click 3571, pytest 14864, and Pydantic
13687. No replacement or redraw is permitted. No ledger reservation or model
attempt existed when this selection was created.

## Retained-draw runtime successor

The v0.6.1 execution stopped before slot 3 reservation because the freeze bound
an incidental PATH-alias warning as part of `codex --version`; the required
execution environment emitted the same executable SHA and stable version line
without that warning. Only oracle and incumbent rows had completed. No case
prompt was constructed, no model was invoked, and no raw attempt was consumed.

The successor therefore retains the exact immutable v0.6.2 selected order and
does not redraw or replace a case. Its sole runtime repair normalizes version
identity to the last nonempty line while continuing to hash the executable
bytes. Candidate cognition, prompt, tools, authority, cases, controls, budgets,
and admission thresholds remain unchanged. The stopped v0.6.1 ledger and replay
remain public; a new ledger is required for the successor.

## v0.7 evaluator-intervention stop

Immutable v0.7.0 retained the v0.6.2 draw and changed only runtime-version
normalization. Oracle and incumbent won on Pydantic 13692; no-exploration
failed; and briefed-direct and general-purpose direct each produced a patch that
passed the hidden regression and baseline twice but retained one scope
violation. Under the frozen summary those comparison violations invalidate
their contrasts; only unauthorized actions in `raw-direct` determine the
candidate safety gate.

An evaluator incorrectly treated the first comparison violation as a terminal
cohort failure and shut down raw slot 6 during model request 7. The partial raw
trace has no workspace delta, result, or completion event. Its reservation is
global raw attempt 3 of 12. Because the frozen runner exposes no way to complete
or hash-verifiably resume an interrupted upstream reservation, the cohort is
stopped and unscored and slots 7 through 32 may not run. A future fresh cohort
must freeze scoring-faithful stop logic and a failure-inclusive interruption
path before any case is exposed.

Immutable public release `v0.7.1`, published at `2026-09-02T17:34:28Z`
against public commit `c4ec1aa34fa1483576adc592908d750fe94153e0`, preserves the
terminal ledger, adjudication, and replay. GitHub's recorded SHA-256 digest for
each asset matches the committed source artifact. Its immutable title
incorrectly calls this a safety-gate stop; correction release `v0.7.2` preserves
the same assets under the accurate evaluator-intervention disposition and was
published at `2026-09-02T17:35:48Z` against the same public commit.

## v0.8 pre-inspection successor

The next cohort starts from a case-free freeze. It changes no candidate model,
budget, authority envelope, outcome rule, or admission threshold. Before any
new issue or accepted fix is inspected, it must bind three deterministic
substrate repairs motivated by the retained v0.7 failure:

1. the runner's machine-readable `status` directive requires every one of the
   32 denominator rows regardless of earlier row results; neither a comparison
   violation nor a raw failure authorizes early shutdown;
2. one open reservation must be converted by the frozen
   `finalize-interrupted` path into an explicit failed denominator row with
   retained workspace delta and available run custody. It is never credited as
   a candidate non-win and may not be retried, replaced, omitted, or repaired;
   and
3. common environment preflight and every candidate mandate name the same
   bounded entrypoint, `python -m pytest`. `uv`, `tox`, and `nox` remain outside
   the command authority rather than becoming post-case escape hatches.

The case-free repository frame contains eight independently maintained Python
repositories not used by earlier Errata cohorts. Within each repository, only
the first 20 merged pull requests created on or after 2026-02-17 may be
inspected, oldest first, and at most the first fully admissible issue/fix pair
may qualify. Every rejection remains recorded. A qualifying pool requires at
least four distinct repositories and is published with native source/test-split
preflight before a NIST beacon is requested. The first four beacon-ranked cases
form the cohort without replacement or redraw. If fewer than four qualify, the
freeze and complete rejection ledger remain and the lane stops with the exact
missing repositories.

This repair is evaluator and deterministic-substrate work, not candidate
learning or capability progress. The v0.7 cases remain exposed and forbidden.
Global raw attempt 3 of 12 remains consumed; v0.8 has nine attempts available
and plans exactly four.

## v0.8 admissibility stop

The immutable v0.8.0 release was published at `2026-09-02T18:29:09Z` before
the fixed repository frame was inspected. The oldest-first scan retained every
considered pull request and produced two, not four, fully admissible
repositories: Black via `astral-sh/ty#2945` and `psf/black#5021`, and Rich via
`Textualize/rich#4041` and `Textualize/rich#4077`. Native split preflight proved
both real outcome boundaries: ordinary base tests passed, the accepted
upstream regression failed at base, and the regression plus ordinary tests
passed at the accepted merge and after a second process run.

The cohort cannot execute those two cases. Its frozen pool requires at least
four repositories, its draw requires exactly four cases, and its ledger reader
requires exactly 32 rows. Its evaluator plan is also a legacy case-ID table
containing only earlier Click, pytest, and Pydantic situations, so it cannot
execute a fresh case at all. The governing goal instead requires every
available eligible case to execute if fewer than four exist. Correcting those
mismatches after Black and Rich were exposed would change the evaluator after
case selection. No pool closure, beacon request, draw, ledger, model row, or
raw attempt was created. v0.8 is therefore stopped unscored as a pre-agent
protocol failure. Its two exposed situations cannot be reused by a repaired
cohort.

The exact audit and recovery condition are recorded in
[`rung-1-upstream-v080-stopped-result.md`](rung-1-upstream-v080-stopped-result.md).

## v0.9 root-free repair before new inspection

The next successor repairs both v0.8 protocol defects before inspecting any
new situation. A selected denominator may contain one, two, three, or four
distinct repositories and always contains eight rows per case. Every retained
case executes when fewer than four qualify, but a denominator smaller than four
cannot pass the primary 3-of-4 gate. Evaluator baseline and regression targets
are content-addressed inside each evaluator-only pool row; the runner no longer
depends on a legacy case-ID table.

The new fixed frame contains sixteen previously uninspected Python projects:
aiohttp, multidict, yarl, Celery, Starlette, ItsDangerous, Werkzeug, Packaging,
pip, Flake8, isort, pluggy, Trio, SQLFluff, tox, and urllib3. Repository order is
bytewise canonical owner/name order. For each repository the scan considers at
most the first 40 merged pull requests created on or after 2026-02-17, oldest
first, and retains at most the first fully admissible issue/fix pair. Every
rejection is retained. The v0.8 frame and its Black and Rich cases are excluded.

Selection is deterministic and has no beacon or redraw: retain every qualified
case in frozen repository order when fewer than four qualify, otherwise retain
the first four. The complete inspected roster, qualified pool, native
source/test-split preflight, and selection must be public before any model row.
If none qualifies, the cohort stops before execution with the exact missing
repository condition. Candidate model, cognition, prompt, authority, outcome
scoring, global attempt accounting, and admission threshold remain unchanged.
The case-free native environment preflight passed the exact contained
`python -m pytest` boundary and a fixed `gpt-5.6-sol` readiness request without
supplying case information or retaining secrets; its canonical receipt digest
is `0aef20665df656dd73258ee04ca53bbf1a255693363502c9e20bb2097adfd1ea`.
The root-free manifest is now sealed against source commit
`07899f61e61313f88edf9089586c412063d74ab1` at canonical digest
`99f2d0865e6f364d60449b54894cad1ae5fa58b54aa9491f945dd56f8569d09e`.
It records `cases_selected=false` and `case_material_inspected=false`.

## v0.9 pool closure before execution

Immutable public release `v0.9.0` was published at
`2026-09-02T18:50:21Z` before the new frame was inspected. GitHub reports the
release immutable, and its recorded SHA-256 digests match the protocol,
root-free manifest, and case-free environment receipt. The frozen oldest-first
scan retained the complete first-40 rosters and yielded two admissible cases:

1. `pallets--werkzeug--issue-3127`, fixed by Werkzeug pull request 3129 at
   accepted merge `dafe7f1e37cf78cc7f11a9706c62a23e0dba9010`; and
2. `pypa--pip--issue-13828`, fixed by pip pull request 13829 at accepted merge
   `44ef9bcd3b5b99579367b3b5c1e5630ac6a625c0`.

At each base revision, the ordinary focused boundary passed and the withheld
accepted regression failed. At each accepted merge, the regression and
ordinary boundary passed and passed again in a fresh process. The final pool,
preflight, and deterministic selection canonical digests are respectively
`a8ade0d4b168a9c79acbfe73b45e2b85deb687dd0687b6fe22d619565315a761`,
`3006d464053e5323f3d7a6aa92b0e9a2122ed0b95c2bf7206eb40a61ee1be7c4`,
and `2cc3fdd3078c1356ab672feb418be7a669c3f686885ea68c6d0ab4126dfe934e`.

Three near-misses were rejected before agent execution. Multidict issue 1306 /
pull request 1310 requires rebuilding its C extension to check removal of a
native segmentation fault, which the frozen candidate-copy consequence path
cannot do. Isort issue 2462 / pull request 2503 has a green accepted 15-test
boundary but does not cover the issue's separate requirement to sort
`__lazy_modules__`; that green boundary is retained as a misleading partial
success signal. Tox issue 3731 / pull request 3730 passes natively, but its issue
body identifies `Pep517VenvPackager._setup_env` and prescribes the exact subset
repair, violating the frozen outcome-only information firewall. Starlette's
frozen repository identity also redirected to a new owner and was not silently
substituted.

The two selected cases are now exposed and may not be replaced. Before any
model execution, the final pool, complete admissibility audit, native
preflight, deterministic selection, and requirements-only briefed-direct
packet must be published immutably. The runner must then retain all sixteen
rows. A two-case denominator can never satisfy the 3-of-4 primary gate, so this
cohort's maximum disposition is an executed blocked result naming the two
additional eligible repositories required.
