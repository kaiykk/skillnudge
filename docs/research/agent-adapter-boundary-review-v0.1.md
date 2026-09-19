# Agent Adapter Boundary Review v0.1

**Status:** ARCHITECTURE REVIEW
**Scope:** Agent execution boundary for the first causal Skill Utility
experiment
**Date:** 2026-09-19
**Live experiment:** NOT AUTHORIZED

This document answers:

> What must remain identical between Control and Treatment so that observed
> utility differences can be attributed to the Skill intervention?

It is based on:

- Skill Artifact Freeze Acceptance Review v0.1;
- Experiment Runner Architecture Review v0.1;
- Utility Measurement Contract v0.1;
- Model / Harness Freeze Review v0.1.

It does not:

- write runtime code;
- implement the Agent Adapter;
- modify the Experiment Runner;
- modify contracts;
- add dependencies;
- connect a provider;
- run a benchmark or live task;
- authorize live experiment execution.

The first causal comparison remains:

```text
Control:
  Agent without an external Skill payload

Treatment:
  The same Agent with the frozen four-file
  systematic-debugging Skill payload
```
---

## 1. Agent Definition

For this experiment, an Agent is the complete execution system that can
change a task trajectory:

```text
Agent =
  Model
  +
  Harness
  +
  Tools
  +
  Execution Policy
  +
  Budget
  +
  Environment
```

The Skill is a declared Treatment intervention inside this Agent boundary. It
must not silently change any other component.

### 1.1 Boundary components

| Component | Meaning | Must be identical across arms? |
| --- | --- | --- |
| Model | Provider, model identifier, snapshot, sampling, reasoning, and output configuration | Yes |
| Harness | Agent loop, message ordering, state handling, retries, termination, and instrumentation | Yes |
| Tools | Filesystem, shell, git, test runner, permissions, network, and tool versions | Yes |
| Execution Policy | Rules for tool use, edits, approvals, failure handling, and stopping | Yes |
| Budget | Steps, tool calls, input/output limits, wall time, retries, and cost limits | Yes |
| Environment | Repository snapshot, worktree, OS image, environment variables, locale, and evaluator-facing setup | Yes |
| Skill payload | Fixed source-unit content and its rendering | No; absent in Control and present in Treatment |

### 1.2 Causal difference

The intended difference is exactly:

```text
Treatment:
  + fixed, version-pinned, four-file systematic-debugging payload

Control:
  + no Skill payload
```

The following are not valid substitutes for a Skill-only difference:

```text
Treatment uses a stronger model
Treatment receives more tools
Treatment gets extra retries
Treatment sees a different system prompt
Treatment receives hidden middleware
Treatment gets a different worktree or environment
Treatment is evaluated with a different oracle
```

If any of these occur, the pair is not clean evidence of Skill utility. It
must be classified as `PROTOCOL_FAILURE` or otherwise excluded according to
the Utility Measurement Contract.

### 1.3 What the Agent Adapter does

The future Agent Adapter is responsible for executing one declared condition:

```text
frozen run metadata
    ->
fixed model and harness
    ->
fixed tools and policy
    ->
Control or Treatment exposure
    ->
observable execution trace
    ->
visible agent result
```

It is not responsible for deciding whether the Skill should be selected,
whether it was useful, or whether it should be kept.

---

## 2. Model Boundary

### 2.1 Model identity to freeze

The following must be recorded and held constant:

```yaml
model:
  provider_identity:
  endpoint_identity:
  model_identifier:
  model_snapshot_or_revision:
  temperature:
  top_p:
  seed_or_determinism_status:
  reasoning_configuration:
  max_input_tokens:
  max_output_tokens:
  stop_configuration:
  transport_timeout:
  retry_policy:
```

Provider credentials and API keys remain local-only. They are not part of the
experiment artifact or trace.

An alias such as `latest`, `default`, or a provider-specific friendly name is
not sufficient by itself. The run must record the effective model identifier
and, when the provider exposes it, the snapshot or backend revision.

### 2.2 Sampling and reasoning configuration

The following must be identical for Control and Treatment:

- temperature;
- top-p or equivalent nucleus sampling;
- seed, if supported;
- reasoning effort or equivalent reasoning configuration;
- maximum input/context budget;
- maximum output tokens;
- stop sequences;
- tool-call sampling behavior;
- response format;
- provider-side reasoning or caching settings that affect execution.

If a provider cannot expose one of these settings, the experiment must record
that limitation and treat the corresponding source of variation as an
unresolved confound. It must not silently use different defaults across arms.

### 2.3 Retry behavior

Retries are part of the Agent boundary, not an incidental transport detail.

The same policy must apply to both arms:

```yaml
retry_policy:
  transport_retry_limit:
  tool_failure_retry_limit:
  model_error_retry_limit:
  task_level_retry_limit:
  backoff_policy:
  retry_context_behavior:
```

The adapter must distinguish:

```text
identical transport retry:
  the same request is retried under the same policy

arm-specific recovery:
  Treatment receives a recovery opportunity or instruction that Control lacks
```

The first is allowed if frozen and recorded. The second is a confound.

### 2.4 Model strength risks

#### Model too strong

A model that already solves nearly every task without external guidance may
create a ceiling effect:

- Control and Treatment both succeed;
- the Skill appears neutral because there is no remaining outcome headroom;
- the model may compress or ignore the procedure;
- any extra context cost may be the only visible Treatment effect.

This does not prove the Skill is useless. It limits the scope of a neutral
result to the tested model, task slice, and environment.

#### Model too weak

A model that cannot reliably operate the repository or test loop may create a
floor effect:

- both arms fail before systematic debugging can matter;
- failures are caused by tool use, context handling, or basic coding limits;
- the Skill appears ineffective even though the experiment did not expose
  its intended capability.

Environment or model failures must not be mislabeled as `SKILL_HURTS`.

#### Model selection principle

The first model should be stable and coding-capable with headroom for both:

```text
Skill benefit
Skill overhead or workflow lock-in
```

The objective is not to choose the strongest available model. The objective is
to produce interpretable evidence under a reproducible model boundary.

### 2.5 Model boundary acceptance

The model boundary is acceptable only when:

1. the same effective model is used for both arms;
2. model and provider metadata are recorded without credentials;
3. sampling and reasoning settings are fixed;
4. max input/output limits are fixed;
5. retries are identical and observable;
6. provider defaults that can affect behavior are either frozen or explicitly
   recorded as unresolved.

---

## 3. Harness Boundary

### 3.1 Recommended harness

The first experiment should use a transparent single-agent loop:

```text
receive task context
    ->
call the same model
    ->
execute one declared tool action or visible response
    ->
append observable result
    ->
repeat under fixed policy
    ->
terminate under fixed conditions
```

The loop may have multiple normal model/tool turns. "Single agent" means that
there is one model-controlled execution path, not that the task must finish in
one turn.

### 3.2 Allowed harness behavior

The harness may provide:

- one fixed conversation state;
- one fixed system/base prompt;
- one fixed task context;
- one fixed tool dispatcher;
- one fixed worktree;
- one fixed termination policy;
- one fixed trace sink;
- one fixed transport retry policy;
- one fixed budget ledger.

The harness must expose its effective configuration to the run manifest or
make any unavailable fields explicit.

### 3.3 Disallowed harness behavior

The first experiment disallows:

```text
subagents
hidden planner
dynamic routing
reflection loop
hidden memory
treatment-only middleware
plugin hooks
automatic Skill discovery
automatic companion Skill loading
arm-specific recovery
cross-run conversation state
```

These are not intrinsically bad product capabilities. They are disallowed
because each can change the trajectory independently of the frozen Skill.

### 3.4 Why no subagents

Subagents introduce additional model calls, prompts, tools, and delegation
policies. If the Treatment delegates differently from Control, the experiment
cannot distinguish:

```text
utility of systematic debugging
from
utility of extra agent capacity
```

Subagents can be studied in a later harness experiment with their own frozen
comparison.

### 3.5 Why no planner

A hidden planner can reorder investigation, create task-specific plans, or
select tools before the declared Skill is visible. It may also use a different
plan in Treatment because the Skill changes its input context.

The first experiment must observe the direct single-agent loop. A visible,
identical task instruction is allowed; a hidden arm-sensitive planner is not.

### 3.6 Why no dynamic routing

Dynamic routing would combine:

```text
capability-gap detection
    ->
intervention selection
    ->
artifact acquisition
    ->
Skill use
```

The first causal experiment must start after the intervention has already been
declared. Routing belongs to a later experiment and must not be included in
the Agent Adapter boundary here.

### 3.7 Why no reflection loop

A reflection or self-critique loop can add extra reasoning calls, verification
steps, or patch revisions. If it is enabled only for one arm, the Treatment
receives more execution policy, not merely a Skill.

A normal visible model response such as a short action summary is allowed in
the trace. A hidden second planner or self-critique process is not.

### 3.8 Why no hidden memory

Persistent memory can contain prior Skill use, repository facts, failed
attempts, or user preferences. It can make one run depend on another and
break paired comparability.

Each run must start from the same declared state. Any memory used by both arms
must be explicit, frozen, and included in the environment or task manifest.

### 3.9 Harness boundary acceptance

The harness boundary is acceptable only if:

- one model execution path is used;
- message ordering is fixed;
- no hidden planner or memory is active;
- no subagents or reflection loop are active;
- retries and termination are identical;
- the Skill is not loaded by an automatic hook;
- all observable events pass through the same trace instrumentation.

---

## 4. Tool Boundary

### 4.1 Identical tool manifest

Control and Treatment must receive the same declared tool manifest:

```yaml
tools:
  filesystem:
    enabled:
    root:
    read_write_scope:
    hidden_paths:
  shell:
    enabled:
    executable:
    timeout:
    environment_image:
  git:
    enabled:
    version:
    remote_access:
    allowed_operations:
  test_runner:
    enabled:
    commands:
    timeout:
    output_limit:
  other_tools:
    enabled: false
```

For the first experiment, the expected tools are:

```text
filesystem
shell
git
task-declared test runner
```

No Treatment-only browser, MCP, web search, issue API, external code search,
computer-use tool, or patch service is allowed.

### 4.2 Filesystem

Both arms must use:

- the same repository snapshot;
- the same base commit;
- separate but equivalent isolated worktrees;
- the same writable path scope;
- the same hidden-path policy;
- the same file permissions;
- the same artifact handoff rules.

The Agent must not access:

```text
reference patches
hidden tests
other task worktrees
other run traces
provider credentials
unrelated home-directory state
```

### 4.3 Shell and process policy

The shell boundary must freeze:

- executable and version;
- working directory;
- environment image;
- locale and timezone when behaviorally relevant;
- process limits;
- command timeout;
- stdout/stderr capture and truncation;
- network policy;
- available package caches.

Different environment variables can change dependency discovery, test
behavior, or model/tool routing. They are part of the causal boundary, not
incidental machine state.

### 4.4 Git

Both arms must use the same:

- Git executable and version;
- repository history and base commit;
- branch and worktree policy;
- local Git configuration;
- remote access policy;
- allowed read/write operations.

Remote fetch, push, and external issue access are disabled unless a later
experiment explicitly freezes them for both arms.

### 4.5 Test runner

The test runner must be identical in:

- command identity;
- environment;
- timeout;
- test selection;
- output capture;
- target/regression distinction;
- evaluator handoff.

The Skill must not receive an easier test command or a test result that is
hidden from Control.

### 4.6 Permissions and network

Permissions must be identical:

```text
filesystem permissions
shell permissions
process permissions
network permissions
credential visibility
test/evaluator visibility
```

The default first-experiment posture is:

```text
local repository worktree: enabled
shell and tests: enabled
git local operations: enabled
remote network access: disabled unless explicitly frozen
provider access: identical through the Agent boundary
hidden evaluator access: Agent disabled
```

### 4.7 Tool boundary acceptance

The tool boundary passes only when the tool manifest can be compared directly
between Control and Treatment. A human-readable label such as "standard
tools" is insufficient.

Any tool, permission, environment, or network mismatch invalidates causal
interpretation and must be recorded as `PROTOCOL_FAILURE`.

---

## 5. Skill Exposure Boundary

### 5.1 Control and Treatment

```yaml
Control:
  skill_payload: null

Treatment:
  skill_payload:
    artifact_id: systematic-debugging-superpowers-v6.4.1-source-unit
    source: four-file frozen source unit
    version: v6.4.1
```

The Treatment payload is the exact artifact accepted by the Skill Artifact
Freeze Acceptance Review. It must not be replaced with:

- the complete Superpowers plugin;
- a rewritten summary;
- a different release;
- a dynamically selected variant;
- an automatically loaded companion Skill;
- a task-specific prompt.

### 5.2 Injection location

The first experiment freezes the injection boundary as:

```text
after fixed base instructions
before fixed task input and repository investigation
```

Conceptually:

```text
fixed base instructions
    ->
fixed Skill wrapper
    ->
four-file Skill payload
    ->
fixed task input
```

The exact message role and wrapper revision must be chosen once by the future
adapter implementation and recorded. The wrapper cannot vary by task,
condition, or model response.

### 5.3 Rendering order

The source-unit rendering order is:

```text
1. skills/systematic-debugging/SKILL.md
2. skills/systematic-debugging/root-cause-tracing.md
3. skills/systematic-debugging/defense-in-depth.md
4. skills/systematic-debugging/condition-based-waiting.md
```

The renderer must:

- preserve the source text;
- use stable file labels and separators;
- apply the same UTF-8 and line-ending policy;
- avoid task-specific additions;
- not resolve excluded cross-Skill references;
- expose the same complete payload to every Treatment run.

### 5.4 Payload identity

The future run record must preserve:

```yaml
skill_exposure:
  artifact_id:
  source_repository:
  source_revision:
  source_file_manifest:
  source_manifest_sha256:
  wrapper_revision:
  rendered_payload_sha256:
  rendered_token_count:
  insertion_boundary: task_start
  additional_tools: false
  additional_permissions: false
  dynamic_routing: false
```

The source manifest hash identifies the four raw files. The rendered payload
hash identifies what the Agent actually received. They must not be collapsed
into one value.

### 5.5 Exposure asymmetry rules

The following are invalid:

```text
Control receives a shortened base prompt
Treatment receives extra task context
Treatment receives an automatic retry because Skill is present
Treatment can discover excluded companion Skills
Control and Treatment receive different wrapper wording
one arm experiences context truncation
```

The first experiment measures static Skill exposure. It does not measure
whether an agent can discover or route to the Skill.

---

## 6. Trace Boundary

### 6.1 Purpose

The trace must make differences in observable work visible while preserving the
privacy and validity boundary:

```text
observable actions and results: allowed
hidden reasoning collection: forbidden
```

The same instrumentation must run for Control and Treatment. Trace capture
must not add an arm-specific prompt, tool, retry, or verification step.

### 6.2 Allowed observable events

The first experiment may record:

```text
agent_start
tool_call
tool_result
test_execution
patch_generated
verification
completion
failure
```

The required debugging evidence includes:

| Event | Observable fields |
| --- | --- |
| `agent_start` | run, task, condition, model/harness identity, exposure boundary |
| `tool_call` | step, call ID, tool name, normalized arguments, start time |
| `tool_result` | call ID, status/exit code, bounded result or hash, duration, truncation |
| `test_execution` | command identity, target/regression kind, status, counts, duration |
| `patch_generated` | changed files, patch hash, revision, insert/delete counts |
| `verification` | kind, status, source, related test or command |
| `failure` | category, source, recoverability, related step, protocol validity |
| `completion` | termination reason, final visible status, budget usage |

### 6.3 Forbidden data

The trace must not collect:

```text
chain of thought
hidden reasoning
private reasoning
internal deliberation
raw hidden reasoning tokens
evaluator-only information
provider credentials
unrelated machine state
```

Short observable action summaries are allowed when emitted by the agent or
harness, but they must be bounded and labeled as observable outputs. They
must not be treated as a reconstruction of hidden reasoning.

### 6.4 Trace validity

If the Agent Adapter cannot capture a required event because of a tool,
provider, or harness limitation, it must record the missing field. It must
not infer the event from a hidden model state.

A trace with insufficient information may lead to:

```text
INCONCLUSIVE
or
PROTOCOL_FAILURE
```

It must not automatically lead to `SKILL_HURTS` or `SKILL_HELPS`.

---

## 7. Confound Register

| Risk | How it changes the observed result | Required mitigation |
| --- | --- | --- |
| Model drift | Control and Treatment are run against different model behavior | Freeze exact model ID, snapshot/revision, endpoint identity, and effective settings |
| Model alias movement | Same label routes to a new backend | Do not rely on moving aliases; record effective model metadata |
| Model sampling asymmetry | Different temperature, top-p, seed, or reasoning effort changes trajectories | Apply one sampling/reasoning configuration to both arms and record unsupported controls |
| Model ceiling | No Skill already solves the task, hiding a possible benefit | Preserve task diversity and interpret neutrality within scope |
| Model floor | Both arms fail for basic coding or tool reasons | Separate agent/environment failure from Skill utility |
| Harness drift | Message order, state handling, or termination changes | Pin harness revision and effective configuration |
| Hidden planner | Treatment receives a different plan or additional model calls | Use transparent single-agent loop; disallow hidden planner |
| Subagent delegation | One arm receives additional agent capacity | Disable subagents and parallel execution |
| Reflection loop | One arm gets extra self-critique or recovery calls | Disable hidden reflection; freeze visible retry policy |
| Hidden memory | Prior runs or repository facts leak into one arm | Start each run from an isolated declared state |
| Tool asymmetry | Treatment can inspect or modify more state | Compare the same tool manifest, permissions, and worktree policy |
| Network asymmetry | One arm can access external information or packages | Freeze network policy and credential visibility |
| Environment-variable drift | Different paths, caches, locales, or provider settings alter behavior | Freeze and record relevant environment variables and process image |
| Retry asymmetry | One arm gets extra transport, tool, or task retries | Use one retry policy and record every retry |
| Context truncation | Treatment or Control sees incomplete instructions or task context | Check effective context length and classify incomplete exposure as protocol failure |
| Wrapper drift | Treatment wording or instruction priority changes | Pin wrapper revision and rendered payload hash |
| Rendering-order drift | Same source files receive different precedence | Freeze explicit four-file order |
| Cross-Skill activation | Missing or extra workflows enter the Treatment | Keep excluded references inert; classify activation as protocol failure |
| Trace overhead | Instrumentation changes timing or context in one arm | Identical trace sink and no trace-only prompt/tool changes |
| Human intervention asymmetry | Manual correction changes one trajectory | Disable intervention or record it identically and exclude unpaired runs |
| Oracle asymmetry | Different evaluator state turns execution variance into outcome variance | Use the same task snapshot, evaluator, checks, and environment |
| Artifact drift | Treatment source differs despite the same version label | Recompute raw file hashes and manifest hash before execution |

### 7.1 Confound classification rule

The Agent Adapter must preserve the distinction:

```text
agent failure:
  the declared Agent executed and did not solve the task

environment failure:
  the execution environment could not support the run

protocol failure:
  Control and Treatment were not comparable

trace insufficiency:
  the outcome may be valid but the trajectory cannot be diagnosed
```

Only a valid paired result with sufficient trace and oracle evidence can
support a Skill lifecycle interpretation.

---

## 8. Adapter Design Acceptance Gate

### 8.1 Minimum design contract

The Agent Adapter design is acceptable when it can express:

```python
run(
    task,
    condition,
    frozen_model_config,
    frozen_harness_config,
    frozen_tool_manifest,
    frozen_execution_policy,
    frozen_budget,
    frozen_environment,
    trace_sink,
) -> observable_agent_result
```

This is a conceptual design boundary only. It does not modify the current
`Agent.run(...)` Protocol or introduce a runtime implementation in this task.

### 8.2 Pair validity checklist

Before interpreting a pair, the execution record must answer `yes` or
explicitly report `unknown` for:

```text
same model and effective provider configuration
same harness revision and message policy
same tool manifest and permissions
same execution policy
same budget and retry policy
same task and repository snapshot
same environment and network policy
same evaluator and trace instrumentation
Control has no Skill payload
Treatment has the complete frozen Skill payload
payload hashes are recorded
no hidden middleware or companion Skill activated
```

An unknown on a load-bearing boundary blocks a causal conclusion.

### 8.3 Final gate

```yaml
gate: CONDITIONAL PASS
meaning:
  - the Agent boundary is sufficiently defined for adapter design
  - the Control/Treatment invariants are explicit
  - the remaining implementation work is bounded
blocking_conditions:
  - exact provider/model configuration is not yet frozen for live execution
  - transparent harness behavior must be demonstrated by implementation
  - tool, environment, retry, and rendering manifests must be recorded
  - no live run may begin from this document alone
```

The conditional pass authorizes only:

```text
design and review of the Agent Adapter boundary
```

It does not authorize:

```text
runtime implementation
provider connection
benchmark execution
live experiment
utility conclusion
```

---

## 9. North Star Alignment Review

```yaml
Lifecycle stage:
  INTERVENE / OBSERVE / DIAGNOSE

Research question:
  What must remain identical between Control and Treatment so that an observed
  utility difference can be attributed to the frozen Skill intervention?

Evidence produced:
  - Agent component definition
  - model identity and sampling boundary
  - transparent harness boundary
  - identical tool and permission manifest
  - fixed Skill exposure boundary
  - observable trace boundary
  - confound register
  - pair validity checklist

Decision enabled:
  KEEP / COMPRESS / MODIFY / REPLACE / RETIRE

Gate:
  CONDITIONAL PASS
```

This review remains aligned with SkillNudge's North Star because it protects
the evidence needed to decide whether an external capability intervention
should continue to exist. It does not optimize a model, rank Skills, or
authorize a larger agent platform.

---

## 10. Scope Record

```text
documentation only: yes
runtime changes: no
Agent Adapter implemented: no
Experiment Runner changed: no
contracts changed: no
dependencies added: no
provider connected: no
benchmark executed: no
live experiment authorized: no
```
