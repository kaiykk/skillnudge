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
2. [CLOSED FOR WEEK 1 WITH DEFERRED VALIDATION] CapabilityContract +
   InterventionPlan + QueryPlan runtime
3. [IN PROGRESS] Candidate Acquisition + Evidence Hydration
4. Judge + Final Advice
5. D001 / D002 / D003 regression runs

Checkpoint 2 is closed for Week 1 with one explicitly deferred validation:
live Integration-primary semantic evidence. The only live Integration attempt
failed at the provider transport boundary before Capability Framing returned;
this is not semantic evidence that Integration routing failed. The deterministic
runtime can represent Integration-primary routing.

For the rest of Week 1, `planning.capability.v1`,
`planning.intervention.v1`, and `planning.query.v0` are frozen. Do not
prompt-tune them unless a later end-to-end failure directly proves that they
block the product loop. Frozen schemas are not rewritten for this status
change.

## Checkpoint 2 Scope

Checkpoint 2 implements only three independently validated planning stages:

```text
InputEnvelope -> Capability Framing -> Intervention Planning -> Query Planning
```

Capability Framing may stop for clarification. Intervention Planning may stop
with `no_intervention` or `clarify`; those early stops skip model-driven Query
Planning and produce the corresponding validated status. Search planning emits
bounded, complementary semantic queries and is checked for cross-stage
consistency before the run completes.

The provider boundary is one minimal OpenAI-compatible structured-output
adapter. A malformed response receives one repair attempt; a second invalid
response fails explicitly. The live model name must be supplied through
`SKILLNUDGE_MODEL`; no durable model default is committed.

Acceptance cases are D001 (Skill primary with Resource companion), D002
(`search`, with Skill or Integration accepted as primary according to the
observed blocker), and D003 (empty `missing_capabilities`,
`no_intervention`, no Query Planning model call). Clarification-edge behavior
is also covered. The live Integration-primary validation remains deferred.

## Checkpoint 3 Scope

Checkpoint 3 connects the real planning output to the existing local retrieval
baseline and stops after Evidence Hydration:

```text
Raw Request
-> Capability Framing
-> Intervention Planning
-> Query Planning
-> Candidate Acquisition
-> Evidence Hydration
-> STOP
```

Checkpoint 3 reuses the frozen Checkpoint 1 SQLite FTS5, BM25, multi-query, and
RRF implementation. It retrieves Top-50 per Skill semantic query, preserves
the semantic query and the translated FTS query, fuses a Top-30 candidate pool,
and hydrates only the fused Top-10. It does not tune BM25, FTS field weights,
Top-K, RRF, `rrf_k`, the corpus, query prompts, or add embeddings/vector
infrastructure.

Week 1 fully supports `family=skill`. If planning selects an Integration family
without an acquisition surface, the runtime returns and traces
`unsupported_family_surface`; it never silently converts Integration into
Skill. Resource acquisition is non-blocking unless an accepted planning case
requires it.

The implementation data structure for Evidence Packs is local runtime output,
not a new frozen product contract. Missing repository, source, license, or
update metadata remains null/unknown; provenance is never inferred. Candidate
Acquisition and Evidence Hydration do not invoke Judge or Final Advice.

Early-stop invariants remain:

- D003 ends at `no_intervention -> QueryPlan skipped` and creates no `04` or
  `05` artifact.
- Clarification cases stop before Candidate Acquisition.
- No `06_judgements.json` or `07_final_advice.json` is created in Checkpoint 3.

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

Checkpoint 1 historical D001 runs create:

```text
runs/<run_id>/
  00_input.json
  01_capability_contract.json
  02_intervention_plan.json
  03_query_plan.json
  trace.jsonl
```

Checkpoint 3 runs extend that layout with `04_candidate_acquisition.json` and
`05_evidence_packs.json` only after successful Candidate Acquisition.
Neither checkpoint creates fake `06_judgements.json` or
`07_final_advice.json` artifacts.

The Checkpoint 1 acquisition artifact records corpus source/version, record
counts, D001 coverage, exact transformed FTS queries, raw per-query results,
RRF data, and fused Top-30. Checkpoint 3 adds the same retrieval evidence to
the real planning run and then writes the bounded Evidence Packs. Trace events
are explicit runtime observations, not hidden chain-of-thought.

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

Checkpoint 1 did not implement CapabilityPlanner, Intervention Router, LLM
QueryPlanner, live discovery, skills.sh or Plugin catalog adapters, web search,
Evidence Hydration, Candidate Judge, Final Advice, embeddings, vector DB,
dense/hybrid retrieval, reranker training, frontend/GUI, auto-install,
Review/Grow/Watch, personalization, multi-agent behavior, or background jobs.
Checkpoint 3 implements only the local Skill acquisition and minimal Evidence
Hydration path described above; Candidate Judge and Final Advice remain
excluded.

## Stop Conditions

Stop and report when the selected corpus lacks the D001 positive, download or
access fails, SQLite cannot build reasonably, FTS5 is unavailable, license or
redistribution terms are uncertain, or the checkpoint would require embedding
or vector infrastructure.
