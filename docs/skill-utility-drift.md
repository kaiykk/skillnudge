# Skill Utility Drift

**Status: [FUTURE RESEARCH HYPOTHESIS]**

This is the deeper research document for the long-term SkillNudge direction.
It supports [`docs/north-star.md`](../north-star.md) and does not change the
frozen Week 1 contracts or implementation sequence.

## Motivation

The static text of a Skill is not the same thing as its utility. A Skill may
help because the current model lacks a behavior, because the harness lacks a
workflow boundary, because the task requires private knowledge, or because the
organization requires a normative procedure.

As the model, harness, tool surface, task distribution, or environment changes,
the same unchanged Skill may have a different effect.

This motivates the conceptual model:

```text
Capability Utility =
f(capability, model, harness, task, task_stage, environment, time)
```

This is not an implemented detector, score, or mathematically validated
equation.

## Definition

**Skill Utility Drift** is the change in a Skill's usefulness even when the
Skill itself does not change, because the surrounding agent system changes.

Conceptual trajectory:

```text
older model:
  substantial positive gain

newer model:
  small or redundant gain

later model or harness:
  more steps, tool calls, or constraint errors
  and net negative utility
```

Skill quality is therefore not an intrinsic permanent property. Utility must be
evaluated in context.

SkillNudge does not claim that this phenomenon has already been empirically
proven by this repository.

## Durable Skill Categories

The project does not hypothesize that all Skills disappear as models improve.
The following categories may remain structurally valuable:

1. **Private or organizational knowledge**
   - internal policies;
   - deployment rules;
   - company workflows;
   - brand guidelines;
   - proprietary domain knowledge.

2. **Normative or compliance behavior**
   - mandatory review checklists;
   - legal memo contracts;
   - finance approval procedures;
   - organization-specific safety processes.

3. **Tool-backed capability**

   Scripts, resources, or executable procedures may create capability that
   reasoning alone cannot provide.

4. **Rare or high-risk procedures**

   A fixed verified procedure may remain preferable when the cost of error is
   high, even if unaided success is often possible.

The categories most exposed to model improvement are hypothesized to be
cognitive-scaffolding Skills, not all Skills equally.

## Cognitive Scaffolding Hypothesis

Many Skills may currently compensate for model limitations with:

- fixed decomposition;
- forced planning;
- critique loops;
- repeated verification;
- prescribed search sequences;
- rigid reflection routines;
- fixed tool-use patterns.

The central hypothesis is:

```text
helpful scaffold
-> redundant scaffold
-> harmful over-scaffolding
```

Possible harm includes extra turns, unnecessary tool calls, context inflation,
blocked model strategies, obsolete tool usage, slower convergence, higher
latency or cost, and increased error probability.

This is a falsifiable hypothesis. It is not a claim that cognitive scaffolds
are already known to decay faster.

## Falsifiable Hypotheses

### H1 - Differential Drift

Cognitive-scaffolding Skills will show larger utility decay across stronger
model generations than private-knowledge or normative Skills.

### H2 - Section-Level Drift

Some Skill sections will become redundant or harmful before the whole Skill
becomes net harmful.

### H3 - Granularity Drift

Model upgrades can change the optimal Skill granularity.

### H4 - Evidence-Driven Compression

A compressed Skill can outperform both the old Skill and the no-Skill baseline
when obsolete scaffolding is removed while high-value constraints are retained.

### H5 - Harness Dependence

Skill utility depends jointly on model and harness. A Skill may regress after a
harness or tool-surface change even when the model does not change.

These hypotheses require controlled evaluations and should remain separate from
confirmed facts.

## Drift Taxonomy

**[WORKING HYPOTHESIS / FUTURE EVAL TAXONOMY]**

1. **Redundancy Drift** - the base model learns the behavior natively.
2. **Over-constraint Drift** - a rigid strategy prevents a better model
   strategy.
3. **Tool Misuse Drift** - a mandated tool or call sequence becomes
   unnecessary or inferior.
4. **Knowledge Staleness** - facts, APIs, procedures, policies, dependencies,
   or examples become obsolete.
5. **Harness Mismatch** - the Skill assumes an older loop, context model, tool
   surface, or runtime.

The taxonomy is a research classification, not a Week 1 requirement.

## Evaluation Matrix

Future evaluation should keep the following dimensions explicit:

| Dimension | Comparison |
|---|---|
| Capability baseline | No Skill / No Capability vs current Skill |
| Evolution candidate | No Skill vs old Skill vs candidate Skill |
| Model | Same Skill across Model A, B, and C |
| Harness | Same model and Skill across harness/tool-surface versions |
| Task | Repeated task families plus unseen tasks |
| Stage | Early exploration, execution, verification, maintenance |
| Outcome | Success, correctness, quality, constraint compliance |
| Cost | Turns, tool calls, latency, tokens, and monetary cost |
| Failure | Error type, redundant action, harmful constraint, stale knowledge |

Possible measurements are not a universal score. They include task success,
trajectory quality, turns, tool calls, redundant calls, latency, tokens/cost,
error types, constraint violations, user intervention, output quality, and
task-specific verified metrics.

## Attribution and Ablation

A Skill should not be treated as one indivisible cause. A future experiment
may split it into:

```text
Section A - planning scaffold
Section B - search procedure
Section C - verification
Section D - output contract
```

Compare:

```text
Full Skill
Skill minus A
Skill minus B
Skill minus C
Skill minus D
No Skill
```

Measure success, tool calls, steps, latency, tokens, failure types, and
trajectory quality. This is **ablation-based capability attribution**. It can
localize contribution, but it does not automatically prove causal certainty.

## Model-Version Experiments

The same Skill should not be assumed optimal across model generations:

```text
Model A: No Skill vs Skill v1
Model B: No Skill vs Skill v1
Model C: No Skill vs Skill v1
```

For a later candidate:

```text
Model C + No Skill
Model C + Skill v1
Model C + Skill v2
```

Model version, harness version, tool surface, task family, Skill version, and
evaluation set must be recorded together.

## Evolution Operators

Future evolution may propose:

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

Distillation must not mean merely summarizing a long Skill. It should mean
keeping measured-utility sections, removing redundant or harmful sections, and
re-evaluating the resulting artifact.

## Promotion and Rollback Gates

No update should be promoted merely because an LLM proposed or rewrote it.

Future promotion should require:

1. a named baseline;
2. a candidate artifact with version and provenance;
3. a controlled evaluation;
4. held-out validation where possible;
5. no unacceptable regression on protected cases;
6. recorded failure and cost signals;
7. an explicit human or policy decision to promote.

The system should support rollback to the previous accepted artifact when a
later evaluation, harness change, or production observation reveals regression.

No universal numeric threshold is defined yet.

## Generalization and Anti-Overfitting

Evolution must not optimize only to the same benchmark that produced the
candidate. Future evaluation should consider:

- held-out validation;
- benchmark-disjoint evolution tasks;
- unseen tasks;
- cross-domain transfer;
- cross-model transfer;
- multiple trajectories rather than one failure;
- successful and failed trajectory contrast;
- restricted and modular modification scope.

One-off reflection or retry inside one task is not self-improvement under the
stronger SkillNudge definition. The stronger definition is:

```text
experience or evaluation signal
-> persistent reusable capability update
-> validated improvement on future tasks
```

## Future Lifecycle

```text
DISCOVER
-> INTERVENE
-> OBSERVE
-> DIAGNOSE
-> EVOLVE
-> EVALUATE
-> PROMOTE / ROLLBACK
```

This is bounded capability management, not unconstrained autonomous RSI.

## Open Questions

- How should private knowledge be evaluated without exposing sensitive data?
- Which outcome metrics remain reliable across domains?
- How many trajectories are needed before a drift diagnosis is credible?
- How should utility be compared when the task distribution itself changes?
- Which sections can be safely ablated without changing the Skill interface?
- How should harness and tool-surface changes be isolated from model changes?
- What is an acceptable regression budget for high-risk procedures?
- When should a Skill be retired versus narrowed or progressively disclosed?

## Week 1 Boundary

Week 1 does not implement drift detection, Review, Grow, Watch, Skill rewrite,
ablation, model-version experiments, compression, retirement, self-evolution,
or trajectory optimization. It establishes the control points and Trace needed
for later evaluation.
