# WAKE -> Evidence Continuation — Phase A Receipt

**Status:** `IMPLEMENTED_BOUNDED_MVP`

## Stage capability

If this stage succeeds, SkillNudge can receive one bounded continuation action
from a resumed Host after `WAKE`, persist the new observable evidence under the
original Evidence Need, and preserve source and WAKE lineage across processes.

## Product path

```text
Evidence Need OPEN
  -> WATCH IGNORE
  -> WATCH WAKE
  -> reactivation_context persisted
  -> Host consumes context
  -> watch continue
  -> continuation evidence persisted under Need
```

The continuation command is:

```bash
skillnudge watch continue --stdin \
  --reactivation-file <path-to-02_reactivation_context.json>
```

The Host supplies an observable action and one or more observable evidence
events. The core validates the exact persisted reactivation context and the
execution boundary before writing the continuation record.

## Cross-session proof

```yaml
session_a:
  need: created
  status: OPEN
session_b:
  watch: IGNORE
  reactivation_context: absent
session_c:
  watch: WAKE
  reactivation_context: persisted
session_d:
  host_action: bounded_evidence_review
  continuation: persisted
  source_refs_preserved: true
  wake_refs_preserved: true
  need_status: OPEN
```

The continuation record is written both to the run artifact and to:

```text
<data-dir>/evidence-needs/<need-id>/continuations/<continuation-id>.json
```

It contains no chain-of-thought or complete Host session transcript.

## Boundaries

```yaml
utility_claim: false
lifecycle_transition: null
need_status_after_continuation: OPEN
automatic_review: false
automatic_validate: false
automatic_resolution: false
automatic_promotion: false
need_discovery: false
scheduler: false
provider: none
```

## Receipt

```yaml
PHASE_A:
  wake_detection: PROVEN
  reactivation_context: PROVEN
  host_evidence_action_completed: PROVEN
  new_evidence_persisted: PROVEN
  evidence_lineage_preserved: PROVEN
  cross_session_resume: PROVEN
PRODUCT_CAPABILITY_ADDED:
  host_can_continue_bounded_evidence_from_persisted_wake_context: true
RUNTIME_CHANGED: true
TESTS: 145
PUBLISH_GATE: PASS
```
