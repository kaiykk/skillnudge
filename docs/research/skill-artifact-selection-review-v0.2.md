# Skill Artifact Selection Review v0.2

**Status:** RESEARCH REVIEW / ORIGINAL SKILL NOT YET FROZEN FOR EXECUTION
**Date:** 2026-09-19
**Scope:** Artifact analysis, provenance, and intervention selection only

This document selects a candidate intervention artifact for the first
SkillNudge Phase 2 utility experiment.

It does not:

- modify Phase 1 runtime, CLI, retrieval, Planning, Judge, or contracts;
- implement Experiment runtime or evaluation code;
- download a Skill into the repository;
- vendor an external repository;
- add dependencies;
- modify or rewrite an external Skill;
- begin Phase 2 implementation.

The current Experiment Card v0.2 defines:

```text
Primary intervention:
  Systematic Debugging Skill

Primary comparison:
  No Skill
  vs
  Original Skill
```

This review answers:

> Should a Systematic Debugging Skill artifact be selected as SkillNudge's
> first utility experiment intervention? If yes, which exact artifact should be
> frozen?

The selection criterion is not popularity, stars, benchmark score, or
community adoption. It is:

> Which artifact gives SkillNudge the cleanest first causal experiment?

---

## 1. Decision Question

### Why the intervention artifact must be frozen

`Original Skill` is a treatment condition, not a vague category. If the source,
file set, version, installation path, or linked resources change during the
experiment, the treatment is no longer stable.

Without an artifact freeze, a result could be caused by:

- a changed Skill body;
- a newly added supporting file;
- a different plugin hook;
- an activated companion Skill;
- a different harness installation;
- a different tool surface;
- a different source revision;
- a different interpretation of what the Skill contains.

The experiment therefore needs an artifact identity that is:

```text
source-addressable
version-pinned
content-hashable
license-reviewable
agent-visible
insertable without changing tools
decomposable for later evolution
```

### Decision boundary

This review selects a source artifact and a bounded intervention boundary. It
does not install that artifact into a local agent or run the utility experiment.

The selected artifact must still be audited once more before live execution
for:

- exact agent-visible rendering;
- provider and harness compatibility;
- absence of hidden external resources;
- content and license verification;
- final manifest hash;
- absence of task-specific knowledge.

---

## 2. Candidate Inventory

The investigation considered two public workflow artifacts and two possible
artifact scopes within the primary repository.

| Artifact | Source | License | Version / revision | Structure | First-experiment suitability |
| --- | --- | --- | --- | --- | --- |
| Superpowers systematic-debugging source unit | `obra/superpowers`, `skills/systematic-debugging/` | MIT | `v6.4.1`; repository tag observed at `5bf4e78011075bcfc0dc295f0724994cd123ee71` | Primary `SKILL.md` plus three explicitly referenced supporting technique files | **High, with a bounded file-set boundary** |
| Superpowers full plugin | `obra/superpowers` | MIT | `v6.4.1` | Plugin manifest, hooks, many skills, supporting docs, harness-specific installation | Low for first causal experiment |
| Aspire Issue Investigation Skill | `microsoft/aspire`, `.agents/skills/issue-investigation/` | MIT | `main` file revision `73b6834143e0f3ae6848665e048961ba6add39ad` | Seven-step issue investigation workflow, routing tables, repro protocol, result template | Medium as a diagnostic comparator; low as the primary artifact |

### Candidate scope principle

The Superpowers repository contains more than one capability. The full
repository or plugin is therefore not automatically the same thing as the
Systematic Debugging Skill.

For this review, a source unit is eligible only when its file boundary can be
stated before execution. A full plugin that activates hooks, other Skills, or
additional tools is a different treatment.

### Research retrieval boundary

The review inspected public repository metadata, official file paths, source
revisions, plugin metadata, license files, and file content structure. No
external Skill was downloaded into the SkillNudge repository and no external
repository was vendored.

---

## 3. Detailed Artifact Analysis

## 3.1 Candidate A: Superpowers systematic-debugging source unit

### Identity

```yaml
name: Superpowers systematic-debugging source unit
source_repository: https://github.com/obra/superpowers
source_directory: skills/systematic-debugging/
source_tag: v6.4.1
source_tag_commit_observed: 5bf4e78011075bcfc0dc295f0724994cd123ee71
maintainer: Jesse Vincent / obra
license: MIT
artifact_scope:
  - skills/systematic-debugging/SKILL.md
  - skills/systematic-debugging/root-cause-tracing.md
  - skills/systematic-debugging/defense-in-depth.md
  - skills/systematic-debugging/condition-based-waiting.md
primary_file_revision:
  commit: c74782ead66b8ded584d9b9cf64dcba95457f320
  git_blob_sha: 095d194ac041502905f15b01d22d294fb94db8b2
  sha256: 808fc5717aa88ad65efff312b11c186294d3e6ee301afb584e2f86599b137787
supporting_file_hashes:
  root-cause-tracing.md: 75b933b6a8c40bdb2031b10f21654395b56ec6ab6bc7b018c18d3fe57aeb7fb8
  defense-in-depth.md: 1e175fb86fc357e58c6aebf5441e481e1b7868b4380c0456b63a17eefbd18ba7
  condition-based-waiting.md: e89fec8400d6cd50f43407cec9fab50976ba4d55d0ec2eb51c0bd68036b54c26
manifest_sha256: 92dc8f44a0a729f72e32e1c000f0e37ad8cfb9cbd6346ed4ddbe92694ebe86eb
```

The manifest hash is the SHA-256 of the ordered path-to-content-hash list
recorded above. It is a review manifest, not a replacement for checking the
source files again immediately before execution.

The repository's public plugin metadata identifies version `6.4.1`, MIT
licensing, Jesse Vincent as author, and a `skills/` directory. The repository
also publishes harness-specific installation paths, including Codex App and
Codex CLI.

### Public structure

The primary `SKILL.md` contains:

- a trigger description for bugs, test failures, and unexpected behavior;
- a root-cause-before-fix principle;
- four phases:
  - root-cause investigation;
  - pattern analysis;
  - hypothesis and testing;
  - implementation and verification;
- red flags and anti-shortcut guidance;
- explicit handling for repeated failed fixes;
- a quick-reference phase table;
- links to three supporting technique files;
- references to other Superpowers Skills for testing and completion
  verification.

The selected source unit includes the three named local supporting technique
files. It does not include the entire Superpowers plugin or any other
Superpowers Skill.

### Intended usage

The source repository presents Superpowers as a composable methodology for
coding agents. Its installation is harness-specific. For Codex, the public
README points to the Codex plugin marketplace rather than requiring a direct
manual prompt copy.

That installation mechanism is useful ecosystem context but is not the
intervention boundary for this experiment. Installing the full plugin would
activate more than systematic debugging and would confound attribution.

### Dependency on harness and tools

The bounded source unit has no intrinsic requirement for a new executable
tool. It is an agent-visible procedure and local reference material.

However, the repository-level installation has dependencies that must not be
silently included in the treatment:

- a harness that can load a Skill or plugin;
- any plugin session-start or activation behavior;
- the availability of referenced companion Skills;
- the agent's normal repository and test tools.

For the first experiment:

```text
No new tools
No plugin hooks
No other Superpowers Skills
No automatic session-start behavior
No hidden repository facts
```

The control and treatment must use the same tool surface. The treatment adds
only the bounded source unit at the declared intervention boundary.

### Capability model

The artifact does not provide one undifferentiated "debugging" capability. Its
main behavioral claims can be mapped as follows:

| Skill component | Expected trajectory change | Observable evidence |
| --- | --- | --- |
| Root-cause investigation | Reproduce the failure, inspect evidence, trace the origin before editing | Error reading, reproduction attempts, code-path inspection, evidence-gathering tool calls |
| Pattern analysis | Compare working and failing examples and identify relevant differences | Reference search, comparison steps, dependency inspection |
| Single-hypothesis testing | Form one explicit explanation and test it with a minimal change | Emitted hypothesis, selected test, one-variable change, test result |
| Verification and regression checking | Validate the target fix and surrounding behavior before completion | Target tests, regression tests, result inspection, final verification |
| Failed-fix recovery | Stop stacking fixes, return to investigation, and revise the hypothesis | Reverted edit, strategy change, new hypothesis, retry sequence |
| Red-flag and anti-shortcut guidance | Reduce symptom fixes, shotgun edits, and premature conclusions | Fewer bundled edits, fewer unverified claims, explicit stop or re-analysis |
| Supporting root-cause tracing | Move backward through callers and data flow to the source of a failure | Call-chain inspection, data-flow tracing, localization changes |
| Supporting defense-in-depth | Add validation at appropriate layers after the cause is understood | Layer-specific validation or regression checks |
| Supporting condition-based waiting | Replace arbitrary waiting with condition-based checks when timing is the cause | Wait-condition inspection, reduced timing guesswork |

These are expected behavior changes, not confirmed utility claims. The
experiment must determine whether they occur and whether they improve the
trajectory.

### Intervention boundary

The recommended boundary is:

```text
At the start of the agent task, after the fixed base instructions
and before the task-specific repository investigation.
```

The treatment receives the four-file source unit, with `SKILL.md` as the
entrypoint and the three supporting files available as local reference
material. The control receives none of these files.

The following are explicitly outside the selected treatment:

- the Superpowers plugin manifest;
- session-start hooks;
- other Superpowers Skills;
- TDD or verification companion Skills;
- Superpowers marketplace behavior;
- extra tools or permissions;
- the repository's creation log and validation tests;
- any task-specific adaptation.

This is a source-unit boundary, not a rewritten copy of the Skill. The
experiment records the source paths, revision, hashes, and excluded
dependencies so that a later execution can reproduce the boundary.

### Experimental causality

The bounded source unit supports a clear comparison:

```text
Control:
  Model + Harness + Tools

Treatment:
  Model + Harness + Tools
  + Superpowers systematic-debugging source unit
```

The boundary is clearer than installing the full plugin because the
treatment does not silently add other procedural capabilities, hooks, or
tools.

It still requires controls for:

- the extra prompt/context length;
- the agent's ability to read supporting files;
- the exact insertion position;
- whether the harness automatically activates referenced Skills;
- any provider-specific system-prompt treatment.

### Bias analysis

#### Prompt bias

The treatment is intentionally a stronger procedural prompt. This is the
intervention, not an accidental flaw, but it creates a direct prompt-length
and instruction-strength effect.

Mitigation:

- keep the control prompt unchanged;
- record exact rendered treatment text;
- measure prompt and context cost;
- do not describe a prompt effect as a general debugging capability without
  trajectory evidence.

#### Tool bias

The full Superpowers plugin can bring hooks and other Skills. The selected
source unit must not activate them.

Mitigation:

- inject only the four-file source unit;
- keep tools and permissions identical;
- fail the protocol if plugin hooks or companion Skills activate.

#### Knowledge leakage

The selected source unit is a generic procedure and does not contain the
selected task statements, reference patches, hidden tests, or repository
facts. The repository's creation log and validation examples are not part of
the treatment.

Mitigation:

- inspect the final agent-visible artifact;
- exclude creation logs, test fixtures, and unrelated repository material;
- audit task prompts for condition leakage.

#### Workflow lock-in

The artifact uses strong mandatory language, a four-phase order, explicit
anti-shortcuts, and a rule for questioning architecture after repeated failed
fixes. That may reduce thrashing, but it may also prevent a model from using a
shorter correct path.

Mitigation:

- retain `F4` over-exploration and `F6` unnecessary procedure overhead;
- record whether the agent had already localized the defect before following
  the procedure;
- use task diversity and held-out tasks;
- allow the result to be neutral or harmful.

#### Benchmark bias

Systematic debugging is naturally aligned with repository-level bug tasks. A
positive result on this slice cannot establish utility for feature work, UI
design, brainstorming, or all software engineering tasks.

Mitigation:

- state the task-family scope explicitly;
- include multiple debugging families;
- exclude feature-only and environment-only tasks;
- do not generalize beyond the tested scope.

#### Prior validation bias

The source repository includes a creation log describing local pressure tests
for the Skill. That is provenance about how the artifact was developed, not
independent evidence that it improves SkillNudge trajectories.

Mitigation:

- treat the creation log as a source note only;
- run a fresh No Skill versus Original Skill comparison;
- do not use upstream self-tests as utility evidence.

#### Version drift

The upstream `main` branch changes over time. A future installation from
`main` would not reproduce this review.

Mitigation:

- pin `v6.4.1`;
- record the tag revision and file hashes;
- fail artifact verification if the manifest changes.

### Evolution analysis

The source unit is suitable for future evolution because it has multiple
meaningful decomposition boundaries:

```text
full source unit
  -> primary SKILL.md sections
  -> supporting technique files
  -> selected procedural rules
```

Potential later probes include:

- remove or compress the red-flag language;
- remove the explicit four-phase ordering;
- remove the hypothesis section;
- remove or compress the verification section;
- remove a supporting technique file;
- replace the waiting guidance with a less prescriptive variant.

Each probe must be tied to an observed failure or redundancy pattern. The
experiment must not use the decomposition to search indefinitely for the best
prompt.

The source unit therefore supports:

- `KEEP` when the full unit improves verified outcomes with acceptable cost;
- `COMPRESS` when a named section adds cost without utility;
- `MODIFY` when a named rule creates a reproducible failure;
- `REPLACE` when another bounded procedure addresses the same capability need
  better;
- `RETIRE` when no scoped utility remains or harm persists.

### Candidate judgment

```yaml
experimental_causality: high
capability_interpretability: high
bias_control: medium
evolution_value: high
reproducibility: high
first_experiment_suitability: high
```

The main condition for the `high` suitability judgment is the bounded
source-unit boundary. The full Superpowers plugin would receive a lower
judgment.

---

## 3.2 Candidate A alternative scope: full Superpowers plugin

### Identity

```yaml
name: Superpowers full plugin
source_repository: https://github.com/obra/superpowers
version: v6.4.1
plugin_manifest: .codex-plugin/plugin.json
license: MIT
author: Jesse Vincent
scope:
  - plugin manifest
  - many composable skills
  - hooks and harness integrations
  - supporting documentation
```

The public plugin metadata describes a broad development methodology covering
planning, TDD, debugging, collaboration, and delivery workflows. The README
documents harness-specific installation, including Codex App and Codex CLI.

### Why it is not the first intervention artifact

The full plugin does not create a clean test of systematic debugging. It may
change:

- planning behavior;
- brainstorming behavior;
- test-driven development behavior;
- subagent delegation;
- completion verification;
- session startup behavior;
- tool or harness integration.

Any measured improvement or harm could therefore be attributed to a combined
workflow package rather than the debugging intervention.

The full plugin remains a possible later intervention for a separate
capability-lifecycle experiment. It is not the Original Skill for this
experiment.

### Causal judgment

```yaml
experimental_causality: low
capability_interpretability: low
bias_control: low
evolution_value: low_for_first_experiment
reproducibility: medium_when_plugin_is_pinned
first_experiment_suitability: low
```

Pinning a plugin version would solve source reproducibility but would not solve
causal attribution.

---

## 3.3 Candidate B: Aspire Issue Investigation Skill

### Identity

```yaml
name: Aspire Issue Investigation
source_repository: https://github.com/microsoft/aspire
source_path: .agents/skills/issue-investigation/SKILL.md
source_revision: 73b6834143e0f3ae6848665e048961ba6add39ad
license: MIT
maintainer: Microsoft .NET Foundation and Aspire contributors
git_blob_sha: c6c3fae7ae0d8878ecd21e03f00be21e4439dd2e
sha256: f27a1fd500137944964891158035aabbfefbd846d7496b6b33bc5450a93bc158
version_status: main snapshot; no independent Skill release tag verified
```

This is a public repository-local Skill, not a generic Skill marketplace
package. The source file is version-pinnable by repository commit and content
hash.

### Public structure

The Skill contains:

- a context-before-reproduction rule;
- an issue dossier step;
- issue-area classification and specialized routing;
- an information-sufficiency check;
- reproduction-environment preparation;
- reproduction and cause narrowing;
- a structured investigation result format;
- a separate path for a requested code fix.

It also contains repository-specific questions and commands involving Aspire
CLI or SDK versions, AppHost shape, OS and shell, external services, Docker,
Azure, GitHub issues, comments, and PR workflows.

### Intended usage

The Skill is intended to investigate issues in the `microsoft/aspire`
repository. It is not presented as a generic debugging procedure that can be
inserted unchanged into an arbitrary coding-agent task.

No standalone installer for this file was identified in the inspected source.
It is a repository-local artifact under `.agents/skills/` and assumes a
harness that discovers or loads repository-local Skills.

The artifact assumes:

- an Aspire GitHub issue or equivalent issue context;
- the Aspire repository and its local conventions;
- access to repository-specific tools and scripts;
- a user approval boundary before posting issue comments or taking certain
  actions;
- an environment that can reproduce Aspire-specific behavior.

### Capability model

| Skill component | Expected trajectory change | Observable evidence |
| --- | --- | --- |
| Context before reproduction | Gather version, OS, install path, project shape, and expected/actual behavior before acting | Information requests, issue-context inspection, reduced premature fixes |
| Specialized routing | Route an issue to area-specific investigation procedures | Selected area, skill handoff, command choice |
| Dependency readiness | Check tools and classify installation or credential risk before changing the environment | Version probes, dependency summary, blocked state |
| Faithful reproduction | Reproduce in an environment matching the report before inferring cause | Setup commands, environment record, reproduction attempts |
| Cause narrowing | Vary one factor at a time and preserve evidence | Controlled comparisons, logs, traces, generated artifacts |
| Evidence-backed result | Report reproduced, not reproduced, blocked, or design-only with confidence | Structured final dossier, likely cause, artifacts, next action |

This is a useful investigation capability, but it measures issue triage and
environment-aware reproduction more than a generic repository debugging
procedure.

### Intervention boundary

A clean treatment would require:

```text
The agent is working inside an Aspire issue-investigation task
and receives the repository-local Skill at task start.
```

That boundary is not portable to the current SkillNudge first experiment,
whose task domain is a broader repository-level debugging slice. If the Skill
is inserted into a non-Aspire task, many instructions become irrelevant or
misleading.

### Bias analysis

#### Repository-specific knowledge

Aspire names its own CLI, AppHost, dashboard, Azure, issue labels, paths,
scripts, and reporting conventions. That is useful domain capability but also
task-context knowledge that can produce an unfair advantage on Aspire tasks.

#### Tool and environment bias

The workflow explicitly considers Docker, GitHub CLI, Azure tooling, browsers,
project-specific scripts, and possible installations. It changes the
environment-preparation behavior and may cause additional tool use.

#### User-interaction bias

The Skill includes approval boundaries for issue comments and follow-up
actions. A task harness without the same user-approval interface would not
execute the same procedure.

#### Capability mixing

The routing table delegates to specialized Aspire Skills. Activating those
dependencies would make the treatment a bundle rather than one artifact.

#### Outcome mismatch

The intended result is often a diagnostic dossier or a request for more
information, not a repository patch that passes a debugging oracle. It does
not align cleanly with the first Experiment Card's task-success and
regression-oracle design.

### Evolution analysis

The Skill is decomposable and has strong evolution value within Aspire:

- context collection can be compressed;
- dependency readiness can be adapted;
- reproduction protocols can be specialized;
- reporting formats can be changed;
- routing rules can be replaced.

However, its evolution would remain repository-specific. It is better suited
to a later experiment about issue-investigation capability, environment-aware
reproduction, or evidence-backed triage.

### Candidate judgment

```yaml
experimental_causality: medium
capability_interpretability: medium
bias_control: low_for_general_debugging
evolution_value: high_within_aspire
reproducibility: medium
first_experiment_suitability: low_as_primary_artifact
```

It is a valid public workflow artifact and a useful negative comparator, but
it should not be selected as the first generic Systematic Debugging Skill.

---

## 4. Recommended First Experiment Artifact

### Selection

```yaml
Selected Artifact:
  name: Superpowers systematic-debugging source unit
  repository: obra/superpowers
  source_tag: v6.4.1
  source_tag_commit_observed: 5bf4e78011075bcfc0dc295f0724994cd123ee71
  source_paths:
    - skills/systematic-debugging/SKILL.md
    - skills/systematic-debugging/root-cause-tracing.md
    - skills/systematic-debugging/defense-in-depth.md
    - skills/systematic-debugging/condition-based-waiting.md
  primary_file_revision: c74782ead66b8ded584d9b9cf64dcba95457f320
  primary_file_git_blob_sha: 095d194ac041502905f15b01d22d294fb94db8b2
  primary_file_sha256: 808fc5717aa88ad65efff312b11c186294d3e6ee301afb584e2f86599b137787
  manifest_sha256: 92dc8f44a0a729f72e32e1c000f0e37ad8cfb9cbd6346ed4ddbe92694ebe86eb

Reason:
  The source unit provides an explicit, version-pinnable, decomposable,
  agent-visible debugging procedure without requiring a new tool surface or
  repository-specific facts.

Scope:
  First utility experiment on repository-level debugging tasks, using the
  declared four-file source unit as the Original Skill.

Intervention boundary:
  Make the source unit available at the fixed task-start boundary. Do not
  install the full Superpowers plugin. Do not activate hooks, companion
  Skills, or additional tools.

Known limitations:
  The artifact is a strong procedural prompt and may cause prompt-length cost,
  workflow lock-in, over-exploration, or false confidence in root-cause claims.
  It is generic but not capability-neutral: it is intentionally aligned with
  debugging tasks. Its value remains to be measured.
```

### Why this is the cleanest first artifact

The selected source unit provides the strongest balance across the North Star
criteria:

1. **Experimental causality**
   Its content can be added or withheld while leaving the model, harness,
   tools, environment, task, and oracle unchanged.
2. **Capability interpretability**
   Its sections map to observable investigation, hypothesis, verification,
   regression, and recovery behavior.
3. **Bias controllability**
   The full plugin can be excluded, preventing other Skills and hooks from
   entering the treatment.
4. **Evolution value**
   Sections and supporting files provide meaningful future ablation and
   compression boundaries.
5. **Reproducibility**
   The source tag, file paths, commit reference, Git blob SHA values, and
   SHA-256 manifest can be checked without relying on a moving `main` branch.

This is not a claim that Superpowers is the best debugging Skill. It is a
claim that this bounded source unit is the clearest first treatment for
studying intervention utility.

### What the artifact measures

The first experiment should interpret the artifact as a bundle of procedural
capabilities:

```text
Root-cause investigation
Pattern comparison
Hypothesis formation and minimal testing
Verification discipline
Regression checking
Recovery after failed attempts
Resistance to shortcut behavior
```

It does not directly measure:

- general software engineering ability;
- code quality independent of the oracle;
- model intelligence;
- benchmark difficulty;
- human debugging expertise;
- utility across all task domains;
- long-term skill evolution.

The experiment must state which of the observable behaviors changed before
claiming that the capability itself created utility.

---

## 5. Experiment Risk Register

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Skill is too long | Utility cannot be attributed and prompt/context cost is hidden | Record rendered token/context cost; retain section-level ablation as a later development probe |
| Full plugin leaks into treatment | Other Skills, hooks, or tools create a bundled intervention | Use only the four-file source unit; verify no plugin activation or companion Skill loading |
| Strong wording creates workflow lock-in | Agent over-explores or refuses an efficient direct fix | Record F4 and F6; include simple and complex debugging tasks; allow neutral or harmful outcomes |
| Supporting files are not available consistently | Runs differ in actual treatment content | Pin all four paths and verify the manifest before execution |
| Cross-Skill references activate hidden capabilities | TDD or verification workflows become unplanned treatments | Treat referenced Skills as excluded dependencies; fail protocol if they activate |
| Task set is naturally favorable to debugging procedure | Positive effect does not generalize beyond selected tasks | Use four debugging families, held-out tasks, and explicit scope limits |
| Task is solved by direct code regeneration | Experiment measures code generation rather than investigation | Include debugging-depth review and require observable oracle-relevant investigation where appropriate |
| Upstream self-tests are mistaken for utility evidence | Existing claims bias the result | Treat creation log as provenance only; run fresh paired conditions |
| Upstream revision moves | Later reruns silently use another artifact | Pin `v6.4.1`, record file hashes, and verify the manifest |
| Prompt placement changes behavior | Treatment effect is mixed with system/user message position | Freeze the insertion boundary and record rendered inputs |
| Oracle or environment failure | Infrastructure failure is misclassified as Skill harm | Separate agent, environment, evaluation, and ambiguity outcomes |
| Artifact license is misunderstood | Redistribution or derivative use creates compliance risk | Record MIT provenance and verify obligations before any local reproduction |
| Skill helps only one model or harness | Result is overgeneralized as universal utility | Scope the decision to the tested model, harness, task family, and window |

---

## 6. North Star Alignment Review

```yaml
Lifecycle stage:
  OBSERVE / DIAGNOSE / EVOLVE

Research question:
  Does this artifact allow SkillNudge to measure whether an external capability
  intervention improves a repository-level debugging trajectory and supports a
  keep, compress, modify, replace, or retire decision?

Evidence produced:
  - source repository and artifact identity
  - version, revision, license, and content hashes
  - bounded intervention boundary
  - capability decomposition
  - observable behavior mapping
  - bias and confound analysis
  - future ablation and evolution boundaries

Baseline:
  No Skill

Treatment:
  Superpowers systematic-debugging source unit at the fixed boundary

Trajectory visibility:
  Investigation, pattern analysis, hypothesis/testing, verification,
  regression checking, recovery, retries, and procedural overhead are
  observable through the Experiment Card v0.2 Trace Artifact.

Evolution implication:
  The source unit can support later section-level compression, modification,
  replacement, or retirement if paired outcome and trajectory evidence
  justifies the action.

Gate:
  CONDITIONAL PASS
```

### Why the gate is conditional

The artifact passes the selection gate because it is identifiable,
decomposable, and insertable without changing the tool surface.

It remains conditional because the following must be completed before live
utility execution:

- final agent-visible rendering;
- exact source and manifest verification;
- confirmation that no companion Skills or hooks activate;
- provider/harness insertion test;
- task-specific leakage audit;
- final human confirmation of the four-file source boundary.

This review does not itself freeze the Experiment Run or authorize Phase 2
implementation.

---

## 7. Final Decision

### Selected artifact

The recommended first intervention artifact is:

```text
obra/superpowers
skills/systematic-debugging/
at tag v6.4.1
with the four-file manifest defined in Section 4
```

The full Superpowers plugin is not selected.

The Aspire Issue Investigation Skill is not selected as the primary artifact.
It remains a useful comparator for a later repository-specific issue-triage
experiment.

### Why it fits SkillNudge's North Star

The selected source unit supports a causal question rather than a marketplace
question:

```text
No Skill
vs
One version-pinned external debugging procedure
```

The treatment can be withheld, inserted, observed, diagnosed, decomposed, and
later evolved or retired. That makes it possible to study whether the
intervention deserves to exist for a defined scope, instead of merely
measuring whether a popular Skill can produce a patch.

### Remaining uncertainties

- Whether the four-file source unit or only `SKILL.md` should be exposed in
  the final harness representation.
- Whether the selected provider and harness automatically resolve the
  cross-Skill references inside `SKILL.md`.
- Whether the source unit's strong procedural language creates unacceptable
  cost on easy debugging tasks.
- Whether all four debugging families in the Experiment Card v0.2 are
  sensitive to the same intervention components.
- What numeric thresholds define material cost, unacceptable regression, and
  sufficient transfer.
- Whether the original source license and any future local packaging impose
  additional distribution obligations.
- Whether an alternative artifact should be tested as a replacement rather
  than as a direct competitor.

### Entry decision

```yaml
Dataset Selection:
  allowed to proceed to the next review step
  subject to final artifact-boundary and manifest verification

Phase 2 implementation:
  not allowed to start from this document

Live utility experiment:
  not allowed to start until the conditional gate is resolved

External Skill download/vendor:
  not performed in this task
```

---

## 8. Evidence Sources

All source references were checked on 2026-09-19. The repository records
identity and provenance only; it does not copy external Skill content.

### Superpowers

- Repository: https://github.com/obra/superpowers
- v6.4.1 source tag: https://github.com/obra/superpowers/tree/v6.4.1
- Primary Skill: https://github.com/obra/superpowers/blob/v6.4.1/skills/systematic-debugging/SKILL.md
- Root-cause tracing: https://github.com/obra/superpowers/blob/v6.4.1/skills/systematic-debugging/root-cause-tracing.md
- Defense in depth: https://github.com/obra/superpowers/blob/v6.4.1/skills/systematic-debugging/defense-in-depth.md
- Condition-based waiting: https://github.com/obra/superpowers/blob/v6.4.1/skills/systematic-debugging/condition-based-waiting.md
- Codex plugin metadata: https://github.com/obra/superpowers/blob/v6.4.1/.codex-plugin/plugin.json
- License: https://github.com/obra/superpowers/blob/v6.4.1/LICENSE

### Aspire

- Repository: https://github.com/microsoft/aspire
- Issue Investigation Skill: https://github.com/microsoft/aspire/blob/73b6834143e0f3ae6848665e048961ba6add39ad/.agents/skills/issue-investigation/SKILL.md
- License: https://github.com/microsoft/aspire/blob/main/LICENSE.TXT

### Related local design sources

- [Skill Utility Drift Experiment Card v0.2](/Users/kai/Desktop/Work/github/kaiykk/skillnudge/docs/research/skill-utility-drift-experiment-card-v0.2.md)
- [Dataset Artifact Selection Review v0.1](/Users/kai/Desktop/Work/github/kaiykk/skillnudge/docs/research/dataset-artifact-selection-review-v0.1.md)
- [North Star Gate v0.1](/Users/kai/Desktop/Work/github/kaiykk/skillnudge/docs/north-star-gate.md)

---

## 9. Scope and Validation Record

This document is documentation-only.

Expected validation:

```text
git diff --check
./scripts/check_publish_gate.sh
```

Expected scope result:

```text
only documentation changed
no runtime or product code changed
no contracts changed
no dependencies changed
no Skill downloaded into the repository
no external repository vendored
Phase 2 implementation NOT started
```
