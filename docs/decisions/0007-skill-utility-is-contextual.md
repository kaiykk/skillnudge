# Decision 0007: Skill Utility Is Contextual

## Status

`[FROZEN]` as a product thesis; `[FUTURE]` as an automated lifecycle capability.

## Decision

Skill utility must be considered in the context of task, stage, model, project,
and time. V0 does not implement automatic Utility Drift detection.

## Context

A Skill can become redundant, overbroad, or overconstraining as models and
projects change. Static quality labels and popularity signals cannot represent
that change.

## Consequences

Future evaluation must retain model, task-stage, source-version, and time
context. Review, Grow, and Watch remain outside Week 1.

## Revisit When

Revisit when comparable cross-model or cross-time traces exist and can support a
bounded utility comparison.
