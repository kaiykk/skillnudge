# SkillNudge North Star

**Status: [FUTURE NORTH STAR]**

This document is the canonical high-level statement of the long-term
SkillNudge direction. It is intentionally separate from the frozen Week 1
contracts and implementation specification.

The labels in this document are part of the evidence discipline:

- `[FROZEN CURRENT DIRECTION]` means an accepted current product or scope
  boundary.
- `[WORKING HYPOTHESIS]` means a falsifiable SkillNudge research assumption.
- `[RESEARCH-BACKED DIRECTION]` means an external source supports the
  direction or makes it a credible research area. It does not prove a
  SkillNudge-specific claim.
- `[FUTURE]` means a later product or research direction, not current
  functionality.

## North Star

> SkillNudge decides when external capabilities actually help an agent,
> measures whether they improve downstream trajectories, and evolves or
> retires them as models and harnesses change.

This is future positioning, not a claim about the current Week 1 system.

## Core Thesis

SkillNudge is not fundamentally a Skill recommendation engine.

The deeper problem is that external agent capabilities are not permanently
useful. A Skill, prompt, workflow, integration, memory strategy, or other
harness capability has utility only relative to the current:

- base model;
- harness or runtime;
- task;
- task stage;
- environment;
- time and model generation.

The conceptual model is:

```text
Capability Utility =
f(capability, model, harness, task, task_stage, environment, time)
```

This is a conceptual model, not a mathematically validated equation or a V0
scoring formula.

The implication is that capability utility is non-stationary. A capability
that materially helps one generation of a model may later become redundant,
unnecessarily expensive, over-constraining, or actively harmful.

## [FROZEN CURRENT DIRECTION]

The current product boundary is a Capability Intervention Advisor:

```text
Capability Diagnosis
-> Intervention Selection
-> Candidate Acquisition
-> Evidence
-> Judge
-> Advice
```

Week 1 establishes observable control points for this loop. The current
accepted runtime still ends at the Week 1 sequence:

```text
Capability
-> Intervention
-> Candidate
-> Evidence
-> Judge
-> Advice
```

Week 1 does **not** implement the full North Star. In particular, Week 1 does
not implement Skill rewrite, Skill ablation, model-version comparison,
automatic compression, retirement, self-evolution, or trajectory
optimization.

The current product principle remains:

> Find the smallest intervention that meaningfully improves the next
> trajectory.

Zero intervention remains a valid result. Retrieval relevance is not the same
as intervention utility.

The frozen contracts and current implementation plan remain the source of
truth for Week 1:

- [`contracts/`](contracts/README.md)
- [`week1-implementation-spec.md`](week1-implementation-spec.md)
- [`runtime.md`](runtime.md)
- [`trace.md`](trace.md)

Understanding the North Star must not expand the Week 1 implementation
sequence.

## [WORKING HYPOTHESIS] Skill Utility Drift

**Skill Utility Drift** is the project concept that the usefulness of a Skill
can change even when the Skill itself does not change, because the base model,
harness, tool surface, task distribution, or environment changes.

Skill quality is not an intrinsic permanent property. Utility must be
evaluated in context.

One possible trajectory is:

```text
older model:
  the Skill produces substantial positive gain

newer model:
  the same Skill produces a small gain

later model:
  the same Skill increases steps, tool calls, or constraint errors
  and becomes net harmful
```

This is a central falsifiable hypothesis for SkillNudge. It has not been
empirically proven by SkillNudge.

The project does not hypothesize that all Skills will disappear as models
improve. Some Skills may remain structurally valuable:

1. **Private or organizational knowledge**
   - internal policies;
   - deployment rules;
   - company-specific workflows;
   - brand guidelines;
   - proprietary domain knowledge.

   Their value is not primarily caused by model weakness. The model simply
   does not possess the current private context.

2. **Normative or compliance behavior**
   - mandatory review checklists;
   - legal memo output contracts;
   - finance approval procedures;
   - organization-specific safety processes.

   The model may know how to perform a task, while the organization still
   requires a particular behavior.

3. **Tool-backed capability**

   A Skill may include scripts, resources, or executable procedures that create
   capability unavailable through reasoning alone.

4. **Rare or high-risk procedures**

   Even when the model can often solve a task unaided, an organization may
   prefer a fixed verified procedure because the error cost is high.

The Skills most exposed to model improvement are hypothesized to be
cognitive-scaffolding Skills, not all Skills equally.

## [WORKING HYPOTHESIS] Cognitive Scaffolding

Many current Skills may compensate for weaknesses of the current model through
reasoning scaffolds such as:

- fixed decomposition;
- forced planning steps;
- critique loops;
- repeated verification;
- prescribed search sequences;
- rigid reflection routines;
- fixed tool-use patterns.

These can be useful for weaker models. As base models improve, some scaffolds
may transition:

```text
helpful scaffold
-> redundant scaffold
-> harmful over-scaffolding
```

Possible harms include:

- unnecessary turns;
- unnecessary tool calls;
- context inflation;
- blocking a better strategy discovered by the model;
- forcing obsolete tool usage;
- slowing convergence;
- increasing latency or cost;
- increasing error probability.

The project does not claim that cognitive-scaffolding Skills decay faster.
That is a falsifiable research hypothesis.

## [WORKING HYPOTHESIS / FUTURE EVAL TAXONOMY]

The current proposed Skill Utility Drift taxonomy is:

1. **Redundancy Drift**

   The base model learns the behavior natively. The Skill adds context or
   latency without measurable gain.

2. **Over-constraint Drift**

   The Skill encodes a rigid strategy that prevents a stronger model from using
   a better strategy.

3. **Tool Misuse Drift**

   The Skill mandates a tool or call sequence that is no longer necessary or
   is inferior under the newer harness or tool ecosystem.

4. **Knowledge Staleness**

   Facts, APIs, procedures, policies, dependencies, or examples embedded in
   the Skill become obsolete.

5. **Harness Mismatch**

   The Skill was designed for an older agent loop, context model, tool surface,
   or runtime and behaves poorly under a newer harness.

This taxonomy is not a Week 1 implementation requirement.

## Three-Layer Project Model

### Layer 1 - Capability Control Plane

**Current / Week 1**

Question:

> When is an external capability worth considering at all?

Core runtime:

```text
Capability Diagnosis
-> Intervention Selection
-> Candidate Acquisition
-> Evidence
-> Judge
-> Advice
```

Week 1 exists to make these control points observable and reviewable.

### Layer 2 - Eval / Utility Layer

**Future Week 2-3 direction**

Transition memo: [`Phase 1 → Phase 2 bridge`](research/phase1-to-phase2-bridge.md)

Question:

> Did the intervention actually improve the downstream trajectory?

The central comparison is:

```text
Expected Effect
vs
Observed Effect
```

Possible measurements include:

- task success or correctness;
- trajectory quality;
- number of turns;
- tool calls and redundant calls;
- latency;
- tokens or cost;
- error type;
- constraint violations;
- user intervention;
- output quality;
- task-specific verified metrics.

Do not collapse these into a fake universal score before the measurement
problem is understood.

### Layer 3 - Capability Evolution Loop

**Future Week 4+ direction**

Question:

> If a capability is no longer optimal, how should it change?

Possible operations:

```text
KEEP
PRUNE
COMPRESS
REWRITE
SPLIT
MERGE
REPLACE
RETIRE
```

Every update must be evaluated before promotion.

## [FUTURE] Capability Lifecycle

The long-term lifecycle is:

```text
DISCOVER
identify a capability gap

-> INTERVENE
select Skill, Integration, or another capability

-> OBSERVE
collect trace, output, task result, and evaluator signals

-> DIAGNOSE
measure utility and identify the failure source

-> EVOLVE
keep, prune, compress, rewrite, split, merge, replace, or retire

-> EVALUATE
compare against controlled baselines

-> PROMOTE / ROLLBACK
```

This is a bounded, evaluation-driven improvement loop. It is not
unconstrained autonomous recursive self-improvement.

## [FUTURE] Evaluation Before Self-Evolution

No capability update should be promoted merely because an LLM rewrote it.

Future comparison should ideally include:

```text
A. No Skill / No Capability baseline
B. Current or Old Skill
C. Candidate evolved Skill
```

The conceptual promotion rule is:

> Promote only when the candidate demonstrates meaningful improvement without
> unacceptable regression.

No universal numeric threshold is defined yet.

## [FUTURE] Ablation-Based Capability Attribution

Evaluation should not treat a whole Skill as one indivisible cause. A Skill
may contain sections with different utility:

```text
Section A - planning scaffold
Section B - search procedure
Section C - verification
Section D - output contract
```

Future ablations may compare:

```text
Full Skill
Skill minus A
Skill minus B
Skill minus C
Skill minus D
No Skill
```

Measure success, tool calls, steps, latency, tokens, failure types, and
trajectory quality. The goal is to identify positive, neutral, redundant, or
negative contribution. This does not by itself establish causal certainty.

This research direction is called **ablation-based capability attribution**.

## [FUTURE] Evidence-Driven Skill Distillation

Skill distillation should not mean asking an LLM to summarize a 200-line Skill
into 50 lines.

The stronger goal is evidence-driven Skill compression:

- keep sections that still provide measured utility;
- remove sections that are redundant, harmful, stale, or over-constraining;
- re-evaluate the compressed Skill.

## [FUTURE] Model x Skill Co-Evolution

The same Skill must not be assumed to remain optimal across model generations.

One possible experiment is:

```text
Model A: No Skill vs Skill v1
Model B: No Skill vs Skill v1
Model C: No Skill vs Skill v1
```

Then derive and evaluate:

```text
Model C + No Skill
Model C + Skill v1
Model C + Skill v2
```

The harness and tool surface must be treated as explicit experimental
dimensions, not hidden constants.

## [FUTURE] Generalization and Anti-Overfitting

A self-evolving capability system must avoid optimizing only to the benchmark
used to evolve it. Future evaluation should consider:

- held-out validation;
- benchmark-disjoint evaluation where possible;
- unseen tasks;
- cross-domain transfer;
- cross-model transfer;
- multiple trajectories rather than one failure;
- successful and failed trajectory contrast;
- restricted and modular modification scope.

These are future evaluation requirements, not current implementation work.

## [FUTURE] What Counts as Self-Improvement

One-off reflection or retry inside a single task is not sufficient to call the
system self-improving.

The stronger SkillNudge definition requires:

```text
experience or evaluation signal
-> persistent update to a reusable capability
-> validated improvement on future tasks
```

This distinction matters for public positioning. Normal retry behavior should
not be casually labeled recursive self-improvement.

## [FUTURE] Illustrative Week 4 Demo

Consider an illustrative Skill named `deep-research-planning-v1` containing:

- fixed decomposition;
- fixed subqueries;
- mandatory repeated search;
- a verification checklist;
- an output structure.

Suppose a newer model produces:

```text
No Skill:
  good success, fewer steps

Old Skill:
  similar or worse success, more search calls,
  more turns, and more context usage
```

An ablation might show:

- fixed subquery decomposition: redundant or harmful;
- verification section: still positive;
- output contract: still positive.

SkillNudge could propose:

```text
deep-research-planning-v2
  remove fixed decomposition
  keep verification
  compress the output contract
```

It would then evaluate No Skill, v1, and v2 and promote v2 only if the
controlled comparison passes the future gate.

All numbers and outcomes in this section are illustrative. They are not
measured SkillNudge results.

## Why Week 1 Exists

Week 1 is not the final product thesis. It builds the capability control plane
needed for later evaluation and evolution.

Current artifacts establish:

```text
CapabilityContract
-> what capability is expected

InterventionPlan
-> what mechanism was selected

Query / Candidate / Evidence
-> what capability was considered

Judge
-> why it was worth using

Trace
-> what decisions occurred
```

Later layers can add `Observed Outcome`, allowing SkillNudge to compare
Expected Effect with Observed Effect.

Without the Week 1 control points and trace, a future evolution loop would
have no reliable attribution surface.

## Product Positioning

Weak positioning:

```text
Skill search engine
Skill recommendation engine
```

Better current positioning:

```text
Capability Intervention Advisor
```

Long-term positioning:

```text
Eval-driven Capability Lifecycle Layer for AI Agents
```

Alternative technical framing:

```text
Evolvable Agent Capability Layer
```

The long-term positioning is future positioning. The current Week 1
implementation does not provide all of these capabilities.

## Proposed Differentiation

**[WORKING DIFFERENTIATION]**

Existing work increasingly studies:

- evolving a known Skill;
- optimizing a harness;
- measuring persistent improvement;
- building evolving Skill libraries.

The proposed SkillNudge focus is the lifecycle decision around capability
intervention itself:

```text
Should a capability intervene now?
Did it actually help?
Has its utility drifted?
Which part still contributes?
Should it be compressed, adapted, replaced, or retired?
```

This is a proposed focus, not a claim that no other project studies these
questions.

## Future Data-Model Implication

Later layers will need to join:

```text
Expected capability
Intervention
Capability version
Model version
Harness version
Task or task family
Trajectory
Outcome or Eval
```

This is a future data-model requirement. Week 1 schemas and runtime are not
redesigned merely to satisfy the North Star.

## Portfolio Positioning

**[FUTURE / PORTFOLIO POSITIONING]**

The project should not be described primarily as:

> I built a Skill recommendation engine.

The problem-first narrative is:

> Agent ecosystems accumulate Skills, prompts, tools, and workflows, but
> their utility is not stationary. A workflow that helped an older model can
> become redundant or harmful as the base model and harness improve.

The future project pitch is:

> I built an eval-driven capability lifecycle layer for evolving agents. It
> decides when external capabilities are worth adding, observes their
> downstream effect, detects utility drift across models and harnesses, and
> uses evaluation-gated updates to compress, rewrite, replace, or retire stale
> capabilities.

This describes the future direction, not current production capability.

## Scope Guard

Understanding the North Star must not cause Week 1 scope expansion.

Until the complete Week 1 loop works, do not implement:

- Skill rewrite;
- Skill ablation;
- model-version testing;
- automatic compression;
- Skill retirement;
- self-evolution;
- trajectory optimization;
- Review, Grow, or Watch.
