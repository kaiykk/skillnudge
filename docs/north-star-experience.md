# North Star Experience Reference

**Status:** canonical product experience reference  
**Updated:** 2026-10-05

This document describes what a person should be able to experience from
SkillNudge. It is not a UI specification, workflow diagram, ontology, or
runtime architecture. The bounded EVOLVE candidate path is implemented; the
full autonomous lifecycle remains out of scope.

## ADVISE

Before starting a task, a person or host Agent can ask:

> Is adding an external capability worthwhile for this task right now?

SkillNudge may recommend a bounded intervention, ask for clarification, or
return no intervention. Relevance alone is not a recommendation to add
something.

## REVIEW

After an Agent has acted, a person can provide a real or sanitized observable
trajectory and ask:

> Is there something here worth testing as an intervention?

SkillNudge identifies a bounded intervention candidate, or returns no
intervention/insufficient evidence. Review keeps event references and
uncertainty. It does not turn every bad case into a Skill problem and does not
prove a capability gap or utility.

## INTERVENTION_ABLATION (optional pre-EVOLVE evidence)

When a candidate is worth testing, a person can compare the no-intervention
condition with the exact intervention on a bounded task:

> Did this intervention change the observed execution outcome under the stated
> conditions?

SkillNudge preserves task, host, model, harness, tool, environment, artifact,
and Oracle identity. The result is scoped to that comparison and may be
positive, neutral, harmful, inconclusive, or not evaluated.

## VALIDATE

After EVOLVE creates a non-active candidate, a person can compare candidate v2
with current capability v1 under the same bounded task and host conditions.
This `CAPABILITY_REVISION` result is evidence for the Human-owned DECIDE step;
it is not an automatic promotion or lifecycle transition.

## EVOLVE

Review evidence that passes the EVOLVE Admission Contract can justify proposing
a changed version of a capability. The Host supplies the semantic proposal;
SkillNudge preserves source identity, parent lineage, exact content, hashes,
and evidence links. An `INTERVENTION_ABLATION` comparison may strengthen
admission when attribution or mechanism is uncertain, but is not universally
required. The result is a non-active candidate that must be compared against
the current capability before any Human lifecycle decision.

Human Principal authority remains final for promotion, rollback, and
retirement. SkillNudge never installs, overwrites, activates, promotes,
rolls back, or retires a capability automatically.

## Experience Invariants

- A bounded result is more important than a confident narrative.
- No intervention is a valid result.
- Every lifecycle step keeps uncertainty and evidence scope visible.
- Home Project research and DSH review are historical or governance inputs;
  they are not SkillNudge runtime dependencies.
