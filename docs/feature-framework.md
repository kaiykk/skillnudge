# Feature Framework

## Status

- `[FROZEN]` Advise is the only Week 1 / V0 capability.
- `[WORKING HYPOTHESIS]` The following responsibility boundaries make failures
  diagnosable without committing to a final implementation architecture.
- `[FUTURE]` Review, Grow, and Watch.

## Responsibility Matrix

| Feature | Goal | Input | Output | Success condition | Failure mode | Week 1 status |
| --- | --- | --- | --- | --- | --- | --- |
| Capability Framing | Identify the missing capability | Raw request and context | CapabilityContract | Captures the blockage without prescribing a known solution | Semantic drift, solution bias, over-interpretation | Planned core |
| Intervention Planning | Allocate search attention across surfaces | CapabilityContract and context | InterventionPlan | Keeps Skill, Plugin, Tool, Resource, and None available when justified | Hard routing, Skill-first bias, budget blindness | Planned core |
| Query Planning | Express the capability through complementary formulations | CapabilityContract | 3-5 queries | Covers capability, outcome, operation, vocabulary, or stage without domain hardcode | Paraphrase spam, missing vocabulary, query leakage | Planned core |
| Candidate Acquisition | Build a bounded pool of inspectable candidates | QueryPlan and source policy | CandidatePool | Returns diverse, traceable candidates without pretending to be final advice | Coverage gap, live-source drift, duplicate candidates | Planned core |
| Evidence Hydration | Turn shallow hits into judgeable evidence | CandidatePool | Evidence packages | Candidate body, provenance, compatibility, license, and freshness are inspectable | Snippet overconfidence, stale or incomplete evidence | Planned core |
| Candidate Judge | Estimate intervention utility | Evidence packages and task context | Judgements and rejection reasons | Separates fit, trust, friction, and stage rather than using relevance alone | Popularity proxy, opaque score, type mismatch | Planned core |
| Final Advice | Give small, explainable next-step guidance | Judgements and uncertainty | 0-2 recommendations or explicit status | The advice is useful now and communicates uncertainty | Recommendation spam, false certainty, forced intervention | Planned core |
| Trace | Preserve explicit artifacts for review | Inputs and all runtime boundaries | Readable run record | A failure can be localized without private chain-of-thought | Missing artifact, sensitive data leakage, narrative bias | Planned core |
| Review | Measure post-use utility | Trace, trajectory, outcome signals | Utility review and failure attribution | Separates selection, trigger, timing, execution, and outcome | Confuses Skill quality with one failed use | Future |
| Grow | Propose evidence-backed revision | Review evidence and source intervention | Local Variant or revision proposal | Improves utility with user approval and bounded replay | Instruction bloat, unapproved mutation, weak eval | Future |
| Watch | Detect meaningful freshness or utility change | Versions, model changes, Review history | Re-evaluation or lifecycle suggestion | Surfaces drift without silently changing behavior | Alert noise, automatic retirement, stale baselines | Future |

## Scope Note

The matrix describes responsibilities and validation targets. It does not imply
that all rows already have code, schemas, adapters, or benchmark results.
