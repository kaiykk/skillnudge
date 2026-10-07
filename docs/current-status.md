# Current Product Status

**As of:** 2026-10-07
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
current_outcome: REVIEW_EVOLVE_VALIDATE_WATCH_MVP
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
watch: IMPLEMENTED_BOUNDED_MVP
watch_scope: PERSISTED_INTERESTING_FUTURE_EVENT_MATCH_WAKE_REACTIVATE_AND_CONTINUE
watch_provider: NONE
watch_cross_session_persistence: PROVEN_BOUNDED
watch_automatic_lifecycle_transition: false
evidence_need: IMPLEMENTED_BOUNDED_MVP
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

The bounded WATCH slice persists one open Evidence Need outside the source
checkout and reloads it in a later process. The v1 WATCH envelope carries the
exact persisted `unresolved_question` and `interesting_future_event` to the
Host; SkillNudge rejects a stale or altered condition context before recording
the Host's `IGNORE`, `WAKE`, or `INSUFFICIENT` result. On `WAKE`, the v2 result
also persists `02_reactivation_context.json`, a minimal Host handoff containing
the suspended question and both source and wake evidence references. A later
Host process can consume that handoff and submit one bounded continuation
action. SkillNudge persists the new observable evidence under the original Need
with source and WAKE lineage. This does not answer the question, close the
Need, claim utility, advance the lifecycle, schedule work, or aggregate events.
Generic cross-session aggregation, scheduling and autonomous evolution remain
unimplemented. The product receipts for this slice are
`docs/product-receipts/interesting-future-event-watch-20261007.md`,
`docs/product-receipts/wake-reactivation-20261007.md`, and
`docs/product-receipts/evidence-continuation-20261007.md`.

The Phase B full learning-loop checkpoint is complete for bounded v0. The
product semantics are coherent across REVIEW, EVOLVE, VALIDATE, Evidence Need,
WATCH, WAKE and Host continuation, while semantic handoff remains explicit and
Human lifecycle authority is preserved. Phase C then found that candidate
generation is not the current bottleneck: the existing evidence is limited by
natural-task availability, evaluation/oracle validity and discriminativeness.
Darwin therefore remains external and is not admitted as an EVOLVE operator.
See `docs/product-receipts/learning-loop-checkpoint-20261007.md`.

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
record source task. Source S returned `VALID / HELPS` from the current Native
Host; H1 was `INVALID / NOT_EVALUATED` because its frozen Oracle contradicted
the task arithmetic; H2 returned a mechanically valid `HELPS` from a fixture,
not a fresh Agent/model trajectory. The round is therefore
`NOT_EVALUATED` for candidate utility, not a promotion result. Candidate v2
was frozen before held-out execution and Human DECIDE remains required. The product receipt is
`docs/product-receipts/first-utility-bearing-evolution-20261006.md`; raw
evidence remains in Home Project.

The first Native held-out follow-up evaluated the same frozen v2 on new Native
Host/model siblings H1R and H3. Both pairs were `VALID / NEUTRAL` with
complete observable trajectories and independently passing Oracles. Candidate
utility remains `NOT_ESTABLISHED`; the bounded round classification is
`NO_NATIVE_UTILITY_OBSERVED`; the Evolution Gradient is
`COLLECT_MORE_DISCRIMINATIVE_EVIDENCE`. The concise product receipt is
`docs/product-receipts/first-native-heldout-utility-20261006.md`; complete arm
trajectories and shadow analysis remain in Home Project.

The follow-up Mechanism-Grounded Autonomous Search Episode 0 reconstructed the
candidate mechanism and searched the existing Native evidence for a natural
discriminative record-admission boundary. It found none and stopped at
`LOW_MARGINAL_INFORMATION`; no new Native pair, candidate v3, Darwin, SkillOpt,
runtime change, or lifecycle mutation occurred. Its product-facing receipt is
`docs/product-receipts/mechanism-grounded-search-episode-0-20261006.md`; the
full search packet remains in Home Project.

Mechanism-Grounded Autonomous Search Episode 1 completed one matched diagnostic
P+/P- pair. Both pairs were `VALID / NEUTRAL`; v1 already passed the positive
probe despite overlapping metadata fields. Mechanism support is therefore
`WEAKENED`, while natural utility remains `NOT_ESTABLISHED`. The next action is
`WAIT_FOR_NATURAL_EVIDENCE`; no additional manufactured probe, Darwin, SkillOpt,
candidate v3, or runtime change is authorized. Product receipt:
`docs/product-receipts/mechanism-grounded-search-episode-1-20261006.md`.

```yaml
home_project:
  role: HISTORICAL_INPUT_ONLY
  runtime_dependency: NONE
```
