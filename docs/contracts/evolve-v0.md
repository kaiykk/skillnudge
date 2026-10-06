# EVOLVE v0

`skillnudge evolve --stdin` is a provider-free, candidate-only product path.
The minimum direct admission chain is:

```text
Review TEST
  -> attribution.primary = capability_candidate
  -> observable Review evidence and intervention candidate
  -> source CapabilityArtifact
  -> host-proposed instruction candidate
```

`validation_result` is optional. When present, it must be a linked, valid
`INTERVENTION_ABLATION` result, but `HELPS` is not a universal pre-EVOLVE
prerequisite. `CAPABILITY_REVISION` is a post-EVOLVE comparison and is not an
EVOLVE input. The Host may use `INTERVENTION_ABLATION` to strengthen evidence
before EVOLVE when attribution or mechanism remains uncertain.

The command verifies Review evidence, optional Validate linkage, and the
source/candidate capability lineage. A raw bad case, non-capability Review
attribution, unrelated validation result, or invalid artifact is rejected.

The output remains non-active:

```yaml
lifecycle_status: CANDIDATE
decision_state:
  status: PENDING_VALIDATION
  suggested_action: VALIDATE
  authority: HUMAN_REQUIRED
```

It never installs, overwrites, activates, promotes, rolls back, or retires a
capability. `CAPABILITY_REVISION` compares candidate v2 with current v1 and
emits bounded decision evidence; the Human Principal owns the final
`PROMOTE`, `KEEP`, `REJECT`, `RETIRE`, `ROLLBACK`, or `WATCH` decision.
