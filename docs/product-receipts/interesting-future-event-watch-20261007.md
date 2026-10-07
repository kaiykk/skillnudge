# Operationalize `interesting_future_event` — Product Slice Receipt

**Status:** `IMPLEMENTED_BOUNDED_MVP`

This slice changes only the explicit persisted-Need WATCH path. Need discovery,
semantic candidate retrieval, Review, Validate, EVOLVE, Darwin, SkillOpt and
lifecycle decisions remain outside the slice.

## Product change

WATCH now uses a v1 envelope with:

```yaml
need_context:
  unresolved_question: <exact persisted value>
  interesting_future_event: <exact persisted value>
```

SkillNudge reloads the Need and rejects a context that differs from the
persisted values. The Host remains responsible for deciding whether the
observable experience instantiates the condition and returns `IGNORE`, `WAKE`,
or `INSUFFICIENT`. The core does not perform semantic text matching.

## Minimal verification

Using one persisted Need across the same temporary data directory, the bounded
tests cover:

```yaml
before_condition: IGNORE
qualifying_condition: WAKE
topically_related_only: IGNORE
insufficient_observable_evidence: INSUFFICIENT
paraphrased_qualifying_condition: WAKE
post_check_need_status: OPEN
```

The test suite also verifies that a changed `need_context` is rejected and that
the receipt/trace records `interesting_future_event_loaded`.

## Boundaries

```yaml
utility_claim: false
lifecycle_transition: null
need_identity_preserved: true
provider: none
automatic_follow_up: false
generic_need_discovery: false
```

## Product receipt

```yaml
PRODUCT_INCREMENT:
  interesting_future_event_operational: true
BEFORE:
  interesting_future_event_used_by_watch: false
AFTER:
  interesting_future_event_used_by_watch: true
BEHAVIOR:
  topical_only: IGNORE
  qualifying_event: WAKE
  insufficient: INSUFFICIENT
BOUNDARIES:
  utility_claim: false
  lifecycle_transition: null
  need_identity_preserved: true
RUNTIME_CHANGED: true
TESTS: PASS
SUPPORTED_CLAIM: >-
  The explicit persisted-Need WATCH path now exposes and verifies the exact
  interesting_future_event condition before recording a Host disposition.
NOT_ESTABLISHED:
  - generic Need discovery
  - semantic matching without Host judgement
  - utility or lifecycle effectiveness
  - cross-session aggregation or scheduling
```
