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
