# Current Product Status

**As of:** 2026-10-05
**Scope:** SkillNudge product repository
**Evidence detail:** Home Project research receipts; this file is the
product-facing summary and does not replace those receipts.

## Product/runtime baseline

The shipped runtime includes the provider-free Native Phase 1 advisor baseline
and the bounded Native Review MVP:

- Codex can explicitly invoke `$skillnudge` from an unrelated repository.
- SkillNudge performs deterministic retrieval and evidence hydration.
- The host Agent owns semantic planning and judgement.
- The public Native Mode does not require a separate SkillNudge model provider.
- A host Agent can submit one observable experience to `skillnudge review --stdin`
  from an unrelated working directory and receive a deterministic bounded
  disposition with event references and uncertainty.

### Current Outcome — Native Review MVP

```yaml
current_outcome: REVIEW_MVP
status: IMPLEMENTED_BOUNDED_MVP
input: one real or sanitized observable Agent experience
output: TEST | WATCH | NO_INTERVENTION | INSUFFICIENT
evidence: same-experience observable event references
provider: NONE
cross_session_aggregation: NOT_IMPLEMENTED
hidden_reasoning_claim: NONE
effectiveness_claim: NONE
```

The Review runtime validates a strict host-produced envelope, rejects unknown
evidence references and private reasoning fields, persists the input/result/
trace outside the source checkout, and emits no provider-backed judgement. A
`TEST` result means only that a bounded intervention is worth validating next;
it is not a proven capability gap or utility result.

This sync does not change `src/`, the CLI, the native contract, retrieval,
planning, or the Phase 1 runtime behavior.

## Research-track position

### Phase 2 — scoped measurement

The first bounded measurement slice and evaluator-only comparison are retained
as scoped research evidence. The result is not a universal utility claim:

```yaml
measurement_slice: COMPLETE_FOR_TESTED_SCOPE
utility: INCONCLUSIVE_OR_NEUTRAL_BY_TESTED_SCOPE
universal_skill_utility: NOT_ESTABLISHED
```

### Phase 3 — capability-gap diagnosis

The bounded Phase 3 evidence and diagnosis campaign is complete for the current
research scope. It established an evidence admission and attribution boundary,
but did not establish a reusable capability gap or a Skill defect:

```yaml
phase3_status: COMPLETE_FOR_CURRENT_BOUNDED_DIAGNOSIS
capability_gap: NONE_ESTABLISHED
reusable_capability_gap: INSUFFICIENT
skill_gap: NONE_ESTABLISHED
variant: NOT_GENERATED
```

This is a valid Phase 3 outcome. It does not mean that capability gaps can
never exist; it means the current evidence does not support one.

### Phase 4A — entry hardening and contract readiness

Phase 4A has been initially opened as controlled contract/readiness work. The
reference task, Oracle, host/evaluator boundary, trace semantics and parity
requirements are being hardened as static artifacts:

```yaml
phase4a_status: ENTRY_HARDENING_IN_PROGRESS
reference_task: PRESERVED_AND_REVIEWED
execution_contract: STATIC_READINESS_ARTIFACTS
control_treatment_run: NOT_AUTHORIZED
run_authorization: NOT_AUTHORIZED
source_skill_change: NO
variant_generation: NO
darwin_skillopt: NOT_CALLED
product_runtime_change: NO
```

`READY_TO_RUN` or `READY_FOR_FRESH_PAIR` is a readiness description, not run
authorization. A future Phase 4A run requires a separate Principal-authorized
execution contract and a fresh receipt.

## What this repository does not claim

- Phase 3 did not prove a general capability gap.
- Phase 4A did not prove positive utility or causal superiority.
- No Variant has been promoted.
- Darwin/SkillOpt has not been activated as a product evolution loop.
- The governance reviewer layer is not SkillNudge runtime or product IA.

Detailed raw traces, DSH outputs, experiment receipts and governance packets
remain in the separate Home Project evidence repository. They are not copied
into this product repository.

## Product-facing next step

The next product slice is a provider-free Validate MVP. It must remain a
separate outcome and may not turn Review dispositions into utility conclusions,
cross-session aggregation, Variant generation, or an evolution loop.
