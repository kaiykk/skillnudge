# Product Evolution

## Status

- `[HISTORICAL EVIDENCE]` The product boundary changed as real user cases
  exposed failures in a Skill-only framing.
- `[FROZEN]` V0 is an Intervention Advisor, not a Skill directory.
- `[WORKING HYPOTHESIS]` Capability framing before candidate search reduces
  solution bias.

## Starting Point: Skill Discovery

The original problem was straightforward:

> Users cannot find a suitable Agent Skill.

The first mental model was:

```text
User task
→ Skill discovery
→ Recommend Skill
```

That model is useful when the user already knows the missing capability and
knows enough vocabulary to search. It breaks when the user only knows that the
next step feels difficult.

## D001: UI Vocabulary Gap

A user may say:

> I want to make a better-looking UI prototype, but I do not know what to
> search for.

The missing terms may include UI/UX, design systems, wireframes, or prototypes.
The reasoning path is:

```text
User problem
→ Missing capability
→ Skill candidate
```

This case motivates capability framing and query expansion before retrieval. A
UI/UX or prototyping Skill may genuinely change the next trajectory, but the
candidate name must not be hardcoded into the product.

## D002: Premature Execution and the Thinking Partner

For early product, architecture, or technical direction questions, an agent can
move too quickly through:

```text
plan
→ files
→ code
→ execution
```

The user may instead need:

```text
discussion
→ divergence
→ problem reframing
→ challenge assumptions
→ gradual convergence
→ execution
```

Brainstorming, lightweight Socratic guidance, a Plugin, a model bridge, or an
interaction mode may each address part of this problem. None is automatically
the right answer. The important observation is:

> The best intervention may not be a Skill.

## D003: No Intervention

For a direct question such as:

> What does this Python error mean?

the best advice may be no additional intervention. Recommending a Skill merely
to demonstrate discovery would add complexity without evidence of benefit.

Therefore:

> **Zero intervention is a valid answer.**

## Resulting Product Boundary

The product definition evolved from **Skill Recommender** to
**Capability Intervention Advisor**:

```text
User problem
→ Missing capability
→ Intervention type
→ Candidate
→ Evidence-based judgement
→ Bounded advice
```

Skill remains an important candidate surface, but the product is not allowed
to force every problem into the Skill category.

## What This Is Not

SkillNudge is different from:

- a larger Skill directory, because it judges whether intervention is useful;
- a Skill installer, because installation is outside the V0 boundary;
- a generic tool marketplace, because candidate acquisition serves a current
  capability contract;
- a bug-fix project, because a failed candidate is evidence about the product
  boundary, not automatically a defect to patch;
- a self-training model, because the product does not update model weights;
- a complete self-evolving platform, because Review, Grow, Watch, and lifecycle
  automation remain future work.
