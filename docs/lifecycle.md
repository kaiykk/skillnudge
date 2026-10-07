# SkillNudge Lifecycle

SkillNudge owns the lifecycle of a Skill artifact, not the algorithm that
authors or optimizes it.

```text
REGISTER
  -> ACTIVE SKILL
  -> REQUEST EVOLUTION
  -> SELECT OPERATOR
  -> EXTERNAL OPERATOR RUN
  -> CANDIDATE
  -> REVIEW RESULT / PROVENANCE
  -> HUMAN DECISION
  -> ACTIVATE | REJECT | ROLLBACK | RETIRE
```

## States

- `REGISTERED`: identity is known, but the Skill is not active.
- `ACTIVE`: the Human-approved version used by a host.
- `EVOLUTION_REQUESTED`: an explicit request records the source version,
  objective, and intended operator.
- `CANDIDATE`: an external operator result has been imported as a non-active
  version with lineage and provenance.
- `DECISION_READY`: the candidate and its operator evidence are available for
  Human review.
- `REJECTED`, `ROLLED_BACK`, and `RETIRED`: Human lifecycle outcomes.

An operator's validation result is evidence attached to a request or candidate;
it is not by itself a lifecycle transition. SkillNudge never promotes a
candidate automatically.

## Minimal Shared Artifact

The first shared artifact is `native.capability-artifact.v0`:

```yaml
capability_id: stable identity
version: immutable version
type: instruction
exact_content: exact bytes
sha256: hash of exact_content
```

Operator-specific metadata and native result references remain in provenance;
SkillNudge normalizes only the identity and lifecycle fields it needs.

