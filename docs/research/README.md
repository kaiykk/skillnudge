# Research Track

## Status

- `[FROZEN]` Product Track has priority over Research Track for V0.
- `[HISTORICAL EVIDENCE]` Prior retrieval and source experiments shaped the
  current local-first boundary.
- `[FUTURE]` Dedicated retrieval benchmarks, model-aware utility evaluation,
  and semantic retrieval comparisons.

Canonical long-term thesis: [`../north-star.md`](../north-star.md).
Canonical North Star bibliography: [`north-star-references.md`](north-star-references.md).

## Two Tracks

### Product Track

The Product Track asks whether a lightweight Capability Intervention Advisor can
complete the loop:

```text
Input
→ Capability
→ Intervention
→ Query
→ Candidate Acquisition
→ Evidence
→ Judge
→ Advice
```

Its first job is to validate product usefulness and diagnosable runtime
contracts on a normal developer laptop.

### Research Track

The Research Track may later study:

- BM25 versus dense retrieval;
- query expansion and query fusion;
- hybrid retrieval;
- retriever benchmarks;
- Skill utility measurement;
- model and source drift.

Research work must preserve source, version, license, and evaluation boundaries.
It must not turn a paper claim or a public README into a confirmed product
capability.

## Priority Rule

Product Track comes first. Existing research and open-source projects can
justify keeping V0 lightweight, but they do not remove the need to validate the
SkillNudge product loop. Research Track should not block V0 unless it reveals a
route-changing source or safety constraint.

## Evidence Placement

Future source snapshots, papers, issues, and trace references belong under
`research/` or an explicitly linked local evidence location. Do not download a
large corpus as part of docs-only work.
