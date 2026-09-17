# Skill Utility Drift

## Status

- `[FUTURE]` Utility Drift is a long-term lifecycle direction.
- `[WORKING HYPOTHESIS]` Skill utility can decline even when the Skill source
  does not change.
- `[HISTORICAL EVIDENCE]` Model upgrades and real task observations motivated
  this concern.
- `[FROZEN]` Week 1 does not implement drift detection, Review, Grow, or Watch.

## The Long-Term Problem

A Skill's static text is not its utility. As foundation models improve, the
capability that once required detailed scaffolding may become native model
behavior. The same Skill can therefore move through:

```text
helpful
→ redundant
→ overconstraining
```

The long-term conceptual model remains:

```text
Utility =
f(
  Skill,
  Model,
  Task,
  Stage,
  Context,
  Time
)
```

This is a framing device, not an implemented detector or score.

## Possible Drift Signals

Future Review or Watch work may examine:

- reduced improvement in comparable tasks;
- a trigger that activates too broadly;
- repeated instructions that the model already follows;
- increased context pressure;
- conflicts with project or host instructions;
- source, version, or compatibility changes;
- user reports that the intervention adds friction.

None of these signals is sufficient on its own to retire a Skill.

## Future Actions

A model-aware lifecycle may recommend:

- keep;
- simplify;
- narrow the trigger;
- add progressive disclosure;
- update;
- replace;
- retire.

Grow must not be equated with writing more instructions. A good revision may
remove recipes, shorten descriptions, narrow activation, or delete duplicated
model capability.

## Boundary

SkillNudge does not currently claim to monitor installed Skills, compare models,
run replay experiments, or automate lifecycle decisions. Those activities
require evidence from Review and Watch before they can become product behavior.
