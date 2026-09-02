# v1.0.2 — pre-inspection durable-custody receipt

This immutable release records the required custody preflight before any
dataset checkout or task inspection. It is infrastructure evidence, not a
capability result.

Two explicit persistent roots outside every future candidate workspace were
absent before initialization. Initializer process 4994 created them, wrote and
fsynced role-bound canaries, read the canaries back byte-for-byte, removed only
the canaries, fsynced the directories, and wrote canonical manifests. Separate
verifier process 5050 reopened both roots and verified their identities,
manifest chains, devices, freeze binding, and canary absence.

- governing freeze file SHA-256:
  `40b9f47b333b259e4e66789e2897faa44c5be781ab440430982a5e6caffd25ca`
- preflight implementation SHA-256:
  `4ec4f542cf879358ff8da2eea17637c71c632971d2527df7286f516c17f2d4c2`
- canonical receipt internal SHA-256:
  `76a48e2aecc365e133825034d6477c6cfc66d3f3a071dde8d9d5faab31055efd`
- receipt file SHA-256:
  `2f7bb518d20d1a50690a3e3fc35ce85092d1427f68ae5a37eaa1e44cccd0e003`
- verified at: `2026-09-02T22:20:18.791746Z`

Both roots currently reside on device `16777230`; the frozen requirement is
distinct non-nested persistent roots, not distinct physical devices. Their
absolute paths are withheld from the public receipt and represented by
path SHA-256 values. Loss, conflict, or tampering remains a fail-closed stop.
