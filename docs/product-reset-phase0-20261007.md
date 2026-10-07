# Product Reset Phase 0 — Repository Classification

**Date:** 2026-10-07  
**Status:** `CLASSIFICATION_COMPLETE_RUNTIME_MIGRATION_NOT_STARTED`

This document records the first repository pass after the Product Reset. It is
the product-side boundary record; Home Project receipts and governance packets
remain outside this repository.

## New North Star

SkillNudge is an **Agent Skill evolution control plane**. It owns canonical
Skill/Capability identity, immutable version lineage, lifecycle state,
operator-result provenance, and Human-controlled activation, rollback, and
retirement. It does not own authoring algorithms, optimization algorithms,
semantic utility judgement, a benchmark framework, or a retrieval research
stack.

## Phase 0 Result

The repository currently contains two layers:

1. a small set of primitives that can become the control plane; and
2. a large, working but legacy Advisor/Review/Validate/WATCH/evaluator tree.

No source file was deleted in this pass. Files marked
`REMOVE_FROM_ACTIVE_TREE` are classified for a recoverable migration after the
new control-plane contracts are implemented. This preserves the existing
Golden Path history without treating it as the new product boundary.

## Classification

### `KEEP`

- `src/skillnudge/__init__.py`, `src/skillnudge/__main__.py`: package entry
  points.
- `src/skillnudge/capability_artifact.py`: exact-content identity, version, and
  hash validation; this is the current CapabilityArtifact v0 primitive.
- `docs/contracts/capability-artifact-v0.md`: minimal artifact identity
  contract, retained without expansion.
- `docs/product-delivery-sync.md`: product-vs-Home-Project ownership and the
  commit decision gate.
- `LICENSE`, packaging metadata, install/publish scripts, and generic test
  infrastructure, subject to the adapter work below.

### `ADAPT`

- `src/skillnudge/cli.py`: keep a stable command entry point, then expose the
  control-plane lifecycle instead of legacy Advisor commands as the primary
  surface.
- `src/skillnudge/evolve.py`: retain candidate emission mechanics, but change
  the input from SkillNudge semantic Review admission to an imported external
  operator result with provenance.
- `src/skillnudge/review.py`, `src/skillnudge/validate.py`: retain strict
  envelope and evidence-reference validation only where it protects imported
  operator results; remove any implication that SkillNudge owns semantic
  utility judgement.
- `src/skillnudge/bootstrap.py`: extract generic data-directory and atomic
  persistence helpers; the bundled-corpus bootstrap is legacy.
- `src/skillnudge/watch.py`, `src/skillnudge/evidence_need.py`: preserve the
  history until an operator workflow demonstrates a need for suspended
  uncertainty; do not expose them in the V0 control-plane lifecycle.
- `src/skillnudge/validate.py` lifecycle status fields: map bounded evaluation
  results to `REVIEW_RESULT`/`DECISION_READY` evidence, never to automatic
  activation.
- Tests for artifact identity, candidate lineage, provenance and Human
  authority: keep their assertions while changing fixtures to the new
  operator contract.
- `README.md`, `README.zh-CN.md`, `docs/architecture.md`,
  `docs/current-status.md`, and `docs/roadmap.md`: rewritten or front-loaded
  with the new product boundary in this pass.

### `REMOVE_FROM_ACTIVE_TREE`

These remain recoverable in Git/history but are no longer part of the active
control-plane product:

- `src/skillnudge/phase1.py`, `planning.py`, `planning_contracts.py`,
  `planning_model.py`, `prompts.py`, `candidate_runtime.py`, `native.py`,
  `retrieval.py`, `judge.py`, `d001.py`: Advisor planning, BM25/RRF retrieval,
  bundled candidate acquisition, and semantic judging.
- `src/skillnudge/experiment_runner.py`, `real_experiment.py`: bespoke
  provider-backed and causal/evaluator machinery.
- `src/skillnudge/evidence_need.py`, `watch.py`: Evidence Need/WATCH/WAKE
  behavior, pending a concrete operator workflow that requires it.
- `src/skillnudge/data/default_corpus.json` and its manifest: bundled 61-Skill
  retrieval corpus.
- `eval/`, legacy run scripts under `scripts/run_*.py`, and tests whose sole
  purpose is the old Advisor, retrieval, provider experiment, or WATCH product
  claims.
- `docs/candidate-acquisition.md`, `capability-map.md`, `data-layer.md`,
  `final-advice.md`, `golden-cases.md`, `judge.md`, `retrieval.md`,
  `runtime.md`, `skill-utility-drift.md`, `week1*.md`, the old research and
  experiment documents, and old product receipts: historical input, not active
  product specification.

## Active Runtime Target

The target active runtime after migration is intentionally small:

- artifact identity/version/hash validation;
- Skill and version lineage records;
- lifecycle state and Human decision records;
- external operator request/result adapters;
- provenance and generic run references;
- atomic persistence and deterministic contract validation.

The current repository has only the first item as a clean reusable primitive.
The remaining items are the next implementation work, not silently claimed as
already shipped.

## New Lifecycle

```text
REGISTER
  -> ACTIVE SKILL
  -> REQUEST EVOLUTION
  -> SELECT OPERATOR (explicit intent in V0)
  -> EXTERNAL OPERATOR RUN
  -> CANDIDATE
  -> REVIEW RESULT / PROVENANCE
  -> HUMAN DECISION
  -> ACTIVATE | REJECT | ROLLBACK | RETIRE
```

`VALIDATE` is an operator-native or host-provided evidence result, not a
mandatory universal phase. `WATCH` and `Evidence Need` are not V0 lifecycle
stages. No automatic promotion or operator selection is introduced here.

## Operator Boundaries

| Operator | Owns | SkillNudge owns |
| --- | --- | --- |
| Skill Conductor | CREATE, REVIEW, STRUCTURE/QUALITY VALIDATE, PACKAGE | request identity, import, provenance, candidate lineage, Human decision |
| Darwin Skill | bounded interactive improve, checkpoints, keep/revert | invocation record, imported candidate identity, lifecycle state |
| Microsoft SkillOpt | trajectory-driven/offline optimization | integration boundary, training provenance, candidate lineage, Human decision |

SkillNudge does not reimplement any operator's authoring, optimization,
benchmark, or semantic judgement system.

## First Integration

`Skill Conductor` is the first operator target. Integration is explicitly
**not started in Phase 0**. The first milestone is one explicit evolution
request producing one imported non-active candidate with preserved provenance;
activation remains Human-controlled.

## Product Capability Gain

Phase 0 adds no new runtime behavior. Its externally verifiable gain is
boundary clarity: a contributor can now identify what SkillNudge owns and what
must remain an external operator. The next phase may add the first real
control-plane behavior.

## Principal Questions Before Phase 1

- Ratify the `REMOVE_FROM_ACTIVE_TREE` list before physical moves/deletions.
- Confirm whether `CapabilityArtifact` remains instruction-only for the first
  operator adapter.
- Confirm the minimum provenance fields required from Skill Conductor.
- Confirm whether legacy `review`/`validate` envelopes should be adapted or
  archived once the external operator contract exists.

## Delivery Gate

```yaml
phase: 0
product_behavior_changed: false
product_boundary_documented: true
runtime_migration_started: false
first_integration_started: false
commit_decision: COMMIT_NOW
commit_reason: "Record the Principal-provided Product Reset boundary and the recoverable repository classification."
push_decision: DEFER
```

