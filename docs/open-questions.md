# Open Design Questions

## Status

These are intentionally unresolved `[WORKING HYPOTHESIS]` boundaries. They
should be answered by narrow experiments or explicit product decisions, not by
accidentally hardcoding a plausible default.

## Questions

### Q1 — CapabilityContract

What is the smallest set of fields that preserves the user's original
expression, missing capability, uncertainty, task stage, and desired outcome?

### Q2 — InterventionPlan

How should Skill, Plugin, Tool, Resource, and No intervention search budgets be
allocated without turning a soft plan into a hard route?

### Q3 — Live Discovery Trigger

When is local evidence or source coverage insufficient enough to justify live
discovery, network cost, and freshness uncertainty?

### Q4 — Judge Score

Does a numeric score improve decisions and reviewability, or does an explicit
dimension table with reasons work better for V0?

### Q5 — Fit, Trust, and Friction

How should these dimensions be compared across intervention classes without
pretending they are commensurable quality units?

### Q6 — BM25 Weighting

How should name, description, tags, body, compatibility, and source fields be
weighted in the first local index?

### Q7 — Corpus Snapshot

Which local Skill corpus snapshot can be licensed, reproduced, and inspected
for the first implementation?

### Q8 — Plugin Refresh

What source and refresh cadence can provide authoritative Plugin metadata
without building a new marketplace?

### Q9 — Tool Search Provider

Which targeted live-search provider is reliable enough for bounded Tool
discovery under local-first constraints?

### Q10 — Model-Aware Utility

How can future Review and Watch compare intervention utility across model,
project, task-stage, and time changes without overclaiming causal evidence?

## Design Rule

Until these questions are answered, documents should describe a direction as
`planned`, `proposed`, or `future`. They must not be silently converted into
implementation contracts.
