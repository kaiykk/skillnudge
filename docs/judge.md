# Candidate Judge

## Status

- `[FROZEN]` The Judge target is intervention utility estimation, not simple
  semantic similarity.
- `[WORKING HYPOTHESIS]` Fit, stage, type, compatibility, trust, and friction
  are the minimum useful judgement dimensions.
- `[WORKING HYPOTHESIS]` A complex numeric score is not required to validate
  the first product loop.
- `[FUTURE]` Learned ranking, model-aware utility measurement, and automatic
  post-use review.

This document defines a product responsibility. It does not implement a Judge
or freeze its final schema.

## Core Question

> Is this intervention worth adding at this point in the user's task?

Retrieval asks whether a candidate is worth inspecting. The Judge asks whether
the intervention is worth using. Those are different decisions:

```text
retrieval relevance ≠ usable intervention
```

## Dimensions

### Capability Fit

Does the candidate address the capability that the user is actually missing,
rather than merely sharing words with the request?

### Stage Fit

Is this intervention appropriate now? A structured workflow may be valuable
after requirements stabilize and premature while the user is still exploring.

### Intervention Type Fit

Is the problem best served by a Skill, Plugin, Tool, Companion Resource, or no
intervention? A SkillNudge result must be allowed to reject Skill as a class.

### Compatibility

Can the candidate work with the relevant host, model, project, operating
environment, and runtime constraints?

### Trust

Can the candidate's identity, source, maintenance, license, and behavior be
verified? Trust is evidence quality, not popularity.

### Friction

How much setup, context, workflow ownership, instruction load, and behavioral
intrusion does the intervention introduce?

## Fit Is Not Trust

A candidate can have high capability fit and low trust because its source or
behavior is poorly documented. A candidate can have high trust and low fit
because it is maintained and popular but solves the wrong problem. The final
advice must preserve both facts rather than compressing them into one opaque
quality label.

## Friction Changes the Bar

The more invasive an intervention is, the stronger its utility evidence should
be. A large workflow Skill may fit the capability but still be a poor first
choice if a small prompt, Plugin, or direct answer would address the same
blockage with less context and setup.

## Outcomes

The Judge should be able to support:

- recommendation;
- rejection with a reason;
- no intervention;
- insufficient evidence;
- clarification before judgement.

These are product-level outcomes, not currently implemented statuses.

## Evidence Discipline

The Judge should prefer full candidate evidence over a title or search snippet.
Star count is not a quality proxy. A low-star candidate may be the best fit with
limited external evidence; that should be reported as high fit with uncertain
trust, not silently discarded or promoted.

## Open Design Boundary

The following remain open:

- whether a numeric score is useful;
- exact dimension weighting;
- rejection thresholds;
- how to compare different intervention classes;
- how post-use utility should update future judgement.

See [`open-questions.md`](open-questions.md).
