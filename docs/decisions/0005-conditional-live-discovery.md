# Decision 0005: Conditional Live Discovery

## Status

`[FROZEN]`

## Decision

Use live discovery only after local coverage/evidence is judged insufficient, or
when a Tool or other surface requires targeted live lookup. Limit the search to
2-3 complementary queries and hydrate only a small number of results.

## Context

GitHub live code search was not a stable universal Skill index in the D001
probe. The failure pointed to source coverage and indexing, not automatically
to a BM25 or capability-framing failure.

## Consequences

Live results remain current-run evidence until provenance, license, identity,
and freshness justify a higher cache level. SkillNudge does not build a massive
ToolHub or PluginHub in V0.

## Revisit When

Revisit when a stable authoritative source and an evidence-backed refresh
policy become available.
