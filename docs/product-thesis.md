# Product Thesis

Canonical long-term statement: [`docs/north-star.md`](north-star.md).
This file remains the detailed current product thesis and V0 boundary.

## Status

- `[FROZEN]` The V0 product boundary is a Capability Intervention Advisor.
- `[FROZEN]` Zero intervention is a valid result.
- `[WORKING HYPOTHESIS]` The smallest useful intervention is usually more
  valuable than a broad recommendation list.
- `[FUTURE]` Utility Drift and the full intervention lifecycle.

## The Problem

The starting problem looked like:

```text
User task
→ Skill discovery
→ Recommend Skill
```

That framing is too narrow for real agent work. A user may be blocked because
they lack a professional concept, a collaboration mode, a tool integration, or
simply a clear explanation. The system therefore needs to ask what capability is
missing before it decides whether a Skill is relevant.

## Product Boundary

SkillNudge is designed to answer:

> What capability is actually missing at this point in the task, and is any
> intervention worth adding at all?

The possible intervention classes are:

- Skill;
- Plugin;
- Tool;
- Companion Resource;
- No intervention.

This is an advice boundary, not an automatic installer or an autonomous
workflow owner.

## Core Principle

> **The right capability, only when it helps.**

The internal design formulation is:

> Find the smallest intervention that meaningfully improves the next trajectory.

The product should not optimize for:

- more Skills;
- more tools;
- more context;
- more scaffolding;
- more recommendations.

## Contextual Utility

The long-term conceptual model is:

```text
Intervention Utility =
f(
  intervention,
  task,
  task_stage,
  model,
  project_context,
  time
)
```

This is not a V0 scoring formula. It records why a static quality label is
insufficient: the same intervention can help in one task stage and be
redundant, intrusive, or harmful in another.

## Evidence Discipline

The following must remain distinct:

- a product design target;
- a working hypothesis;
- an observation from a real task;
- a claim in a README or paper;
- a confirmed implementation behavior.

Until implementation and validation exist, documents must use terms such as
`planned`, `designed`, `proposed`, or `future`. This repository does not claim
that the V0 runtime, retrieval, corpus, Judge, or trace system already exists.
