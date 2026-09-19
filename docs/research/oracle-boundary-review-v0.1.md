# Oracle Boundary Review v0.1

**Status:** ARCHITECTURE REVIEW
**Scope:** Oracle boundary for the first causal Skill Utility experiment
**Date:** 2026-09-20
**Live experiment:** NOT AUTHORIZED

This document answers:

> What evidence is sufficient to determine whether an Agent solved a
> debugging task, without leaking evaluator information into the Agent
> trajectory?

It is based on:

- Utility Measurement Contract v0.1;
- Experiment Runner Architecture Review v0.1;
- Agent Adapter Boundary Review v0.1;
- Task Slice Selection Protocol v0.1;
- Skill Artifact Freeze Acceptance Review v0.1.

It does not:

- write runtime code;
- implement an evaluator;
- modify the Experiment Runner;
- modify contracts;
- download SWE-bench or another dataset;
- run a benchmark or live task;
- connect a provider;
- authorize live experiment execution.

The first causal comparison remains:

```text
Control:
  Agent without the frozen Skill payload

Treatment:
  The same Agent with the frozen four-file
  systematic-debugging Skill payload
```

The Oracle is the evaluation boundary after Agent execution. It must determine
whether the visible result satisfies the task acceptance conditions without
becoming an additional capability available to the Agent.

---

## 1. Oracle Definition

### 1.1 Oracle composition

For the first experiment:

```text
Oracle =
  Task Success Evaluation
  +
  Regression Safety Evaluation
  +
  Diagnostic Evidence
```

These components are related but not interchangeable.

### Task Success Evaluation

Answers:

> Did the Agent resolve the declared target issue under the task's acceptance
> conditions?

It may inspect:

- the final patch or workspace state;
- the declared target checks;
- task-specific behavioral constraints;
- the target issue's observable acceptance behavior.

Task success requires more than a plausible patch or a model assertion that the
task is complete.

### Regression Safety Evaluation

Answers:

> Did the proposed change preserve the protected behavior that the task does
> not authorize the Agent to break?

It may use:

- existing tests;
- explicitly declared regression tests;
- protected behavior checks;
- interface or constraint checks defined before evaluation.

A target check passing while protected behavior fails is not a clean success.
It is a regression outcome.

### Diagnostic Evidence

Answers:

> What evidence explains whether the result was a valid success, a task
> failure, a regression, or an invalid evaluation?

Diagnostic evidence includes:

- target check results;
- regression check results;
- evaluator validity;
- environment and dependency failures;
- bounded diagnostics;
- relevant trace references;
- evaluator revision and execution environment;
- whether the result is interpretable under the frozen protocol.

Diagnostic evidence explains the outcome. It does not replace the outcome
oracle.

### 1.2 Oracle is not Agent capability

The Oracle is not part of the Agent capability being compared.

The Agent:

```text
receives the task-visible context
uses the frozen tools and execution policy
produces a visible result or patch
```

The Oracle:

```text
receives the declared task artifact and Agent result
runs or inspects the predeclared evaluation
produces outcome and validity evidence
```

The Oracle must not:

- guide the Agent during execution;
- repair the Agent result;
- reveal hidden tests;
- reveal the reference patch;
- expose expected solution details;
- choose a more favorable evaluator for one arm;
- decide whether the Skill should be kept, compressed, modified, replaced, or
  retired.

The Oracle may use information that is intentionally hidden from the Agent.
That asymmetry is valid only when the information remains inside the
post-execution evaluation boundary.

### 1.3 Oracle and causal attribution

The same Oracle behavior must be applied to Control and Treatment:

```text
same task snapshot
same target checks
same regression checks
same evaluator revision
same evaluation environment
same validity rules
```

If the evaluator differs between arms, the result is not evidence of Skill
utility. It is `PROTOCOL_FAILURE` or an excluded comparison according to the
Utility Measurement Contract.

---

## 2. Agent Visibility Boundary

### 2.1 Information the Agent may see

The Agent may receive only information declared as task-visible:

```text
repository snapshot
base commit and working tree
task or issue description
public documentation and public tests
declared tool manifest
declared environment information
normal command and test results produced by its tools
frozen Control or Treatment context
```

The exact visibility depends on the task artifact. "Public" does not
automatically mean "available in the Agent context"; the task record must state
what is exposed.

For a repository debugging task, the Agent may normally inspect the repository
and run the public or task-declared tests through the identical tool surface.
The Agent must not receive evaluator-only metadata merely because the Oracle
uses it later.

### 2.2 Information the Agent must not see

The following are evaluator-only:

```text
hidden tests
reference patch
reference solution
expected patch shape
evaluator source or private evaluator logic
hidden acceptance criteria
held-out task labels
other arm's trace or result
oracle diagnostics generated after execution
evaluation-only environment variables
post-hoc analyst labels
```

The Agent also must not infer hidden information through an accidental tool
surface, generated file, environment variable, cache, or error message.

### 2.3 Public tests and hidden tests

Public tests may be visible to the Agent when the task artifact declares them
as part of the repository or task context. Hidden tests remain Oracle-only.

The experiment must record:

```yaml
agent_visible_checks:
  - repository tests:
  - task-declared tests:
  - public acceptance information:

oracle_only_checks:
  - hidden tests:
  - private regression checks:
  - evaluator-only constraints:
```

This is a design record, not a new runtime schema in this documentation task.

### 2.4 Reference patch boundary

The reference patch may be useful for:

- Oracle construction;
- task audit;
- expected behavior analysis;
- reviewer diagnosis;
- checking whether the task artifact is coherent.

It must not be:

- copied into the Agent worktree;
- included in the task prompt;
- exposed through a test failure;
- placed in a shared cache;
- used to generate Agent-visible hints;
- used as a patch-similarity target for success.

Task correctness should be evaluated by declared behavior and checks, not by
whether the Agent reproduced the reference patch text or file layout.

### 2.5 Evaluator logic boundary

The evaluator may contain private logic for:

- selecting hidden checks;
- validating regression safety;
- classifying environment failures;
- determining evaluator validity.

That logic is outside the Agent visibility boundary. The Agent must receive
only the normal outputs of its declared tools and public checks during
execution.

If evaluator logic or evaluator-only output enters the Agent trajectory, the
comparison is invalid even if the final patch passes.

### 2.6 Visibility acceptance

The visibility boundary passes when:

1. task-visible and evaluator-only fields are explicitly listed;
2. the Agent worktree cannot access reference patches or hidden tests;
3. public tests are distinguished from hidden checks;
4. evaluator-only failures are not sent back as Agent hints;
5. Control and Treatment receive the same task-visible information;
6. the Oracle runs only after the Agent execution boundary closes.

---

## 3. Success Criteria

### 3.1 Primary outcome

The primary outcome is:

```text
target issue resolved
and
patch behavior satisfies the declared target acceptance checks
```

For a valid success:

- the Agent produced a visible patch or workspace result;
- the target issue's acceptance condition is satisfied;
- the evaluation environment is valid;
- no protected regression invalidates the result;
- the result can be attributed to the declared task execution rather than an
  evaluator or protocol failure.

Patch plausibility, natural-language confidence, and similarity to a reference
patch are not sufficient on their own.

### 3.2 Patch correctness

Patch correctness means that the resulting behavior satisfies the task's
declared target condition under the immutable task snapshot and evaluation
procedure.

The Oracle should prefer behavioral checks:

```text
target behavior passes
target failure is no longer reproduced
declared constraints remain satisfied
```

It should not require an identical implementation unless the task explicitly
has a structural contract that is part of the public or declared acceptance
criteria.

### 3.3 Regression safety

Regression safety requires:

```text
existing protected behavior remains valid
and
declared regression checks pass
```

The exact checks are task-specific and must be frozen before interpreting
Control/Treatment outcomes. A task without a credible regression-preservation
check may be excluded, deferred, or labeled as having limited oracle quality.

### 3.4 Outcome states

The Oracle should preserve separate facts rather than collapse them into one
score:

```yaml
outcome:
  target:
    status: pass | fail | unknown
  regression:
    status: pass | fail | unknown
  evaluator:
    status: valid | invalid | unknown
  overall:
    status: success | failure | inconclusive | protocol_failure
```

This is a review shape, not an instruction to change the current
`OracleResult` runtime schema.

### 3.5 Failure categories

#### Wrong fix

The Agent changed the repository, but the target behavior remains incorrect or
the change addresses the wrong cause.

#### Incomplete fix

The Agent improved or partially corrected the target behavior, but the
declared target acceptance condition is not fully satisfied.

#### Regression

The target behavior may pass, but protected or previously working behavior
fails.

#### Environment failure

The declared evaluation environment could not run correctly, for example:

- missing dependency that the frozen environment should have supplied;
- broken process or filesystem setup;
- unavailable service required by the declared task;
- timeout caused by infrastructure instability;
- nondeterministic test infrastructure failure.

Environment failure is not automatically Agent failure and is not evidence
that the Skill hurts.

#### Evaluator failure

The Oracle or its checks were invalid, unavailable, inconsistent, or unable to
determine the declared outcome.

Evaluator failure is not a task failure.

### 3.6 Failure classification table

| Category | Target result | Regression result | Evaluator validity | Interpretation |
| --- | --- | --- | --- | --- |
| Success | Pass | Pass | Valid | Valid task success |
| Wrong fix | Fail | Pass or unknown | Valid | Agent did not resolve the target |
| Incomplete fix | Partial or fail | Pass or unknown | Valid | Target acceptance was not fully met |
| Regression | Pass or partial | Fail | Valid | Target improvement is invalidated by protected behavior loss |
| Environment failure | Unknown | Unknown | Invalid or blocked | Infrastructure result, not Skill failure |
| Evaluator failure | Unknown | Unknown | Invalid | Oracle cannot support a task conclusion |
| Protocol failure | Any | Any | Comparison invalid | Control/Treatment attribution is not valid |

The table preserves distinct evidence classes. It is not an automatic scoring
formula.

---

## 4. Oracle Artifact

### 4.1 Task Artifact

The Task Artifact defines what the Agent is asked to do and what immutable
state is evaluated.

At minimum it should identify:

```yaml
task_artifact:
  task_id:
  source_dataset_or_origin:
  repository:
  base_commit:
  issue_description:
  task_visible_files_or_context:
  public_test_metadata:
  target_behavior:
  declared_constraints:
  environment_reference:
  provenance:
```

The current runner has a deliberately smaller placeholder shape:

```text
task_id
repository
commit
test_command
```

This review does not expand that runtime schema. It records the additional
conceptual fields a future SWE-bench-derived bridge will need to preserve.

The Task Artifact must be identical between Control and Treatment.

### 4.2 Oracle Artifact

The Oracle Artifact defines how the visible Agent result is evaluated:

```yaml
oracle_artifact:
  oracle_id:
  evaluator_version:
  evaluator_revision:
  evaluation_environment:
  target_checks:
    - command_or_check_id:
      purpose:
      expected_condition:
      visibility: public | oracle_only
  regression_checks:
    - command_or_check_id:
      purpose:
      expected_condition:
      visibility: public | oracle_only
  protected_constraints:
  timeout_policy:
  retry_policy:
  output_capture_policy:
  validity_rules:
  failure_taxonomy:
```

The Oracle Artifact must be frozen before interpreting paired outcomes. It
must not be edited after seeing which arm performs better.

### 4.3 Oracle input and output boundary

Conceptually:

```text
Task Artifact
    +
Agent-visible result or isolated worktree
    +
Oracle Artifact
    ->
Oracle Result
```

The Oracle may additionally use evaluator-only metadata:

```text
hidden tests
reference patch metadata
private regression checks
evaluator implementation
```

Those inputs remain outside the Agent trajectory.

The current runtime Protocol is intentionally minimal:

```python
Oracle.evaluate(
    task: TaskArtifact,
    result: Any,
) -> OracleResult
```

The future adapter may need a richer worktree or evaluation context, but that
is a separate implementation decision. This review does not change the
Protocol or implement a SWE-bench evaluator.

### 4.4 Oracle Result

The future Oracle Result should preserve:

```yaml
oracle_result:
  target_status:
  regression_status:
  overall_status:
  diagnostics:
  tests_passed:
  tests_failed:
  evaluator_valid:
  failure_source:
  evaluator_revision:
  evaluation_environment_hash:
```

The existing runtime `OracleResult` already preserves a smaller subset:

```text
success
regression
diagnostics
tests_passed
```

The richer fields are design considerations only. Missing fields must be
handled as missing evidence, not guessed from the Agent output.

### 4.5 Oracle artifact immutability

For each paired run, preserve:

```text
task artifact identity
oracle artifact identity
evaluator revision
evaluation environment identity
target check results
regression check results
bounded diagnostics
validity result
```

The Oracle Artifact must not vary by condition. If a task requires a condition
specific to the repository or test environment, that condition must be part of
the shared task/evaluator definition, not a Treatment-specific exception.

---

## 5. SWE-bench-Derived Task Risks

SWE-bench-derived tasks are a possible future source of repository debugging
tasks. This review does not download or select a final dataset. The risks
below must be addressed before a task is eligible for a live experiment.

### 5.1 Flaky tests

Tests may fail intermittently because of:

- timing;
- concurrency;
- network dependencies;
- external services;
- nondeterministic ordering;
- resource pressure;
- test isolation failures.

Risk:

```text
The Oracle labels an infrastructure fluctuation as a wrong fix or regression.
```

Required evidence:

- repeated baseline test status during task audit;
- test timeout and retry policy;
- known flake record;
- target/regression check separation;
- evaluator validity classification.

A test that cannot provide a stable interpretation should not be used as a
load-bearing success criterion without an explicit validity policy.

### 5.2 Environment instability

Repository tasks can depend on:

- package installation;
- language runtime versions;
- operating system behavior;
- service availability;
- network access;
- compiler or test-runner versions;
- system resource limits.

Risk:

```text
Control and Treatment appear different because their evaluation environments
were not equivalent or because the environment was invalid.
```

Required evidence:

- immutable or hashable evaluation environment;
- repository base commit;
- dependency and tool versions;
- environment setup result;
- bounded timeout policy;
- separate environment-failure status.

Environment instability must not be converted into `SKILL_HURTS`.

### 5.3 Ambiguous issue descriptions

An issue may have:

- multiple plausible interpretations;
- incomplete reproduction steps;
- unstated compatibility requirements;
- a mismatch between issue text and reference patch;
- behavior that depends on private context.

Risk:

```text
The Oracle rewards one interpretation even though the Agent received an
ambiguous task, or the task is impossible to judge from the visible inputs.
```

Required evidence:

- task description audit;
- explicit target behavior;
- declared constraints;
- acceptable behavior range;
- reviewer decision on whether the task is sufficiently specified.

An ambiguous task can produce `INCONCLUSIVE` or be excluded. A reference
patch must not silently become the hidden expected answer.

### 5.4 Missing dependencies

Dependencies may be unavailable, incorrectly pinned, or incompatible with the
task environment.

Risk:

```text
The Agent cannot investigate or test the repository for reasons unrelated to
the Skill, while the Oracle reports a task failure.
```

Required evidence:

- dependency readiness before the run;
- install or cache provenance;
- setup logs;
- distinction between missing declared dependency and Agent misuse;
- evaluator validity status.

If the required environment cannot be reconstructed, the task is not ready
for causal utility interpretation.

### 5.5 Evaluator leakage

Leakage can occur through:

- hidden test files in the Agent worktree;
- reference patches in shared directories;
- error messages that reveal expected output;
- evaluator environment variables;
- generated reports copied into the task workspace;
- cached results from another run;
- tool commands that expose evaluator paths or logic.

Risk:

```text
The Agent receives information that differs from the declared task-visible
context, so the result no longer measures the intended intervention.
```

Required evidence:

- isolated Agent and Oracle worktrees;
- explicit visibility manifest;
- hidden-test and reference-patch access checks;
- cache and environment-variable audit;
- no evaluator output returned during Agent execution.

Any evaluator leakage into one arm is `PROTOCOL_FAILURE`, not a Skill win.

### 5.6 Reference patch bias

A reference patch may be correct but not unique. Comparing the Agent patch to
reference text can reject a behaviorally correct solution or reward an
unnecessary similarity.

The primary Oracle should evaluate behavior and declared constraints. Reference
patches are for Oracle construction and audit, not Agent guidance or default
patch-similarity scoring.

### 5.7 Oracle readiness filter

A task should not enter live execution unless:

```text
target behavior is explicit
target check is valid
regression protection is defined
environment is reproducible
evaluator identity is pinned
Agent-visible and Oracle-only information are separated
failure classification is available
```

This is an eligibility filter, not a benchmark selection algorithm.

---

## 6. Utility Interpretation

### 6.1 Required comparison unit

The minimum causal unit remains a valid paired task comparison:

```text
same task
same repository snapshot
same Agent boundary
same Oracle Artifact

Control:
  no Skill payload

Treatment:
  frozen systematic-debugging payload
```

One successful Treatment run does not establish `SKILL_HELPS`. One failed
Treatment run does not establish `SKILL_HURTS`.

### 6.2 Interpretation labels

These labels are scoped research interpretations, not automatic metrics:

#### `SKILL_HELPS`

Use only when, within the declared scope:

- the paired comparison is valid;
- the Oracle is valid;
- the Treatment shows a meaningful favorable change in verified outcome,
  trajectory, cost, or risk evidence;
- the change is not explained by environment, evaluator, or protocol failure;
- the evidence supports a diagnosis of how the Skill contributed.

This label does not imply that the Skill helps every model, harness, task, or
repository.

#### `SKILL_NEUTRAL`

Use when:

- the paired comparison and Oracle are valid;
- no material favorable or harmful difference is observed within scope;
- the trace and outcome evidence are sufficient to distinguish neutrality from
  missing evidence;
- the result is not simply caused by a ceiling, floor, or invalid task that
  prevents interpretation.

If the experiment cannot distinguish neutrality from insufficient evidence,
use `INCONCLUSIVE` instead.

#### `SKILL_HURTS`

Use only when:

- the paired comparison and Oracle are valid;
- the Treatment creates a reproducible harmful change in outcome, regression
  safety, cost, trajectory, or risk;
- the harm is not caused by context truncation, provider failure,
  environment instability, evaluator failure, or protocol asymmetry;
- the trace provides enough evidence to diagnose the harmful mechanism.

Extra steps alone do not prove harm. They may be productive or wasteful; the
Oracle and trace must be considered together.

#### `INCONCLUSIVE`

Use when evidence is insufficient to distinguish help, neutrality, or harm,
including:

- incomplete or ambiguous task acceptance;
- insufficient trace for diagnosis;
- unclear target or regression result;
- small or unstable evidence window;
- unresolved model ceiling or floor effects;
- contradictory evidence without a valid explanation;
- missing evidence that does not make the protocol itself invalid.

`INCONCLUSIVE` is a valid research result. It should lead to a bounded
evidence or protocol question, not an automatic Skill rewrite.

#### `PROTOCOL_FAILURE`

Use when the comparison or evaluator is invalid, including:

- Control and Treatment received different tools, model settings, budgets, or
  environments;
- hidden tests, reference patches, or evaluator logic leaked into the Agent
  trajectory;
- the evaluator changed after seeing results;
- the Oracle used different checks or environments by condition;
- the frozen Skill payload was incomplete, altered, or replaced;
- cross-Skill or plugin behavior activated unexpectedly;
- provider, harness, or trace failure made the two arms incomparable.

`PROTOCOL_FAILURE` is not `SKILL_HURTS` and not `SKILL_NEUTRAL`.

### 6.3 No automatic thresholds

This review does not define automatic thresholds for:

- success-rate difference;
- number of passed tests;
- token overhead;
- latency;
- steps;
- regression count;
- minimum task count;
- lifecycle promotion.

Thresholds require a separate experiment design decision that considers task
family, validity, transfer, and uncertainty. The Oracle supplies evidence; it
does not make an unreviewed lifecycle decision.

### 6.4 Utility evidence chain

The required interpretation chain is:

```text
Agent result
    ->
Oracle outcome
    ->
trace and diagnostic evidence
    ->
valid paired comparison
    ->
scoped utility interpretation
```

If the chain breaks at the task, environment, evaluator, or protocol layer,
the result must remain `INCONCLUSIVE` or `PROTOCOL_FAILURE`.

---

## 7. Final Gate

### 7.1 Gate decision

```yaml
gate: CONDITIONAL PASS
meaning:
  - the Oracle boundary is sufficiently defined for design and implementation
    planning
  - Agent-visible and evaluator-only information are explicitly separated
  - task success, regression safety, and diagnostic evidence are distinct
  - failure and utility interpretation labels are bounded
blocking_conditions:
  - no real evaluator has been implemented or validated
  - no task artifact or SWE-bench-derived slice has been frozen
  - evaluator and environment reproducibility remain unverified
  - no live benchmark or experiment may begin from this document
```

The conditional pass authorizes only:

```text
Oracle design review
and
future bounded implementation planning
```

It does not authorize:

```text
benchmark execution
live experiment
runtime implementation
provider connection
SWE-bench download
utility conclusion
```

### 7.2 Pre-execution acceptance checklist

Before a future implementation can claim Oracle readiness, it must answer:

```text
task artifact identity is pinned
repository base commit is reproducible
target behavior and checks are explicit
regression checks are explicit
evaluator revision is pinned
evaluation environment is reproducible
Agent-visible fields are listed
Oracle-only fields are isolated
reference patch cannot enter Agent workspace
hidden tests cannot enter Agent workspace
Control and Treatment use the same Oracle
environment, evaluator, and protocol failures are distinguishable
```

An unknown on any load-bearing item blocks a causal utility conclusion.

---

## 8. North Star Alignment Review

```yaml
Lifecycle stage:
  OBSERVE / DIAGNOSE / EVALUATE

Research question:
  What evidence is sufficient to determine whether the Agent solved a
  debugging task without leaking evaluator information into the trajectory?

Evidence produced:
  - Oracle composition
  - Agent visibility boundary
  - target and regression success criteria
  - task and Oracle artifact shapes
  - SWE-bench-derived task risk register
  - scoped utility interpretation labels
  - pre-execution Oracle readiness checklist

Baseline:
  No Skill

Treatment:
  Frozen four-file systematic-debugging Skill payload

Decision enabled:
  KEEP / COMPRESS / MODIFY / REPLACE / RETIRE

Gate:
  CONDITIONAL PASS
```

This review remains aligned with SkillNudge's North Star because it protects
the evidence needed to decide whether an external capability intervention
creates durable utility. It does not turn the Oracle into an Agent capability,
a benchmark score, or an automatic Skill promotion mechanism.

---

## 9. Scope Record

```text
documentation only: yes
runtime changes: no
Oracle implemented: no
Experiment Runner changed: no
contracts changed: no
dependencies added: no
SWE-bench downloaded: no
benchmark executed: no
provider connected: no
live experiment authorized: no
```
