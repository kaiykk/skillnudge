# Autonomous Evolution WATCH Slice Receipt

**Status:** `IMPLEMENTED_BOUNDED_MVP`

**Scope:** one persisted Evidence Need plus one later host experience

**Provider:** none

## Contract

`skillnudge need create --stdin` persists one `native.evidence-need.v0` with
candidate identity, question, why the question remains open, evidence role, scope and source references under
the per-user SkillNudge data directory. `skillnudge watch --stdin` reloads an
`OPEN` need and validates one host-produced experience against that identity,
scope, and the exact persisted `unresolved_question`/
`interesting_future_event` context. The v0 receipt below is the historical
baseline; the operational v1 slice is recorded in
`interesting-future-event-watch-20261007.md`.

The only dispositions are `IGNORE`, `WAKE`, and `INSUFFICIENT`. The result
contains event references and explicit non-claims:
`utility_claim=false`, `lifecycle_transition=null`, and `provider=null`.
The need remains `OPEN`; WATCH does not invoke Review, Validate, Evolve,
Darwin, SkillOpt or promotion.

## Acceptance matrix

| Case | Expected result |
| --- | --- |
| Need created in process A, loaded in process B | `OPEN` survives process boundary |
| Unrelated bounded experience | `IGNORE` |
| Relevant bounded experience | `WAKE` |
| Evidence-poor experience | `INSUFFICIENT` |
| Unknown event reference | deterministic rejection |
| Closed need | deterministic rejection; no wake |
| Candidate hash mismatch | deterministic rejection |
| Private reasoning field | deterministic rejection |
| Routing fixture marked `WATCH_ROUTING_TEST_EVIDENCE` | never promoted to natural utility evidence |

## Integrated E2E

Using one temporary shared `SKILLNUDGE_DATA_DIR`, independent CLI processes
completed the following sequence:

```yaml
session_A_need_create: OPEN
session_B_unrelated: IGNORE
session_C_relevant: WAKE
session_D_evidence_poor: INSUFFICIENT
post_check_need_status: OPEN
```

The process boundary was real: later commands loaded
`need-episode-1` from disk rather than rebuilding it in memory. Every E2E
experience was explicitly marked `WATCH_ROUTING_TEST_EVIDENCE`; no natural
utility evidence was created.

## Evidence classification

The E2E routing envelopes are deliberately constructed product fixtures. They
prove bounded persistence and routing only. They are
`WATCH_ROUTING_TEST_EVIDENCE`, not `NATURAL_UTILITY_EVIDENCE`, and do not prove
candidate utility, mechanism truth, generalization, or promotion.

## Final receipt

```yaml
BASELINE:
  name: SkillNudge Autonomous Evolution Baseline v0
  frozen: true
  document: docs/autonomous-evolution-baseline-v0.md

MULTI_BRANCH:
  branches:
    evidence_need:
      completed: true
    watch:
      completed: true
    baseline:
      completed: true
  integration_completed: true
  semantic_drift_detected: false

EVIDENCE_NEED:
  schema_version: native.evidence-need.v0
  persisted: true
  survives_process_boundary: true
  evidence_role: NATURAL_UTILITY_EVIDENCE
  status: OPEN

WATCH:
  implemented: true
  provider_free: true
  dispositions:
    - IGNORE
    - WAKE
    - INSUFFICIENT

E2E:
  need_created_in_session_A: true
  unrelated_experience:
    separate_session: true
    result: IGNORE
  relevant_experience:
    separate_session: true
    result: WAKE
  insufficient_experience:
    result: INSUFFICIENT

WAKE_BOUNDARY:
  utility_claim_created: false
  lifecycle_transition_created: false
  evolve_called: false
  validate_called: false
  darwin_called: false
  skillopt_called: false

EVIDENCE_ROLES:
  routing_test_promoted_to_natural_utility: false

PRODUCT:
  runtime_changed: true
  tests: 136
  publish_gate: PASS
  commit: 3ef905f
  pushed: true

WATCH_STATUS: IMPLEMENTED_BOUNDED_MVP
NEXT_BOTTLENECK: Principal review before a natural Native Host experience
FRAME_REOPEN_REQUIRED: false
```
