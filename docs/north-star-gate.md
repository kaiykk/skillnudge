# SkillNudge North Star Gate v0.1

**Status:** MANDATORY REVIEW FRAMEWORK FOR PHASE 2+
**Date:** 2026-09-19
**Scope:** Documentation-only design gate

This document is the mandatory review framework for future SkillNudge Phase 2+
research, experiments, implementation proposals, and architecture changes.

It does not modify Phase 1 runtime behavior, existing contracts, retrieval,
Planning, Judge, CLI behavior, or the Phase 2 experiment implementation.

---

## 1. Purpose

SkillNudge is a **Capability Lifecycle Evaluation System**.

It is not optimizing for:

- finding the most popular Skill;
- maximizing a benchmark score without understanding the intervention;
- recommending more capabilities;
- keeping every capability that was once useful;
- treating retrieval relevance as proof of utility.

The core research question is:

> When should an external capability intervention exist?

The word `exist` is intentionally broader than `be recommended`. It includes:

- whether the capability should be introduced;
- whether it should remain active;
- whether only part of it should remain;
- whether it should be modified or replaced;
- whether it should be removed or retired;
- whether its decision should be conditional on model, harness, task, stage,
  or environment.

An external capability intervention may be a Skill, Integration, Resource,
tool procedure, workflow, memory strategy, or another bounded addition to an
agent trajectory. Skills are one intervention type, not the permanent center
of the product definition.

### The central distinction

The following statements are different:

```text
The capability is relevant.
The capability is retrievable.
The capability is recommended.
The capability was used.
The capability improved the trajectory.
The capability should remain in the system.
```

Only the last two are lifecycle utility questions, and they require observed
trajectory and outcome evidence. A proposal that stops at relevance,
retrieval, or recommendation has not yet demonstrated lifecycle value.

### Phase boundary

Phase 1 established the control-plane path:

```text
Capability Discovery
-> Intervention Planning
-> Candidate Acquisition
-> Candidate Evaluation
```

Phase 2 studies whether an intervention changed the downstream trajectory.
This gate prevents Phase 2 and later work from silently collapsing back into
Skill search, Skill ranking, Skill recommendation, or benchmark optimization
without a lifecycle decision.

---

## 2. Capability Lifecycle Model

The lifecycle is:

```text
DISCOVER
    |
    v
INTERVENE
    |
    v
OBSERVE
    |
    v
DIAGNOSE
    |
    v
EVOLVE
    |
    v
PROMOTE / ROLLBACK / RETIRE
```

`EVALUATE` is a cross-cutting evidence function in this gate. It is applied to
the observed outcome and diagnosis before an evolution or promotion decision;
it is not a reason to skip the lifecycle stages above.

### DISCOVER

**Question it answers:**

> Is there a capability gap, intervention opportunity, or recurring failure
> worth investigating?

**Evidence it produces:**

- the user or task context;
- the observed blockage or failure;
- the capability that appears to be missing or insufficient;
- uncertainty about whether an external intervention is needed;
- the boundary between a real capability gap and a project fact, environment
  failure, or agent lapse.

**Lifecycle contribution:**

Discovery defines what future intervention decision is being made. It prevents
the system from treating every request as a reason to search for or attach a
Skill.

Discovery evidence is not proof that a candidate capability is useful.

### INTERVENE

**Question it answers:**

> Should an external capability be inserted into this trajectory, and what
> intervention class is being considered?

**Evidence it produces:**

- the selected intervention type and version;
- the intervention insertion boundary;
- the control and treatment conditions;
- the expected effect;
- the conditions under which intervention should not occur;
- any relevant task, stage, model, harness, or environment scope.

**Lifecycle contribution:**

Intervention turns a capability hypothesis into a testable treatment. It makes
clear what changed between the control trajectory and the treatment trajectory.

An intervention decision must not be treated as a successful outcome merely
because the selected capability is plausible or popular.

### OBSERVE

**Question it answers:**

> What actually happened after the intervention was inserted?

**Evidence it produces:**

- the complete or sufficiently reconstructable trajectory;
- actions and tool calls;
- intermediate and final outputs;
- verification behavior;
- task outcome;
- latency, turns, tokens, cost, and other declared process measures;
- user corrections or human interventions;
- protocol deviations and environment failures.

**Lifecycle contribution:**

Observation creates the evidence boundary between expected utility and
observed utility. Without it, later keep, modify, or retire decisions are
based on intention rather than behavior.

### DIAGNOSE

**Question it answers:**

> Why did the intervention succeed, fail, remain neutral, or create harm?

**Evidence it produces:**

- the difference between control and treatment trajectories;
- failure mode and error type;
- useful, redundant, restrictive, stale, or misapplied sections;
- whether the intervention changed task correctness, cost, or safety;
- whether the result was caused by the capability, the model, the harness,
  the environment, or an invalid task;
- uncertainty and alternative explanations.

**Lifecycle contribution:**

Diagnosis prevents a raw success rate from becoming an unjustified rewrite.
It identifies whether the next lifecycle action should be keep, compress,
modify, replace, retire, or collect better evidence.

### EVOLVE

**Question it answers:**

> Given the evidence, what bounded change to the intervention is justified?

**Evidence it produces:**

- the proposed versioned change;
- the specific observation or diagnosis motivating it;
- preserved behavior;
- intentionally removed or changed behavior;
- expected benefit and possible regression;
- development evidence used to form the proposal;
- the held-out evidence required before promotion.

**Lifecycle contribution:**

Evolution converts diagnosis into a reversible candidate. It must not be an
unconstrained LLM rewrite or a response to one attractive example.

Evolution is optional. A valid result may be to keep the current intervention,
leave it unchanged, or retire it.

### PROMOTE / ROLLBACK / RETIRE

**Question it answers:**

> Should this intervention version remain active, be reverted, or be removed
> from the execution path?

**Evidence it produces:**

- comparison against the named baseline;
- held-out or future-task behavior;
- protected-case and regression results;
- version and provenance;
- scope of validity;
- rollback path;
- known conditions where the decision does not apply.

**Lifecycle contribution:**

This is the lifecycle control point. It turns evaluation into an operational
decision while preserving reversibility and preventing accidental permanent
adoption.

Promotion is not a reward for a good-looking proposal. Retirement is not a
claim that the capability is globally useless. Both decisions are scoped to
the model, harness, task family, stage, environment, and evidence window that
was actually tested.

---

## 3. North Star Decision Gate

Every future Phase 2+ proposal, experiment, implementation, or architecture
change must answer all five questions below.

An answer may be `unknown` while research is still exploratory, but the
unknown must be explicit and the proposal must explain how it will be
resolved. An unanswered question is not an implicit pass.

### Q1. Lifecycle Alignment

**Which lifecycle stage does this work belong to?**

Allowed examples:

- `DISCOVER`
- `INTERVENE`
- `OBSERVE`
- `DIAGNOSE`
- `EVOLVE`

If the work spans stages, name the primary stage and list the supporting
stages. Do not describe a proposal only as "improving SkillNudge" or "improving
search."

The answer must explain:

- the lifecycle question being answered;
- why this stage is the correct ownership boundary;
- which adjacent stage is explicitly out of scope.

### Q2. Capability Decision Evidence

**Does this work produce evidence that helps decide whether to:**

- keep a capability;
- compress a capability;
- modify a capability;
- replace a capability;
- retire a capability?

If no, explain why the work is necessary and how it connects to a later
lifecycle decision. Work that produces only a list of Skills, relevance scores,
or benchmark rankings is not sufficient by itself.

The evidence should identify the decision grain. Examples:

```text
This experiment can decide whether the Original Skill should remain active
for this model and debugging task family.

This trace analysis can decide whether the verification section should be
preserved while the fixed search procedure is compressed.

This source investigation can decide whether a candidate is eligible for a
later intervention trial, but cannot decide utility by itself.
```

### Q3. Baseline Definition

**Does this work compare a control against an intervention?**

```text
Control:
  Agent without external capability

Treatment:
  Agent with external capability
```

The proposal must state:

- what the control actually receives;
- what the treatment adds or changes;
- which model, harness, tools, task, environment, and evaluator are held
  constant;
- what outcome is being compared;
- how protocol deviations are handled.

If the work does not use this baseline, explain why. Acceptable explanations
may include:

- a source-provenance or artifact-integrity study that precedes an
  intervention trial;
- an observation-only diagnostic that does not claim utility;
- a lifecycle migration or rollback operation whose causal comparison already
  exists in a prior evidence set.

The exception must not be used to turn a recommendation or popularity result
into a utility claim.

### Q4. Trajectory Visibility

**Does this work help understand why the intervention succeeded or failed?**

Relevant visibility may include:

- action sequence;
- tool usage;
- reasoning pattern as represented by observable agent actions and artifacts;
- verification behavior;
- user correction;
- retry or recovery behavior;
- failure mode;
- constraint violation;
- unnecessary step, call, or context;
- interaction between capability, model, harness, and environment.

A final answer or aggregate score alone is insufficient when it cannot support
diagnosis. If full trajectory capture is impossible, the proposal must state
the reduced observation boundary and the resulting limitation.

### Q5. Evolution Implication

**If the experiment succeeds or fails, what future action does it enable?**

Examples:

- routing policy;
- conditional intervention;
- Skill compression;
- Skill rewrite;
- replacement with another capability type;
- intervention retirement;
- rollback to a prior accepted version;
- preserve the current intervention because no change is justified.

The answer must be conditional rather than rhetorical:

```text
If success improves with no unacceptable cost, keep the intervention within
the tested scope.

If success is unchanged but the intervention adds steps, compress the
identified redundant section and re-evaluate on held-out tasks.

If the intervention causes replicated regressions, retire or replace it unless
protected-case evidence requires a narrower conditional policy.
```

---

## 4. Anti-patterns

The following patterns fail the North Star Gate unless they are explicitly
reframed as a bounded prerequisite for a lifecycle decision.

### Anti-pattern 1: Find the most popular Skill

**Why wrong:**

Popularity is not utility. Stars, downloads, registry position, or community
activity do not show that the capability improves an agent trajectory or
should remain installed.

**What would make it admissible:**

Use popularity only to form a candidate set or study ecosystem exposure, then
run a controlled intervention comparison with observable outcomes.

### Anti-pattern 2: Build a larger Skill marketplace

**Why wrong:**

A larger catalog, installer, or marketplace does not answer whether a capability
should exist, whether it helped, or whether it should be retired.

**What would make it admissible:**

Treat acquisition as a bounded input to an intervention experiment and state
which later keep, modify, replace, or retire decision the acquisition work
enables.

### Anti-pattern 3: Optimize benchmark score only

**Why wrong:**

A higher benchmark score does not explain the intervention mechanism. It may
hide extra turns, tool calls, latency, cost, regressions, over-constraint, or
failure on unseen tasks.

**What would make it admissible:**

Use task success as one primary outcome alongside trajectory visibility,
guard metrics, cost, failure categories, and a named lifecycle decision.

### Anti-pattern 4: Generate a new Skill automatically

**Why wrong:**

Generation is not evidence-driven evolution. An automatically produced Skill
has no lifecycle value until its provenance, expected behavior, controlled
comparison, promotion gate, and rollback path are defined.

**What would make it admissible:**

Generate only a versioned candidate from an explicit diagnosis, evaluate it
against a named baseline and held-out tasks, and allow keep, rollback, or
retirement as outcomes.

### Anti-pattern 5: Recommend more capabilities by default

**Why wrong:**

Capability volume is not capability utility. A system that recommends
something for every request can increase context, cost, conflicts, and
decision noise.

**What would make it admissible:**

Preserve no-intervention and conditional-intervention outcomes, and show why
the additional capability changes the expected trajectory.

### Anti-pattern 6: Treat one successful trace as proof

**Why wrong:**

One trajectory cannot separate capability effect from task luck, model
stochasticity, environment state, or agent behavior.

**What would make it admissible:**

Use repeated, paired, scope-bounded evidence and record uncertainty,
protocol deviations, and held-out behavior.

---

## 5. Review Template

Copy the following template into every future Phase 2+ proposal, experiment
card, implementation plan, or architecture review. A proposal may add detail,
but it must not omit these fields.

## North Star Alignment Review

**Proposal / Change:**

**Owner:**

**Date:**

**Current status:**

### Lifecycle stage

Lifecycle stage:

```text
DISCOVER | INTERVENE | OBSERVE | DIAGNOSE | EVOLVE
```

Primary lifecycle question:

Supporting stages:

Explicitly out of scope:

### Research question

Research question:

What decision will this work support?

### Capability decision evidence

Capability decision evidence:

```text
KEEP | COMPRESS | MODIFY | REPLACE | RETIRE | NONE YET
```

Evidence produced:

Evidence not produced:

If no lifecycle decision is enabled yet, explain why this work is a necessary
prerequisite and name the next evidence-producing step:

### Baseline

Baseline:

```text
Control:
  No external capability

Treatment:
  With external capability
```

What is held constant:

What changes between control and treatment:

If the control/treatment comparison is not applicable, explain why:

### Trajectory observability

Trajectory observability:

- action sequence:
- tool usage:
- reasoning or planning artifacts:
- verification behavior:
- failure mode:
- user or evaluator intervention:
- protocol deviations:

What remains invisible:

### Expected evolution decision

Expected evolution decision:

```text
KEEP | COMPRESS | MODIFY | REPLACE | RETIRE | CONDITIONAL INTERVENTION | UNKNOWN
```

If the experiment succeeds:

If the experiment is neutral:

If the experiment fails or causes harm:

Rollback or retirement condition:

### Risks

```yaml
risks:
  - risk:
    impact:
    mitigation:
  - risk:
    impact:
    mitigation:
```

### Scope boundary

This proposal will not:

- change existing contracts without a separate approved change;
- change Phase 1 retrieval, Planning, Judge, or CLI behavior unless explicitly
  reviewed as a separate lifecycle decision;
- treat recommendation, relevance, popularity, or generated text as utility
  evidence by itself;
- promote an adapted capability without a named baseline and evaluation;
- remove a capability globally based on evidence from one model, harness, task
  family, or environment.

### Gate result

```text
PASS | CONDITIONAL | FAIL
```

Gate rationale:

Required follow-up before implementation or promotion:

Reviewer:

Review date:

---

## 6. Gate Interpretation

### PASS

Use `PASS` only when the proposal:

- names a lifecycle stage and research question;
- identifies the capability decision it informs;
- defines a control and treatment, or documents a valid prerequisite
  exception;
- provides a trajectory observation boundary;
- states the action enabled by success, neutrality, or failure;
- records scope, risks, and uncertainty.

`PASS` means the proposal is aligned for its stated scope. It does not mean
that the experiment has succeeded.

### CONDITIONAL

Use `CONDITIONAL` when the direction is aligned but one or more evidence
dependencies remain unresolved. A conditional proposal may continue with
research or artifact preparation, but it may not claim utility, promote a
capability, or silently begin a broader implementation.

The missing evidence and the condition for clearing it must be named.

### FAIL

Use `FAIL` when the proposal:

- optimizes popularity, retrieval, or recommendation volume as an endpoint;
- has no identifiable lifecycle decision;
- cannot distinguish control from treatment and makes no valid exception;
- exposes no useful trajectory or failure evidence;
- proposes generation, rewrite, or promotion without evaluation and rollback;
- expands scope without a capability lifecycle reason.

A failed proposal may be rewritten with a narrower research question. The gate
is a design boundary, not a permanent rejection of the underlying idea.

---

## 7. Permanent Review Rule

Before any Phase 2+ work is implemented, promoted, or described as a product
capability, the North Star Alignment Review must be completed and stored with
the relevant proposal or experiment artifact.

The review must be repeated when any of the following changes:

- intervention type or version;
- model or model generation;
- harness or tool surface;
- task family or evaluation scope;
- baseline or treatment definition;
- promotion, rollback, or retirement policy;
- intended product claim.

The gate does not require every future project to use the same benchmark,
model, Skill, or metric. It requires every project to preserve the same
decision logic:

```text
What capability decision is being made?
Compared with what baseline?
What happened in the trajectory?
What evidence explains why?
What lifecycle action follows?
```

If those questions cannot be answered, the work may remain exploratory
research, but it must not be presented as Capability Lifecycle Evaluation.
