# Operator Integrations

External operators own creation and optimization. SkillNudge provides a narrow
control-plane adapter around them.

## Common Boundary

```text
EvolutionRequest
  -> operator invocation
  -> operator-native result
  -> imported CapabilityArtifact candidate
  -> provenance + lineage
  -> Human decision
```

The common request/result envelope must carry only fields needed for identity,
version lineage, status, operator identity/version, native result reference,
and provenance. It must not pretend that the three operators share one
algorithm.

## Operators

### Skill Conductor — first

Owns Skill creation, review, structure/quality validation, and packaging.
SkillNudge will request an operation and import the resulting candidate; it
will not duplicate Skill Conductor's authoring or evaluation framework.

### Darwin Skill — later

Owns bounded interactive improvement, Human checkpoints, and keep/revert.
SkillNudge records the invocation and imports the chosen candidate with native
evidence.

### Microsoft SkillOpt — later

Owns trajectory-driven and offline optimization. SkillNudge imports the chosen
candidate plus training provenance after the first two adapters have proven the
control-plane boundary.

## Human Authority

The Human Principal owns activation, rollback, rejection, retirement, and any
promotion decision. `DECISION_READY` is evidence availability, not permission
to mutate the active Skill.

## Explicit Non-goals

No autonomous operator routing, global utility score, benchmark framework,
retrieval research stack, Darwin reimplementation, SkillOpt reimplementation,
or automatic lifecycle loop is part of the first integration.

