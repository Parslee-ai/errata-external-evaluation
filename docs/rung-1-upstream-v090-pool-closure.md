# Rung-1 upstream v0.9 pool closure

## Disposition

The prospectively frozen sixteen-repository scan produced two admissible cases,
not four. Under the frozen data-driven denominator, both cases and all sixteen
rows must execute. The primary 3-of-4 gate is unavailable regardless of the
row outcomes. No replacement, omission, or repair is permitted after this
closure.

## Retained cases

| Case | Base revision | Accepted merge | Native split |
| --- | --- | --- | --- |
| Werkzeug issue 3127 / PR 3129 | `795f4eaf6ef1fdc2fd1d7114c61ad384ede4322c` | `dafe7f1e37cf78cc7f11a9706c62a23e0dba9010` | base ordinary pass; base regression fail; accepted regression and ordinary pass twice |
| pip issue 13828 / PR 13829 | `db6fa4e1075d9d6503f8b136df6426282ee551b2` | `44ef9bcd3b5b99579367b3b5c1e5630ac6a625c0` | base ordinary pass; base regression fail; accepted regression and ordinary pass twice |

## Mismatch-first rejections

- Multidict 1306/1310: the accepted boundary is a C-extension segmentation
  fault, but the frozen candidate-copy evaluator cannot rebuild that extension.
- Isort 2462/2503: the accepted 15-test boundary is green but omits the issue's
  independent `__lazy_modules__` sorting requirement. This is a retained
  misleading partial-success signal.
- Tox 3731/3730: the issue body names the exact method and subset repair, so it
  violates the outcome-only candidate information firewall.
- Starlette: the frozen canonical repository redirects to a different owner;
  the post-freeze identity substitution was rejected.

## Content addresses

- Root-free freeze canonical SHA-256:
  `99f2d0865e6f364d60449b54894cad1ae5fa58b54aa9491f945dd56f8569d09e`
- Final pool canonical SHA-256:
  `a8ade0d4b168a9c79acbfe73b45e2b85deb687dd0687b6fe22d619565315a761`
- Native preflight canonical SHA-256:
  `3006d464053e5323f3d7a6aa92b0e9a2122ed0b95c2bf7206eb40a61ee1be7c4`
- Selection canonical SHA-256:
  `2cc3fdd3078c1356ab672feb418be7a669c3f686885ea68c6d0ab4126dfe934e`
- Requirements-only briefed-direct packet file SHA-256:
  `5b2b8e558cb0cfffd3d62a4abda39dd932e2530759ea48dcf6057a8a8c23ad7e`

At pool closure, no model row or new raw attempt exists. The exact missing
condition for primary admission is two additional fresh independently authored
repositories satisfying the already frozen rules. They cannot be added to this
exposed cohort.
