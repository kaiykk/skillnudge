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
`WATCH` loads one open need and one later host-observed experience, exposes the
persisted `unresolved_question` and `interesting_future_event` to the Host,
then emits exactly one of `IGNORE`, `WAKE`, or `INSUFFICIENT`. The core checks
that this context is unchanged; it does not perform semantic text matching.

On `WAKE`, the provider-free core also persists a minimal reactivation context
for the Host. It contains the exact Need identity and subject, the unresolved
question, the persisted wake condition, the Need's source evidence references,
the new wake evidence references, and the observed execution context. This is
a bounded handoff for continuing evidence work; it is not an answer to the
question and does not run Review, Validate, Evolve, Darwin, SkillOpt,
promotion, or any lifecycle mutation. `IGNORE` and `INSUFFICIENT` do not create
this context. The host remains the semantic authority; SkillNudge validates
identity, the exact persisted condition context, evidence references, scope,
persistence, and the bounded result.

The resumed Host can submit exactly one bounded continuation envelope through
`watch continue --stdin --reactivation-file`. SkillNudge validates the persisted
WAKE context, records the Host action and observable evidence, and persists the
new record under the original Need. The Need remains `OPEN`; this is evidence
continuity, not automatic Review, Validate, resolution, promotion, or lifecycle
mutation.

This slice is provider-free and supports one persisted need plus later
matching and one bounded continuation evidence record. It is not a daemon, scheduler, generic event bus, registry,
cross-session aggregation service, utility scorer, or autonomous evolution
loop.
