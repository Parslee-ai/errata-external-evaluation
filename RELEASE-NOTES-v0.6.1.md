# Corrected Lane-A upstream successor freeze v0.6.1

This release supersedes and invalidates v0.6.0 before selection. The v0.6.0
beacon receipt template retained a stale v0.4.2 human-readable rule. The sole
attempted endpoint returned HTTP 404 before any pulse bytes were received; no
receipt, case ranking, reservation, model attempt, or result exists.

v0.6.1 changes only the beacon provenance rule and its release-specific
precommitment. The rule now identifies the immutable release through the frozen
`release_url`, and the draw verifier requires this exact v0.6.1 URL. Candidate
cognition, prompt, tools, authority, budgets, eight-case pool, qualification,
briefings, controls, admission thresholds, and the two-consumed-attempt count
are unchanged.

- source commit: `eaba864fd50789f4cc556c31705a67e0a00dac21`
- candidate-freeze canonical digest:
  `7ae52db5061ce3c60b0d41d67f7c0d7861ebc6d4196034351be87b76e785e7bc`
- candidate-freeze file SHA-256:
  `680acb60eebc5d90d652993135b021668b705fdb890186bf6eba6e44c2591b8f`
- unchanged pool canonical digest:
  `e9c602da8f700dabf25bcfceac5d03034bc5e89ac2d9520798ad3676dd809618`
- unchanged preflight canonical digest:
  `4fb1f81a947eb1b37f8eedcb98cd6befa46e264745c8ed6439c2284d34fad586`
- corrected protocol file SHA-256:
  `54bf1a52478f332ef51e58cbaf46f5c1057f984188d564782fe9dd9e8dc4e32e`

The first NIST Beacon 2.0 pulse strictly after this release's immutable
publication timestamp will select four cases without replacement. No redraw is
permitted. At publication, v0.6.1 has no pulse, draw, reservation, attempt, or
result.
