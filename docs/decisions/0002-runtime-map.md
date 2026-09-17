# Decision 0002: Runtime Map

## Status

`[FROZEN]`

## Decision

V0 uses eight explicit layers:

```text
Intake / Context
→ Capability Framing
→ Intervention Planning
→ Query Planning
→ Candidate Acquisition
→ Evidence Hydration
→ Candidate Judgement
→ Final Advice
```

Trace crosses the complete flow.

## Context

Without boundaries, a single prompt can mix understanding, retrieval, judgement,
and expression into an unreviewable result.

## Consequences

Each layer needs explicit input, output, uncertainty, and failure boundaries.
Candidate Acquisition does not directly produce Final Advice.

## Revisit When

Revisit only if a bounded experiment shows that the diagnostic value is lower
than the cost of recording the intermediate artifacts.
