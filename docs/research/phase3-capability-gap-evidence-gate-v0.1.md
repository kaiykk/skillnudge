# Phase 3 Capability Gap Evidence Gate v0.1

**Status:** Model Track gate; implementation not authorized
**Date:** 2026-09-29
**Scope:** SkillNudge product Phase 3 only

This gate defines the product boundary for Phase 3. It does not add runtime
behavior, a registry implementation, a scoring system, or an evolution loop.

## 1. Phase identity

Phase 1 already covers Capability Discovery and Intervention Planning. Phase 3
must not recreate that layer. Phase 3 is:

> **Capability Gap Evidence Accumulation and Diagnosis**

Its question is:

> Which capability gap, if any, is supported by real agent experience evidence?

The output is a diagnosis artifact, not a changed Skill:

```text
Agent Experience
    -> Evidence Bundle
    -> Failure / Success Pattern
    -> Capability Gap Diagnosis
    -> Evidence-backed Evolution Hypothesis
    -> Principal Review
```

## 2. Input boundary

Allowed evidence sources:

- observable agent trajectories and execution traces;
- task outcomes and evaluator results;
- failure cases and successful counterexamples;
- user corrections or explicit acceptance/rejection;
- execution receipts, tests, diffs, and cleanup records;
- scoped Phase 2 utility measurements.

An Agent or LLM statement that a Skill “needs improvement” is not evidence by
itself. Raw traces, derived patterns, attribution, and hypotheses remain
separate objects.

## 3. Output boundary

Phase 3 produces a Capability Gap Registry and an evidence-backed evolution
hypothesis. A registry entry has this minimum semantic shape:

```yaml
capability_gap:
  id: gap-<stable-local-id>
  name: <capability description>
  scope: <task/scenario conditions>
evidence:
  source_experiences:
    - <experience-id>
  failure_pattern: <observed repeated or attributable pattern>
  outcome_impact: <observable consequence>
  attribution_alternatives:
    - skill_gap | agent_lapse | environment | project_fact | unclear
hypothesis:
  statement: <capability may improve the observed outcome under this scope>
  status: SUPPORTED | INSUFFICIENT | TASK_SPECIFIC_NOISE | UNCLEAR
  rationale: <evidence-bounded explanation>
```

The registry is not a Variant, candidate patch, promotion decision, or
lifecycle action.

## 4. Cardinality and evidence identity

The frozen semantic cardinality is:

```text
one capability-gap hypothesis
    1:N scenario-aware experience evidence units
```

Each evidence unit retains its own task/scenario identity. Every hypothesis
must bind:

```text
experience evidence
    + failure or success pattern
    + outcome impact
```

Multiple experiences do not mean arbitrary task pooling. Numeric minimums and
an independence test remain open until real Phase 3 evidence is observed.

## 5. Aggregation boundary

Aggregation is constrained, but no algorithm is frozen:

- preserve scenario, task-family, host, model, harness, environment, and
  intervention conditions;
- do not silently combine unlike experiences into one universal score;
- state which evidence identities are included and excluded from every
  synthesis;
- do not define a confidence threshold, weighting scheme, ranking score, or
  statistical rule in this gate.

## 6. Discovery Oracle

Phase 3 uses a **Discovery Oracle**, not the Phase 2 utility Oracle. Its only
question is:

> Is this capability-gap hypothesis supported by the supplied evidence?

Allowed outcomes:

```text
SUPPORTED
INSUFFICIENT
TASK_SPECIFIC_NOISE
UNCLEAR
```

The Discovery Oracle must return evidence references and a reason. It must not
judge whether a Skill improved downstream utility, generate a Variant, or make
a lifecycle decision.

## 7. Minimum bounded loop

```text
Experience Collection
    -> Failure / Success Pattern Mining
    -> Capability Gap Diagnosis
    -> Evidence-backed Hypothesis
    -> Discovery Oracle
    -> Human / Principal Review
```

The loop may create or update a registry entry and a review packet only. It
must not modify a Source Skill or start an optimization loop.

## 8. Stop and reopen conditions

Stop the current diagnosis when any of the following is true:

```text
no repeated or otherwise attributable capability pattern
OR evidence is insufficient
OR the hypothesis cannot be distinguished from task-specific noise
OR attribution is UNCLEAR
OR Ownership, Cardinality, Lifecycle, or Authority changes or is unclear
```

These are semantic stop conditions, not an automatic stopping algorithm.

## 9. Phase 4 boundary

Phase 4 owns the evolution question:

```text
Principal-reviewed Capability Gap Hypothesis
    -> authorized Evolution Operator
       (Human / Darwin / Reflexion / LLM proposal)
    -> Candidate Capability Variant
    -> held-out evaluation and regression review
    -> Principal lifecycle decision
```

Phase 3 does not include:

- Source Skill modification;
- Variant or candidate-patch generation;
- Darwin, hill-climbing, mutation, or selection;
- promotion, rollback, retirement, or automatic evolution;
- a universal capability score.

Darwin is therefore a Phase 4 Evolution Operator. The previous read-only
Darwin evaluator probe does not authorize full optimization or give Darwin a
Phase 3 role.

## 10. Gate status

This document is a Model Track gate, not an implementation contract. Before
Phase 3 runtime work starts, Principal / North Star Gate review must ratify:

1. the Phase 3 question and output boundary;
2. the one-hypothesis-to-many-experiences semantic cardinality;
3. the evidence identity and alternative-attribution requirements;
4. the Discovery Oracle boundary and outcome enum;
5. the Phase 4 and Darwin boundary;
6. the exact Execution Agent contract.

The following remain deliberately unfrozen: minimum experience count,
confidence/statistical threshold, aggregation formula, automatic stopping
algorithm, Variant schema, and lifecycle threshold.
