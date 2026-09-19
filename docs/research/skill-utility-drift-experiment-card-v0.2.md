# Skill Utility Drift Experiment Card v0.2

**Status:** RESEARCH DESIGN / NOT PHASE 2 IMPLEMENTATION AUTHORIZATION
**Date:** 2026-09-19
**Scope:** Experiment protocol, evidence model, and decision criteria only

This document upgrades the Phase 2 experiment design from v0.1. It defines
what evidence is required to decide whether an external capability
intervention should exist, remain active, be compressed, be modified, be
replaced, or be retired.

It does not:

- implement Phase 2 runtime;
- implement a benchmark runner;
- download or vendor a dataset;
- implement SWE-bench integration;
- add dependencies;
- change Phase 1 retrieval, Planning, Judge, contracts, runtime, or CLI
  behavior;
- freeze a final dataset;
- authorize Phase 2 coding.

The first intervention remains:

```text
Systematic Debugging Skill
```

The first task domain remains:

```text
Repository-level debugging tasks
```

The first causal comparison remains:

```text
No Skill
vs
Original Skill
```

The experiment treats a Skill as one type of external capability
intervention. The same evidence model should remain usable for an Integration,
Resource, tool procedure, workflow, memory strategy, or other bounded
capability.

---

## 1. Experiment Objective

### Research question

> When an external capability intervention is inserted into an agent
> trajectory, under what conditions does it create measurable utility gain, and
> when should it be removed, compressed, replaced, or retired?

For the first experiment:

> Under a fixed model, fixed harness, fixed tools, fixed environment, and a
> bounded repository-level debugging task family, does the Systematic Debugging
> Skill improve the trajectory over the No Skill control, and what evidence
> explains the result?

The experiment must allow all of the following conclusions:

```text
Skill helps
Skill is neutral
Skill hurts
Evidence is inconclusive
Protocol or environment failure prevents a utility conclusion
```

### Why this matters

SkillNudge is a Capability Lifecycle Control Plane, not a Skill marketplace.
The central question is not whether a Skill is relevant, popular, retrievable,
or plausible. The central question is whether inserting the intervention
changes an agent trajectory in a way that justifies a lifecycle decision.

The experiment therefore needs evidence that connects:

```text
intervention
-> observable trajectory
-> verified outcome
-> diagnosed mechanism
-> lifecycle decision
```

A final pass rate without trajectory and failure evidence cannot explain
whether a Skill helped, whether it only added cost, whether it was redundant,
or whether the outcome was caused by the environment.

### Assumptions being challenged

The experiment challenges, without assuming they are false:

1. A relevant Skill is probably useful.
2. A longer or more procedural Skill is safer than a shorter one.
3. A Skill that helped once should remain installed.
4. Stronger models benefit from the same scaffolding as weaker models.
5. More planning and verification steps necessarily improve debugging.
6. Benchmark success alone is sufficient evidence for keeping an intervention.
7. A historical trajectory can be treated as a causal No Skill versus Skill
   comparison.

### Current hypothesis

> Many existing Skills may improve weaker models by providing procedural
> guidance, but the same Skills may become redundant, restrictive, or harmful
> as base models and harnesses improve.

This remains a hypothesis. v0.2 does not claim to prove utility drift across
model generations because the first experiment keeps model and harness fixed.
A later experiment must vary those factors explicitly if it is to test the
broader drift claim.

---

## 2. Experimental Philosophy

### Controlled intervention experiment

The first experiment is a controlled intervention comparison:

```text
Control:
  Model + Harness + Tools
  - External Skill

Treatment:
  Model + Harness + Tools
  + Systematic Debugging Skill
```

The intervention is inserted at a fixed, documented boundary. The task,
repository snapshot, evaluator, tool surface, model configuration, and
resource budget remain the same.

The goal is not:

> Find the best Skill.

The goal is:

> Understand when an intervention creates durable utility and what evidence
> supports the next lifecycle action.

Durable utility means that the observed effect is not explained by one lucky
trajectory, one broken environment, or one task-specific artifact. It does not
mean that the intervention must be useful for every model, harness, task
family, or future version.

### Lifecycle comparison

The first causal comparison is:

| Condition | Description |
| --- | --- |
| No Skill | Baseline agent capability without an external capability intervention |
| Original Skill | The version-pinned Systematic Debugging Skill, unchanged |

Evolution conditions are evaluated only after the original comparison has
produced a bounded diagnosis:

| Condition | Description |
| --- | --- |
| Adapted Skill | A versioned compressed, modified, or replaced intervention evaluated after development evidence |
| Retired Skill | The previously useful intervention removed from the execution path; behaviorally this may equal No Skill, but its lifecycle decision remains explicit |

`Adapted Skill` and `Retired Skill` must not be used to retroactively tune or
reinterpret the primary No Skill versus Original Skill comparison.

### What is held constant

The first experiment must record and hold constant:

- model name and exact model version;
- provider and sampling configuration;
- harness and runtime version;
- system instructions unrelated to the intervention;
- tool definitions, permissions, and ordering;
- repository snapshot and task environment;
- task statement and agent-visible inputs;
- acceptance tests and evaluator version;
- maximum time, turn, tool, and token budgets where applicable;
- network and filesystem access;
- randomization or seed policy;
- termination and recovery rules;
- human intervention policy.

If one of these changes across a paired comparison, the run is a protocol
deviation. It must not silently enter the primary utility analysis.

### Intervention boundary

The Original Skill must be version-pinned and recorded by source, revision,
license, and content hash before execution.

The treatment must not:

- modify the task statement;
- provide hidden evaluator information;
- add tools unavailable to the control;
- reveal the reference patch;
- reveal held-out labels or task-selection metadata;
- receive information from later evaluator results;
- receive human coaching that the control does not receive.

`No Skill` means no external debugging intervention. It does not mean an
artificially weakened model or a degraded tool environment.

### No universal utility score

v0.2 defines an evidence framework, not one permanent scalar utility score.
Outcome, cost, process, safety, and transfer remain visible as separate
dimensions. A later policy may combine them for a specific domain, but any
combination must preserve the underlying evidence and declared risk tolerance.

---

## 3. Evidence-First Experiment Data Architecture

The experiment starts from the evidence required for a lifecycle decision, not
from the shape of a particular dataset.

```text
Skill Utility Experiment Data Model

                    Experiment Run

                          |
        -----------------------------------------
        |                  |                    |
   Task Artifact      Trace Artifact      Oracle Artifact

                          |
                          v

                 Diagnostic Artifact

                          |
                          v

             Evolution Decision Evidence
```

The artifacts are related but not interchangeable:

- a Task Artifact describes what the agent was asked to do;
- a Trace Artifact describes what the agent visibly did;
- an Oracle Artifact describes whether the result satisfies the acceptance
  condition;
- a Diagnostic Artifact explains why the outcome occurred;
- Evolution Decision Evidence records what lifecycle action the evidence can
  justify.

### 3.1 Experiment Run

An `Experiment Run` is the unit that links one task, one condition, one trial,
and one declared execution configuration.

Minimum fields:

| Field | Purpose |
| --- | --- |
| `run_id` | Immutable identifier for the execution |
| `task_id` | Reference to the Task Artifact |
| `condition` | `no_skill`, `original_skill`, `adapted_skill`, or `retired_skill` |
| `trial_id` | Distinguishes repeated trials for the same task-condition pair |
| `configuration` | Model, provider, harness, tools, budgets, seed, evaluator |
| `artifact_refs` | Links to Task, Trace, Oracle, and Diagnostic artifacts |
| `run_status` | Valid, protocol deviation, environment failure, evaluation failure, or incomplete |
| `started_at` / `ended_at` | Timing and audit information |
| `provenance` | Skill source/version/hash and task source/revision |

The run record is not a new runtime contract. It is the minimum research
record required to reconstruct a comparison.

### 3.2 Task Artifact

A Task Artifact defines the reproducible problem presented to the agent. It is
not merely a prompt and is not merely a row copied from a benchmark.

The candidate source for the first pilot is a manually audited slice derived
from **SWE-bench Verified**. The design should describe this source as:

> SWE-bench provides a reproducible task/oracle substrate.

It should not describe SWE-bench alone as the SkillNudge benchmark or assume
that all source tasks are suitable for debugging-utility research.

Minimum Task Artifact fields:

| Field | Required meaning |
| --- | --- |
| `task_id` | Stable task identifier within the SkillNudge pilot |
| `source_artifact` | Source dataset and immutable revision or snapshot |
| `repository` | Repository identity and applicable license/provenance |
| `commit` | Base repository commit or immutable snapshot |
| `issue_description` | Agent-visible problem statement |
| `environment` | Setup procedure, image/version, dependencies, platform constraints |
| `test_oracle` | Target and regression checks, commands, expected results, evaluator version |
| `reference_patch_metadata` | Evaluator-side reference patch identity or provenance; never agent-visible |
| `task_type` | Manual classification such as bug fix, feature, refactor, or ambiguous |
| `debugging_depth` | Whether success requires investigation beyond direct code generation |
| `oracle_quality` | Review of determinism, coverage, and acceptance clarity |
| `environment_risk` | Setup and infrastructure risk independent of agent behavior |
| `skill_sensitivity` | Hypothesis about which observable behaviors the intervention could affect |
| `selection_notes` | Evidence and reviewer rationale for inclusion or exclusion |

The Task Artifact must also identify what is intentionally not exposed to the
agent:

- reference patch;
- test labels such as `FAIL_TO_PASS` and `PASS_TO_PASS` when they reveal
  evaluator structure;
- development or held-out split;
- manual selection scores;
- the expected failure taxonomy;
- the intervention condition.

### 3.3 Trace Artifact

A Trace Artifact records observable execution, not hidden chain-of-thought.
The experiment must not require storage or reconstruction of private internal
reasoning.

Observable event categories include:

#### Investigation

- file search;
- repository exploration;
- symbol or dependency inspection;
- error reproduction;
- test discovery;
- reading an existing implementation or configuration.

#### Hypothesis and verification behavior

- explicit hypothesis statement when the agent emits one;
- selected code location or suspected cause;
- test execution;
- validation attempt;
- regression check;
- comparison between expected and observed output.

The record should preserve observable agent artifacts such as emitted text,
tool calls, tool inputs, tool outputs, test output, patch events, and final
responses. It must not claim to know an internal thought that was not
observable.

#### Recovery

- failed attempt;
- strategy change;
- rollback or reverted edit;
- alternative hypothesis;
- retry after a failed test;
- termination after unresolved failure.

Minimum Trace Artifact fields:

| Field | Purpose |
| --- | --- |
| `trace_id` | Stable trace identifier |
| `run_id` | Links the trace to an Experiment Run |
| `sequence_index` | Orders observable events |
| `event_type` | Search, inspection, edit, test, verification, recovery, or termination |
| `actor` | Agent, tool, evaluator, or human |
| `tool_name` | Tool used, if applicable |
| `observable_input_ref` | Reference to recorded tool or agent input |
| `observable_output_ref` | Reference to recorded tool or evaluator output |
| `files_or_symbols` | Affected or inspected locations when available |
| `result` | Success, failure, changed strategy, or no-op |
| `timestamp` | Event timing when available |
| `redaction_status` | Indicates whether sensitive output was removed |

The Trace Artifact should support comparing investigation, hypothesis
formation, verification, and recovery without turning the experiment into a
CoT collection project.

### 3.4 Oracle Artifact

An Oracle Artifact records the outcome of the task and the validity of the
evaluation.

Minimum fields:

| Field | Purpose |
| --- | --- |
| `oracle_id` | Stable oracle result identifier |
| `run_id` | Links the result to the run |
| `evaluator_version` | Identifies the evaluator and test environment |
| `target_checks` | Required task-specific acceptance checks |
| `regression_checks` | Required checks for surrounding behavior |
| `actual_results` | Exit codes, test outputs, and observed statuses |
| `task_success` | Verified success, failure, or inconclusive |
| `regression` | Whether required behavior regressed |
| `failure_class` | Agent, environment, evaluation, or task ambiguity |
| `oracle_notes` | Reviewable explanation of unexpected results |

The artifact must distinguish:

```text
agent failure
environment failure
evaluation failure
task ambiguity
```

#### Agent failure

The run reached a valid, available task environment and evaluator, but the
agent produced an incorrect patch, failed to diagnose the issue, introduced a
regression, exceeded its budget, or terminated without satisfying the task.

#### Environment failure

The task could not be executed or evaluated because of dependency setup,
container, network, credential, tool, platform, or infrastructure failure.
Environment failure is not evidence that the Skill helped or hurt.

#### Evaluation failure

The evaluator, test command, reference setup, or result collection was broken,
misconfigured, inconsistent, or unable to determine the result. Evaluation
failure is not evidence of agent utility.

#### Task ambiguity

The task or acceptance condition was not sufficiently clear or reproducible to
support a valid causal comparison. An ambiguous task should be excluded or
reclassified, not silently counted as an agent failure.

### 3.5 Diagnostic Artifact

A Diagnostic Artifact explains the difference between paired outcomes. It is
the bridge from observation to lifecycle evidence.

Minimum fields:

| Field | Purpose |
| --- | --- |
| `diagnostic_id` | Stable diagnostic identifier |
| `comparison_refs` | Control/treatment runs being compared |
| `validity_status` | Valid comparison, protocol deviation, or insufficient evidence |
| `outcome_delta` | Success, regression, cost, and transfer differences |
| `failure_taxonomy` | Applicable F-category or neutral/helping behavior |
| `mechanism_evidence` | Trace and oracle references supporting the diagnosis |
| `alternative_explanations` | Model, task, environment, or evaluator explanations |
| `confidence` | High, medium, low, or unresolved |
| `scope` | Model, harness, task family, environment, and evaluation window |

The Diagnostic Artifact must not turn a correlation into a causal claim when
the paired comparison is invalid.

### 3.6 Evolution Decision Evidence

Evolution Decision Evidence is a reviewable package that records what action,
if any, the experiment supports.

Minimum fields:

| Field | Purpose |
| --- | --- |
| `decision_id` | Stable decision record |
| `intervention_version` | Original or adapted intervention identity |
| `baseline` | Named control condition |
| `evidence_window` | Tasks, trials, split, and evaluation period |
| `decision_scope` | Model, harness, task family, environment, and stage |
| `observed_utility` | Outcome, cost, safety, process, and transfer evidence |
| `decision` | Keep, compress, modify, replace, retire, or inconclusive |
| `rationale` | Evidence-bounded explanation |
| `protected_cases` | Cases where the decision must not be generalized |
| `rollback_condition` | Evidence that would reverse or narrow the decision |
| `review_status` | Draft, reviewed, accepted, or rejected |

This artifact records decision support. It does not execute a promotion,
rollback, or retirement action.

---

## 4. Task Slice Selection Protocol

### 4.1 Source boundary

The first candidate source is:

```text
SWE-bench Verified-derived slice
```

This does not mean:

- use all 500 tasks;
- call SWE-bench the permanent SkillNudge benchmark;
- assume repository issue resolution is pure debugging;
- use source popularity or leaderboard results as utility evidence;
- freeze a task list before artifact and oracle review.

The source is useful because it can provide a reproducible repository,
commit, issue, environment, and test-oracle substrate. SkillNudge must create
its own audited task identity, observable trace, paired conditions, and
diagnostic evidence.

### 4.2 Selection target

The hypothesis-driven pilot target is:

```text
24 tasks
4 debugging families
16 development tasks
8 held-out tasks
```

This is a pilot protocol, not a benchmark claim. The number may be reduced
before execution if reproducible tasks cannot be obtained, but the shortfall
must be recorded as a limitation and must not be described as equivalent
evidence.

Where feasible:

- each debugging family appears in both development and held-out sets;
- at least one repository is held out entirely;
- no task is duplicated across conditions as a different task identity;
- the held-out set is not used to edit, compress, select, or reject an
  Adapted Skill.

### 4.3 Debugging families

The pilot should cover four families:

| Family | Example failure shape | Observable capability under test |
| --- | --- | --- |
| Logic and boundary defects | Off-by-one, incorrect branch, empty-input behavior | Hypothesis formation and edge-case verification |
| State and data-flow defects | Stale state, wrong transformation, incorrect default | Repository exploration and causal tracing |
| Error-handling defects | Exception swallowed, wrong error path, missing validation | Failure reproduction and negative-path verification |
| Regression and integration defects | Interface mismatch or surrounding behavior break | Regression safety, recovery, and constraint handling |

These are selection and analysis labels. They are not agent-visible prompt
labels and should not be used to force a particular procedure.

### 4.4 Inclusion criteria

Include a candidate task only when manual review can establish:

- a reproducible bug or incorrect behavior from a pinned commit;
- a clear failure symptom;
- an acceptance oracle that can be run repeatedly;
- a task that requires investigation rather than only direct code generation;
- an environment that can be recorded and bounded;
- source and task provenance that can be retained;
- a reasonable chance that the intervention could change observable
  investigation, hypothesis, verification, or recovery behavior;
- a task size compatible with the pilot budget.

The candidate may still be difficult. The goal is not to select only easy tasks
that maximize pass rate.

### 4.5 Exclusion criteria

Exclude or separately label candidates that are primarily:

- feature requests;
- large refactors;
- documentation-only changes;
- formatting-only changes;
- environment-only failures;
- unclear acceptance conditions;
- flaky, time-dependent, or external-service-dependent without a stable
  substitute;
- dominated by setup or credential failure;
- impossible to reproduce from the pinned snapshot;
- likely to reveal evaluator-only metadata to the agent.

Excluded tasks are not failed model runs. They are failures of artifact
eligibility or protocol readiness.

### 4.6 Manual review record

Each candidate receives a manual review record before entering the pilot:

| Field | Values or review question |
| --- | --- |
| `task_type` | Debugging-dominant, feature, refactor, documentation, environment-only, unclear |
| `debugging_depth` | Direct repair, local investigation, multi-step investigation, repository-level diagnosis |
| `oracle_quality` | Determinism, coverage, regression protection, acceptance clarity |
| `environment_risk` | Low, medium, high, with setup and platform evidence |
| `skill_sensitivity` | Which observable behaviors could plausibly be changed by the Skill |
| `repository_diversity` | Whether the task adds independent repository or code-pattern coverage |
| `selection_decision` | Include, exclude, or defer |
| `reviewer_rationale` | Evidence supporting the decision |

`skill_sensitivity` is a hypothesis field, not a license to select only tasks
expected to favor the Skill. The final slice must preserve task diversity and
include cases where the intervention may be redundant or restrictive.

### 4.7 Development and held-out split

The development split is used to:

- verify task setup and oracle execution;
- inspect whether the Trace Artifact captures the required observable events;
- classify failure patterns;
- propose a bounded ablation or Adapted Skill;
- test whether the evidence model is usable.

The held-out split is used to:

- run the pre-registered No Skill versus Original Skill comparison;
- test transfer across task families or repositories;
- evaluate an Adapted Skill candidate after it is frozen;
- detect overfitting to development traces.

No held-out result may be used to rewrite the Adapted Skill before the held-out
decision is recorded.

### 4.8 Selection procedure

The review sequence is:

```text
source candidate
-> pin task and repository identity
-> reproduce environment and oracle
-> classify task structure
-> review debugging depth and skill sensitivity
-> assign development or held-out role
-> freeze pilot slice
```

The selection procedure ends before any live agent utility run is interpreted.
It does not download or vendor the source dataset in this documentation task.

---

## 5. Experimental Arms

### 5.1 Primary arms

The primary causal run matrix is:

```text
For each valid development and held-out task:

  Control:
    Model + Harness + Tools
    - External Skill

  Treatment:
    Model + Harness + Tools
    + Original Systematic Debugging Skill
```

The same task snapshot, issue description, environment, oracle, budgets, and
tool surface must be used for the paired conditions.

### 5.2 Evolution and ablation arms

After the Original-versus-No-Skill comparison has produced a bounded
diagnosis, development evidence may support:

```text
Full Original Skill
Skill minus verification section
Skill minus hypothesis section
Skill minus another explicitly named section
Adapted Skill
Retired Skill
```

These are not all required in the first pilot. Each added arm must answer a
specific attribution or lifecycle question and must not become an open-ended
search for a favorable result.

The intended interpretation is:

- ablation asks which section may be contributing, adding cost, or causing
  harm;
- Adapted Skill tests a versioned change derived from that diagnosis;
- Retired Skill tests whether removing a previously useful intervention
  preserves required outcomes within the tested scope.

### 5.3 Retired Skill semantics

`Retired Skill` may execute behaviorally as No Skill. It remains a separate
research condition because the lifecycle question is different:

```text
No Skill:
  no intervention was proposed or inserted

Retired Skill:
  a previously accepted intervention was deliberately removed
```

Retirement must preserve the previous version, evidence, scope, protected
cases, and rollback condition.

### 5.4 Run pairing and repetition

Results are paired by:

```text
task_id + trial_id
```

For a stochastic provider, the pilot target is at least two independent trials
per task-condition pair; three is preferred when budget allows. A deterministic
provider must be declared deterministic rather than counting repeated identical
outputs as independent evidence.

The trial policy, seed policy, and any provider nondeterminism must be recorded
before interpreting the result.

### 5.5 Protocol deviations

A run is excluded from the primary causal comparison when the model, harness,
tools, environment, task snapshot, task statement, budget, evaluator,
intervention boundary, or human assistance differs from its paired condition.

The run remains in the research record as a protocol deviation. Raw outputs
must not be manually edited to make the pair appear valid.

---

## 6. Metrics and Evidence Rules

Metrics are evidence dimensions. They are not an automatic ranking formula.

### 6.1 Outcome metrics

Outcome metrics answer:

> Did the agent solve the task while preserving required behavior?

Record:

- verified task success;
- target `FAIL_TO_PASS` behavior where applicable;
- required `PASS_TO_PASS` behavior where applicable;
- regression safety;
- constraint compliance;
- patch acceptance;
- environment and evaluator validity.

Primary success requires:

```text
target acceptance checks pass
and
required regression checks pass
and
the evaluator is valid
```

A plausible patch, a correct diagnosis without a patch, or one visible test
passing is not sufficient.

### 6.2 Efficiency metrics

Efficiency metrics answer:

> Did the intervention achieve an equivalent or better result with an
> acceptable amount of work?

Record separately:

- wall-clock time;
- total turns or steps;
- tool calls;
- redundant tool calls;
- token usage or estimated cost when available;
- time to first plausible diagnosis;
- time to first passing target check;
- retries and reverted edits;
- patch size and files touched;
- human interventions.

The report must not optimize one cost metric while hiding another.

### 6.3 Process metrics

Process metrics answer:

> What changed in the observable trajectory, and why might the intervention
> have helped or harmed?

Record observable evidence for:

- investigation and repository exploration;
- localization of the likely fault;
- hypothesis formation when emitted by the agent;
- test selection and execution;
- verification discipline;
- regression checking;
- recovery after failed attempts;
- search efficiency;
- unnecessary exploration or procedural overhead;
- strategy change and rollback.

These metrics must be derived from Trace and Oracle Artifacts. They must not
pretend to measure hidden chain-of-thought.

### 6.4 Transfer metrics

Transfer metrics answer:

> Does the observed effect extend beyond the development examples that
> motivated it?

Record:

- held-out task success;
- held-out regression safety;
- held-out efficiency;
- transfer across debugging families;
- transfer across repositories;
- effect consistency by task family;
- cases where the Skill is neutral or harmful.

An effect observed only on development tasks is evidence for further research,
not evidence of a promoted intervention.

### 6.5 Validity and coverage metrics

Before utility analysis, report:

- number of eligible tasks;
- number of valid runs by condition;
- number of environment failures;
- number of evaluator failures;
- number of protocol deviations;
- number of excluded or ambiguous tasks;
- trial completion rate;
- missing Trace or Oracle fields.

Validity failures are evidence about experiment readiness, not evidence for or
against the Skill.

### 6.6 Failure taxonomy

The first taxonomy is deliberately small:

| Code | Failure or behavior | Observable meaning |
| --- | --- | --- |
| `F1` | Wrong localization | The agent focused on the wrong file, symbol, or causal region |
| `F2` | Insufficient hypothesis | The agent did not form, revise, or test a useful explanation |
| `F3` | Missing verification | The agent edited or concluded without adequate target or regression checks |
| `F4` | Over-exploration | The agent spent substantial effort on low-value search or investigation |
| `F5` | Regression introduction | The target appeared fixed but required surrounding behavior broke |
| `F6` | Unnecessary procedure overhead | The Skill added steps, context, or tool calls without corresponding benefit |

The taxonomy is diagnostic, not a hidden score. Multiple codes may apply to
one run. New categories may be proposed only when recurring evidence cannot be
represented by the existing categories.

The following are not Skill failure categories:

- environment setup failure;
- evaluator failure;
- unresolved task ambiguity;
- missing provider authorization;
- an unrecorded protocol deviation.

### 6.7 Evidence sufficiency

A utility conclusion requires, at minimum:

1. a valid paired control/treatment comparison;
2. a verified oracle result;
3. enough valid trials to state the uncertainty;
4. an observable trajectory or explicit explanation of the observation limit;
5. a failure or mechanism diagnosis when the result is non-neutral;
6. held-out or otherwise transfer evidence before promotion beyond development;
7. no unresolved environment or evaluator failure that explains the outcome.

If these conditions are not met, the correct result is `INCONCLUSIVE` or
`PROTOCOL_FAILURE`, not `NEUTRAL`.

### 6.8 Uncertainty treatment

The report should include:

- per-task outcomes;
- paired task-level changes;
- per-family outcomes;
- aggregate summaries;
- confidence intervals, bootstrap intervals, or another declared uncertainty
  method appropriate to the data;
- cost distributions rather than only averages;
- failure-category transitions;
- development versus held-out separation.

The pilot is small. It should not make population-level claims from a narrow
sample or treat a tiny numerical difference as durable utility.

---

## 7. Decision Rules

These are evidence rules for research review. They are not automatic runtime
behavior and do not promote or retire a Skill by themselves.

### 7.1 Result classification

#### `SKILL_HELPS`

Use this classification only when:

- the Original Skill improves verified task success or a pre-registered
  efficiency outcome;
- the result is visible in paired task analysis, not only one aggregate;
- there is no unacceptable regression, constraint, or environment effect;
- the effect is reproduced across trials or is otherwise supported by declared
  uncertainty;
- held-out tasks show transfer within the stated scope.

The conclusion must name the tested model, harness, task family, environment,
and evaluation window.

#### `SKILL_NEUTRAL`

Use this classification when:

- the comparison is valid;
- no credible outcome or efficiency improvement is observed;
- no material harm is observed;
- the evidence is sufficient to distinguish a small effect from missing data
  or infrastructure failure.

Neutral means utility was not demonstrated in the tested scope. It does not
mean the Skill is globally useless.

#### `SKILL_HURTS`

Use this classification when:

- verified success decreases;
- regression or constraint failures increase;
- the intervention causes material, uncompensated cost;
- or a repeated failure pattern shows over-constraint or procedure harm;
- and the effect is not explained by environment, evaluator, or protocol
  failure.

One anomalous trajectory is a diagnostic signal, not sufficient evidence for a
global retirement decision.

#### `INCONCLUSIVE`

Use this classification when:

- the task set or trial count cannot separate effect from noise;
- the trajectory record is insufficient to diagnose the outcome;
- transfer was not tested where promotion is being considered;
- or the result is compatible with materially different explanations.

Inconclusive evidence should improve the experiment protocol before changing
the intervention.

#### `PROTOCOL_FAILURE`

Use this classification when:

- the control and treatment were not comparable;
- the model, harness, tools, environment, evaluator, or budget changed;
- an evaluator or setup failure invalidated the result;
- or agent-visible leakage changed the treatment.

Protocol failure is preserved for audit and excluded from utility conclusions.

### 7.2 Lifecycle action rules

| Action | Evidence pattern | Scope |
| --- | --- | --- |
| Keep | Repeatable verified utility with acceptable cost, safety, and held-out transfer | Keep for the tested model, harness, task family, environment, and evidence window |
| Compress | Equivalent verified outcome remains after removing a named section, with lower cost or less overhead | Compress only the supported redundant section and re-evaluate |
| Modify | A named section causes a reproducible failure or ambiguity and a bounded change addresses it | Create a versioned Adapted Skill and test it on held-out tasks |
| Replace | Another bounded intervention addresses the same capability need with stronger evidence or fewer harms | Compare under the same baseline and scope |
| Retire | No measurable utility remains or consistent harm persists after validity and protected-case checks | Remove from the tested execution scope and retain rollback evidence |
| No decision | Evidence is neutral but insufficient, inconclusive, or protocol-invalid | Collect better evidence; do not force a lifecycle action |

### 7.3 Specific evidence patterns

The experiment must be able to distinguish:

```text
success improvement
  + acceptable cost
  + transfer evidence
  -> support KEEP
```

```text
same outcome
  + lower cost after removing a named section
  -> support COMPRESS
```

```text
benefit exists
  + recurring, diagnosable failure pattern
  -> support MODIFY
```

```text
alternative intervention dominates
  + same capability need
  + cleaner or safer evidence
  -> support REPLACE
```

```text
no measurable utility
  or
consistent harm
  + valid comparison
  + no protected-case exception
  -> support RETIRE within tested scope
```

These are decision patterns, not automatic thresholds. Numeric thresholds for
material cost, acceptable regression, and minimum effect size must be reviewed
and frozen before interpreting live results.

### 7.4 Protected cases and scope

A debugging Skill may have value that the first task slice does not measure,
such as private organizational procedure, compliance, tool-specific knowledge,
or a protected failure mode.

Therefore:

- no result retires a capability globally by default;
- protected cases must be recorded before a retirement decision;
- decisions are scoped to model, harness, task family, environment, and
  evaluation window;
- rollback must remain possible;
- a later positive result does not erase earlier harm; it narrows the
  intervention scope or changes the decision policy.

---

## 8. Evolution and Ablation Protocol

### 8.1 Why ablation is needed

The Original Skill may contain multiple behaviors:

- problem decomposition;
- hypothesis formation;
- search or inspection procedure;
- verification checklist;
- output or handoff format;
- recovery instructions.

A full-treatment effect does not prove that every section contributed. A
section-level diagnosis is required before compression or modification.

### 8.2 Allowed development probes

After the primary comparison, development-only probes may include:

```text
Original Skill
minus verification section
Original Skill
minus hypothesis section
Original Skill
minus prescribed search section
No Skill
```

The exact ablation must be linked to an observed F-category or redundancy
claim. Do not create a combinatorial grid merely to search for a favorable
number.

### 8.3 Adapted Skill requirements

Every Adapted Skill proposal must record:

- source version and content hash;
- changed section;
- evidence that motivated the change;
- intended behavior preserved;
- behavior intentionally removed or changed;
- expected benefit;
- possible regression;
- development evidence;
- held-out test required for promotion;
- rollback target.

An LLM-generated rewrite is only a candidate artifact. It is not evidence of
improvement and cannot be promoted without a named comparison.

### 8.4 Evolution sequence

```text
valid development evidence
-> bounded diagnosis
-> versioned Adapted Skill proposal
-> frozen candidate
-> held-out evaluation
-> keep, rollback, modify, replace, or retire decision
```

Held-out results must not be fed back into the Adapted Skill before the
held-out decision is recorded.

---

## 9. North Star Alignment Review

**Lifecycle stage:**

```text
OBSERVE / DIAGNOSE
```

Supporting stage:

```text
EVOLVE
```

**Research question:**

> Does the evidence model allow SkillNudge to determine whether the
> Systematic Debugging Skill should exist for a defined model, harness, task
> family, and environment?

**Capability decision evidence:**

The card produces the protocol and artifact structure required to support
`KEEP`, `COMPRESS`, `MODIFY`, `REPLACE`, `RETIRE`, or `NO DECISION`. It does not
make one of those decisions before data exists.

**Baseline:**

```text
Control:
  Model + Harness + Tools - External Skill

Treatment:
  Model + Harness + Tools + Original Skill
```

**Trajectory observability:**

The Trace Artifact captures observable search, inspection, test execution,
verification, recovery, and termination events. Hidden chain-of-thought is out
of scope.

**Expected evolution decision:**

The result may justify keeping the Original Skill, compressing a named
section, modifying a diagnosed failure mode, replacing the intervention,
retiring it within scope, or collecting more evidence.

**Gate result:**

```text
PASS FOR RESEARCH DESIGN
NOT AUTHORIZATION FOR PHASE 2 IMPLEMENTATION
```

---

## 10. Questions the Experiment Must Answer

Before any Phase 2 implementation is proposed, the research record must
answer:

1. **What exactly is the intervention artifact?**
   What source, version, license, content hash, insertion boundary, and
   agent-visible content define the Original Skill?

2. **What exactly is the control condition?**
   What does the No Skill agent receive, and which model, harness, tools,
   environment, evaluator, budget, and task inputs are held constant?

3. **What evidence proves utility?**
   Which verified outcome, cost, process, safety, and held-out evidence shows
   that the intervention changed the trajectory beneficially?

4. **What evidence proves redundancy?**
   Which ablation or compression comparison preserves the required outcome
   while removing a named section or reducing procedural overhead?

5. **What evidence justifies evolution?**
   Which observed failure pattern motivates a bounded Adapted Skill, and what
   held-out result would promote or roll it back?

6. **Are we measuring capability utility or benchmark performance?**
   Can the result explain the intervention's effect and support a lifecycle
   decision, rather than only report a pass rate?

If any answer is unknown, the unknown must be recorded with an evidence plan.
It must not be silently treated as a pass.

---

## 11. Frozen Research Decisions

This v0.2 card freezes the following design choices for the next review:

1. The evidence model is designed from lifecycle decision requirements, not
   from a dataset schema alone.
2. The experiment uses six linked artifact classes:
   Experiment Run, Task Artifact, Trace Artifact, Oracle Artifact, Diagnostic
   Artifact, and Evolution Decision Evidence.
3. Trace capture records observable behavior and does not collect hidden
   chain-of-thought.
4. The first source direction is a manually audited SWE-bench Verified-derived
   slice, not the full 500-task source set.
5. The pilot target is 24 tasks, four debugging families, and a
   development/held-out split of 16/8, subject to artifact availability and
   explicit shortfall reporting.
6. The primary causal arms are No Skill and Original Skill under fixed
   model, harness, tools, environment, task, budget, and evaluator.
7. Adapted, ablation, and Retired conditions are secondary lifecycle probes
   and require development evidence and versioned provenance.
8. Outcome, efficiency, process, transfer, and validity evidence remain
   separately visible.
9. The initial failure taxonomy is F1 through F6:
   localization, hypothesis, verification, exploration, regression, and
   unnecessary procedure overhead.
10. Environment failure, evaluation failure, and task ambiguity are not Skill
    failure evidence.
11. Keep, compress, modify, replace, and retire are evidence-gated,
    scope-bounded decisions, not automatic consequences of one run.
12. This card does not freeze a final dataset and does not authorize Phase 2
    implementation.

---

## 12. Remaining Uncertainties

The following remain open:

- Which exact Systematic Debugging Skill artifact is the canonical Original
  Skill, and what provenance can be retained?
- Which 24 source tasks satisfy the inclusion criteria after manual and oracle
  review?
- Is 24 tasks with two or three trials per pair enough to distinguish a useful
  effect from stochastic noise?
- Which repository or task should be held out entirely?
- What exact definitions and thresholds should count as material cost,
  unacceptable regression, or minimum effect?
- Can all selected environments be reproduced without provider, network, or
  credential failure?
- Which observable events are sufficient to label hypothesis formation without
  collecting hidden reasoning?
- Which failure taxonomy categories can be assigned reliably by independent
  reviewers?
- How should patch quality be handled when tests pass but maintainability or
  latent defects differ?
- What evidence is required before a task-family-specific retirement becomes a
  broader routing or lifecycle policy?
- Which later model or harness comparisons are needed to test utility drift
  rather than one fixed configuration?

These questions are research dependencies, not permission to start coding.

---

## 13. Phase 2 Implementation Gate

Phase 2 implementation must not start from this document alone.

Before a separate implementation change is proposed, the project must review:

1. the canonical intervention artifact and provenance;
2. the manually audited task slice and its oracle records;
3. the fixed model, harness, tools, provider, and environment configuration;
4. the Trace and Oracle Artifact capture boundary;
5. the repetition and uncertainty policy;
6. the development/held-out split;
7. the lifecycle decision thresholds and protected-case policy;
8. the publish and credential exclusion gate for any local configuration;
9. the exact implementation scope and its non-interference with Phase 1.

The decision to begin Phase 2 coding is a later human-reviewed change. This
document only defines what the experiment must be able to establish.

---

## 14. Scope and Validation Record

This document is documentation-only.

Required validation for this change:

```text
git diff --check
./scripts/check_publish_gate.sh
```

Expected scope result:

```text
only documentation changed
no runtime code changed
no dependencies changed
no dataset downloaded
Phase 2 implementation NOT started
```
