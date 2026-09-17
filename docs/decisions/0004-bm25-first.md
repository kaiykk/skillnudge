# Decision 0004: BM25-First Retrieval

## Status

`[FROZEN]`

## Decision

The V0 retrieval direction is:

```text
CapabilityContract
→ 3-5 complementary queries
→ SQLite FTS5 / BM25
→ per-query Top-K
→ rank fusion
→ bounded Candidate Pool
```

Embedding, vector databases, and GPU are optional future upgrades, not V0
installation requirements.

## Context

The first product risk is whether the Intervention Advisor loop is useful. A
lightweight, inspectable baseline keeps that question separate from a larger
dense-retrieval research program.

## Consequences

Vocabulary mismatch, source coverage, field weighting, and candidate diversity
remain explicit validation questions. BM25 Top-1 accuracy is not the product
objective.

## Revisit When

Revisit after a controlled product experiment shows a residual retrieval failure
that is not explained by capability framing, query planning, source coverage,
or evidence availability.
