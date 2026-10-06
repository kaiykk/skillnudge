# Evolution Gradient

**Status:** FROZEN CONCEPTUAL MODEL  
**Runtime status:** NOT A RUNTIME CONTRACT  
**Lifecycle status:** NOT A NEW LIFECYCLE STAGE  
**Updated:** 2026-10-06

## Purpose

An **Evolution Gradient** is an evidence-bounded directional signal derived
from evaluation results. It helps determine what evidence or capability change
may be worth considering next. It is a planning aid for a future evolution
cycle, not an action and not a lifecycle decision.

The current SkillNudge round established only a bounded evaluation record:

- the Native Host source task produced `VALID / HELPS`;
- H1 was `INVALID / NOT_EVALUATED` because its frozen Oracle was inconsistent;
- H2 was a mechanically valid fixture result, not fresh Native Host utility
  evidence;
- candidate utility remains `NOT_ESTABLISHED`.

These facts may inform a future direction, but they do not themselves create a
gradient, prove a capability gap, or authorize another run.

## What It Is Not

```text
Evolution Gradient != mathematical gradient
Evolution Gradient != scalar utility score
Evolution Gradient != causal truth
Evolution Gradient != candidate rewrite
Evolution Gradient != lifecycle authority
```

It must not become a global ranking, confidence score, automatic trigger, or
post-hoc explanation of an invalid run.

## Three-Layer Separation

The conceptual relationship is:

```text
EVALUATION FACT
      -> CAUSAL HYPOTHESIS
      -> EVOLUTION GRADIENT
      -> future candidate update (only after explicit lifecycle gates)
```

These are separate objects with separate evidence standards.

### Evaluation Fact

An Evaluation Fact contains only bounded observed or validated information,
such as:

- pair status and validation result;
- Oracle validity;
- execution provenance and observability tier;
- artifact identities and hashes;
- observable trajectory references;
- tested scope and parity context.

It contains no explanation or rewrite recommendation. Invalid, mechanical-only,
and not-evaluated results remain facts with their original limitations.

### Causal Hypothesis

A Causal Hypothesis is a tentative, falsifiable explanation for an Evaluation
Fact. Multiple alternatives must remain possible when the evidence does not
discriminate between them. For example, a source-positive and held-out-negative
pattern could indicate source-specific overfit, over-constraint, an environment
difference, or an evaluation defect. It must not be collapsed into a capability
truth without supporting evidence.

### Evolution Gradient

An Evolution Gradient is a bounded direction for the next evidence or design
step. Possible directions include:

```text
REPAIR_EVALUATION
COLLECT_MORE_EVIDENCE
PRESERVE_MECHANISM_AND_GENERALIZE
NARROW_TRIGGER
REMOVE_SOURCE_SPECIFICITY
REDUCE_CONSTRAINT
NO_CAPABILITY_CHANGE
REJECT_CANDIDATE
READY_FOR_HUMAN_DECIDE
```

The label is a recommendation, not an executed candidate update. It must point
back to the facts and hypotheses that support it, state uncertainty, and keep
the tested scope visible.

## Relationship To The Product Lifecycle

The canonical lifecycle remains:

```text
ADVISE -> REVIEW -> EVOLVE -> VALIDATE -> DECIDE
```

`WATCH` remains cross-cutting. Evolution Gradient is reasoning around this
lifecycle, not another box in it. In particular:

- `REVIEW` may produce a bounded intervention candidate, but not an Evolution
  Gradient that claims effectiveness;
- `EVOLVE` may create a non-active candidate only under its existing admission
  contract;
- `VALIDATE` produces scoped Evaluation Facts that may support a gradient;
- `DECIDE` remains Human-owned and is not implied by `READY_FOR_HUMAN_DECIDE`;
- no gradient can install, activate, promote, roll back, retire, or rewrite a
  capability.

Evaluation should not merely be the endpoint of capability evolution. It should
also become a learning signal for the next evolution cycle. Before automatic
learning is allowed, evaluation fact, causal hypothesis, and candidate update
must remain separate objects.

## Future Operators

The conceptual operator relationship is deliberately staged:

```text
Current:  Host-generated candidate
Next:     Darwin as an EVOLVE operator
Later:    SkillOpt-like persistent skill learning
```

Darwin, if separately authorized and implemented in the future, would be a
candidate search or optimization operator inside `EVOLVE`. It would not own
`REVIEW`, `VALIDATE`, `DECIDE`, or lifecycle authority. SkillOpt-like learning
would require repeated, provenance-preserving trajectories, Evaluation Facts,
competing hypotheses, Evolution Gradients, candidate updates, and held-out
validation. None of this is implemented by this document.

## Current Boundary

This document freezes vocabulary and separation only. It does not add a CLI
command, schema, score, automatic loop, telemetry system, Darwin integration,
SkillOpt integration, promotion rule, or new evidence claim. The current
utility round remains `NOT_EVALUATED_FOR_CANDIDATE_UTILITY`, and future native
held-out work requires a newly frozen task family, consistent Oracle, real Host
trajectories for both arms, and explicit Principal authorization.
