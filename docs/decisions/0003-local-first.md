# Decision 0003: Local-First Acquisition

## Status

`[FROZEN]`

## Decision

Check local evidence and coverage first. Use bounded live discovery only when
local evidence is insufficient or the Intervention Plan points to a live-only
surface.

## Context

Unbounded live search increases latency, source drift, rate-limit exposure, and
difficulty reproducing a recommendation. A local corpus also makes provenance
and failure decomposition possible.

## Consequences

Local corpus is a default source, not the whole world. Candidate lifecycle must
distinguish stable catalog, validated cache, and current-run results.

## Revisit When

Revisit when local coverage or refresh cost makes the boundary impractical for
the product's actual source universe.
