# Task Slice Selection Protocol v0.1

**Status:** RESEARCH PROTOCOL / FINAL TASK SET NOT FROZEN
**Date:** 2026-09-19
**Scope:** Candidate mining, task audit, balance, and split design only

This protocol defines how SkillNudge should construct the first task slice for
its Phase 2 Skill Utility experiment.

The experiment compares:

```text
Control:
  No Skill

Treatment:
  Original Systematic Debugging Skill
```

The current source direction is:

```text
SWE-bench Verified-derived
manually audited task slice
```

This document does not:

- download SWE-bench;
- create or freeze the final 24 tasks;
- execute any task;
- implement a benchmark runner;
- implement evaluation code;
- modify the Experiment runtime;
- modify Phase 1 runtime, CLI, retrieval, Planning, Judge, or contracts;
- modify the selected Skill artifact;
- start Phase 2 implementation.

The protocol is designed to answer:

> How should SkillNudge construct a task slice that allows causal evaluation
> of external capability utility?

It is not designed to maximize the number of tasks won by the Skill.

---

## 1. Selection Philosophy

### 1.1 The task slice is part of the causal design

The same intervention can produce different conclusions under different task
distributions:

```text
Task Distribution A:
  multi-file bug
  unclear root cause
  regression
  dependency interaction

Result:
  Systematic Debugging Skill appears highly effective
```

That result may be real. It may also be partly caused by selecting tasks that
already require the procedure supplied by the Skill.

```text
Task Distribution B:
  typo
  syntax error
  simple failing assertion
  direct compiler message

Result:
  Systematic Debugging Skill appears useless or harmful
```

That result may be real. It may also be caused by selecting tasks where the
intervention is unnecessary.

The first task slice must therefore preserve the conditions under which the
Skill may:

```text
help
remain neutral
add unnecessary overhead
create workflow lock-in
fail for reasons unrelated to the intervention
```

### 1.2 The goal is lifecycle evidence

The goal is not:

```text
maximize Skill win rate
```

The goal is:

```text
measure where the intervention helps
measure where the intervention is neutral
measure where the intervention hurts
explain why
support KEEP / COMPRESS / MODIFY / REPLACE / RETIRE
```

The task slice must make it possible to distinguish:

- a genuine capability gain;
- an intervention that adds process without improving outcomes;
- an intervention that is too rigid for simple tasks;
- a task that is invalid because the environment or oracle failed;
- a result that is inconclusive because the slice or trace is insufficient.

### 1.3 Do not select after seeing treatment outcomes

The task slice must be selected before interpreting No Skill versus Original
Skill outcomes.

It is prohibited to:

- run an initial batch;
- retain tasks where the Skill wins;
- remove tasks where the Skill loses;
- rebalance the slice after seeing treatment outcomes;
- move tasks between development and held-out because of results;
- tune the Skill or metrics against held-out outcomes.

Any post-outcome task change must be recorded as a new protocol version and
must not be presented as the original experiment.

### 1.4 Sensitivity is an analysis dimension, not a selection score

Every eligible task receives a pre-run `skill_sensitivity` hypothesis:

```text
low
medium
high
```

This field estimates whether the Systematic Debugging Skill could plausibly
change the trajectory. It does not mean:

```text
high sensitivity = good task
low sensitivity = bad task
```

Low-sensitivity tasks are necessary because they test whether the Skill knows
when not to impose a long procedure. High-sensitivity tasks are necessary
because they test whether the Skill provides real capability gain. Medium
sensitivity tasks test the transition between these cases.

### 1.5 Candidate pool before final slice

The protocol produces these intermediate artifacts:

```text
source snapshot
-> mined candidate pool
-> eligibility-audited pool
-> balanced candidate frame
-> development/held-out proposal
-> final task slice
```

The current task is to define the process and the records. It does not create
the candidate pool or freeze the final 24 tasks.

---

## 2. Candidate Mining Protocol

### 2.1 Input and output

```yaml
input:
  source:
    - SWE-bench Verified task pool
  source_revision:
    - immutable dataset revision to be recorded before mining
  source_metadata:
    - task records
    - repository and base commit metadata
    - issue description
    - environment metadata
    - test and oracle metadata
    - reference patch metadata

output:
  candidate_task_pool:
    - one local review record per candidate
    - source provenance preserved
    - no treatment outcomes
    - no final include/exclude decision assumed
```

The source snapshot must be recorded before candidate mining. If the source
revision changes, the mining pass must be treated as a new input.

### 2.2 Stage 0: source identity and provenance lock

Before filtering any task:

1. record the source dataset name and immutable revision;
2. record the source repository revision used for task metadata;
3. record applicable dataset, repository, and task licenses;
4. record the fields available for oracle and environment review;
5. record any missing metadata;
6. preserve source task identifiers without treating them as final
   SkillNudge task identifiers.

No task is eligible for review if its source identity cannot be reconstructed.

### 2.3 Stage 1: mechanical candidate mining

Apply only broad, non-semantic filters to form the initial candidate pool.
Mechanical filters may remove records that are obviously unusable, but they
must not attempt to predict whether the Skill will win.

Candidate mining should retain a record for:

- repository and base commit;
- issue title and body;
- task metadata;
- environment metadata;
- target test metadata;
- regression test metadata;
- reference patch metadata;
- source and license provenance.

The initial pool should preserve tasks across repositories and issue shapes.
Do not mine only the easiest, shortest, or most highly rated tasks.

### 2.4 Stage 2: broad semantic classification

For each mined task, classify the issue at a coarse level:

```text
bug fix
regression fix
behavior correction
failure diagnosis
integration repair
state or timing issue
feature request
new capability
documentation
large refactor
architecture redesign
environment-only
unclear
```

This first classification is a review hypothesis. It is not final until a
human audit checks the issue, repository state, patch, and oracle.

### 2.5 Stage 3: debugging-family pre-binning

Assign a provisional family:

```text
root_cause_localization
regression_debugging
dependency_integration
timing_state
other
unclear
```

Provisional family labels are used to organize human review. They must not be
shown to the agent or inserted into the task prompt.

### 2.6 Stage 4: environment and oracle readiness filter

Mark a candidate as `defer` or `exclude` when source metadata shows that the
task may be dominated by:

- broken environment setup;
- missing dependency or unavailable package;
- private resource or credential;
- external service that cannot be version-locked;
- missing test command;
- missing target or regression oracle;
- ambiguous evaluation result;
- known flaky or time-dependent behavior.

This is not a final execution test. It is an eligibility filter. A later
artifact audit must verify the environment and oracle before a candidate can
enter the experiment.

### 2.7 Candidate pool size

The mining stage should produce more candidates than the target slice. The
exact multiplier is not frozen, but the protocol should aim for at least:

```text
2x the eventual total task target
```

and preferably more when family or sensitivity coverage is sparse.

For a 24-task pilot, this means a review pool of at least 48 candidates when
the source supports it. The purpose is not to select the best 24 by outcome
prediction. It is to preserve legitimate alternatives after eligibility,
family, repository, and negative-case review.

If fewer candidates are available, record the shortfall and do not describe
the result as a balanced benchmark.

### 2.8 Mining output record

Every candidate receives a stable local review identifier and preserves:

```yaml
candidate_mining_record:
  candidate_id:
  source_task_id:
  source_dataset:
  source_revision:
  repository:
  base_commit:
  issue_title:
  issue_summary:
  source_license:
  initial_task_type:
  initial_debugging_family:
  metadata_completeness:
  mining_status:
    retain_for_audit
    defer
    exclude
  mining_reason:
```

`mining_status` is not the final human selection decision.

---

## 3. Human Audit Schema

### 3.1 Two-pass audit

Human review should use two passes:

```text
Pass 1:
  task eligibility, oracle, environment, provenance

Pass 2:
  debugging family, depth, sensitivity hypothesis, negative-utility status
```

Pass 1 prevents a task with a broken environment or weak oracle from being
selected because it appears theoretically interesting. Pass 2 records the
capability-analysis dimensions after the task is known to be potentially
eligible.

The reviewer must not use observed No Skill or Skill outcomes in either pass.

### 3.2 Required task review record

Every candidate that reaches human audit receives:

```yaml
task_review:
  task_id:
  source_task_id:
  repository:
  commit:
  issue_summary:

  task_type:
    bug
    regression
    integration
    state
    other
    feature
    refactor
    documentation
    environment_only
    unclear

  debugging_family:
    root_cause_localization
    regression_debugging
    dependency_integration
    timing_state
    other
    unclear

  debugging_depth:
    local
    multi_step
    cross_component
    stateful
    unclear

  skill_sensitivity:
    low
    medium
    high

  oracle_quality:
    strong
    medium
    weak

  environment_risk:
    low
    medium
    high

  negative_utility_candidate:
    true
    false

  selection:
    include
    exclude
    defer

  rationale:
```

The exact field values are review labels, not agent-visible task information.

### 3.3 Required audit evidence

The reviewer must inspect enough source material to answer:

#### Repository and commit

- Does the repository exist at the claimed base commit?
- Is the base state available without private access?
- Is the repository and task provenance recorded?

#### Issue and task type

- Is the issue actually a defect or behavior correction?
- Does the issue only appear to be debugging while actually requesting a
  feature, new capability, or architecture redesign?
- Is the intended behavior clear enough to audit?

#### Oracle

- Is there a target behavior check?
- Is there a regression-preservation check?
- Are `FAIL_TO_PASS` and `PASS_TO_PASS` available, or is there an equivalent
  target/regression oracle?
- Can the evaluator distinguish a fixed target from a broken surrounding
  behavior?

#### Environment

- Can dependencies be obtained from public and reproducible sources?
- Is the test command known?
- Is the environment likely to fail before agent behavior is exercised?
- Does the task require a private resource, secret, or external service?

#### Investigation requirement

- Does success require at least some diagnosis, reproduction, localization,
  hypothesis testing, or verification?
- Could the task be solved by directly regenerating a known answer without
  debugging?

### 3.4 Review rationale requirements

The rationale must cite observable task evidence, not expected treatment
outcomes. Good rationale:

```text
The issue describes a regression in behavior across two modules, has
FAIL_TO_PASS and PASS_TO_PASS checks, and requires reproducing the failure
before the patch location is clear.
```

Bad rationale:

```text
The Skill will probably help this task.
```

### 3.5 Sensitivity assignment

Assign sensitivity before any agent run:

```text
Low:
  The failure is likely local and obvious; the Skill may add overhead.

Medium:
  Reproduction and one or more checks are needed, but the fault boundary is
  relatively local.

High:
  Multiple files, components, hypotheses, state transitions, or recovery
  attempts are plausibly required.
```

The reviewer must record:

- why the task was assigned the level;
- which Skill capability component could matter;
- what evidence would falsify the sensitivity hypothesis;
- whether the task is also a negative-utility candidate.

### 3.6 Inter-rater review

Because task type and debugging depth are judgment-sensitive:

- at least two reviewers should independently audit the final candidate frame
  where feasible;
- disagreements must be recorded;
- disagreements should be resolved before task assignment to development or
  held-out;
- a disagreement is not evidence for excluding a task unless it reveals
  genuine ambiguity in task or oracle eligibility.

The review should preserve the original ratings and the resolution rationale.

---

## 4. Inclusion and Exclusion Rules

### 4.1 Inclusion rules

Include a candidate in the eligible frame only when all of the following are
true:

1. `repository` and `commit` are immutable and accessible.
2. The issue describes a bug, regression, behavior correction, failure
   diagnosis, integration repair, or state/timing defect.
3. The intended behavior is sufficiently clear to review.
4. The environment and dependencies are publicly obtainable or already
   captured.
5. A test command or equivalent evaluator is defined.
6. The task has both target-fix evidence and regression-preservation evidence:

   ```text
   FAIL_TO_PASS
   +
   PASS_TO_PASS
   ```

   or a documented equivalent.
7. The task can be paired under No Skill and Original Skill without changing
   tools, evaluator, or task input.
8. The task contributes useful family, repository, depth, or sensitivity
   coverage.
9. The task does not expose private resources or evaluator-only information.
10. The task allows observable investigation, verification, or recovery
    evidence to be captured.

The criteria do not require that the task be likely to favor the Skill.

### 4.2 Exclusion rules

Exclude a candidate when it is primarily:

- a feature request;
- a new capability request;
- documentation or comment work;
- a large refactor;
- architecture redesign;
- formatting-only work;
- an environment-only issue;
- a task with no valid target or regression oracle;
- a task whose acceptance condition is materially ambiguous;
- a task whose setup requires a private resource, secret, or unavailable
  service;
- a task that cannot be reproduced from the pinned snapshot;
- a task dominated by dependency or infrastructure failure;
- a task whose evaluator leaks hidden information into the agent input;
- a task that cannot be assigned to a debugging family or `other` with a
  defensible rationale.

### 4.3 Defer rules

Use `defer` rather than `exclude` when:

- the task is conceptually relevant but environment verification is pending;
- oracle quality is potentially adequate but not yet audited;
- repository provenance is incomplete but likely recoverable;
- task family or sensitivity is disputed;
- a dependency can likely be reproduced but requires a separate readiness
  check.

Deferred tasks must not enter the final slice until the missing evidence is
resolved.

### 4.4 Broken environment is not agent failure

If a task fails because of:

- missing dependency;
- unavailable container;
- network or credential failure;
- platform incompatibility;
- broken setup script;
- unavailable external service;

the task or run is marked as environment-invalid. It is not counted as a No
Skill failure or Original Skill failure.

### 4.5 Weak oracle is not neutral utility

If the target and regression checks cannot distinguish:

```text
correct target repair
from
plausible or lucky patch
```

the task is excluded or deferred. A weak oracle cannot support a neutral
utility conclusion.

---

## 5. Balance Strategy

### 5.1 Balance purpose

Balance is used to prevent the first slice from being dominated by one task
shape. It is not used to manufacture a favorable effect size.

The pilot target remains:

```text
24 tasks
4 debugging families
16 development tasks
8 held-out tasks
```

### 5.2 Proposed coverage matrix

The initial planning matrix is:

| Debugging family | Low sensitivity | Medium sensitivity | High sensitivity | Target total |
| --- | ---: | ---: | ---: | ---: |
| Root-cause localization | 2 | 2 | 2 | 6 |
| Regression debugging | 2 | 2 | 2 | 6 |
| Dependency / integration | 2 | 2 | 2 | 6 |
| Timing / state | 2 | 2 | 2 | 6 |
| **Target total** | **8** | **8** | **8** | **24** |

This matrix is a coverage target, not a frozen quota. Family and sensitivity
are not fully independent:

- a timing/state task may naturally be high sensitivity;
- a dependency task may be medium or high sensitivity;
- a simple regression may be low sensitivity;
- some source repositories may not provide all cells.

If a cell cannot be filled without weakening oracle or reproducibility
requirements, preserve the stronger eligibility evidence and record the cell
shortfall. Do not admit an invalid task to make the matrix symmetrical.

### 5.3 Development and held-out balance

The 16/8 split should preserve the diagnostic structure:

```text
development:
  16 tasks for protocol checks, metric refinement, and bounded adaptation

held_out:
  8 tasks for final utility and transfer evidence
```

Where the candidate pool permits:

- all four families appear in both splits;
- all three sensitivity levels appear in both splits;
- at least one repository is held out entirely;
- at least 20%-30% of the total slice are low-sensitivity or explicitly
  negative-utility candidates.

For 24 tasks, the minimum negative-utility coverage target is 6 tasks, with
8 preferred if the source supports it. A low-sensitivity label alone does not
automatically make a task a negative-utility candidate; the review must record
why the Skill could plausibly add overhead or lock-in.

### 5.4 Negative-utility preservation rule

The final slice must not remove a task merely because:

- the Skill is expected to lose;
- the task looks too easy;
- the task makes average Skill win rate smaller;
- the task exposes unnecessary procedure overhead.

Those are precisely the cases needed to determine whether the intervention
should be conditional rather than always attached.

### 5.5 Repository diversity

Balance should consider repository identity in addition to family and
sensitivity:

- avoid filling all cells from one repository;
- prefer multiple repository snapshots;
- hold out at least one repository where feasible;
- record language and repository ecosystem coverage;
- do not treat multiple issues from the same repository as fully independent
  evidence.

### 5.6 Selection rule

After eligibility review, select the pilot frame in this order:

```text
eligibility
-> oracle and environment validity
-> repository diversity
-> debugging-family coverage
-> sensitivity and negative-utility coverage
-> development/held-out separation
-> reviewer agreement
```

Expected Skill benefit must not be an earlier or stronger selection criterion
than validity and coverage.

### 5.7 Balance record

The balanced candidate frame should record:

```yaml
balance_record:
  target_total:
  eligible_pool_total:
  family_counts:
  sensitivity_counts:
  negative_utility_candidate_count:
  repository_counts:
  language_counts:
  development_proposal:
  held_out_proposal:
  cell_shortfalls:
  shortfall_reasons:
  reviewer_disagreements:
```

This record is evidence about the slice, not a benchmark score.

---

## 6. Bias Controls

### 6.1 Selection bias

**Risk:** The candidate pool is selected for tasks where the Skill is expected
to help.

**Control:**

- mine broadly before semantic selection;
- preserve low, medium, and high sensitivity;
- require explicit negative-utility candidates;
- document excluded and deferred candidates;
- do not use treatment outcomes during selection.

### 6.2 Difficulty bias

**Risk:** All tasks are either trivial or impossible, hiding intervention
effects.

**Control:**

- record debugging depth;
- include local, multi-step, cross-component, and stateful tasks;
- use a development set to verify task executability;
- report outcomes by family and sensitivity;
- mark both-condition failures as agent or artifact evidence rather than
  assuming Skill neutrality.

### 6.3 Oracle bias

**Risk:** The evaluator rewards a lucky patch or fails to recognize a valid
repair.

**Control:**

- require target and regression checks;
- preserve `FAIL_TO_PASS` and `PASS_TO_PASS` or documented equivalents;
- version the evaluator;
- review reference patch metadata without exposing it to the agent;
- separate evaluator failure from agent failure;
- use trajectory evidence to identify blind retries and missing verification.

### 6.4 Environment bias

**Risk:** Missing dependencies, container problems, network state, or
platform differences dominate the outcome.

**Control:**

- record environment and dependency readiness before task assignment;
- exclude private or unrepeatable resources;
- separate environment-invalid tasks from model outcomes;
- keep environment, tool surface, and access policy identical across arms;
- preserve setup logs and failure classification.

### 6.5 Contamination bias

**Risk:** The model has seen public issue text, reference patches, tests, or
repository state.

**Control:**

- record public provenance and task age where practical;
- avoid evaluator-only fields in agent-visible input;
- interpret success as scoped to the tested model and task window;
- emphasize paired trajectory changes, not only pass rate;
- do not claim contamination-free evidence unless it was actually verified.

### 6.6 Trajectory instrumentation bias

**Risk:** The instrumentation records more detail in one condition or treats
emitted reasoning as hidden internal reasoning.

**Control:**

- use the same Trace Artifact schema for both arms;
- record only observable messages, tool calls, tool outputs, patches, tests,
  and evaluator events;
- do not collect or infer hidden chain-of-thought;
- record missing observability as a limitation;
- define event categories before interpreting treatment outcomes.

### 6.7 Sensitivity labeling bias

**Risk:** Reviewers assign high sensitivity because they expect the Skill to
win, then use that label as evidence that it did.

**Control:**

- assign sensitivity before execution;
- require a rationale tied to task structure;
- keep sensitivity separate from outcome;
- preserve reviewer disagreement;
- report outcomes by sensitivity without treating the label as ground truth.

### 6.8 Split leakage

**Risk:** Development tasks, traces, or outcomes leak into held-out selection
or Skill modification.

**Control:**

- freeze held-out identities before live comparison;
- do not use held-out task text to rewrite the Skill;
- do not use held-out outcomes to tune metrics;
- do not move a task between splits after seeing outcomes;
- record every split change as a new protocol version.

### 6.9 Human audit confirmation checklist

Before accepting the balanced frame, reviewers must answer:

#### If the Skill wins

- Could task selection bias explain the result?
- Are high-sensitivity tasks overrepresented?
- Are low-sensitivity and negative-utility tasks present?
- Did the Skill improve verified outcomes, or only produce longer traces?
- Did the effect transfer to held-out families and repositories?
- Could contamination, oracle leakage, or environment differences explain the
  result?

#### If the Skill loses

- Are the tasks too simple for the intervention to be necessary?
- Did the Skill add overhead or lock the agent into an inefficient workflow?
- Were high-sensitivity tasks present?
- Did the treatment receive the same tools and environment as control?
- Did the oracle reject correct or partially correct behavior?
- Was the failure caused by provider, harness, environment, or evaluator
  rather than the Skill?

#### If there is no difference

- Is the oracle too weak to expose process quality?
- Was the trajectory sufficiently captured?
- Were there enough valid trials to distinguish noise from neutrality?
- Did the task slice contain both tasks where the Skill should matter and tasks
  where it should not?
- Was the intervention actually inserted and rendered identically across
  treatment runs?
- Could both arms have failed because the tasks were too hard?

This checklist produces review evidence. It does not change the outcome after
the fact.

---

## 7. Development / Held-Out Protocol

### 7.1 Development set purpose

The development set is for:

- validating environment setup;
- validating target and regression oracles;
- checking Trace Artifact coverage;
- refining metric definitions before the held-out comparison;
- classifying recurring failure patterns;
- proposing a bounded Skill ablation or Adapted Skill;
- discovering protocol failures.

Development outcomes may inform a versioned Adapted Skill proposal. They do not
constitute final utility evidence for promotion beyond the tested development
scope.

### 7.2 Held-out set purpose

The held-out set is for:

- final No Skill versus Original Skill utility evidence;
- transfer across debugging families;
- transfer across repositories where feasible;
- evaluation of an Adapted Skill after it is frozen;
- detecting overfitting to development tasks and traces.

The held-out set must remain untouched by:

- Skill modification;
- Skill compression;
- task selection;
- family rebalancing;
- sensitivity relabeling for favorable interpretation;
- metric tuning;
- outcome-driven exclusion.

### 7.3 Split freeze

Before any treatment outcome is interpreted:

1. record the task identities in development and held-out;
2. record the family, sensitivity, and negative-utility labels;
3. record the repository and source revisions;
4. record the split rationale;
5. record any repository-level holdout;
6. create an immutable split manifest.

Changing the split after this point creates a new protocol version.

### 7.4 Run order

The recommended order is:

```text
candidate mining
-> human audit
-> balance proposal
-> split freeze
-> development readiness runs
-> protocol correction if needed
-> freeze intervention and metrics
-> held-out No Skill vs Original Skill
-> diagnostic review
```

Development readiness runs may reveal that a task or oracle is invalid. A
task may then be removed from the development set, but the reason and
replacement rule must be recorded. Held-out identities must not be replaced
based on treatment outcomes.

### 7.5 Adapted Skill boundary

If development evidence supports an Adapted Skill:

```text
development evidence
-> named failure or redundancy diagnosis
-> versioned Adapted Skill
-> freeze candidate
-> held-out evaluation
```

The Adapted Skill must not be changed after inspecting held-out results until
the held-out decision is recorded.

### 7.6 Invalid and incomplete runs

The experiment record must separately mark:

```text
valid agent outcome
environment failure
evaluation failure
task ambiguity
protocol deviation
incomplete trace
```

Invalid runs remain auditable but do not enter the primary utility conclusion.

### 7.7 Required split manifest

The future split manifest should contain:

```yaml
split_manifest:
  source_dataset:
  source_revision:
  protocol_version: task-slice-selection-protocol-v0.1
  development:
    - task_id:
      repository:
      family:
      sensitivity:
      negative_utility_candidate:
  held_out:
    - task_id:
      repository:
      family:
      sensitivity:
      negative_utility_candidate:
  repository_holdout:
  split_rationale:
  frozen_at:
  reviewer:
```

The manifest is a research artifact. It is not created by this documentation
task.

---

## 8. Remaining Uncertainties

The following questions remain open:

1. Which exact SWE-bench Verified revision and task metadata snapshot will be
   used for candidate mining?
2. Can the source pool provide enough eligible tasks across all four families
   and all three sensitivity levels without weakening oracle requirements?
3. Which tasks should be treated as explicit negative-utility candidates
   rather than merely low-sensitivity tasks?
4. Is a 2x candidate pool large enough, or will repository and environment
   failures require a larger mining multiplier?
5. Which exact oracle checks are sufficiently strong for target repair and
   regression preservation?
6. Which repository-level holdout best tests transfer without making the pilot
   too small?
7. How should reviewers resolve family and sensitivity disagreements when task
   structure crosses categories?
8. What minimum trial count is needed to distinguish neutral utility from
   stochastic noise?
9. Can the trace instrumentation observe verification and recovery without
   creating condition-specific overhead?
10. What contamination evidence is practical for the selected model and task
    snapshot?
11. What shortfall rule should apply if one family or sensitivity cell cannot
    be filled?
12. Which findings would justify using a Lite-derived fallback instead of the
    Verified-derived source direction?

These are research dependencies. They do not authorize task execution,
evaluation implementation, or Phase 2 runtime work.

---

## 9. North Star Alignment Review

```yaml
Lifecycle_stage:
  OBSERVE / DIAGNOSE

Research_question:
  How should SkillNudge construct a task slice that allows causal evaluation
  of external capability utility?

Evidence_produced:
  - candidate selection protocol
  - candidate mining and provenance requirements
  - human audit schema
  - inclusion, exclusion, and defer rules
  - family and sensitivity balance strategy
  - negative-utility preservation rule
  - anti-bias controls
  - development/held-out split strategy

Decision_enabled:
  KEEP / COMPRESS / MODIFY / REPLACE / RETIRE

Decision_boundary:
  The protocol enables later lifecycle decisions but does not make a utility
  decision before paired runs and valid diagnostic evidence exist.

Gate:
  CONDITIONAL PASS
```

The gate remains conditional because:

- no candidate pool has been mined in this task;
- no final 24 tasks have been selected;
- task and oracle audits have not been completed;
- no split manifest has been frozen;
- no No Skill versus Original Skill run has been executed.

---

## 10. Scope and Validation Record

This document is documentation-only.

Required validation:

```text
git diff --check
./scripts/check_publish_gate.sh
```

Required scope confirmation:

```text
documentation only: yes
runtime changes: no
benchmark downloaded: no
external repository vendored: no
dependency changes: no
final 24 tasks selected: no
task execution started: no
Phase 2 implementation started: no
```

---

## Related Design Sources

- [Dataset Artifact Selection Review v0.2](/Users/kai/Desktop/Work/github/kaiykk/skillnudge/docs/research/dataset-artifact-selection-review-v0.2.md)
- [Skill Utility Drift Experiment Card v0.2](/Users/kai/Desktop/Work/github/kaiykk/skillnudge/docs/research/skill-utility-drift-experiment-card-v0.2.md)
- [North Star Gate v0.1](/Users/kai/Desktop/Work/github/kaiykk/skillnudge/docs/north-star-gate.md)
