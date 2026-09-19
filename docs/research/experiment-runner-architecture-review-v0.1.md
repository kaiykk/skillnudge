# Experiment Runner Architecture Review v0.1

**Status:** ARCHITECTURE REVIEW
**Execution status:** NO RUNTIME CHANGE
**Authorization status:** NOT BENCHMARK AUTHORIZATION
**Date:** 2026-09-19

This document reviews the architecture boundary required before connecting
real models, task artifacts, or evaluators to the minimal Phase 2 experiment
runner.

It does not:

- modify runtime code;
- modify the existing experiment schemas or Protocols;
- add dependencies;
- run a benchmark or a task;
- download a dataset;
- connect a provider;
- vendor the selected Skill or an external repository;
- authorize live experiment execution.

The first experiment remains:

```text
Control:
  No Skill

Treatment:
  Original Systematic Debugging Skill
```
The North Star question remains:

> When should an external capability intervention exist?

The narrower architecture question is:

> What execution boundaries are needed to attribute a verified trajectory
> difference to the declared Skill intervention rather than to a model,
> harness, tool, trace, or evaluator difference?

---

## 1. Existing Boundary and Review Scope

The current minimal runner has this shape:

```text
TaskArtifact
    |
    v
ExperimentRunner
    |
    +--> Agent.run(task, condition, trace)
    |        |
    |        +--> AgentResult
    |
    +--> Oracle.evaluate(task, result)
             |
             +--> OracleResult

AgentResult + OracleResult + Trace
    |
    v
UtilityEvidence
```

The current implementation already provides:

- declarative `Control` and `Treatment` conditions;
- a placeholder `TaskArtifact`;
- run identity and frozen execution metadata;
- an append-only observable trace;
- an injectable `Agent` Protocol;
- an injectable `Oracle` Protocol;
- separate outcome, trajectory, and cost evidence;
- no universal utility score;
- rejection of obvious hidden-reasoning fields in persisted payloads.

This review does not replace that boundary. It identifies what a future real
adapter must guarantee before the runner is connected to a model or a
SWE-bench-derived task.

### 1.1 Existing contracts that remain in force

The architecture must preserve these existing decisions:

```text
same task
same repository snapshot
same model and provider configuration
same harness
same tool surface
same evaluator
same budget and retry policy

No Skill
versus
Original Skill
```

The following are not interchangeable:

```text
relevant Skill
retrieved Skill
recommended Skill
used Skill
useful Skill
```

This review concerns the boundary at which the Skill is actually inserted and
the evidence needed to assess its effect. It does not turn retrieval or
recommendation into a Phase 2 objective.

---

## 2. Skill Injection Boundary

### 2.1 Candidate boundaries

The first experiment can insert the Original Systematic Debugging Skill in
three materially different ways:

| Boundary | What changes | Benefits | Main confounders |
| --- | --- | --- | --- |
| Prompt/context injection | A fixed, version-pinned Skill payload is added to the agent-visible task context | Deterministic; easy to withhold from Control; does not change tools or permissions; simple to hash and audit | Wrapper wording, placement, token overhead, and instruction priority become part of the treatment |
| Harness middleware | The harness loads or transforms the Skill during execution | More similar to a production Skill system; can preserve resource boundaries and lifecycle hooks | Hidden loading, message reordering, automatic retries, hooks, caching, activation rules, or other harness behavior can be mistaken for Skill utility |
| Tool-backed capability | The Skill is exposed through a tool or resource the agent can query | Useful for studying discovery, retrieval, and resource use | Changes the tool surface; introduces discoverability, tool-selection, timing, and retrieval confounders |

Dynamic routing is not a fourth treatment boundary for this experiment. It
would combine intervention selection with intervention utility and would make
the result ambiguous.

### 2.2 Recommended first boundary

Use **fixed prompt/context injection at task start**.

The conceptual sequence is:

```text
fixed base instructions
    +
fixed Original Systematic Debugging Skill payload
    +
fixed task input
    ->
repository investigation
```

The Control sequence is:

```text
fixed base instructions
    +
fixed task input
    ->
repository investigation
```

The treatment payload must be:

- the exact bounded source unit selected by the artifact review;
- pinned to a repository revision or release;
- rendered by one fixed wrapper;
- inserted once at the declared task-start boundary;
- identical across Treatment runs;
- free of task-specific hints, reference patches, hidden tests, or evaluator
  metadata;
- incapable of adding tools, permissions, network access, subagents, or
  retries.

The treatment is therefore a static capability intervention represented as
agent-visible context. It is not a routing decision and it is not a claim that
the production system should always inject Skills in this manner.

### 2.3 Injection identity

A future run record should preserve enough identity to distinguish a changed
artifact from a changed wrapper or context budget:

```yaml
skill_injection:
  mode: fixed_prompt_context
  source_repository:
  source_revision:
  source_file_manifest:
  source_content_hash:
  wrapper_revision:
  rendered_payload_hash:
  rendered_token_count:
  insertion_boundary: task_start
  additional_tools: false
  additional_permissions: false
  dynamic_routing: false
```

This is a design record, not an instruction to expand the current
`ExperimentRun` schema in this documentation change.

### 2.4 Why not harness middleware first

Harness middleware is appropriate when the research question is:

> Does the complete production Skill-loading mechanism create utility?

That is not the first question. The first question is whether the declared
Systematic Debugging procedure changes the observable trajectory under a
controlled environment.

Middleware could silently add:

- a session-start message;
- a different system-message ordering;
- a Skill activation trigger;
- a supporting Skill;
- an extra context source;
- automatic retries after a failed tool call;
- a different context window or truncation policy.

If any of these differ between arms, the experiment no longer isolates the
declared intervention.

### 2.5 Why not tool-backed capability first

A tool-backed Skill would answer a mixed question:

```text
Can the agent discover, call, read, and use a capability resource?
```

That is valuable for a later discovery or routing experiment. It is not the
cleanest first test of whether the debugging procedure itself creates utility.
The first experiment must not give the Treatment a tool that the Control does
not have.

### 2.6 Injection-specific risks

Prompt/context injection is the recommended boundary, but it does not remove
all causal ambiguity:

1. The Skill consumes context and may reduce the space available for the task.
2. The wrapper may accidentally make the Treatment more authoritative than the
   base instructions.
3. A long procedure may change behavior through instruction volume rather than
   useful debugging content.
4. The model may ignore the Skill, partially follow it, or over-apply it.
5. The selected source unit may refer to resources that are not included in the
   bounded treatment.

These risks must be recorded and diagnosed. They are not reasons to add
dynamic routing to the first experiment.

---

## 3. Observable Trace v0.2

### 3.1 Purpose

Trace v0.2 should make trajectory differences visible without collecting
private chain-of-thought or reconstructing hidden reasoning.

The trace must answer:

```text
What did the agent observe?
What actions did it take?
What tests and verification did it perform?
Where did it fail or recover?
What patch did it produce?
Why did the run terminate?
What execution cost and protocol failures occurred?
```

It must not answer:

```text
What was the model's private chain-of-thought?
What hidden reasoning tokens did the model generate?
What evaluator information was concealed from the agent?
```

Trace v0.2 is a design proposal only. The current
`trace.event.experiment.v0` schema and its event names are not changed by this
review.

### 3.2 Event set

The existing event vocabulary is sufficient as the base for the debugging
experiment:

```text
agent_start
tool_call
tool_result
test_execution
patch_generated
verification
failure
completion
```

The following table defines the minimum observable information expected for a
future v0.2 trace. Fields are intentionally bounded and operational; they are
not a request to persist raw model reasoning.

| Event | Required observable information | Why it matters |
| --- | --- | --- |
| `agent_start` | run ID, task ID, condition, model/harness identity, injection boundary, budget identity | Establishes the arm and execution context before any action |
| `tool_call` | step ID, call ID, tool name, normalized observable arguments, working-directory identity, start time | Shows investigation, editing, testing, and navigation actions |
| `tool_result` | call ID, status or exit code, bounded output or output hash, duration, truncation indicator | Shows what evidence the agent actually received without preserving unbounded or sensitive output |
| `test_execution` | test kind, command identity, status, pass/fail counts when available, duration, output reference or hash | Separates target testing, regression testing, and other verification |
| `patch_generated` | patch revision, changed-file list, patch hash, insert/delete counts, generation status | Shows patch scope and whether the agent revised or bundled changes |
| `verification` | verification kind, status, source, target/regression relation, related test or command ID | Shows whether the agent checked its hypothesis and protected against regression |
| `failure` | category, source, recoverability, related step/call ID, protocol-validity flag | Separates agent, tool, environment, evaluator, and protocol failures |
| `completion` | termination reason, final visible status, budget usage, protocol-validity flag | Shows whether the agent stopped after success, failure, budget exhaustion, or an invalid run |

### 3.3 Common event fields

Each event should be correlatable without relying on event ordering alone:

```yaml
event:
  schema_version:
  run_id:
  event_id:
  timestamp:
  step_id:
  event:
  details:
```

The current implementation does not yet require `event_id` or `step_id` on
every event. Their addition belongs to a separate implementation change if
the real adapter needs them.

### 3.4 Observable action summaries

Trajectory analysis may benefit from a short agent-visible action summary, for
example:

```text
Inspecting the failing call path before editing.
Running the target test after the minimal patch.
Rechecking the regression test after a failed fix.
```

Such a summary is allowed only as an observable output emitted by the agent
or harness. It must be:

- short;
- action-oriented;
- bounded;
- optional when the harness cannot provide it;
- clearly labeled as an observable summary, not a reasoning transcript.

The trace must never require raw chain-of-thought, hidden reasoning fields, or
post-hoc reconstruction of private deliberation. An absent summary is missing
observable data, not permission to infer hidden reasoning.

### 3.5 Event payload rules

The future trace adapter must:

- preserve tool and test identity;
- normalize arguments enough for comparison without leaking secrets;
- bound command output and record truncation;
- use hashes or artifact references for large patches and outputs;
- distinguish an agent-visible result from an evaluator-only result;
- record whether an event came from the agent, tool, environment, evaluator,
  or protocol layer;
- reject fields named or equivalent to `chain_of_thought`, `cot`,
  `hidden_reasoning`, `internal_reasoning`, `private_reasoning`, or
  `thoughts`;
- avoid storing credentials, tokens, API keys, or unrelated environment data.

Trace capture must not add Treatment-only context, tools, retries, or
verification. Both arms use the same trace instrumentation.

### 3.6 Derived trajectory evidence

The raw trace should support separate derived observations:

```yaml
trajectory_evidence:
  investigation:
    files_read:
    searches:
    call_path_or_data_flow_checks:
  hypothesis_testing:
    observable_action_summaries:
    test_after_change_events:
    patch_revisions:
  verification:
    target_test_count:
    regression_test_count:
    verification_count:
  recovery:
    failed_attempts:
    strategy_changes:
    reverted_or_replaced_patches:
  termination:
    reason:
    budget_exhausted:
  protocol:
    environment_failures:
    evaluator_failures:
    missing_events:
```

These are analysis views, not a universal score. A longer trajectory may be
more productive; a shorter trajectory may have skipped necessary verification.
The trace must preserve enough context to make that distinction.

### 3.7 What Trace v0.2 can and cannot establish

Trace evidence can establish:

- that the Treatment read, edited, tested, or verified differently;
- that the Control and Treatment used different numbers or types of actions;
- that one arm recovered from a failed attempt differently;
- that the Skill introduced repeated procedure or unnecessary work;
- that a run was invalid because of protocol or environment failure.

Trace evidence alone cannot establish:

- that the Skill caused a correct patch;
- that an observed action was caused by a hidden thought;
- that a shorter trace is better;
- that a single trace supports a lifecycle decision;
- that a model's self-reported confidence is calibrated.

The trace must be paired with a valid Oracle result and the declared
experiment scope.

---

## 4. Agent Adapter Boundary

### 4.1 Responsibility split

The `ExperimentRunner` and the future real Agent Adapter must have different
responsibilities.

#### ExperimentRunner owns

- run identity and experiment metadata;
- condition validation;
- task artifact handoff;
- output directory and artifact naming;
- creation of the trace sink;
- one invocation for one condition;
- handoff to the Oracle Adapter;
- assembly of outcome, trajectory, and cost evidence;
- preservation of protocol failures as invalid evidence.

#### Agent Adapter owns

- model/provider invocation;
- the single-agent harness loop;
- fixed base prompt construction;
- fixed Treatment payload insertion;
- the declared filesystem, shell, git, and test tools;
- step, token, latency, retry, and termination budgets;
- isolated worktree interaction;
- observable event emission;
- visible final result and usage metadata.

### 4.2 Responsibilities explicitly outside the Agent Adapter

The Agent Adapter must not:

- dynamically decide whether a Skill is needed;
- retrieve or rerank Skills;
- add Treatment-only tools or permissions;
- call the Oracle during agent execution;
- access reference patches, hidden tests, or evaluator diagnostics;
- use arm-specific recovery logic;
- silently switch models, providers, or harness versions;
- emit private chain-of-thought;
- convert evaluator failure into an agent failure;
- make a KEEP, COMPRESS, MODIFY, REPLACE, or RETIRE decision.

The adapter executes a declared condition. It does not decide whether the
condition was useful.

### 4.3 Current interface

The current implementation seam is intentionally small:

```python
Agent.run(
    task: TaskArtifact,
    condition: Condition,
    trace: TraceRecorder,
) -> AgentResult
```

This interface should remain unchanged in this documentation-only review.
`Condition` remains declarative:

```json
{"skill": null}
```

or:

```json
{"skill": "systematic-debugging-v6.4.1"}
```

The current fixture agent is not evidence of real model execution.

### 4.4 Future adapter contract

A future real adapter should preserve the same logical boundary even if its
internal implementation needs richer metadata:

```python
AgentAdapter.run(
    task: TaskArtifact,
    condition: Condition,
    trace_sink: TraceRecorder,
) -> AgentExecutionResult
```

The conceptual result should contain only observable execution information:

```yaml
AgentExecutionResult:
  visible_result:
  termination_reason:
  steps:
  tokens:
  latency_ms:
  retries:
  protocol_valid:
  workspace_artifact:
```

`AgentExecutionResult` is a design name, not a new runtime type introduced by
this task. Any future implementation must decide whether to extend the
existing `AgentResult` or map richer adapter data into separate artifacts.

### 4.5 Required invariants for the adapter

For a valid paired comparison:

```text
Control and Treatment use the same:
  model and provider configuration
  base prompt
  harness loop
  tool manifest
  filesystem and shell policy
  worktree setup
  step and token budgets
  retry policy
  termination policy
  trace instrumentation
```

The only intended difference is:

```text
Treatment receives the declared Original Systematic Debugging Skill payload.
```

The adapter must record enough metadata to detect a violation. If it cannot
prove the arms were comparable, the pair is `PROTOCOL_FAILURE`, not evidence
that the Skill helped or hurt.

### 4.6 Worktree and human-intervention boundary

The adapter must define a per-run isolated worktree or equivalent immutable
workspace boundary. It must prevent access to:

- other task worktrees;
- reference patches;
- hidden tests;
- provider credentials;
- unrelated home-directory state;
- prior run artifacts unless explicitly declared.

Human intervention must be either disabled or recorded identically for both
arms. A user correction, manual patch, or approval cannot be silently folded
into the agent trajectory.

---

## 5. Oracle Adapter Boundary

### 5.1 Responsibility

The Oracle Adapter evaluates the visible result in an isolated evaluation
environment. It answers whether the task outcome satisfies the declared
acceptance conditions. It does not explain the agent's hidden reasoning and it
does not choose the intervention.

For a SWE-bench-derived task, the future bridge conceptually receives:

```yaml
task_evaluation_input:
  task_id:
  repository:
  base_commit:
  issue_or_task_statement:
  target_test_metadata:
  regression_test_metadata:
  evaluation_environment:
  reference_patch_metadata:
```

The reference patch is Oracle-only metadata. It must never be visible to the
Agent Adapter.

### 5.2 Evaluation sequence

The future adapter should follow a fixed sequence:

```text
immutable task snapshot
    ->
isolated agent worktree result
    ->
patch or workspace handoff
    ->
isolated evaluation worktree
    ->
declared target checks
    ->
declared regression checks
    ->
constraint and evaluator validity checks
    ->
OracleResult
```

The evaluation worktree must not reuse mutable state from the agent process in
a way that changes the oracle. Any transfer from the agent worktree must be
explicit and recorded.

### 5.3 Oracle output boundary

The current Oracle Protocol is:

```python
Oracle.evaluate(
    task: TaskArtifact,
    result: Any,
) -> OracleResult
```

That Protocol remains unchanged by this review. A future SWE-bench adapter may
need a richer task or workspace handoff, but the implementation change must
preserve the same conceptual boundary:

```python
OracleAdapter.evaluate(
    task: TaskArtifact,
    agent_result: AgentResult,
    evaluation_context: EvaluationContext,
) -> OracleResult
```

The conceptual result should distinguish:

```yaml
OracleResult:
  success:
  regression:
  diagnostics:
  tests_passed:
  evaluator_valid:
  failure_source:
  target_checks:
  regression_checks:
```

The additional fields above are design considerations, not additions to the
current runtime schema in this task.

### 5.4 Oracle responsibilities

The Oracle Adapter must:

- reconstruct or access the declared base repository snapshot;
- apply the agent result or patch without changing its semantics;
- execute the declared target checks;
- execute the declared regression checks;
- record test status, counts, duration, and bounded diagnostics;
- distinguish target failure from regression failure;
- distinguish agent, environment, evaluator, and protocol failure;
- report evaluator validity separately from task success;
- use identical evaluator behavior for Control and Treatment;
- preserve an immutable record of the evaluator revision and environment.

### 5.5 Oracle non-responsibilities

The Oracle Adapter must not:

- expose reference patches to the agent;
- expose hidden tests or evaluator-only metadata;
- repair the agent patch before evaluation;
- choose a more favorable test command for one arm;
- infer success from the model's self-report;
- convert an environment failure into `success: false` without a validity flag;
- decide whether the Skill should be kept, compressed, modified, replaced, or
  retired;
- silently change the task after seeing the Treatment result.

### 5.6 Failure classification

The following results must remain distinct:

```text
valid task failure:
  the agent result was evaluated and did not satisfy the oracle

regression:
  the target behavior may pass but protected behavior fails

environment failure:
  the declared evaluation environment could not run correctly

evaluator failure:
  the oracle or test harness was invalid or unavailable

protocol failure:
  Control and Treatment were not comparable

inconclusive:
  the evidence is insufficient to distinguish benefit, neutrality, or harm
```

Environment, evaluator, and protocol failures are not evidence that the Skill
hurts. They invalidate or limit the causal interpretation.

---

## 6. Causal Invariants

Before real execution, the implementation must be able to demonstrate:

### 6.1 Intervention invariant

The Treatment differs from Control only by the declared version-pinned Skill
payload at the declared injection boundary.

### 6.2 Tool invariant

Both arms have the same:

```text
filesystem
shell
git
test execution
network policy
timeouts
environment variables
working directory rules
```

No Treatment-only MCP, browser, web search, plugin hook, subagent, or patch
helper is allowed.

### 6.3 Execution invariant

Both arms use the same:

```text
model
provider endpoint
harness revision
base instructions
step budget
token budget
retry policy
termination policy
trace instrumentation
```

### 6.4 Evaluation invariant

Both arms use the same:

```text
task snapshot
oracle revision
evaluation environment
target checks
regression checks
validity rules
```

### 6.5 Information-boundary invariant

The agent can see only the task information and tools declared for its arm.
The agent cannot see:

- reference patches;
- hidden tests;
- evaluator-only metadata;
- the other arm's trace or result;
- secret provider configuration.

### 6.6 Evidence invariant

No lifecycle conclusion may be based on:

- one run;
- one successful patch;
- a benchmark score without trajectory diagnosis;
- a trace without a valid oracle;
- an oracle result without a paired Control run;
- missing evidence silently treated as neutrality.

---

## 7. Readiness Questions Before Implementation

This review is conditionally ready for a separate implementation task, but the
following questions remain open:

1. Which exact authorized model ID and provider configuration can be frozen
   without exposing credentials?
2. Can the chosen harness provide the required single-agent, no-hook, no-routing
   profile and export its effective configuration?
3. Can the selected Skill source unit be rendered without unresolved companion
   Skill or plugin dependencies?
4. What final source manifest, revision, and content hashes will be recorded
   immediately before execution?
5. Which trace fields are available without adding context or changing model
   behavior?
6. What output truncation and redaction policy is sufficient for tool results
   and test logs?
7. How will the future task artifact expose SWE-bench-derived base commits,
   issue statements, target tests, regression tests, and evaluator metadata
   without expanding the current placeholder schema prematurely?
8. Can the Oracle Adapter create a clean evaluation worktree for every run?
9. Which environment and evaluator failures cause a pair to be excluded rather
   than labeled as Skill failure?
10. What budget is enough to observe recovery without making the experiment
    primarily a long-horizon budget study?

These are implementation-readiness questions. They do not authorize benchmark
execution and do not justify redesigning the current runner before evidence
shows that its boundary is insufficient.

---

## 8. North Star Alignment Review

```yaml
Lifecycle stage:
  OBSERVE / DIAGNOSE / EVALUATE

Research question:
  What execution boundaries are required to attribute a verified trajectory
  difference to the Original Systematic Debugging Skill rather than to model,
  harness, tool, trace, or evaluator drift?

Evidence produced:
  - injection boundary comparison
  - observable Trace v0.2 proposal
  - Agent Adapter responsibility boundary
  - Oracle Adapter responsibility boundary
  - causal invariants
  - readiness questions and confounders

Decision enabled:
  KEEP / COMPRESS / MODIFY / REPLACE / RETIRE

Gate:
  CONDITIONAL PASS
```

### Gate interpretation

The review passes conditionally because it defines a narrow architecture for a
future causal experiment:

```text
fixed prompt/context intervention
    ->
minimal transparent single-agent adapter
    ->
observable trace
    ->
isolated oracle adapter
    ->
multidimensional utility evidence
```

It does not authorize:

- connecting the real provider;
- downloading or freezing a dataset;
- running a live task;
- implementing Trace v0.2;
- implementing a real Agent Adapter;
- implementing a SWE-bench evaluator;
- making a lifecycle decision about the Skill.

The next implementation task, if separately approved, must preserve this
boundary and must not silently turn the runner into a general agent framework,
benchmark platform, or Skill routing system.

---

## 9. Scope Record

```text
documentation only: yes
runtime changes: no
schema changes: no
dependency changes: no
CLI changes: no
provider connection: no
benchmark execution: no
dataset download: no
external repository vendoring: no
Skill source modification: no
```
