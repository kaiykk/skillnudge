# GitHub Search Failure

## Status

- `[HISTORICAL EVIDENCE]` A D001 retrieval probe did not reliably recall a known
  positive candidate through GitHub live code search.
- `[FROZEN]` GitHub live code search is not the primary universal Skill
  discovery backend for V0.
- `[WORKING HYPOTHESIS]` Source coverage and indexing must be solved before
  downstream retrieval quality can be judged fairly.

## Probe

The known positive was `ui-ux-pro-max`, used as a probe for D001. Several GitHub
`gh search code` queries were attempted, including broader formulations and
positive-aware or oracle-style queries. The candidate was not stably recalled
within a useful candidate window, and the experiment also encountered rate
limiting.

This record is about a source and indexing failure, not proof that:

- BM25 is inadequate;
- capability framing is inadequate;
- query expansion is inadequate;
- the known candidate is universally best.

## Design Consequence

The useful conclusion is:

> Source coverage and indexing are prerequisites for downstream retrieval.

Therefore the V0 direction is:

```text
Stable corpus + lightweight index
→ local retrieval
→ conditional live fallback
→ evidence hydration
```

GitHub remains useful for a known candidate:

```text
known candidate
→ source fetch
→ SKILL.md hydration
→ provenance
→ freshness
```

It should not be treated as a complete Skill universe index.

## What Is Not Yet Proven

This historical probe does not establish the best corpus, index weighting,
query count, or live-discovery threshold. Those remain open design questions.
