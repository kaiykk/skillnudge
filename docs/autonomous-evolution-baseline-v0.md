# SkillNudge Autonomous Evolution Baseline v0

**FROZEN ARCHITECTURAL BASELINE**

**NOT A NEW LIFECYCLE**

This baseline preserves the current North Star while making suspended
uncertainty explicit.

```text
Human Principal
  owns goal, invariants, evidence semantics, lifecycle authority
        |
   Frozen Frame
        |
   Agent system: bounded search, experiment selection, evidence accumulation,
   frontier management, pruning, stopping
        |
Evaluation Facts -> Mechanism / Hypothesis -> Evolution Gradient -> Next Action
                                                        /      |      \
                                                     WATCH   EVOLVE   DECIDE
                                                       |
                                             future qualifying evidence
                                                       |
                                                      WAKE
```

The Principal owns the frame and lifecycle decisions. The Agent may search and
accumulate evidence only inside that frame. Complex internal loops are system
complexity; they must not become required user complexity.

An Agent should know when to continue learning, when to stop, why it stopped,
and what future evidence would justify learning again. Freeze protects against
premature drift; Evolution protects against frozen mistakes.

## Bounded WATCH slice

An `Evidence Need` is one persisted `OPEN` unresolved question. It is not a
capability gap, utility result, candidate, promotion state, or lifecycle stage.
`WATCH` loads one open need and one later host-observed experience, then emits
exactly one of `IGNORE`, `WAKE`, or `INSUFFICIENT`.

`WAKE` is only a persisted receipt. It does not run Review, Validate, Evolve,
Darwin, SkillOpt, promotion, or any lifecycle mutation. The host remains the
semantic authority; SkillNudge validates identity, evidence references,
scope, persistence, and the bounded result.

This slice is provider-free and supports one persisted need plus later
matching. It is not a daemon, scheduler, generic event bus, registry,
cross-session aggregation service, utility scorer, or autonomous evolution
loop.
