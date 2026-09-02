# v1.0.3 — redacted deterministic task ranking

This immutable release publishes the full first-64 ranking derived from the
frozen 1,077-row dataset and NIST pulse 1924372. It precedes gold evaluation
and model cognition and consumes no raw attempt.

Thirty-seven rows pass the static recency, completeness, prior-use, and Linux
checks. The first statically eligible rows are ranks 6, 9, 10, and 13:

- `casey__just-3200`
- `langchain4j__langchain4j-5792`
- `alibaba__nacos-14917`
- `twpayne__chezmoi-5016`

They are not yet selected: the frozen scan must retain every gold-three-times,
empty-patch, and host preflight disposition in rank order and enforce distinct
repositories. A failing row is retained as a rejection, never replaced by
discretion.

The receipt exposes identifiers, repository/date metadata, image names,
content digests, and test counts only. It does not expose task statements,
accepted patches, hidden tests, hints, or commands.

- ranking implementation SHA-256:
  `28418a45e473d888dc1abb0f0bc81f67ea8eb8b0a5595bd6894e2ef3be326803`
- canonical ranking internal SHA-256:
  `91223766b884f5cd4317633d085e6da682bd23149054c2d0b0960986a4a71cf6`
- ranking receipt file SHA-256:
  `bad8fc4df597261636efc6d4274f998394d9d57a940c9979b7d78925b6545485`
