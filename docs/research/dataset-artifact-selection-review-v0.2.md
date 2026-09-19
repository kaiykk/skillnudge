# Dataset Artifact Selection Review v0.2

**Status:** RESEARCH DIRECTION REVIEW / FINAL TASK SET NOT FROZEN
**Date:** 2026-09-19
**Scope:** Task artifact selection for the first Skill Utility experiment

SkillNudge Phase 2 is not a benchmark project.

The North Star question is:

> When should an external capability intervention exist?

The first utility experiment compares:

```text
Control:
  No Skill

Treatment:
  Original Systematic Debugging Skill
```

The task artifact is therefore not selected because it gives the highest
benchmark score. It is selected because it can support a clean comparison of
agent trajectories and a later lifecycle decision:

```text
KEEP
COMPRESS
MODIFY
REPLACE
RETIRE
```

This review does not:

- implement an evaluation runtime;
- implement a benchmark runner;
- download or vendor any dataset;
- execute tasks;
- modify Phase 1 or Phase 2 runtime;
- modify retrieval, Planning, Judge, CLI, or contracts;
- freeze a final dataset;
- start Phase 2 implementation.

---

## 1. Decision Question

### Why task artifact selection is causal experiment design

A task artifact determines what the agent can encounter, what counts as
success, which failures are visible, and which intervention effects can be
detected.

The same Skill can appear useful or harmful depending on the task artifact:

```text
Tasks require long investigation
  -> procedural Skill may appear unusually useful

Tasks are trivial one-line fixes
  -> the same Skill may only add overhead

Tasks are too difficult for both conditions
  -> the Skill may appear neutral because it cannot rescue the task

Oracle checks only visible tests
  -> a lucky patch may appear successful

Environment is unstable
  -> infrastructure failure may be misclassified as Skill failure
```

Task artifact selection therefore determines whether the experiment can
distinguish:

```text
Skill helps
Skill is neutral
Skill hurts
Experiment is inconclusive
```

The artifact must support a paired No Skill versus Skill comparison, but it
must also preserve enough context to explain why the paired outcomes differ.

### What this review is and is not

This is a research direction review. It selects a base artifact strategy and a
task-slice protocol, not a final list of tasks.

The output should answer:

1. What task artifact should SkillNudge use first?
2. What evidence can that artifact produce?
3. What evidence does it not produce?
4. What biases must be controlled before interpreting utility?
5. What selection protocol should freeze the first pilot slice later?

---

## 2. Task Artifact Requirements

The first experiment requires a task artifact with the following minimum
properties.

```yaml
task_requirements:
  repository_context: required
  debugging_nature: required
  oracle: required
  reproducibility: required
  trajectory_visibility: preferred
  task_family_diversity: required
  negative_cases: required
```

### Repository context: required

The task should expose a real or realistically structured repository snapshot,
not only an isolated code fragment.

Why:

- systematic debugging includes exploration and localization;
- the agent may need to trace data flow across files;
- regression behavior is often outside the immediately failing line;
- repository context allows trajectory evidence beyond code regeneration.

Repository context does not require every task to be large. A small repository
is acceptable when the investigation boundary is explicit and reproducible.

### Debugging nature: required

The task must involve an incorrect behavior, failing test, regression,
integration failure, state problem, or another defect that requires diagnosis.

A repository-level feature request or broad refactor is not automatically a
debugging task. It may be useful for another experiment, but it should not be
silently counted as evidence for Systematic Debugging Skill utility.

### Oracle: required

The task must have an executable or otherwise reviewable acceptance condition.
The oracle should distinguish:

```text
target behavior fixed
required surrounding behavior preserved
evaluation itself valid
```

The oracle should preserve target checks and regression checks separately where
possible. A final patch that looks plausible is not sufficient.

### Reproducibility: required

The repository commit, environment, dependencies, test command, evaluator,
and relevant configuration must be pin-able.

Reproducibility includes the ability to classify setup failure separately from
agent failure. A task that cannot be reproduced should be excluded or marked
as an artifact failure, not counted as a failed treatment run.

### Trajectory visibility: preferred

The task artifact itself does not need to contain historical agent
trajectories. The future experiment harness can capture them. However, the
task must permit observation of:

- repository exploration;
- error reproduction;
- hypothesis formation when the agent emits one;
- test and verification behavior;
- regression checking;
- recovery after failed fixes;
- unnecessary exploration or procedural overhead.

An artifact with only a final pass/fail signal is insufficient for diagnosing
why a Skill helped or harmed.

### Task-family diversity: required

The task slice must include multiple debugging families. Otherwise the
experiment may only prove that the Skill fits one narrow defect shape.

The proposed families are defined in Section 5.

### Negative cases: required

The slice must include tasks where a strong procedure may be redundant or
harmful:

- obvious one-line bugs;
- direct compiler or type errors;
- simple failing tests with a local cause;
- tasks where a long investigation is unnecessary.

Negative cases are not adversarial traps. They test whether the intervention
can remain conditional rather than forcing the same process everywhere.

---

## 3. Dataset Comparison Matrix

The candidates are evaluated by the question each can answer, not by a single
rank.

| Dataset type | What question it answers | Strength | Weakness | Utility Experiment Fit |
| --- | --- | --- | --- | --- |
| SWE-bench Verified | Can an agent resolve a human-filtered repository issue under a task-specific test oracle? | Strong repository context, task metadata, and reviewed oracle boundary | Not debugging-pure; no native intervention traces; environment is heavy | **Strong base substrate after manual audit** |
| SWE-bench Lite | Can an agent resolve a smaller, lower-cost subset of repository issues? | Lower pilot cost and easier initial coverage | Selection effects, less task coverage, still not debugging-pure, no native traces | **Good feasibility substrate or fallback** |
| DebugBench / debugging-focused datasets | Can a model repair controlled buggy programs across bug categories and languages? | Stronger debugging specificity and category coverage | Often snippet-level or synthetic; artifact and oracle packaging may be unresolved; weak repository context | **Diagnostic probe or complementary slice, not default base** |
| Agent trajectory datasets | What investigation, tool-use, verification, waste, and recovery patterns appear in historical runs? | Rich process-level evidence | No clean No Skill versus Skill counterfactual; model/harness confounding | **Diagnostic and metric-design supplement** |

### Candidate A: SWE-bench Verified

#### What it can answer

SWE-bench Verified can provide a repository, issue, base commit, environment,
patch target, and task-specific test boundary for a paired experiment.

The current public SWE-bench information describes Verified as a
human-filtered 500-instance subset, while Lite is a lower-cost 300-instance
subset. These labels identify available source artifacts; they do not make
either artifact a complete SkillNudge utility experiment. See Sources 1
through 5.

#### Why it is useful

- real repository and issue context;
- task-specific `FAIL_TO_PASS` and `PASS_TO_PASS` style oracle fields;
- a path to pinned base commits and task environments;
- a natural control/treatment pairing;
- enough heterogeneity to construct a small debugging-focused slice.

#### What it cannot answer by itself

- whether the trajectory was systematic;
- whether the agent formed and tested a useful hypothesis;
- whether a successful patch was lucky;
- whether the Skill was necessary rather than merely compatible;
- whether an intervention should be kept outside the tested scope.

Those questions require a trace artifact and paired execution records.

#### North Star role

```text
Primary task and oracle substrate
```

It is not, by itself:

```text
Skill utility evidence
```

### Candidate B: SWE-bench Lite

#### What it can answer

Lite can support a smaller, lower-cost repository-level pilot using the same
general task/oracle structure as SWE-bench.

#### Advantages for the first pilot

- smaller initial execution burden;
- easier to inspect the entire candidate source set before selecting a slice;
- lower risk of committing to a large evaluation operation before the trace
  protocol is usable;
- useful for validating environment and oracle handling.

#### Disadvantages

- the smaller subset may have its own selection bias;
- lower cost does not imply better debugging sensitivity;
- task-family diversity may be narrower;
- it remains a repository issue-resolution artifact rather than a
  debugging-pure artifact;
- its oracle does not expose the intervention trajectory.

#### North Star role

```text
Feasibility substrate or bounded pilot fallback
```

Lite is attractive if Verified-derived task setup proves too expensive, but
the switch should be recorded as a change in evidence scope, not treated as a
drop-in replacement.

### Candidate C: DebugBench and debugging-focused datasets

#### What it can answer

DebugBench is designed to measure debugging performance across controlled bug
categories and languages. The paper describes 4,253 instances, four major bug
categories, and 18 minor types, with bugs injected into collected code and
checked through quality-control procedures. See Source 6.

This makes the family useful for asking:

```text
Does a debugging procedure change behavior on known bug types?
```

#### Advantages

- stronger debugging-specific framing;
- easier category-based coverage analysis;
- potential for controlled bug families;
- possible sensitivity to hypothesis, feedback, and verification behavior.

#### Disadvantages

- snippet or problem-level tasks may remove repository navigation;
- synthetic bug injection may create unnatural locality or repair patterns;
- code regeneration can substitute for diagnosis;
- runtime feedback can become a confounding treatment;
- exact public packaging, evaluator, license, and environment may require
  additional artifact verification.

#### North Star role

```text
Debugging-specific diagnostic probe
```

It may answer whether the Skill changes controlled debugging behavior, but it
does not automatically establish transfer to repository-level intervention
utility.

### Candidate D: Agent trajectory datasets

#### What they can answer

SWE-agent and OpenHands trajectory resources can help answer:

```text
Which observable process signals distinguish useful,
wasteful, lucky, or failed agent behavior?
```

They are particularly useful for designing:

- hypothesis proxies;
- investigation and search metrics;
- verification discipline measures;
- retry and recovery labels;
- regression and waste taxonomies.

#### Advantages

- rich action, tool, observation, patch, and outcome records;
- direct visibility into process rather than only final success;
- useful source of failure patterns and metric candidates;
- can expose lucky-pass or blind-retry behavior that binary evaluation hides.

#### Disadvantages

- historical trajectories do not provide the No Skill counterfactual;
- model, harness, prompt, tool, and evaluator are confounded;
- original collection environment may be difficult to reproduce;
- source-repository and model-output license boundaries may vary;
- using historical traces to design the Skill can leak the target procedure.

#### North Star role

```text
Trajectory diagnostic source
```

They should not be used as the causal task artifact for the first utility
experiment.

---

## 4. Bias Analysis

### 4.1 Skill alignment bias

If every selected task requires long, multi-step debugging, the Systematic
Debugging Skill may look useful because the task distribution was chosen for
it.

If every task is a direct local fix, the same Skill may look neutral or harmful
because the procedure is unnecessary.

Mitigation:

- include low, medium, and high Skill-sensitivity tasks;
- include negative-utility candidates;
- report effects by task family and sensitivity level;
- do not select only tasks expected to favor the intervention.

### 4.2 Difficulty bias

Tasks that are too easy may hide capability differences. Tasks that are too
hard may cause both conditions to fail for unrelated reasons.

Mitigation:

- record baseline difficulty evidence during task audit;
- preserve a mixture of local and multi-step debugging;
- separate unresolved agent failure from environment or oracle failure;
- do not use average pass rate as the only decision signal.

### 4.3 Oracle bias

Tests may fail to capture better investigation, maintainability, or a correct
but differently structured repair. Conversely, a patch may pass visible tests
without reflecting a disciplined debugging process.

Mitigation:

- preserve target and regression checks separately;
- record the evaluator version and test scope;
- capture observable traces;
- classify lucky or blind success as a diagnostic concern;
- do not replace the oracle with unbounded human preference.

### 4.4 Environment failure

The task artifact must distinguish:

```text
agent failure:
  the agent had a valid environment but did not solve the task

environment failure:
  setup, dependency, container, network, credential, or platform failure

evaluation failure:
  the oracle or evaluator could not validly determine the result

task ambiguity:
  the task or acceptance condition was not sufficiently clear
```

Only valid agent outcomes should enter the primary Skill utility comparison.
The other classes remain important evidence about artifact readiness.

### 4.5 Contamination risk

Public issue text, repository states, reference patches, and tests may have
appeared in model training data. A successful treatment may reflect memorized
task knowledge rather than a procedural intervention.

Mitigation:

- record task age and public availability where practical;
- avoid exposing reference patches or evaluator-only fields;
- treat success as scoped evidence;
- prioritize trajectory changes and verification behavior;
- do not claim model-independent Skill utility.

### 4.6 Trajectory leakage

Historical agent traces may already contain systematic debugging behavior.
Using them to design the task slice or Skill wording can leak the intended
strategy into the treatment.

Mitigation:

- use trajectories for metric and failure taxonomy design;
- keep the selected task slice and treatment wording separate;
- do not expose historical trace text to the agent;
- record whether a task was used for development or held-out evaluation.

### 4.7 Repository and language bias

SWE-bench-derived tasks are concentrated in repository and language
ecosystems. DebugBench may emphasize other languages or snippet shapes.

Mitigation:

- report repository and language coverage;
- avoid general claims beyond the tested scope;
- use DebugBench as a diagnostic comparison unless its environment is
  independently verified;
- preserve repository-level context for the primary experiment.

---

## 5. Proposed First Task Slice Design

This section defines a selection protocol, not a final dataset.

### 5.1 Recommended base direction

```yaml
base_dataset_direction:
  source: SWE-bench Verified-derived task/oracle substrate
  use_all_source_tasks: false
  final_task_set_frozen: false
  role: primary repository-level task and oracle substrate
```

The source artifact should be manually filtered and independently audited.
The source dataset's category or benchmark identity must not replace a
SkillNudge task identity.

### 5.2 Task families

The first slice should target four families:

| Family | Task shape | Why it exists |
| --- | --- | --- |
| A. Root-cause localization | The visible symptom is separated from the actual fault location | Tests repository exploration, evidence gathering, and localization |
| B. Regression debugging | A change or interaction breaks previously valid behavior | Tests PASS_TO_PASS preservation, regression checking, and recovery |
| C. Dependency or integration issue | The failure crosses modules, interfaces, versions, or external boundaries | Tests multi-component evidence gathering and assumption checking |
| D. Timing or state issue | The failure depends on state propagation, ordering, waiting, or lifecycle behavior | Tests reproduction discipline, data-flow tracing, and condition-based verification |

These family labels are for task selection and diagnosis. They must not be
shown to the agent as a hint about the expected procedure.

### 5.3 Sensitivity dimension

Each candidate task receives a pre-run hypothesis about Skill sensitivity:

```text
Low:
  A direct local fix is likely sufficient.

Medium:
  Investigation is required but the fault boundary is relatively local.

High:
  Multiple files, hypotheses, dependencies, state transitions, or recovery
  attempts are likely required.
```

Examples:

| Sensitivity | Example | Why include |
| --- | --- | --- |
| Low | Obvious one-line bug, direct compiler error, simple failing test | Detects unnecessary procedure overhead and negative utility |
| Medium | Single-module bug requiring reproduction and one hypothesis test | Tests whether the Skill improves discipline without overwhelming the task |
| High | Multi-step localization, regression, dependency, timing, or state issue | Tests the intended systematic debugging capability |

`skill_sensitivity` is not a selection score that maximizes expected treatment
benefit. The slice should preserve all three levels where available.

### 5.4 Negative utility candidates

The slice must deliberately retain candidate tasks where the Skill may hurt:

- an obvious one-line fix;
- a direct compiler or type error;
- a simple failing test with a local cause;
- a task where exhaustive exploration is unnecessary;
- a task where an existing clear test already identifies the fault.

Expected risks:

- extra tool calls;
- delayed repair;
- unnecessary hypothesis narration;
- refusal to take a direct fix;
- over-editing;
- false claims that a simple task requires architectural investigation.

These cases are necessary to test whether the intervention should be
conditional rather than permanently active.

### 5.5 Candidate task review fields

Each source candidate should receive a manual review record:

| Field | Review question |
| --- | --- |
| `task_id` | Can the task be given a stable local identity? |
| `repository` | What repository and license/provenance apply? |
| `commit` | Is the base snapshot immutable? |
| `task_type` | Debugging-dominant, feature, refactor, documentation, environment-only, or unclear? |
| `debugging_family` | A, B, C, or D? |
| `debugging_depth` | Local, multi-step, cross-component, stateful, or unclear? |
| `skill_sensitivity` | Low, medium, or high hypothesis? |
| `oracle_quality` | Are target and regression checks deterministic and meaningful? |
| `environment_risk` | Is setup likely to dominate agent behavior? |
| `trajectory_visibility` | Can investigation, verification, and recovery be observed? |
| `negative_case` | Could the Skill plausibly add unnecessary procedure? |
| `selection_decision` | Include, exclude, or defer? |
| `selection_rationale` | What evidence supports the decision? |

### 5.6 Inclusion criteria

Include a task only when:

- repository and base commit are pinned;
- the bug or incorrect behavior is reproducible;
- a target oracle exists;
- required regression behavior is identifiable;
- the task requires at least some investigation;
- environment risk is bounded and recordable;
- source and redistribution boundaries are understood;
- the task can be paired across No Skill and Original Skill;
- the task contributes useful family or sensitivity coverage.

### 5.7 Exclusion criteria

Exclude or separately label tasks that are primarily:

- feature requests;
- broad refactors;
- documentation-only changes;
- environment-only failures;
- unclear acceptance;
- flaky or time-dependent without a stable reproduction;
- dependent on private credentials or private organizational knowledge;
- dominated by setup rather than debugging;
- missing a valid regression or target oracle.

An excluded task is not an agent failure.

### 5.8 Pilot size and split

The working pilot target remains:

```yaml
pilot_size:
  total_tasks: 24
  debugging_families: 4
  development_tasks: 16
  held_out_tasks: 8
  preferred_trials_per_task_condition: 2
  preferred_trials_if_budget_allows: 3
```

This is a hypothesis-driven pilot, not a benchmark.

The split should:

- preserve all four families across development and held-out where feasible;
- hold out at least one repository if artifact coverage allows;
- prevent held-out results from being used to rewrite the Skill;
- report any shortfall rather than silently shrinking the evidence claim.

### 5.9 What the task artifact supplies and what the harness supplies

The task artifact should supply:

```text
task_id
repository
base commit
issue description
environment metadata
target oracle
regression oracle
reference patch metadata
provenance
selection labels
```

The future experiment harness must supply:

```text
No Skill or Original Skill condition
observable Trace Artifact
run configuration
tool and step records
Oracle Artifact execution
agent/environment/evaluation failure separation
paired comparison
```

No task artifact can provide the causal counterfactual by itself.

---

## 6. Recommendation

### Recommended direction

```yaml
base_dataset:
  SWE-bench Verified-derived manually audited slice

selection_strategy:
  - start from task/oracle metadata
  - manually classify debugging nature and family
  - verify reproducibility and oracle quality
  - assign low/medium/high Skill sensitivity hypothesis
  - preserve negative utility candidates
  - create development/held-out split
  - freeze only after artifact and oracle audit

pilot_size:
  24 tasks target
  4 debugging families
  16 development
  8 held-out

supplements:
  DebugBench-style categories for debugging-specific coverage analysis
  Agent trajectory datasets for process metrics and failure taxonomy design

final_dataset_frozen:
  false
```

### Why this supports the North Star

This direction provides the clearest separation of roles:

```text
Verified-derived slice:
  task and oracle substrate

Fresh No Skill vs Original Skill runs:
  causal intervention comparison

Trace Artifact:
  trajectory visibility

DebugBench categories:
  debugging-specific coverage lens

Historical trajectories:
  process-metric and failure-taxonomy reference

Diagnostic Artifact:
  explanation of why the intervention helped, was neutral, or hurt
```

It does not pretend that one dataset solves every evidence problem.

The direction can support:

```text
success improvement
  -> KEEP candidate

same success, lower cost after removing a section
  -> COMPRESS candidate

benefit with a recurring named failure
  -> MODIFY candidate

another bounded intervention dominates
  -> REPLACE candidate

no utility or consistent harm under valid evidence
  -> RETIRE within tested scope
```

The recommendation is therefore about causal usefulness, not benchmark
prestige.

### Why not freeze the full Verified or Lite dataset

Using all source tasks would make the first phase harder to audit and would
increase the chance that task-family impurity, environment failures, or
contamination dominate the result.

The first experiment needs a small, inspectable, falsifiable slice. Full-scale
evaluation can be considered only after the trace, oracle, and failure
classification protocol is shown to work.

### Why not make DebugBench the base by default

DebugBench may provide cleaner debugging categories, but controlled or
synthetic bug repair can reduce the repository exploration and recovery
behaviors that the selected Skill claims to affect.

It is better used as:

```text
coverage lens
diagnostic probe
future complementary task family
```

unless its exact artifact package, oracle, environment, and license are
independently verified.

### Why not use historical trajectories as the task artifact

Historical trajectories are excellent for observing process, but they do not
give the same task, model, harness, and environment under No Skill and Skill.
They can inform what to observe, not prove the intervention caused the
difference.

---

## 7. Remaining Unknowns

The following questions remain unresolved before the task slice can be frozen:

1. Which exact Verified source tasks are debugging-dominant rather than
   feature, navigation, or general maintenance tasks?
2. Is the 24-task target feasible with enough repository and family diversity?
3. Which task should be held out by repository rather than only by issue?
4. What minimum oracle review is required before a task becomes eligible?
5. What contamination evidence can be collected for the selected model?
6. Which environment failures are common enough to require task exclusion?
7. Can the Trace Artifact observe hypothesis formation without collecting
   hidden chain-of-thought?
8. Which historical trajectory fields are reliable enough to inform process
   metrics?
9. How should target success, regression safety, cost, and process evidence be
   combined without inventing a premature universal utility score?
10. What numeric thresholds define material cost, unacceptable regression, and
    sufficient transfer?
11. Which DebugBench artifact, if any, can be independently verified for
    packaging, oracle, license, and reproducibility?
12. What evidence would justify switching from a Verified-derived base slice to
    a Lite-derived slice?

These are evidence dependencies, not permission to start task execution or
Phase 2 implementation.

---

## 8. North Star Alignment Review

```yaml
Lifecycle_stage:
  OBSERVE / DIAGNOSE

Research_question:
  Which task artifact best isolates whether the Original Systematic Debugging
  Skill changes an agent trajectory in a useful way?

Evidence_produced:
  - task artifact requirements
  - candidate role comparison
  - oracle and reproducibility analysis
  - trajectory visibility boundary
  - bias and contamination analysis
  - negative utility task protocol
  - development/held-out selection protocol

Decision_enabled:
  KEEP / COMPRESS / MODIFY / REPLACE / RETIRE

Decision_not_yet_enabled:
  No utility decision before paired runs and valid diagnostic evidence

Gate:
  CONDITIONAL PASS
```

### Gate interpretation

The review passes as a research direction because it defines a task/oracle
substrate, a causal comparison, and a route to trajectory diagnosis.

It remains conditional because:

- the final task list is not frozen;
- source task and oracle audits have not been performed;
- contamination and environment risk are not yet resolved;
- the future Trace Artifact has not been exercised on real tasks;
- no live No Skill versus Original Skill run has been executed.

---

## 9. Validation and Scope Record

This change is documentation-only.

Expected validation:

```text
git diff --check
./scripts/check_publish_gate.sh
```

Required confirmation:

```text
documentation only: yes
runtime changes: no
benchmark downloaded: no
external repository vendored: no
dependency changes: no
task execution started: no
Phase 2 implementation started: no
```

---

## Sources

The following public sources were used as evidence references. No dataset or
repository was downloaded into SkillNudge.

1. Official SWE-bench overview and dataset family:
   https://www.swebench.com/
2. SWE-bench repository and evaluation tooling:
   https://github.com/SWE-bench/SWE-bench
3. SWE-bench Lite dataset card:
   https://huggingface.co/datasets/SWE-bench/SWE-bench_Lite
4. SWE-bench Verified dataset card:
   https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified
5. Official SWE-bench Verified report:
   https://openai.com/index/introducing-swe-bench-verified/
6. DebugBench paper:
   https://arxiv.org/abs/2401.04621
7. SWE-agent trajectory dataset:
   https://huggingface.co/datasets/nebius/SWE-agent-trajectories
8. OpenHands trajectory dataset:
   https://huggingface.co/datasets/nebius/SWE-rebench-openhands-trajectories
9. AgentLens trajectory analysis:
   https://arxiv.org/abs/2605.12925

Related local design documents:

- [Skill Utility Drift Experiment Card v0.2](/Users/kai/Desktop/Work/github/kaiykk/skillnudge/docs/research/skill-utility-drift-experiment-card-v0.2.md)
- [Dataset Artifact Selection Review v0.1](/Users/kai/Desktop/Work/github/kaiykk/skillnudge/docs/research/dataset-artifact-selection-review-v0.1.md)
- [North Star Gate v0.1](/Users/kai/Desktop/Work/github/kaiykk/skillnudge/docs/north-star-gate.md)
