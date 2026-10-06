# Autonomous Evolution WATCH Slice Receipt

**Status:** `IMPLEMENTED_BOUNDED_MVP`

**Scope:** one persisted Evidence Need plus one later host experience

**Provider:** none

## Contract

`skillnudge need create --stdin` persists one `native.evidence-need.v0` with
candidate identity, question, why the question remains open, evidence role, scope and source references under
the per-user SkillNudge data directory. `skillnudge watch --stdin` reloads an
`OPEN` need and validates one host-produced experience against that identity
and scope.

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
