# Decision 0001: Capability Intervention Advisor

## Status

`[FROZEN]`

## Decision

SkillNudge is a Capability Intervention Advisor, not merely a Skill search
engine or directory.

## Context

Users may not know the capability or vocabulary they need. A semantically
related candidate may still be wrong for the task stage, host, or workflow.
The useful intervention may be a Skill, Plugin, Tool, Companion Resource, or
none.

## Options Considered

- Build a larger Skill directory.
- Build only Skill search or installation.
- Route every problem to a Skill.
- Frame the missing capability first, then judge the intervention class and
  utility.

## Consequences

- Retrieval relevance is not final recommendation.
- Output must stay small and explain uncertainty.
- No intervention remains valid.
- Skill is an important surface, not a mandatory answer.

## Revisit When

Revisit if real tasks show that intervention-class reasoning has no useful
incremental value and users consistently need only a pure Skill directory.
