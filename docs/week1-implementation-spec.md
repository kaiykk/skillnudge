# Week 1 Implementation Specification

## Status

**IMPLEMENTATION BASELINE**

This document translates the frozen V0 contracts into a staged implementation.
It does not reopen the Runtime Map or add product behavior outside the frozen
boundaries.

## Objective

Build the first working version of SkillNudge as a lightweight Capability
Intervention Advisor on a normal developer laptop. Work proceeds through
observable checkpoints rather than implementing the whole runtime in one pass.

## Checkpoints

1. [CLOSED] Skill Corpus -> Local SQLite -> FTS5/BM25 -> D001 raw retrieval -> Trace
1.1 [CLOSED] D001 candidate identity diagnostic
2. [IN PROGRESS] CapabilityContract + InterventionPlan + QueryPlan runtime
3. Candidate Acquisition + Evidence Hydration
4. Judge + Final Advice
5. D001 / D002 / D003 regression runs

The current implementation task is Checkpoint 2. Candidate Acquisition remains
out of scope until this planning checkpoint is complete and reviewed.

## Checkpoint 1 Scope

### Corpus

- Use a practical public Skill corpus with real metadata and body content.
- Verify the known D001 identity before building the complete index:
  `nextlevelbuilder/ui-ux-pro-max-skill` / `ui-ux-pro-max`.
- If coverage is absent, report `CORPUS_COVERAGE_FAILURE` and do not silently
  switch corpus, add a hand-written positive, or call it retrieval failure.

### Storage and Retrieval

- Store normalized records in SQLite.
- Index `name`, `description`, and `body` with SQLite FTS5.
- Use a small BM25 retriever with raw SQLite BM25 scores preserved.
- Build the index reproducibly and idempotently, with safe rebuild behavior.
- Run the three frozen D001 Skill queries independently.
- Merge per-query results with deterministic Reciprocal Rank Fusion.
- Emit a fused Top-30 with query ranks, raw scores, contributions, and fused
  rank.

The minimum normalized record is:

```text
candidate_id
name
description
body
repo
source_url
license
updated_at
source
```

Missing source fields remain unknown; this checkpoint does not invent the
universal Candidate schema.

### Trace

Each D001 run must create:

```text
runs/<run_id>/
  00_input.json
  01_capability_contract.json
  02_intervention_plan.json
  03_query_plan.json
  04_candidate_acquisition.json
  trace.jsonl
```

Do not create fake `05_evidence_packs.json`, `06_judgements.json`, or
`07_final_advice.json` artifacts at this checkpoint.

The acquisition artifact records corpus source/version, record counts, D001
coverage, exact transformed FTS queries, raw per-query results, RRF data, and
fused Top-30. Trace events are explicit runtime observations, not hidden
chain-of-thought.

## Frozen D001 Fixture

The fixture contains these three Skill queries:

```text
ui ux prototyping guidance
translate vague visual intent into interface design
design system wireframe prototype interaction design
```

The known candidate name is not placed in any query. The Resource query from
the QueryPlan pressure test is omitted because Checkpoint 1 indexes Skills
only.

## Engineering Tests

The focused tests cover corpus parsing/import, SQLite build, FTS querying, BM25
result structure, deterministic RRF, duplicate handling, trace creation, and
D001 coverage. They are engineering smoke tests, not a product-quality
benchmark. Do not use synthetic metrics to claim recommendation quality.

## Explicit Non-Goals

Checkpoint 1 does not implement CapabilityPlanner, Intervention Router, LLM
QueryPlanner, live discovery, skills.sh or Plugin catalog adapters, web search,
Evidence Hydration, Candidate Judge, Final Advice, embeddings, vector DB,
dense/hybrid retrieval, reranker training, frontend/GUI, auto-install,
Review/Grow/Watch, personalization, multi-agent behavior, or background jobs.

## Stop Conditions

Stop and report when the selected corpus lacks the D001 positive, download or
access fails, SQLite cannot build reasonably, FTS5 is unavailable, license or
redistribution terms are uncertain, or the checkpoint would require embedding
or vector infrastructure.
