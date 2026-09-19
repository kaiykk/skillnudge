# Skill Utility Drift Experiment Card v0.1

**Status:** DESIGN BASELINE / PHASE 2 RESEARCH ONLY
**Date:** 2026-09-19
**Scope:** Documentation and research design only

This experiment card defines a falsifiable Phase 2 research direction. It does
not implement Phase 2 runtime, add evaluation code, change existing contracts,
or change Phase 1 retrieval, planning, Judge, or CLI behavior.

SkillNudge is not a Skill marketplace. It is a **Capability Lifecycle Control
Plane**.

The long-term lifecycle is:

```text
DISCOVER
-> INTERVENE
-> OBSERVE
-> DIAGNOSE
-> EVOLVE
-> EVALUATE
-> PROMOTE / ROLLBACK
```

Phase 1 established the control-plane question:

> When should an agent consider external capability?

Phase 2 investigates the outcome question:

> Did the capability actually improve the trajectory?

Skills are one type of external capability intervention. The experiment must
remain valid if the same design is later applied to an Integration, Resource,
tool procedure, or other capability.

---

## 1. Experiment Objective

### Research question

When an external capability intervention is inserted into an agent trajectory,
under what conditions does it create measurable utility gain, and when should it
be removed, compressed, replaced, or retired?

The first experiment narrows this to:

> Under a fixed model, fixed harness, fixed environment, and fixed debugging
> task family, does the Systematic Debugging Skill produce a measurable
> improvement over the no-intervention baseline, and what evidence would
> justify keeping, adapting, or retiring it?

The first experiment does not claim to measure all forms of Skill utility. It
tests one intervention, one task family, and one controlled execution setting
before expanding to model-version or harness-version comparisons.

### Why this matters

A Skill can look useful because it is relevant to a task, because a Judge
expects it to help, or because it produces a plausible-looking trace. None of
those observations establishes that the intervention improved the result.

The same Skill may:

- improve correctness while increasing turns or tool calls;
- improve weaker models but add no value for a stronger model;
- help on one debugging class and hurt on another;
- preserve success while adding unnecessary procedural cost;
- encode a rigid sequence that prevents a better agent strategy;
- remain valuable because it supplies private, normative, or tool-backed
  capability rather than cognitive scaffolding.

SkillNudge therefore needs an outcome-level experiment that separates:

```text
plausible relevance
from
observed utility
```

### Assumptions being challenged

This experiment challenges, without presuming they are false, the following
assumptions:

1. A relevant Skill is probably useful.
2. A longer or more procedural Skill is safer than a shorter one.
3. A Skill that helped once should remain installed.
4. A newer or stronger model benefits from the same scaffolding.
5. More planning and verification steps necessarily improve debugging.
6. A single success rate is enough to decide whether an intervention should be
   kept.
7. A Skill can be evaluated independently of the model, harness, task family,
   and environment in which it is used.

### Current hypothesis

> Many existing Skills may improve weaker models by providing procedural
> guidance, but the same Skills may become redundant, restrictive, or harmful
> as base models and harnesses improve.

This is a hypothesis, not a conclusion. The experiment must allow all three
outcomes:

```text
Skill helps
Skill neutral
Skill hurts
```

The first experiment can establish evidence for utility in one controlled
setting. It cannot, by itself, prove utility drift across model generations.
That requires a later model-by-intervention comparison with model and harness
versions explicitly recorded.

---

## 2. Experimental Philosophy

### Controlled intervention framing

This is a controlled intervention experiment, not a Skill popularity contest or
an attempt to find the most comprehensive Skill.

We compare:

```text
Control:
  Agent without external capability intervention

Treatment:
  Agent with external capability intervention
```

Possible evolution is evaluated separately:

```text
Original intervention
vs
Adapted intervention
```

The goal is not:

> Find the best Skill.

The goal is:

> Understand when an intervention creates durable utility.

`Durable utility` means an observed improvement that survives repeated trials,
does not rely on a one-off lucky trajectory, and transfers to held-out tasks
within the defined task family. It does not mean that the intervention must
remain useful forever or across every model and harness.

### Conditions

| Condition | Description |
| --- | --- |
| No Skill | Agent baseline capability with no external capability intervention |
| Original Skill | Existing Systematic Debugging Skill, unchanged and version-locked |
| Adapted Skill | A modified, compressed, or otherwise evolved intervention produced after development evidence and evaluated on held-out tasks |
| Retired Skill | A previously useful intervention removed from the execution path; operationally this may execute as No Skill, but its lifecycle meaning remains distinct |

The first causal comparison is `No Skill` versus `Original Skill`. `Adapted
Skill` and `Retired Skill` are lifecycle conditions that must not be used to
retroactively tune or reinterpret the original comparison.

If `Retired Skill` executes identically to `No Skill`, it is not an independent
behavioral treatment. It records the decision to remove a previously accepted
intervention and allows post-retirement monitoring to remain explicit.

### What is held constant

For the first experiment, hold constant:

- base model name and exact model version;
- provider and sampling configuration;
- harness/runtime version;
- tool definitions and tool permissions;
- repository snapshot and task environment;
- task prompt and acceptance tests;
- maximum time, turn, and tool budgets;
- system instructions unrelated to the intervention;
- observation and termination rules;
- network and filesystem access;
- randomization or seed policy;
- evaluator version.

The intervention is the only intended treatment difference. If another
variable changes, the run is not a clean comparison and must be recorded as a
protocol deviation.

### Intervention insertion boundary

The Skill must be injected at a fixed, documented point in the agent
trajectory, using the same channel and formatting for every treatment run.

The intervention must not:

- change the task statement;
- add hidden evaluator information;
- add tools that the control does not have;
- change the test suite;
- provide a reference patch;
- include post-hoc human coaching;
- receive information from later trajectory outcomes.

The control agent retains its normal system prompt, tool surface, and model
capabilities. `No Skill` means no external debugging intervention, not an
artificially weakened agent.

### Utility is multidimensional

The experiment must not collapse every outcome into an unexamined universal
score. Utility is recorded as a profile:

```text
task correctness
constraint and regression safety
trajectory cost
user or evaluator intervention
failure type
transfer to held-out tasks
```

A decision may use a primary outcome and pre-registered guard metrics, but a
single scalar must not hide a success-rate decrease or a serious regression.

### Execution shape

```text
Agent
 |
 +---- No Skill
 |
 +---- Original Skill
 |
 +---- Adapted Skill
```

```text
    |
    v
```

```text
Utility Evaluation
```

```text
    |
    v
```

```text
Keep / Modify / Retire
```

This diagram describes the research loop, not a Phase 2 runtime to be
implemented in this change.

---

## 3. First Experiment Selection

### Recommended first intervention

**Skill:** Systematic Debugging Skill

The selected Skill should be version-pinned before the experiment. The first
run must evaluate the existing artifact as-is. Its source, commit or version,
license, body hash, and any bundled resources must be recorded outside the
execution prompt.

### Why this Skill

Systematic debugging is a good first intervention because it has a narrow
behavioral claim: the agent should localize a defect, form and test a
hypothesis, make a corrective change, and verify that the correction does not
break surrounding behavior.

It is useful for a first experiment because the intervention can be tested
against observable outcomes rather than only a subjective quality judgement.

### Why not the alternatives

#### Not a UI design Skill

UI quality often requires visual judgement, design taste, rendering context, or
human preference. Automated checks can help, but they are not a sufficiently
clean primary outcome for the first utility experiment.

#### Not a brainstorming Skill

Brainstorming quality is difficult to score without a strong task-specific
rubric. A brainstorming intervention can be valuable, but its first benchmark
would risk measuring evaluator preference rather than downstream task utility.

#### Not a general workflow Skill

A general workflow Skill changes too many behaviors at once. It would be
difficult to identify which procedure caused an outcome and would make
ablation and retirement decisions ambiguous.

### Selection criteria

The first experiment must satisfy all five criteria:

1. **Automatically verifiable outcome**
   A test or other deterministic checker can verify the main task result.
2. **Clear success/failure signal**
   The task has an explicit acceptance condition, not only a subjective
   quality judgement.
3. **Transferable tasks**
   The task family contains more than one repository, bug type, or code
   pattern so the result is not tied to one example.
4. **Suitable for ablation**
   The Skill can be decomposed into meaningful procedural sections without
   changing the task interface.
5. **Suitable for future Skill evolution**
   The evidence can support a decision to keep, compress, modify, replace, or
   retire the intervention without requiring a new measurement philosophy.

---

## 4. Task Dataset Design

### Task unit

The task unit is one reproducible debugging episode:

```text
repository snapshot
+ bug report or failing behavior description
+ initial checkout state
+ executable test command
+ acceptance oracle
+ fixed agent/harness configuration
+ one trajectory under one intervention condition
```

Each task must have:

- a pinned repository commit or immutable snapshot;
- a self-contained task statement;
- a deterministic setup procedure;
- at least one failing test, reproducible failure, or explicit incorrect
  behavior;
- a target acceptance test or checker;
- a regression test set covering behavior that must remain correct;
- a bounded execution budget;
- no evaluator-only information available to the agent;
- a record of expected environment and dependencies;
- a license and provenance that permit the task to be used for the planned
  research.

The task is not merely a prompt. It is the combination of the problem,
environment, oracle, and provenance needed to compare trajectories.

### Minimal benchmark shape

Do not begin with full-scale SWE-bench or another large benchmark. Start with a
small, manually inspected, reproducible slice that makes every failure
reviewable.

The recommended pilot target is:

```text
24 tasks
4 debugging families
at least 4 repository snapshots
16 development tasks
8 held-out evaluation tasks
```

The exact count may be reduced only before execution if reproducible tasks are
unavailable. A shortfall must be recorded as a design limitation, not silently
treated as equivalent evidence. The held-out set must not be used to write,
compress, select, or reject an Adapted Skill.

The first pilot should prioritize task diversity and inspectability over
volume:

| Debugging family | Example failure shape | Why it matters |
| --- | --- | --- |
| Logic and boundary defects | Off-by-one, incorrect branch, empty-input behavior | Tests hypothesis formation and edge-case reasoning |
| State and data-flow defects | Stale state, wrong transformation, incorrect default | Tests tracing across local functions and data boundaries |
| Error-handling defects | Exception swallowed, wrong error path, missing validation | Tests diagnosis and verification beyond the happy path |
| Regression and integration defects | Existing behavior breaks after a local change or interface mismatch | Tests whether the procedure handles surrounding constraints |

These families are design categories, not gold labels for a model prompt. The
agent receives the task statement and repository, not the experiment's
taxonomy.

### Development and held-out split

The development split is used to:

- validate that the task format is executable;
- identify protocol failures;
- inspect whether the Original Skill has plausible section-level effects;
- formulate an Adapted Skill candidate;
- define which evidence is sufficient for an evolution proposal.

The held-out split is used only for:

- the pre-registered comparison of conditions;
- testing transfer within the task family;
- evaluating whether an Adapted Skill generalizes beyond its development
  examples;
- checking for regressions introduced by modification.

Where possible, at least one repository should be held out entirely rather
than splitting only neighboring issues from the same repository.

### Inclusion criteria

Include a task only when:

- the bug can be reproduced from the pinned snapshot;
- the acceptance oracle is deterministic enough for repeated runs;
- the required dependencies can be installed or are already captured;
- the task can be completed within the declared resource budget;
- the task's main outcome is distinguishable from incidental formatting;
- the task does not require private credentials or private organizational
  knowledge;
- the task's source and license provenance can be recorded.

### Exclusion criteria

Exclude or mark separately any task with:

- flaky or time-dependent tests;
- required external services that cannot be version-locked;
- an evaluator that depends mainly on subjective human preference;
- an ambiguous issue statement with no reviewable acceptance condition;
- hidden state that cannot be reproduced;
- an environment that changes during execution;
- a task whose difficulty is dominated by setup rather than debugging;
- a task that leaks the condition or the expected intervention through its
  wording.

An excluded task must not be quietly converted into a failed model run.

### Repeated trials

Each task-condition pair should be run with multiple independent trials when
the provider is stochastic. The minimum pilot target is two trials per pair;
three is preferred when budget permits.

If the provider is deterministic under the selected configuration, repeated
identical outputs must be recorded as deterministic behavior rather than
counted as independent evidence. A seed or determinism declaration must be
stored with each run.

The same task must be paired across conditions. Results should be analyzed at
the task level before aggregate summaries so that a few easy tasks cannot hide
failure on difficult ones.

---

## 5. Execution Protocol

### Run matrix

The initial run matrix is:

```text
development tasks:
  No Skill
  Original Skill

held-out tasks:
  No Skill
  Original Skill
```

Only after the Original-versus-No-Skill comparison and development analysis
produce an explicit evolution proposal may the following be added:

```text
held-out tasks:
  Adapted Skill
  Retired Skill
```

The `Retired Skill` condition is included when the research question is whether
removing a previously useful intervention preserves outcome quality while
reducing cost or harmful constraints. It should not be presented as a distinct
capability if its execution path is identical to No Skill.

### Agent-facing inputs

The agent receives the same:

- task statement;
- repository snapshot;
- tool definitions;
- system and harness instructions;
- resource budget;
- termination policy.

The only planned difference is the presence or absence of the external
capability intervention at the fixed insertion boundary.

The agent must not receive:

- task split labels;
- condition names;
- expected outcome labels;
- benchmark annotations;
- the reason the task was selected;
- later evaluator results;
- an adapted Skill derived from held-out failures.

### Required run record

The future evaluation record should be sufficient to reconstruct the
comparison. At minimum it should preserve:

| Record group | Required information |
| --- | --- |
| Identity | Task ID, repository snapshot, condition, Skill version, trial ID |
| Configuration | Model version, provider, harness version, tools, seed, budgets |
| Input | Task statement hash or immutable reference, intervention insertion point |
| Trajectory | Turns, tool calls, timestamps, failures, retries, termination reason |
| Output | Final patch or artifact, final response, changed files |
| Verification | Target test result, regression test result, checker version |
| Cost | Tokens when available, wall-clock time, tool count, human interventions |
| Provenance | Skill source, commit/body hash, license, dataset source |

This is an experiment-record design, not a request to add a new runtime
contract in this phase.

### Protocol deviations

A run is a protocol deviation if any of the following changes across a paired
comparison:

- model or model configuration;
- harness or tool surface;
- repository snapshot;
- task statement;
- test or evaluator version;
- budget;
- intervention placement;
- manual assistance.

Protocol deviations should be excluded from the primary comparison and
reported separately. They must not be repaired by editing raw outputs.

---

## 6. Utility Measurement

### Primary outcome

The primary outcome is **verified task success**:

```text
target acceptance checks pass
and
required regression checks pass
```

A task is not counted as successful merely because the agent produced a
plausible patch, described the right cause, or passed one visible test while
breaking required surrounding behavior.

The exact acceptance commands and regression scope are task metadata. They must
be frozen before the corresponding run set is interpreted.

### Secondary outcomes

Record secondary outcomes separately:

- time to first plausible diagnosis;
- time to first passing target check;
- total turns;
- total tool calls;
- redundant tool calls;
- wall-clock latency;
- token usage or estimated cost, when available;
- number of retries or reverted edits;
- patch size and files touched;
- regression count;
- constraint violations;
- human intervention count;
- failure category.

Secondary metrics explain how utility was created or lost. They do not replace
the primary correctness outcome.

### Failure categories

Use failure categories for diagnosis, not as hidden scoring weights:

| Category | Meaning |
| --- | --- |
| Diagnosis failure | The agent did not identify a plausible root cause |
| Localization failure | The agent focused on the wrong code or behavior |
| Verification failure | The agent changed code without adequate confirmation |
| Regression failure | The target appeared fixed but required behavior broke |
| Over-constraint | The intervention prevented a better or simpler strategy |
| Redundant procedure | The intervention added work without improving the result |
| Tool or environment failure | The task could not be evaluated because of infrastructure or dependency failure |
| Task ambiguity | The acceptance condition was not sufficiently clear |

`Tool or environment failure` and `Task ambiguity` must not be reported as
evidence that the Skill helped or hurt.

### Utility gain definition

For a fixed task family, an intervention has measurable utility gain only when
the paired evidence shows an improvement that is both:

1. **Outcome-relevant**
   It improves verified task success, or preserves success while materially
   reducing a pre-registered cost or failure mode.
2. **Guarded against harm**
   It does not introduce an unacceptable regression in correctness, safety,
   constraint compliance, or held-out transfer.

The primary report should show:

- absolute success rate by condition;
- paired task-level success changes;
- confidence intervals or an equally explicit uncertainty treatment;
- cost deltas among successful and all runs;
- failure-category changes;
- per-task and per-family results;
- development versus held-out results.

Do not call an intervention useful because it wins on a single average that
conceals task failures or a large cost increase.

### Interpreting the three outcomes

#### Skill helps

Classify the Original Skill as helping when it produces a reproducible
improvement over No Skill on the primary outcome or a clearly pre-registered
efficiency outcome, with no unacceptable guard-metric regression and evidence
of transfer to held-out tasks.

#### Skill neutral

Classify the Skill as neutral when the comparison does not show a credible
outcome improvement and does not show a meaningful harm. Neutral does not mean
the Skill is universally useless. It means utility was not demonstrated in
this task, model, harness, and environment.

#### Skill hurts

Classify the Skill as harmful when it lowers verified success, increases
regression or constraint failures, or adds material trajectory cost without a
compensating outcome gain, and the effect is replicated beyond a single
anomalous run.

An inconclusive or infrastructure-failed comparison is neither neutral nor
harmful. It is an evidence failure and must be reported as such.

---

## 7. Ablation and Evolution Design

### Why ablation is needed

An Original Skill is not one indivisible treatment. It may contain:

- problem decomposition;
- hypothesis formation;
- search or inspection procedure;
- verification checklist;
- output or handoff format;
- tool-use instructions.

If the full Skill changes an outcome, the experiment should not assume that
every section contributed equally.

### Ablation sequence

After the initial No Skill versus Original Skill comparison, development-only
analysis may propose bounded ablations such as:

```text
Full Original Skill
Skill minus decomposition section
Skill minus prescribed search section
Skill minus verification section
Skill minus output-format section
No Skill
```

The ablation set must be declared before its results are interpreted. It must
not be expanded indefinitely to search for a favorable result.

Ablation is for attribution and evolution evidence. It does not change the
Phase 1 Judge or the existing intervention contracts.

### Adapted Skill

An Adapted Skill is a versioned candidate derived from explicit evidence, not
from an unconstrained rewrite. Each change must state:

- which section changed;
- the observed failure or redundancy it addresses;
- what behavior is intentionally preserved;
- what behavior may be lost;
- which development evidence supports the change;
- which held-out evidence will decide whether it is promoted.

Adaptation operations may include:

```text
COMPRESS
  remove or shorten redundant procedural content

MODIFY
  clarify or reorder a procedure without changing its intended boundary

REPLACE
  substitute a procedure shown to be obsolete or harmful

PRUNE
  remove a section whose contribution is not supported

RETIRE
  remove the intervention from the execution path
```

An LLM-generated rewrite is a candidate artifact, not evidence of improvement.

### Data separation for evolution

The sequence must be:

```text
development evidence
-> adaptation proposal
-> frozen Adapted Skill
-> held-out evaluation
-> promotion or rollback decision
```

Held-out task outcomes must not be fed back into the Adapted Skill before the
held-out decision is recorded. Otherwise the comparison becomes an
optimization loop over the evaluation set.

---

## 8. Keep, Modify, Replace, and Retire Rules

These rules are decision principles for the experiment. They are not Phase 2
runtime behavior.

| Decision | Evidence required | Interpretation |
| --- | --- | --- |
| Keep | Original Skill shows repeatable utility on verified outcomes with no unacceptable guard regression | Retain the current version for this model, harness, task family, and environment |
| Compress | Success is preserved while identifiable Skill sections add cost or duplicate native behavior | Remove or shorten the supported redundant sections, then re-evaluate |
| Modify | A specific section causes a reproducible failure or ambiguity and a bounded change addresses it | Produce a versioned Adapted Skill and test on held-out tasks |
| Replace | The intervention's strategy is consistently inferior for a task family, while another bounded intervention addresses the same capability need | Compare the replacement under the same control conditions |
| Retire | No meaningful gain remains, or harm persists, after checking task coverage and protected requirements | Remove the intervention and monitor the No Skill path |

No decision should be based on:

- one successful or failed trajectory;
- an LLM's preference for one wording;
- a higher relevance score;
- a larger number of instructions;
- a change made after inspecting the held-out results;
- a benchmark result with unresolved environment failure.

### Retirement is not the same as deletion

Retirement is a lifecycle decision that records:

- the last accepted version;
- the model, harness, and task scope in which it was evaluated;
- the evidence for removal;
- known protected cases where it may still be required;
- a rollback path if later evidence reverses the decision.

A Skill retired for one model and task family is not automatically retired
globally.

---

## 9. Analysis Plan

### Paired analysis

The primary comparison should be paired by task. This controls for the fact
that one bug may be much harder than another.

Report:

1. per-task outcome under each condition;
2. per-family outcome;
3. aggregate success rate;
4. paired success changes;
5. cost changes conditional on success and across all runs;
6. failure-category transitions;
7. held-out transfer;
8. protocol deviations and excluded runs.

### Uncertainty

The experiment must state uncertainty rather than treating a small pilot as a
stable population estimate. Use confidence intervals, bootstrap intervals, or
another declared uncertainty method appropriate to paired binary and
trajectory-cost outcomes.

If the pilot is too small to distinguish help from noise, the correct
conclusion is `inconclusive`, not `neutral`.

### Model and harness scope

The first experiment keeps model and harness fixed. Its conclusion must be
scoped accordingly:

```text
This intervention helped / was neutral / hurt
for this model,
this harness,
this task family,
this environment,
and this evaluation window.
```

Only a later experiment may vary model or harness while preserving the other
dimensions. Such a study is required to test the broader model-improvement
drift hypothesis.

### No universal utility score yet

The first experiment should not invent a single permanent utility formula.
Success, cost, safety, and transfer remain separately visible. A later product
layer may define decision policies for particular domains, but those policies
must be grounded in observed trade-offs and explicit risk tolerance.

---

## 10. Threats to Validity

### Task selection bias

A hand-curated debugging slice may favor tasks where systematic procedure is
helpful. Mitigation: include multiple bug families, multiple repositories, and
held-out tasks with provenance.

### Prompt or artifact leakage

Task wording may accidentally reveal the desired procedure or the condition.
Mitigation: inspect prompts for intervention leakage and keep benchmark
metadata out of agent-visible input.

### Adaptation overfitting

Repeatedly changing an Adapted Skill against the same tasks can create
benchmark-specific behavior. Mitigation: separate development and held-out
tasks, freeze candidate versions, and record every proposal.

### Evaluator leakage

If the agent can infer hidden tests or the evaluator's exact implementation,
success may not represent debugging ability. Mitigation: keep evaluator
details out of the task prompt and record any accidental disclosure.

### Model and harness drift

A provider update, tool change, or system prompt change can masquerade as Skill
utility drift. Mitigation: pin and record all execution configuration.

### Stochastic trajectories

A single lucky or unlucky trajectory can distort a conclusion. Mitigation:
repeat trials where possible and use paired, task-level analysis.

### Cost metric distortion

Tokens, turns, and latency may move in different directions. Mitigation: report
the metric vector and do not optimize one cost measure while hiding another.

### Incomplete notion of debugging quality

Passing tests may miss maintainability, readability, or latent defects.
Mitigation: use deterministic checks as the primary outcome and add bounded
human review as a secondary diagnostic, never as an unbounded replacement for
the oracle.

### Protected-value interventions

A Skill may be useful for compliance, private knowledge, or a mandatory
procedure even when it does not improve generic coding success. Mitigation:
do not generalize a debugging result into a global retirement decision.

---

## 11. Falsifiable Predictions and Decision Outcomes

The experiment should be able to produce any of the following outcomes:

### Outcome A: Original Skill helps

The Original Skill improves verified debugging success or preserves success
while reducing a declared failure or cost, and the effect transfers to held-out
tasks. The result supports keeping the Skill within the tested scope.

### Outcome B: Original Skill is neutral

The Original Skill does not produce a credible improvement or harm. The result
supports treating it as optional or investigating whether only a subset of its
sections is useful.

### Outcome C: Original Skill hurts

The Original Skill produces replicated lower success, more regressions,
over-constraint, or uncompensated cost. The result supports a bounded
compression, modification, replacement, or retirement investigation.

### Outcome D: Evidence is inconclusive

The task set, environment, evaluator, or trial count is insufficient to
separate effects from noise. The result supports improving the experiment
protocol, not changing the Skill or claiming drift.

### Outcome E: Protocol failure

The comparison is invalid because a model, harness, tool, task, evaluator, or
credential boundary changed. The result is excluded from utility conclusions
and preserved as a protocol failure.

---

## 12. What This Card Freezes

This documentation baseline freezes the following research choices:

1. The research target is utility of an inserted capability intervention, not
   Skill popularity or relevance.
2. The first intervention is Systematic Debugging Skill.
3. The first task family is objectively verifiable debugging, not UI design,
   brainstorming, or general workflow.
4. The first causal comparison is No Skill versus Original Skill under fixed
   model, harness, environment, task, and tool conditions.
5. A minimal, reproducible task slice is preferred to full-scale SWE-bench at
   the start.
6. Task success, cost, safety, failure type, and transfer remain separate
   evidence dimensions.
7. Adapted and Retired conditions are evaluated only with versioned provenance
   and development/held-out separation.
8. Keep, modify, replace, and retire are evidence-gated decisions, not
   automatic consequences of one trajectory.
9. The first experiment does not modify Phase 1 contracts or runtime behavior.
10. No Phase 2 implementation starts from this card alone.

These are research-design decisions, not new runtime contracts.

---

## 13. Unresolved Research Questions

The following questions remain open and must be answered before a full Phase 2
implementation or broader claim:

- Which Systematic Debugging Skill artifact is the canonical first version,
  and what source/version/license provenance can be retained?
- Is the proposed 24-task pilot large enough to distinguish small utility
  gains from stochastic noise?
- What exact success and regression checks are reliable across the selected
  repositories?
- How should patch quality be reviewed when automated tests pass but code
  quality differs?
- Which sections of the Original Skill are safe to ablate independently?
- What minimum effect size should count as materially useful for this task
  family?
- How should token, latency, and tool-call costs be compared when provider
  reporting is incomplete?
- How should an intervention be evaluated when it carries private,
  organizational, normative, or tool-backed value that debugging success does
  not capture?
- What additional model or harness versions are needed before the broader
  utility-drift hypothesis can be tested?
- What rollback and promotion evidence is sufficient for an adapted version?

These are research questions, not permission to add runtime behavior in this
documentation change.

---

## 14. Phase 2 Implementation Gate

Phase 2 implementation should **not** start after creating this card.

Before implementation, the project should separately confirm:

1. the canonical Systematic Debugging Skill artifact and provenance;
2. the minimal task slice and its deterministic acceptance oracles;
3. the model, harness, tool, and provider configuration to be held constant;
4. the trial and uncertainty policy;
5. the development/held-out split;
6. the exact promotion, rollback, compression, and retirement decision gates;
7. that the planned evaluation can be performed without modifying Phase 1
   contracts or behavior.

Only after those research inputs are reviewed should the project decide
whether a separate Phase 2 implementation change is warranted. This card
itself does not authorize that implementation.
