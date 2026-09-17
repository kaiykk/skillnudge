# Model Evolution and Skills

## Status

- `[HISTORICAL EVIDENCE]` Discussion of stronger models raised the possibility
  that Skill utility changes over time.
- `[WORKING HYPOTHESIS]` Skill ecosystems need lifecycle management, not only
  discovery.
- `[FUTURE]` Model-aware Review, Grow, Watch, and utility-drift evaluation.

This document records product implications. It does not claim that SkillNudge
currently detects any of them.

## Design Implications

As models become more capable:

- old scaffolding may become unnecessary;
- long descriptions may increase context pressure;
- broad triggers may activate the wrong intervention;
- several Skills may compete for context;
- progressive disclosure may become more important;
- detailed recipes may overconstrain a capable model;
- AGENTS.md and Skill instructions may need contextual loading;
- model behavior changes may alter the value of the same Skill.

## Lifecycle Hypothesis

A Skill ecosystem should eventually support more than discovery:

```text
discover
→ use
→ review
→ simplify / update / replace
→ watch for drift
```

The correct future action may be to remove instructions rather than add them.
This is why Grow and Watch are separated from V0 Advise.

## Boundary

These observations do not justify a Week 1 model benchmark, automatic
personalization, or a self-evolving Skill optimizer. They justify recording
model, task stage, context, source version, and time wherever later evidence can
support comparison.
