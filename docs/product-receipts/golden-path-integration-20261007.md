# Golden Path Integration Campaign — Product Receipt

**Date:** 2026-10-07
**Status:** `INTEGRATED_BOUNDED_V0`

## Correction to prior status

The earlier Phase B receipt remains valid as a component-level checkpoint. Its
statement that the bounded lifecycle was coherent did not prove one integrated
trajectory. This addendum preserves that history and records the stronger
cross-process integration result below.

## Stage capability

If this stage succeeds, one capability uncertainty can cross multiple
executions, wait for a qualifying future experience, resume from the persisted
suspended point, and reach an existing evaluation primitive and Human decision
readiness without losing lineage.

## Canonical case

```yaml
case: structured-record-transformation
evidence_mode: sanitized_host_observable_fixture
source_capability: record-identity/v1
candidate_capability: record-identity/v2
natural_utility_claim: false
```

The case reuses the existing CapabilityArtifact, Review, Validate, Evidence
Need, WATCH, WAKE, and continuation contracts. No Golden-Path-only runtime was
introduced.

## Integrated trajectory

```text
review-source
  -> TEST
validate-initial
  -> VALID / NEUTRAL
evolve
  -> CANDIDATE (non-active)
need create
  -> OPEN, unresolved question persisted
watch-ignore
  -> IGNORE, no reactivation context
watch-wake
  -> WAKE, reactivation context persisted
continuation
  -> Host bounded evidence action, continuation evidence persisted under Need
review-postwake
  -> TEST from the persisted continuation evidence
validate-postwake
  -> VALID / NEUTRAL / DECISION_READY / KEEP / HUMAN_REQUIRED
```

The same candidate identity is carried through the source artifact, EVOLVE
result, Need subject, WAKE context, continuation evidence, and post-WAKE
CAPABILITY_REVISION validation. The Need remains `OPEN` because the bounded
result is neutral and Human lifecycle authority is still required.

## Lineage and boundaries

```yaml
review: preserved
source_capability: preserved
candidate: preserved
initial_validation: preserved
evidence_need: preserved
wake: preserved
continuation: preserved
post_wake_evaluation: preserved
candidate_active: false
utility_claim: false
automatic_promotion: false
automatic_lifecycle_mutation: false
human_authority: preserved
```

## Integration issues found

The first campaign attempts failed in the temporary integration harness, not in
SkillNudge runtime:

1. A full CapabilityArtifact was passed into the Need subject instead of the
   canonical three-field identity projection.
2. `version` / `sha256` were initially mapped without the Need contract's
   `candidate_version` / `candidate_sha256` names.
3. The CAPABILITY_REVISION harness initially sent an intervention hash; that
   mode correctly requires `intervention_identity: null` and a
   `capability_identity` per arm.

The final regression test uses explicit adapters for these existing contracts.
No product runtime bug or new semantic contract was required.

## Campaign result

```yaml
GOLDEN_PATH:
  completed: true
  canonical_case: structured-record-transformation
FULL_LEARNING_LOOP:
  status: INTEGRATED_BOUNDED_V0
HUMAN_BOUNDARY:
  preserved: true
CANDIDATE_GENERATION:
  bottleneck_status: NOT_CURRENT_BOTTLENECK
DARWIN:
  admission_reopened: false
PRODUCT_RUNTIME:
  changed: false
TESTS:
  golden_path: PASS
  canonical_suite: 146_PASS
PUBLISH_GATE: PASS
WHAT_SKILLNUDGE_CAN_NOW_DO: >-
  Carry one capability uncertainty from observable diagnosis through candidate
  evaluation, suspension, future WAKE, bounded evidence continuation, and
  post-WAKE Human decision readiness with preserved lineage.
REMAINING_PRODUCT_GAP: >-
  The Host still explicitly transports result artifacts between primitives;
  SkillNudge does not provide generic orchestration or automatic lifecycle
  mutation.
PRINCIPAL_GATE:
  required: false
  reason: >-
    The campaign stayed within existing lifecycle, evidence, and Human
    authority semantics.
```
