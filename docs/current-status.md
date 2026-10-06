# Current Product Status

**As of:** 2026-10-06
**Scope:** SkillNudge product repository
**Evidence detail:** Detailed research receipts remain historical inputs in
Home Project; this file is the product-facing summary and does not replace
those receipts. Home Project is not a SkillNudge runtime dependency.

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
- A `TEST` result can be passed to `skillnudge validate --stdin` with one
  frozen task, exact instruction identity, parity-controlled Control/Treatment
  records, and an observable Oracle.

### Current Outcome — Native Review + Validate MVP

```yaml
current_outcome: REVIEW_EVOLVE_VALIDATE_MVP
status: IMPLEMENTED_BOUNDED_MVP
input: one real or sanitized observable Agent experience
output: TEST | WATCH | NO_INTERVENTION | INSUFFICIENT
evidence: same-experience observable event references
provider: NONE
cross_session_aggregation: NOT_IMPLEMENTED
hidden_reasoning_claim: NONE
effectiveness_claim: NONE
validate: IMPLEMENTED_BOUNDED_MVP
evolve: IMPLEMENTED_BOUNDED_MVP
evolve_evidence: HOST_ATTESTED_DIRECT_PATH_DOGFOOD
native_direct_review_to_evolve: PROVEN_FOR_ONE_BOUNDED_TASK
capability_revision_outcome: NEUTRAL
decision_authority: HUMAN_REQUIRED
auto_promotion: NOT_IMPLEMENTED
```

The Review runtime validates a strict host-produced envelope, rejects unknown
evidence references and private reasoning fields, persists the input/result/
trace outside the source checkout, and emits no provider-backed judgement. A
`TEST` result means only that a bounded intervention is worth validating next;
it is not a proven capability gap or utility result. A Validate result is
scoped to one task/intervention/host/model and does not authorize promotion,
rewrite, or evolution.

EVOLVE now creates one immutable instruction candidate when a linked Review
`TEST` has primary `capability_candidate` attribution, observable evidence,
source artifact identity, and valid host-proposed content. A bounded
`INTERVENTION_ABLATION` result may strengthen admission but is optional and
does not need to be `HELPS` merely to create a candidate. Post-EVOLVE `VALIDATE`
reuses the existing `validate` command in `CAPABILITY_REVISION` mode. No candidate is
installed or promoted. Retrieval, planning, and Phase 1 runtime behavior are
unchanged.

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

The direct Review -> EVOLVE -> CAPABILITY_REVISION path has now completed one
isolated Native Host dogfood. The result is `NEUTRAL` with
`DECISION_READY / KEEP / HUMAN_REQUIRED`; it does not establish candidate
utility, a reusable capability gap, cross-session aggregation, automatic
promotion, or autonomous evolution. The product delivery receipt is
`docs/product-receipts/direct-review-evolve-native-20261006.md`; the complete
trajectory and governance packet remain in Home Project.

The first bounded utility-evidence round then exercised a fresh structured
record task family. Source S and held-out H2 returned `VALID / HELPS`; H1 was
`INVALID / NOT_EVALUATED` because its frozen Oracle contradicted the task
arithmetic. This is a `MIXED_OBSERVATION`, not a stable utility or promotion
result. Candidate v2 was frozen before held-out execution and Human DECIDE
remains required. The product receipt is
`docs/product-receipts/first-utility-bearing-evolution-20261006.md`; raw
evidence remains in Home Project.

```yaml
home_project:
  role: HISTORICAL_INPUT_ONLY
  runtime_dependency: NONE
```
