# Model / Harness Freeze Review v0.1

**Status:** RESEARCH DESIGN / EXECUTION ENVIRONMENT NOT YET FROZEN
**Date:** 2026-09-19
**Scope:** Model, harness, tool surface, injection boundary, budget, and
randomness review

This document defines the minimum execution environment required for the first
SkillNudge Phase 2 Skill Utility experiment.

The experiment compares:

```text
Control:
  No Skill

Treatment:
  Original Systematic Debugging Skill
```

The North Star question is:

> When should an external capability intervention exist?

The purpose of this review is narrower:

> How can SkillNudge attribute an observed difference to the Skill
> intervention rather than to a model, harness, tool, budget, or randomness
> change?

This document does not:

- write runtime code;
- implement Phase 2;
- add dependencies;
- execute a benchmark or task;
- download a dataset;
- vendor an external repository;
- change the current Phase 1 runtime, CLI, retrieval, Planning, Judge, or
  contracts.

The review is a freeze proposal, not an execution authorization.

---

## 1. Freeze Principle

### 1.1 The treatment difference must be narrow

The first causal comparison should differ in one intended way:

```text
Control:
  same model
  same harness
  same tools
  same task
  same environment
  same evaluator
  no external Skill

Treatment:
  same model
  same harness
  same tools
  same task
  same environment
  same evaluator
  + Original Systematic Debugging Skill
```

If the treatment also receives a different system prompt, tool, sandbox,
network policy, retry policy, model route, or hidden helper, the result is not
a clean Skill utility comparison.

### 1.2 Freeze identity, not only labels

The following labels are insufficient:

```text
GPT-5.6
Codex
OpenHands
standard tools
default settings
```

The experiment must record exact identities:

```text
provider
base URL or endpoint identity
model ID
model snapshot or provider revision, when available
harness release or commit
prompt and tool manifest revision
task and environment revision
evaluator revision
budget and randomness configuration
```

An alias can move while its label remains unchanged. A provider endpoint can
route to a different backend while the model string remains unchanged. Neither
should be treated as a frozen execution environment without evidence.

### 1.3 No strongest-model objective

The first experiment should not maximize model capability. A model that solves
almost every task without the Skill may create a ceiling effect. A model that
fails almost every task may create a floor effect. Both make intervention
utility difficult to observe.

The target is a stable, coding-capable, agent-suitable model with enough
headroom for the Skill to help and enough competence for the Skill to hurt
through unnecessary procedure.

---

## 2. Model Selection Review

### 2.1 Selection criteria

Each candidate is reviewed on four dimensions:

| Dimension | Question |
| --- | --- |
| Reproducibility | Can the exact model and provider behavior be recorded and rerun? |
| Coding capability | Can the model work on repository-level debugging tasks without an artificial failure floor? |
| Agent suitability | Can it follow tool-use, editing, testing, and termination protocols? |
| Research validity | Does it leave measurable headroom for both Skill benefit and Skill harm? |

The scores below are planning aids, not model benchmark results:

```text
0 = unsuitable or unknown
1 = weak
2 = limited
3 = usable with material caveats
4 = strong with bounded caveats
5 = directly suitable
```

### 2.2 Candidate model classes

| Candidate | Reproducibility | Coding capability | Agent suitability | Research validity | Review |
| --- | ---: | ---: | ---: | ---: | --- |
| Frontier flagship | 3 | 5 | 4 | 2 | Strong capability, but high ceiling, high cost, and likely excessive for the first causal slice |
| High-capability general coding model | 3 | 5 | 4 | 3 | Usable, but still risks ceiling effects and makes the first experiment expensive |
| Stable mid-tier coding model | 4 | 4 | 4 | 5 | Best initial balance if the authorized endpoint serves a verifiable exact ID |
| Cost-sensitive coding model | 4 | 3 | 3 | 3 | Useful for a later cost or model-scaling study; possible floor effects for repository debugging |
| Local open-weight model | 4 after weight and runtime pinning | 2-4 | 2-4 | 3 | Strong control over weights, but serving runtime, quantization, context, and hardware become additional confounders |
| Deterministic fake model | 5 | 0 for real coding | 0 for real coding | 0 for utility claims | Test fixture only; cannot be the first Skill utility model |

These are model classes, not claims that a particular provider exposes a
particular model ID. The experiment must verify availability and effective
behavior at the authorized provider endpoint. A third-party OpenAI-compatible
endpoint must not be assumed to expose the same models or controls as the
upstream API.

### 2.3 Frontier flagship

**Benefits**

- high probability of producing valid patches;
- strong tool-use and repository reasoning;
- less risk that the harness appears broken because the model cannot act.

**Risks**

- ceiling effects can make No Skill and Original Skill look equally strong;
- a high-capability model may ignore or compress the Skill naturally;
- higher cost limits repeated trials;
- a moving flagship alias can change the treatment baseline;
- a positive result may be hard to generalize to ordinary agent settings.

**Research judgment**

Do not select the frontier flagship for the first experiment merely because it
is strongest. It is a useful later comparison model after the first protocol
has demonstrated that traces, oracles, and budgets work.

### 2.4 High-capability general coding model

This class is a plausible candidate when the research priority is realistic
coding performance. It provides enough capability to solve repository tasks but
still risks ceiling effects on a small, manually audited slice.

It is acceptable as a fallback when the recommended mid-tier model is not
available at the authorized provider endpoint. The exact ID, provider, and
revision must still be frozen.

### 2.5 Stable mid-tier coding model

This is the preferred class for the first experiment.

**Benefits**

- enough coding ability to execute repository-level tasks;
- lower cost permits paired and repeated trials;
- more headroom for both procedural benefit and unnecessary overhead;
- less likely than a frontier flagship to make the Skill effect invisible;
- compatible with the existing explicit `SKILLNUDGE_MODEL` provider boundary.

**Risks**

- may fail some high-sensitivity tasks for reasons unrelated to the Skill;
- provider documentation may not guarantee a permanent snapshot;
- a third-party endpoint may silently map the model ID to a different backend;
- reasoning and sampling controls may differ across providers.

**Research judgment**

Recommended for the first experiment if the exact model ID is available and
the provider can expose stable configuration evidence.

### 2.6 Cost-sensitive model

This class can be useful for a later model-scaling or cost-utility study. It
may be too weak for the first repository-level debugging slice, especially if
the task selection includes cross-component and stateful failures.

It should not be selected solely to reduce token cost because a floor effect
can make both arms fail before the intervention can matter.

### 2.7 Local open-weight model

Local weights can improve auditability and reduce provider drift, but the
serving stack becomes part of the experiment:

- model weights and tokenizer;
- quantization;
- inference runtime;
- GPU or CPU hardware;
- context and batching settings;
- sampling implementation;
- memory pressure and timeout behavior.

This is a valid later research path. It is not the cleanest first path unless
the local serving environment is already mature and fixed.

### 2.8 Model recommendation

```yaml
recommended_model_class:
  stable_mid_tier_coding_model

preferred_model_id:
  unresolved_until_provider_readiness

current_local_candidate:
  gpt-5.6-terra
  # Candidate only; verify at the authorized third-party endpoint before use.

selection_rule:
  - use the exact model ID, not a moving alias
  - verify the authorized provider serves that exact ID
  - record provider and endpoint identity without recording credentials
  - do not silently fall back to another model
  - keep model, reasoning setting, sampling setting, and output limit fixed

fallback:
  the closest stable, non-preview, coding-capable model exposed by the same
  authorized provider, with a new review record if the model ID changes

not_selected:
  frontier flagship solely for maximum coding capability
```

The exact model is **not yet frozen** until the authorized endpoint confirms
the model ID, effective configuration, and reproducible response metadata.

The current project convention remains:

```text
SKILLNUDGE_MODEL=<exact-model-id>
SKILLNUDGE_MODEL_BASE_URL=<authorized-endpoint>
```

Provider credentials remain local-only and are not part of this document or
the research manifest.

---

## 3. Harness Selection Review

### 3.1 Harness candidates

| Harness | Benefits | Risks | Experimental confounders |
| --- | --- | --- | --- |
| Mature coding agent harness | Realistic repository work, tested tool loop, existing trace and sandbox support | Hidden system prompts, automatic retries, plugin hooks, subagents, dynamic routing, changing defaults | Skill effect may be mixed with harness behavior or an unrecorded update |
| Minimal agent loop | Transparent control of messages, tools, budgets, retries, and traces | Requires its own implementation and may underrepresent real coding-agent behavior | Harness may be too weak or too artificial to support realistic debugging |
| SkillNudge own harness | Direct integration with the project's lifecycle artifacts and future product | Not yet validated for Phase 2 execution; implementation changes can alter behavior while measuring it | Product implementation, instrumentation, and intervention effects become entangled |

### 3.2 Mature coding agent harness

A mature harness can provide:

- repository-aware tool use;
- shell and file editing;
- test execution;
- sandboxing;
- approval and network controls;
- trace or event records;
- a realistic coding-agent trajectory.

Its main research danger is hidden capability. A mature harness may add:

- system prompts;
- default skills;
- automatic context gathering;
- retry or recovery logic;
- subagent delegation;
- dynamic tool selection;
- plugin or hook activation;
- prompt caching or conversation state;
- default model or reasoning changes.

For the first experiment, a mature harness is admissible only if it supports a
locked, single-agent, no-plugin, no-dynamic-routing profile and can export its
effective configuration. Otherwise it is not a clean causal environment.

### 3.3 Minimal agent loop

A minimal loop can make the experiment legible:

```text
read task context
-> call model
-> execute one declared tool action
-> append observable result
-> repeat until completion or budget exhaustion
```

**Benefits**

- no hidden planner or subagent;
- exact control over tool surface;
- explicit retry and termination behavior;
- direct Trace Artifact mapping;
- easier comparison of No Skill and Original Skill.

**Risks**

- may omit realistic harness behavior;
- may create an artificial agent that does not resemble the target deployment;
- requires a future implementation decision;
- an immature loop can introduce bugs that look like Skill effects.

The minimal loop must not be implemented in this documentation change. It is
the recommended protocol shape for a later, separately approved experiment
runtime.

### 3.4 SkillNudge own harness

The SkillNudge harness is the long-term integration target because it can
connect:

```text
Task Artifact
-> Trace Artifact
-> Oracle Artifact
-> Diagnostic Artifact
-> Evolution Decision Evidence
```

It is not yet the first execution harness by default. Building the harness and
measuring Skill utility in the same change would make it difficult to tell
whether a failure came from:

- the model;
- the tool loop;
- trace instrumentation;
- task setup;
- the Skill;
- the evaluator.

The own harness can become the selected harness after a separate readiness
review proves that its control and treatment paths are behaviorally identical
apart from Skill presence.

### 3.5 Harness recommendation

```yaml
recommended_harness:
  minimal_transparent_single_agent_loop

required_properties:
  - one model call path
  - no subagents
  - no hidden planner
  - no automatic Skill discovery
  - no plugin hooks
  - explicit tool manifest
  - explicit budget and retry policy
  - observable event trace
  - fixed termination behavior
  - isolated task worktree

not_selected_for_first_run:
  full mature harness with uninspectable defaults

implementation_boundary:
  must be a separate approved Phase 2 implementation change
```

If a mature harness is used for feasibility reasons, it must first pass the
same locked-profile requirements. “Mature” is not itself evidence of
experimental validity.

---

## 4. Tool Surface Freeze

The two arms must expose the same tools, permissions, working directory,
network policy, command environment, and evaluator interface.

### 4.1 Frozen tool manifest

The proposed first-experiment tool surface is:

| Tool surface | Frozen behavior |
| --- | --- |
| Filesystem | One isolated task worktree or snapshot; read/write only inside the declared workspace; no access to other tasks, reference patches, hidden tests, credentials, or unrelated home-directory state |
| Shell | One fixed shell and environment image; same command timeout, working directory, environment variables, locale, and process limits |
| Git | Same CLI version and repository state; local `status`, `diff`, `log`, blame, branch, and patch operations allowed as declared; no remote fetch or push during the run |
| Test execution | The same task-provided target and regression commands; same evaluator image, timeout, and output capture; hidden evaluator checks remain unavailable to the agent |
| Patch/editing | The same file-edit mechanism or shell-based editing path; no treatment-only patch tool |
| Other tools | No web search, browser, MCP, issue API, external code search, subagent, or computer-use tool in the first causal run |

### 4.2 Network policy

The preferred run policy is:

```text
network disabled during agent execution
```

Dependencies, container images, and task artifacts should be prepared before
the paired run. If a task genuinely requires network access, both arms must
receive the same network policy and the task must be marked as a special
environment condition rather than silently mixed with offline tasks.

The model provider connection is an execution control channel, not an
agent-visible repository tool. Its endpoint, timeout, retry behavior, and
authorization status must be identical across arms.

### 4.3 Why identical tools matter

If the Skill arm receives a better tool surface, the experiment measures:

```text
Skill + additional capability
```

rather than:

```text
Skill intervention
```

Examples of invalid asymmetry:

- treatment can search the web while control cannot;
- treatment activates a repository-local helper Skill;
- treatment receives a richer filesystem root;
- treatment gets a different test command or timeout;
- treatment receives an automatic retry after a failed tool call;
- treatment uses a different shell or container image;
- treatment can inspect evaluator metadata.

### 4.4 Tool manifest identity

Before execution, record:

```yaml
tool_manifest:
  shell:
  shell_version:
  git_version:
  test_commands:
  test_runner_versions:
  filesystem_root:
  writable_roots:
  network_policy:
  environment_image:
  command_timeout:
  process_limits:
  enabled_tools:
  disabled_tools:
  evaluator_interface:
```

No tool manifest is created by this documentation task.

---

## 5. Skill Injection Boundary

### 5.1 Candidate boundaries

| Boundary | Benefits | Risks | Causal judgment |
| --- | --- | --- | --- |
| Prompt injection | Exact, deterministic treatment; no new tool surface; easy to withhold from control | Adds context length; wrapper wording and placement can affect behavior | Strongest first causal boundary |
| Static Skill resource | Preserves file/resource identity; can model real Skill loading; supports resource-level provenance | Agent may choose whether to read it; filesystem/resource visibility changes; read timing becomes a confound | Good later realism, weaker first attribution |
| Dynamic routing | Tests whether the system decides when to intervene | Mixes routing quality, candidate acquisition, intervention presence, and Skill utility | Exclude from first causal experiment |

### 5.2 Recommended boundary

Use a **fixed prompt injection at task start**, generated deterministically
from the version-pinned Original Skill source unit:

```text
fixed base instructions
-> fixed Original Skill payload
-> fixed task input
-> repository investigation
```

The No Skill control receives the same base instructions and task input without
the Skill payload.

The injection must:

- happen once at the declared task-start boundary;
- use the same wrapper and ordering for every treatment run;
- include no task-specific hints;
- include no reference patch or hidden evaluator information;
- add no tools or permissions;
- preserve the source manifest and content hash;
- record the rendered payload hash and token count.

This is prompt injection as a causal treatment, not dynamic recommendation.
The source remains a static, version-pinned artifact even though the first
runtime representation is a fixed prompt payload.

### 5.3 Why not static resource loading first

A static resource file is attractive for production realism, but it introduces
an additional question:

```text
Did the Skill help,
or did the agent decide to find and read the Skill resource?
```

That changes discoverability and tool behavior. It is a valid later
experiment, especially for studying resource retrieval, but it is not the
cleanest first test of whether the procedure itself changes the trajectory.

### 5.4 Why not dynamic routing first

Dynamic routing would test several capabilities at once:

```text
need detection
-> intervention decision
-> Skill acquisition
-> Skill rendering
-> debugging behavior
```

The first experiment must keep routing out of the treatment. Otherwise a
negative result could mean that the Skill was not selected, and a positive
result could mean that routing exposed a better context rather than that the
procedure was useful.

### 5.5 Injection manifest

The future run manifest must record:

```yaml
skill_injection:
  mode: fixed_prompt_payload
  boundary: task_start_before_repository_investigation
  source_repository:
  source_revision:
  source_paths:
  content_hash:
  rendered_payload_hash:
  rendered_token_count:
  wrapper_revision:
  companion_skills_enabled: false
  hooks_enabled: false
  dynamic_routing: false
```

The manifest must not include the provider API key or other credentials.

---

## 6. Budget and Randomness Controls

### 6.1 Proposed first-run budget

The initial budget should be fixed before interpreting utility results:

```yaml
run_budget:
  max_agent_steps: 40
  max_tool_calls: 80
  max_wall_clock_minutes: 20
  max_output_tokens_per_model_turn: 4096
  max_total_output_tokens_per_run: 32000
  max_patch_retries: 2
  max_human_interventions: 0
```

These are starting protocol values, not a hidden optimization target. A
readiness run may show that the values are too small or too large, but changing
them after seeing treatment outcomes creates a new protocol version.

The budget applies identically to No Skill and Original Skill. Unused budget
is not converted into extra retries for one arm.

### 6.2 Step and tool accounting

Define one agent step as:

```text
one model decision that may produce a response and at most one declared tool
action batch according to the harness protocol
```

If the harness permits multiple tool calls in one model response, the run must
still record both step count and individual tool-call count.

Do not report only wall-clock time. A Skill may trade fewer retries for longer
reasoning, or fewer tool calls for larger context. The budget ledger must
preserve the vector.

### 6.3 Retry policy

Retries must distinguish transport failure from agent behavior:

```text
provider transport timeout:
  at most one identical transport retry;
  record the retry;
  if it fails again, mark the run provider/environment invalid

tool execution failure:
  return the same observable error to both arms;
  do not silently repair the command

model content failure:
  do not inject a corrective coaching message;
  count the step and continue only under the fixed harness policy

task-level retry:
  none in the primary run
```

There must be no arm-specific recovery, manual coaching, or hidden automatic
retry.

### 6.4 Randomness controls

Use the most deterministic configuration supported by the authorized provider:

```yaml
sampling:
  temperature: 0_if_supported
  top_p: 1_if_supported
  seed: fixed_if_supported
  reasoning_effort: fixed_medium_or_provider_equivalent
  max_output_tokens: fixed
```

If a provider does not support one of these controls, record:

```text
unsupported
```

Do not emulate unsupported determinism by manually editing outputs or
selecting favorable runs.

The exact provider behavior must be measured during readiness testing:

- effective model ID;
- effective reasoning setting;
- effective sampling setting;
- provider request and response identifiers;
- usage metadata;
- retry and timeout records.

### 6.5 Repeated trials

The current protocol target remains:

```text
at least 2 trials per task-condition pair
3 preferred when budget permits
```

Repeated identical outputs under a declared deterministic provider do not become
independent evidence merely because they were run twice.

Trial IDs, seed values, and provider response metadata must be recorded. The
same trial policy must apply to both arms.

### 6.6 Concurrency and isolation

The preferred first-run setting is:

```text
one task run at a time
one isolated worktree per run
no shared mutable cache across paired arms
```

If parallelism is later introduced, it must preserve task isolation, provider
rate-limit behavior, filesystem independence, and comparable scheduling
conditions.

---

## 7. Frozen Variable Register

The following variables must be frozen before the first valid utility run:

| Variable group | Required frozen value |
| --- | --- |
| Model | Exact model ID, provider, endpoint identity, effective model metadata |
| Provider | OpenAI-compatible request contract, timeout, transport retry, response storage policy |
| Harness | Release or commit, single-agent mode, prompt wrapper, tool loop, termination rules |
| Skill | Original source revision, file manifest, content hash, rendered payload hash |
| Task | Task ID, repository commit, task statement, environment snapshot |
| Tools | Shell, filesystem, Git, test runner, command timeout, enabled/disabled tools |
| Network | Disabled during agent run unless explicitly part of a separate task condition |
| Evaluator | Target tests, regression tests, evaluator version, output classification |
| Budget | Steps, tool calls, wall time, output tokens, retry limits |
| Randomness | Temperature, top-p, seed, reasoning effort, provider determinism status |
| Trace | Same event schema, same capture mechanism, same redaction policy |
| Human interaction | Zero coaching or intervention during primary runs |
| Concurrency | Sequential or explicitly controlled parallel execution |

A change to any row after the first treatment outcome is observed requires a
new protocol version or an explicit protocol-deviation record.

---

## 8. Final Recommendation

### Recommended model

```yaml
model:
  class: stable_mid_tier_coding_model
  preferred_id: unresolved_until_provider_readiness
  current_local_candidate: gpt-5.6-terra
  condition:
    - current_local_candidate is not a confirmed public model identity
    - exact ID must be served by the authorized endpoint
    - no alias fallback
    - provider and model metadata must be recorded
    - exact model is not frozen until readiness verification
```

The recommendation is based on research validity, not maximum coding score:
the first experiment needs enough capability to operate the repository task
while retaining headroom for both Skill benefit and Skill overhead.

### Recommended harness

```yaml
harness:
  type: minimal_transparent_single_agent_loop
  mode:
    - no subagents
    - no hidden planner
    - no dynamic Skill routing
    - no plugin hooks
    - explicit tools
    - explicit trace
    - explicit budgets
```

This harness is a future implementation target, not code added by this task.

### Recommended Skill injection

```yaml
skill_injection:
  mode: fixed_prompt_payload
  boundary: task_start_before_repository_investigation
  routing: disabled
  tools_added: false
  companion_skills: disabled
  hooks: disabled
```

### Frozen variables

At minimum, freeze:

```text
model ID and provider endpoint
harness release or commit
tool manifest
task and environment snapshot
Original Skill source manifest and hashes
prompt wrapper and rendered payload
step, tool, token, and wall-clock budgets
retry policy
sampling and reasoning configuration
network and filesystem policy
evaluator and trace schema
human intervention policy
```

### Unresolved risks

1. The authorized third-party endpoint may not expose the preferred model ID.
2. A provider may not expose a stable model snapshot or deterministic seed.
3. The minimal loop may underrepresent the mature coding-agent behavior that
   SkillNudge eventually targets.
4. Fixed prompt injection may measure context and instruction effects together
   with procedural capability.
5. A 40-step budget may favor one task family or hide long-horizon recovery.
6. Offline network policy may exclude valid integration tasks.
7. A model floor or ceiling effect may remain after task selection.
8. Trace instrumentation may alter latency or context if not isolated.
9. A provider update may change behavior without changing the visible model ID.
10. The selected Skill may contain strong normative language that creates
    over-exploration on low-sensitivity tasks.

---

## 9. North Star Alignment Review

```yaml
Lifecycle_stage:
  OBSERVE / DIAGNOSE / EVALUATE

Research_question:
  What minimum frozen model, harness, tool, injection, budget, and randomness
  environment is required to attribute a trajectory difference to the Original
  Systematic Debugging Skill rather than to execution-environment drift?

Evidence_produced:
  - model candidate comparison
  - harness candidate comparison
  - identical tool-surface definition
  - fixed Skill injection boundary
  - budget and retry policy
  - randomness and determinism policy
  - frozen-variable register
  - unresolved confounder list

Decision_enabled:
  KEEP / COMPRESS / MODIFY / REPLACE / RETIRE

Decision_boundary:
  The review enables a valid future intervention comparison. It does not make
  a Skill utility decision before paired task runs and diagnostic evidence.

Gate:
  CONDITIONAL PASS
```

### Gate interpretation

The design passes conditionally because it defines a narrow causal environment,
but the following are still unverified:

- the authorized provider's exact model ID and effective snapshot;
- the final harness implementation and commit;
- readiness of the frozen tool manifest;
- provider support for sampling and seed controls;
- end-to-end trace and oracle capture;
- task-specific budget adequacy.

No Phase 2 implementation or live task execution is authorized by this
document.

---

## 10. Validation and Scope Record

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
Phase 2 implementation: no
benchmark execution: no
dataset download: no
external repositories vendored: no
dependency changes: no
```

---

## Sources

The model and harness comparison used the following public primary sources:

1. OpenAI API model catalog:
   https://developers.openai.com/api/docs/models
2. OpenAI Responses API documentation:
   https://developers.openai.com/api/docs/guides/responses
3. OpenAI Codex CLI repository:
   https://github.com/openai/codex
4. Codex CLI README:
   https://github.com/openai/codex/blob/main/README.md
5. Codex CLI configuration reference:
   https://github.com/openai/codex/blob/main/docs/config.md

Related local design sources:

- [Skill Utility Drift Experiment Card v0.2](/Users/kai/Desktop/Work/github/kaiykk/skillnudge/docs/research/skill-utility-drift-experiment-card-v0.2.md)
- [Skill Artifact Selection Review v0.2](/Users/kai/Desktop/Work/github/kaiykk/skillnudge/docs/research/skill-artifact-selection-review-v0.2.md)
- [Task Slice Selection Protocol v0.1](/Users/kai/Desktop/Work/github/kaiykk/skillnudge/docs/research/task-slice-selection-protocol-v0.1.md)
- [North Star Gate v0.1](/Users/kai/Desktop/Work/github/kaiykk/skillnudge/docs/north-star-gate.md)
