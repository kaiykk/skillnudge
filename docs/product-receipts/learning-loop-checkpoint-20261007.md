# Full Learning-Loop Checkpoint and Candidate Bottleneck Diagnosis

**Date:** 2026-10-07
**Scope:** SkillNudge product repository

## Stage capability

If this checkpoint succeeds, SkillNudge has a coherent bounded product story:
an observable experience can become Review evidence, a qualifying Review can
produce a non-active candidate, Validate can produce scoped evidence for a
Human decision, and unresolved uncertainty can be persisted, watched, woken,
and continued with new evidence.

This checkpoint does not add a new runtime primitive. It verifies product
coherence after the Phase A continuation increment.

## Phase B — full learning-loop checkpoint

```yaml
FULL_LEARNING_LOOP: COMPLETE_BOUNDED_V0
capability_lifecycle_coherence: PASS_BOUNDED
evidence_continuity: PASS_BOUNDED
human_boundary: PASS
product_usability: PASS_BOUNDED
```

The bounded narrative is:

```text
observable experience
  -> REVIEW TEST | WATCH | NO_INTERVENTION | INSUFFICIENT
  -> EVOLVE candidate-only when Review admission qualifies
  -> VALIDATE scoped comparison
  -> Human KEEP / PROMOTE / REJECT / RETIRE / ROLLBACK / WATCH decision
  -> Evidence Need OPEN when uncertainty remains
  -> WATCH IGNORE | WAKE | INSUFFICIENT
  -> WAKE reactivation context
  -> Host continuation action
  -> new evidence persisted under the original Need
```

Evidence survives task, process, and time boundaries through explicit run
artifacts, immutable candidate identity, validation lineage, persisted Need
identity, WAKE references, and continuation records. The Host still performs
the semantic handoff between commands; SkillNudge is not an orchestration
engine and does not infer missing links.

The Human boundary remains explicit:

```yaml
candidate_is_active_capability: false
helps_is_automatic_promotion: false
wake_is_lifecycle_transition: false
human_lifecycle_authority: true
```

## Phase C — candidate-generation bottleneck diagnosis

```yaml
CANDIDATE_GENERATION: NOT_CURRENT_BOTTLENECK
```

The accumulated product evidence does not show that Host candidate generation
is the dominant failure source:

| Evidence | What it shows | Bottleneck implication |
| --- | --- | --- |
| Direct Review -> EVOLVE dogfood | Candidate-only path completed; revision was `NEUTRAL` | No candidate-generation failure isolated |
| First utility-bearing round | Source `HELPS`, held-out H1 invalid and H2 fixture-only | Evidence/oracle/Native-arm problem, not candidate quality |
| Native held-out H1R/H3 | Both valid and `NEUTRAL` | Generalization signal is absent; candidate quality is not isolated |
| Mechanism Episode 1 | P+/P- both `NEUTRAL`; v1 already passed P+ | Mechanism/task discriminativeness is weak |
| Episode 0 | No natural discriminative boundary; low marginal information | Natural evidence is the limiting input |

The current product bottleneck is therefore better described as
`NATURAL_EVIDENCE_AND_EVALUATION_DISCRIMINATIVENESS`, with Host/task boundary
and Oracle quality as alternatives. This is a diagnosis of the evidence
record, not a new runtime feature or a capability-gap claim.

## Phase D decision

```yaml
DARWIN:
  evaluated: false
  outcome: KEEP_EXTERNAL
  reason: candidate_generation_not_current_bottleneck
  admission_authorized: false
```

Darwin is not integrated, SkillOpt is not started, and no candidate or
lifecycle state is changed by this checkpoint.

## Boundaries

```yaml
runtime_code_changed_by_checkpoint: false
automatic_orchestration: false
automatic_promotion: false
global_utility_score: false
phase4_or_rnd_framework_change: false
```

## Result

```yaml
PHASE_REACHED: PHASE_C_COMPLETE_BOUNDED_V0
PRODUCT_CAPABILITIES_ADDED:
  - Phase A: WAKE can resume one bounded Host evidence action and persist it with lineage
  - Phase B: lifecycle can be explained as one coherent bounded product loop
  - Phase C: product can reject Darwin as premature when candidate generation is not the bottleneck
FULL_LEARNING_LOOP:
  status: COMPLETE_BOUNDED_V0
CANDIDATE_GENERATION:
  bottleneck_status: NOT_CURRENT_BOTTLENECK
DARWIN:
  evaluated: false
  outcome: KEEP_EXTERNAL
PRODUCT_RUNTIME:
  new_runtime_commit: c5c5ebe
  tests: 145
  publish_gate: PASS
```
