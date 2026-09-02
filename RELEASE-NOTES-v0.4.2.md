# Corrected no-live-recruitment Lane-A pre-draw freeze v0.4.2

This release supersedes `v0.4.1` before any canonical beacon receipt, case
ranking, reservation, or model attempt. A pre-draw audit found that the v0.4.1
evaluator resolved the configured Python launcher symlink. For a virtual
environment, that changes interpreter startup discovery and can make the
frozen test dependencies unavailable. The first NIST pulse intended for
v0.4.1 became visible during diagnosis, but it was never accepted into a
receipt or used to rank cases and is permanently ineligible.

Version `v0.4.2` preserves the absolute invoked launcher path without resolving
its symlink. A regression test commits that boundary. It also predeclares a new
future selection rule:

1. take this immutable release's GitHub `publishedAt` timestamp;
2. convert it to Unix milliseconds;
3. request the official NIST Randomness Beacon 2.0 endpoint
   `/pulse/time/next/<publishedAt-ms>`;
4. require the returned pulse timestamp to be strictly later;
5. interpret its 128-hex-character `outputValue` as 64 entropy bytes;
6. set `beacon_digest = SHA-256(entropy)`; and
7. rank cases by ascending
   `SHA-256(beacon_digest || 0x00 || case_sha256)` with no redraw.

- Source commit: `cbdaa04e1f2bab4a9985eb78953b0507e6413b3c`
- Candidate-freeze canonical digest: `75ebfa5e10902ef71cb296779cef0830a45cc1cf10a5b9a21a3a924665fd5481`
- Candidate-freeze file SHA-256: `04b8012adffd1e0dc233cc8750b87453b3e6339a12295554ca6001386c41eba9`
- Protocol SHA-256: `eb22b9e7daa59ead2aaa485188b670db39ef10decbc448bf6b878704306384c9`
- Runner SHA-256: `c5a08397ce2a4dae3ff08980536ebc68f83f3f5a2c4b394682d0dcb9a1b0057a`
- NIST fetch/verifier SHA-256: `2e01ca70579fef1f791d4a3c7ce016466d7604002d8bb5f5b459ccb363f553bd`
- Draw implementation SHA-256: `f7dda09295721a4039b21fb42bc8351cd67463f0387560d9c8666296ac574b26`

This remains preparation, not a draw, model attempt, outcome, or capability
result. At publication: zero canonical beacon receipts, zero draws, zero
reservations, and zero scored attempts under v0.4.2.
