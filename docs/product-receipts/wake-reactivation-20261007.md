# WAKE -> Actionable Evidence Reactivation — Product Slice Receipt

**Status:** `IMPLEMENTED_BOUNDED_MVP`

This slice extends the explicit persisted-Need WATCH path. It does not change
the semantic Host decision (`IGNORE`, `WAKE`, or `INSUFFICIENT`) and does not
introduce Need discovery, scheduling, Review, Validate, EVOLVE, or lifecycle
automation.

## Contract correction

The input envelope remains `native.watch-envelope.v1`. The result protocol is
`native.watch-result.v2` because a valid `WAKE` now has a product handoff:

```yaml
reactivation_context:
  schema_version: native.watch-reactivation.v0
  need_id: <exact persisted Need identity>
  subject: <exact persisted candidate identity>
  unresolved_question: <exact persisted value>
  interesting_future_event: <exact persisted value>
  source_evidence_refs: <persisted Need refs>
  wake_evidence_refs: <refs from the WAKE assessment>
  execution_context: <validated host context>
```

The context is created and persisted only for `WAKE` as
`02_reactivation_context.json`. `IGNORE` and `INSUFFICIENT` return
`reactivation_context: null` and create no handoff file.

## Minimal end-to-end proof

One persisted Need was used across independent steps:

```yaml
session_a: Evidence Need created and remains OPEN
session_b: non-qualifying experience -> IGNORE -> no reactivation context
session_c: qualifying experience -> WAKE -> reactivation context persisted
host_continuation: independent process consumed the context and emitted
  HOST_CONTINUATION_STEP_READY
```

The continuation step only proves that the Host can recover the suspended
question and new wake evidence without manually reconstructing the Need. It
does not claim that the uncertainty was answered.

## Boundaries

```yaml
need_status_after_wake: OPEN
utility_claim: false
lifecycle_transition: null
automatic_review_or_validate: false
automatic_follow_up: false
need_discovery: false
provider: none
chain_of_thought_persisted: false
```

## Product receipt

```yaml
PRODUCT_INCREMENT:
  wake_reactivation_context_operational: true
BEFORE:
  wake_behavior: persisted receipt only
AFTER:
  wake_behavior: persisted bounded Host reactivation context
BEHAVIOR:
  ignore: no reactivation context
  wake: context persisted and exposed
  insufficient: no reactivation context
  host_continuation: independently consumed context
BOUNDARIES:
  utility_claim: false
  lifecycle_transition: null
  need_status: OPEN
  need_identity_preserved: true
RUNTIME_CHANGED: true
TESTS: PASS
SUPPORTED_CLAIM: >-
  A valid WAKE now reconstructs the persisted uncertainty and attaches the new
  wake evidence as a bounded Host handoff that can be consumed cross-process.
NOT_ESTABLISHED:
  - uncertainty resolution
  - utility or validation effectiveness
  - automatic Review, Validate, EVOLVE, or lifecycle mutation
  - generic Need discovery, scheduling, or aggregation
```
