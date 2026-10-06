# SkillNudge Agent Invariants

## Eval -> Evolve

Freeze protects against premature drift; evolution protects against frozen
mistakes.

Classify evaluation failure before changing direction:

```text
IMPLEMENTATION_FAILURE -> repair inside the current frame
MODEL_ASSUMPTION_FAILURE -> bounded model repair
FRAME_CONTRADICTION -> FRAME_REOPEN_CANDIDATE
```

A frame-reopen candidate may be triggered by new Human Principal intent, new
upstream or prior-art evidence, or evidence that a frozen assumption blocks the
North Star. Agents may propose reopening but may not silently reinterpret a
frozen rule. Only the Human Principal may amend or supersede a frozen frame.
Every amendment records the trigger, old rule, new rule, evidence, unchanged
boundaries, and Principal authority. After ratification, version and freeze the
frame again, then resume the interrupted work.

## Upstream-First

Before experimentally rediscovering semantics owned by an existing source,
read the canonical contract and mature prior art, perform the local
compatibility check, and search only unresolved gaps.

## Authority Boundary

The Human Principal owns goals, frozen invariants, evidence semantics, and
lifecycle authority. Agents may autonomously perform bounded hypothesis
search, experiment selection, evidence accumulation, pruning, and stopping
inside the frozen frame.

## Evidence Roles

Designed diagnostic probes may support or falsify a mechanism.
They must never be promoted into natural utility or generalization evidence.

## Autonomous Evolution Baseline

The default control model is defined in
`docs/autonomous-evolution-baseline-v0.md`.

Bounded autonomous search may continue without Principal review while it
remains inside the frozen frame. Suspended uncertainty may be persisted and
later reactivated by qualifying evidence, but reactivation is not a utility
claim or lifecycle mutation.
