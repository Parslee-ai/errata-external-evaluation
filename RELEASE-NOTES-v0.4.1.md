# Corrected no-live-recruitment Lane-A pre-draw freeze v0.4.1

This release supersedes `v0.4.0` before any beacon fetch, draw, reservation, or
model attempt. Version `v0.4.0` said a future public beacon would select the
cases but did not name the provider or canonical entropy bytes. It is retained
as an invalid pre-draw freeze and will never be used for selection.

Version `v0.4.1` predeclares the exact future rule:

1. take this immutable release's GitHub `publishedAt` timestamp;
2. convert it to Unix milliseconds;
3. request the official NIST Randomness Beacon 2.0 endpoint
   `/pulse/time/next/<publishedAt-ms>`;
4. require the returned pulse timestamp to be strictly later;
5. interpret its 128-hex-character `outputValue` as 64 entropy bytes;
6. set `beacon_digest = SHA-256(entropy)`; and
7. rank cases by ascending
   `SHA-256(beacon_digest || 0x00 || case_sha256)` with no redraw.

The canonical receipt retains the release URL, request URL, complete pulse,
signature, certificate identifier, raw-response digest, entropy digest, and
time boundary. The fetch and verifier are frozen in `rung1_nist_beacon.py`.

- Source commit: `e6c0627449214372a5a11373bc636c336ab3131f`
- Candidate-freeze canonical digest: `f4b6858eedfe96516e826fbc95cb0bd467cc7a9ecefe675f18b2a25c6d771a97`
- Candidate-freeze file SHA-256: `5f91a850d97f21108a3d146ee70085fb43482d4cb65548b5a459937f4cc24d68`
- Protocol SHA-256: `3f0678cebb2e219dd6201d26004f4a72c76f09d568366b525744d4d9bee3aa0a`
- NIST fetch/verifier SHA-256: `7a14413cedf973b76ba1d8aa1485e65694678690fa4edb443435fe0101f9d514`
- Draw implementation SHA-256: `070083ad9816e6d72b7edf965159c7db5e4f60b15cb87f4fd50bdd8a592efb28`

All unchanged pool, preflight, briefing, runner, and control assets from
`v0.4.0` remain bound by the corrected candidate freeze. This remains
preparation, not a draw, model attempt, outcome, or capability result. At
publication: zero beacon fetches, zero draws, zero reservations, and zero
scored attempts under either release.
