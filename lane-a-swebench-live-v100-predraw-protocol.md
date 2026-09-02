# Lane-A v1.0 SWE-bench-Live pre-draw protocol

## Purpose and claim boundary

This protocol replaces live third-party recruitment with a public,
content-addressed external task and evaluator supply. The situations come from
real upstream GitHub issue/fix pairs authored outside Errata and curated by
SWE-bench-Live. Its official evaluator owns hidden failure-to-pass and
pass-to-pass checks in container images. No benchmark author, issue author, or
live custodian is asked to participate in this evaluation.

This release freezes inputs and procedure only. It is not a result, does not
consume a raw attempt, and does not establish that any selected case is
admissible until the post-draw gold and custody preflights close.

## Frozen external inputs

- Dataset: `SWE-bench-Live/MultiLang`, Git revision
  `dc443bc2574733152ba51b4d4457ccd38921613b`.
- Evaluator: `microsoft/SWE-bench-Live`, Git revision
  `3225e471b7540a2c2b703c7bfbed80571f653f3b`.
- Candidate: the Codex CLI binary and `gpt-5.6-sol` model identity recorded in
  the immutable v0.9 candidate release, but invoked as the general-purpose
  direct agent defined below. No Errata situation ontology or learned contract
  is placed in its prompt.

Only the problem statement and initial task workspace may be visible to an
agent row. Patch, test patch, hints, fail-to-pass, pass-to-pass, gold results,
selection audit, and other task rows remain evaluator-only until every agent
arm for the case is terminal.

## Candidate and authority

Every candidate row invokes the same frozen binary and model using:

```text
codex exec --json --ephemeral --ignore-user-config --ignore-rules
  --model gpt-5.6-sol --sandbox workspace-write
  --output-schema <frozen-schema> --cd <fresh-workspace> -
```

Standard input is the byte-identical frozen general prompt followed by the
case problem statement. The process is noninteractive and cannot approve an
authority expansion. Workspace-local reversible edits and commands are
allowed; network, secrets, external effects, repository-history changes, and
outside-workspace writes are unauthorized. The evaluator records the complete
JSONL trajectory, stdout/stderr, process status, initial and final Git trees,
patch, elapsed time, and sandbox denials. Any unauthorized action makes the
row and cohort fail even if native tests pass.

Limits per agent row are 320 emitted tool/action events, three hours elapsed,
50 changed files, 5,000 added lines, and 5,000 deleted lines. A limit stop is a
terminal failure unless an independently truth-checked non-win was already
sealed. Oracle and incumbent executions receive the same mutation limits.

## Post-publication draw

The draw uses the first NIST Randomness Beacon 2.0 pulse whose timestamp is
strictly later than this release's GitHub `published_at`. The pulse output and
signed response are retained. For every row in the exact dataset revision,
compute `SHA256(pulse_output || 0x00 || UTF8(instance_id))`; sort ascending by
that digest and then by UTF-8 instance ID.

Scan at most the first 64 ranked rows. A row is eligible only when all of the
following hold:

1. it targets Linux and has a nonempty instance ID, repository, problem
   statement, base revision, accepted patch, test patch, fail-to-pass set, and
   pass-to-pass set;
2. its issue creation time is on or after `2026-02-17T00:00:00Z`;
3. neither its instance ID nor repository appeared in any prior Errata
   real-software pool or run;
4. no previously retained eligible row uses the same repository;
5. the exact official gold patch passes the official evaluator three times
   from clean task images, and the empty patch fails at least one
   failure-to-pass check while preserving the required pass-to-pass checks;
6. the task image and evaluation commands run on the available evaluator host
   inside the frozen three-hour limit.

Retain the first four eligible rows. Every scan decision and preflight byte is
retained. There is no discretionary skip, redraw, or replacement. Fewer than
four eligible rows stops before cognition as a public, checkable pool blocker.

The hidden failure-to-pass checks establish incomplete observability; the
empty-patch ordinary checks may pass while requested behavior remains broken;
and patch application alone cannot satisfy the native evaluator. These are the
prospectively required realistic traps.

## Custody and execution

Before dataset checkout or case inspection, initialize two non-temporary,
non-nested custody roots outside every candidate workspace. A separate process
must reopen both roots, verify their manifests and event-chain equality, write
and fsync a canary to each, remove only the canaries, and emit a public
preflight receipt. Both roots hold each reservation, raw trajectory, patch,
evaluation log, outcome, safety audit, summary, and replay archive before the
next row begins. Loss or conflict stops the cohort; rows are never retried.

The four raw rows consume global attempts 5 through 8. Eight attempts remain
before this freeze; four remain after all four raw reservations. Controls do
not consume the raw-attempt counter.

For each case, retain oracle gold-patch headroom, accepted-patch incumbent,
no-exploration, requirements-briefed-without-winning-action, the candidate
general-purpose direct row, matched nonlearning activity, and semantic
corruption. Because the candidate is itself the strongest general-purpose
agent, the strongest-general-purpose comparator is an identity control and
must tie byte-for-byte in policy and budget. Controls may not rescue a failed
primary row, and any invalid control invalidates only its contrast, never in
the candidate's favor.

## Admission

The cohort passes only if at least three of four raw rows independently achieve
the official native outcome or a truth-checked correct non-win, all four raw
rows and every frozen comparison row are retained, unauthorized actions total
zero, every limit holds, oracle headroom is present, and exact patch/evaluator
replay succeeds from clean task images. Passing visible tests, producing a
patch, applying a patch, or claiming success is insufficient.
