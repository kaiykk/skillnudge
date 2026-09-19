# Skill Artifact Freeze Acceptance Review v0.1

**Status:** ACCEPTANCE REVIEW
**Scope:** Treatment artifact identity and experimental boundary only
**Date:** 2026-09-19
**Live experiment:** NOT AUTHORIZED

This review answers:

> Is the frozen Skill artifact sufficiently identifiable and bounded to become
> the Treatment intervention of a causal utility experiment?

It reviews the existing:

- Skill Artifact Selection Review v0.2;
- Skill Artifact Manifest Freeze v0.1;
- Experiment Runner Architecture Review v0.1.

It does not:

- write runtime code;
- add dependencies;
- vendor or download the external Skill;
- modify the Experiment Runner;
- modify contracts;
- connect a provider;
- run a benchmark or live task;
- make a legal conclusion about the external license.

The artifact under review is:

```text
Repository:
  obra/superpowers

Release:
  v6.4.1

Source unit:
  skills/systematic-debugging/SKILL.md
  skills/systematic-debugging/root-cause-tracing.md
  skills/systematic-debugging/defense-in-depth.md
  skills/systematic-debugging/condition-based-waiting.md
```
---

## 1. Acceptance Summary

| Dimension | Decision | Review result |
| --- | --- | --- |
| Identity acceptance | PASS | Repository, release, tag object, peeled commit, ordered paths, and hash strategy are recorded |
| Boundary acceptance | PASS WITH SCOPE LIMIT | The four-file unit excludes the full workflow package, but does not isolate each internal debugging technique |
| Provenance and license acceptance | CONDITIONAL | Provenance and MIT record are present; final snapshot and redistribution record remain pre-run requirements |
| Intervention exposure acceptance | PASS WITH SCOPE LIMIT | Fixed task-start prompt/context injection is adequate for the first causal question, but does not test discoverability |
| Overall artifact gate | CONDITIONAL APPROVAL | Ready for engineering integration of the declared boundary; not ready for live execution without the pre-run gate |

The artifact is sufficiently identifiable and bounded to serve as the intended
Original Skill treatment **provided that** the pre-run verification record
recomputes the source hashes, confirms the exact four-file boundary, verifies
rendering completeness, and keeps all excluded dependencies inactive.

---

## 2. Identity Acceptance

### 2.1 Required identity fields

The Manifest Freeze records:

```yaml
repository:
  url: https://github.com/obra/superpowers

release:
  tag: v6.4.1

tag_object:
  sha: b92c4fa87ea1252077a7f7d3bf420e52325dd25e
  type: annotated_tag

peeled_commit:
  sha: 5bf4e78011075bcfc0dc295f0724994cd123ee71

included_files:
  ordered:
    - skills/systematic-debugging/SKILL.md
    - skills/systematic-debugging/root-cause-tracing.md
    - skills/systematic-debugging/defense-in-depth.md
    - skills/systematic-debugging/condition-based-waiting.md

hash_strategy:
  raw_file_sha256: required
  canonical_manifest_sha256: required
  rendered_payload_sha256: required
```

This is sufficient to resolve the source tree independently of a moving
branch or an unpinned human-readable version label.

### 2.2 Reproducibility checks

| Check | Result | Reason |
| --- | --- | --- |
| Repository is named | PASS | `obra/superpowers` and the repository URL are recorded |
| Release tag is named | PASS | `v6.4.1` is explicit |
| Tag object is recorded | PASS | Annotated tag object SHA is separate from the content commit |
| Peeled commit is recorded | PASS | File resolution uses `5bf4e780...` |
| Included paths are explicit | PASS | Exactly four repository-relative paths are listed |
| File ordering is explicit | PASS | Entry point first, then three supporting files |
| Raw file hashing is defined | PASS | SHA-256 is computed over exact source bytes |
| Canonical manifest hashing is defined | PASS | Stable path-to-digest serialization is specified |
| Rendered payload hashing is defined | PASS | Source identity is separated from agent-visible representation |
| Supporting-file hashes are independently rechecked | PENDING | Existing values are carried forward and must be recomputed before execution |

### 2.3 Identity decision

```yaml
decision: PASS
condition:
  - pre-run verification must recompute all four raw file hashes
  - the recomputed canonical manifest hash must match
  - a mismatch creates a new artifact revision or blocks the run
```

The absence of individually recorded Git blob SHAs for the three supporting
files does not make the artifact unidentifiable because the peeled commit,
ordered paths, raw SHA-256 strategy, and carried-forward file digests together
provide a reproducible identity. Recording those blob SHAs during the pre-run
verification is still recommended for audit convenience.

---

## 3. Boundary Acceptance

### 3.1 Included boundary

The Treatment source unit includes only:

```text
skills/systematic-debugging/SKILL.md
skills/systematic-debugging/root-cause-tracing.md
skills/systematic-debugging/defense-in-depth.md
skills/systematic-debugging/condition-based-waiting.md
```

The first file is the entrypoint. The other three files are explicitly named
supporting techniques within the same systematic-debugging directory.

### 3.2 Excluded boundary

The following remain outside the Treatment:

```text
full Superpowers plugin
plugin manifest as executable integration
hooks and session-start behavior
all other Skills
TDD workflow
verification-before-completion workflow
planning and brainstorming workflows
subagent or parallel-execution workflows
code-review and delivery workflows
marketplace and installer behavior
upstream tests, fixtures, examples, and creation logs
dynamic routing
additional tools or permissions
task-specific adaptation
```

Cross-Skill references in `SKILL.md` are unresolved references, not implicit
inclusions. A harness must not fetch or activate them automatically.

### 3.3 Isolation question

The relevant isolation question is:

> Does the boundary isolate a bounded systematic-debugging intervention from
> the general coding workflow automation supplied by the full plugin?

It does, for the first experiment, because:

- the source paths are explicit;
- the full plugin is excluded;
- hooks and session-start behavior are excluded;
- other workflow Skills are excluded;
- no new tools or permissions are added;
- dynamic routing is disabled;
- the Control can receive the same execution environment without the payload.

The boundary does **not** isolate every internal component of systematic
debugging. For example, root-cause tracing, verification discipline,
defense-in-depth, and condition-based waiting remain bundled within the
Original Skill treatment.

That limitation is acceptable for the first question:

```text
No Skill
vs
Original four-file systematic-debugging source unit
```

It is not sufficient for a later claim such as:

```text
The verification section alone caused the observed utility.
```

That would require a separately preregistered ablation or evolution
experiment.

### 3.4 Boundary decision

```yaml
decision: PASS
scope_limit:
  - isolates source-unit treatment from full-plugin automation
  - does not isolate individual source-unit components
  - unresolved cross-Skill references must remain inert
```

---

## 4. Provenance and License Acceptance

### 4.1 Provenance record

The current record includes:

```yaml
source_repository: https://github.com/obra/superpowers
release_tag: v6.4.1
tag_object_sha: b92c4fa87ea1252077a7f7d3bf420e52325dd25e
peeled_commit_sha: 5bf4e78011075bcfc0dc295f0724994cd123ee71
source_directory: skills/systematic-debugging/
included_path_manifest: four ordered paths
previous_manifest_sha256: 92dc8f44a0a729f72e32e1c000f0e37ad8cfb9cbd6346ed4ddbe92694ebe86eb
```

The repository contains provenance metadata and hash records only. It does
not contain the external source files.

### 4.2 License record

The upstream release is recorded as MIT-licensed, with `LICENSE` retained as a
provenance-only source reference.

This review does not determine:

- whether a particular redistribution model is legally sufficient;
- whether a future local packaging choice creates additional obligations;
- whether a provider or harness has its own licensing requirements.

It records only the experiment requirements:

1. Preserve the upstream repository, release, and license provenance.
2. Preserve the required MIT notice if source content is copied or
   redistributed in a local snapshot or execution bundle.
3. Do not treat a local rendered payload as provenance-free.
4. Record whether the execution environment used a read-only snapshot or a
   controlled source fetch.
5. Do not change source content while preparing the artifact.

### 4.3 Future snapshot requirement

Before live execution, the future preparation task must record:

```yaml
future_snapshot:
  repository_url:
  release_tag:
  tag_object_sha:
  peeled_commit_sha:
  included_paths:
  excluded_paths:
  file_sha256:
  manifest_sha256:
  license_path:
  license_hash:
  snapshot_location_or_reference:
  verification_timestamp:
```

The snapshot location may be outside this repository. Credentials, tokens, and
private provider configuration must not be placed in the review artifact.

### 4.4 Provenance decision

```yaml
decision: CONDITIONAL
reason:
  - source identity and MIT provenance are recorded
  - final local snapshot and license record are not yet independently verified
  - no legal conclusion is made
blocking_condition:
  - complete the pre-run provenance and hash verification before live execution
```

This conditional result does not reject the artifact. It prevents an
unverified future copy from being treated as the same treatment.

---

## 5. Intervention Exposure Acceptance

### 5.1 Proposed exposure

The first experiment uses:

```text
fixed task-start prompt/context injection
```

The conceptual Treatment sequence is:

```text
fixed base instructions
    ->
fixed wrapper
    ->
four-file source-unit payload
    ->
fixed task input
    ->
repository investigation
```

The Control receives the same base instructions and task input without the
source-unit payload.

### 5.2 Benefits

#### Causal clarity

The Treatment variable is narrow:

```text
same model
same harness
same tools
same task
same environment
same evaluator
same budgets
same retries
    +
fixed source-unit payload
```

This avoids mixing Skill utility with:

- retrieval quality;
- candidate selection;
- dynamic routing;
- resource discoverability;
- plugin activation;
- Treatment-only tools;
- hidden middleware behavior.

#### Deterministic exposure

The same source unit can be:

- rendered in a fixed order;
- hashed before execution;
- withheld entirely from Control;
- exposed identically across Treatment runs;
- compared against a later adapted or compressed version.

This is sufficient for the first causal question:

> Does this declared external procedure change the trajectory or outcome when
> it is present?

### 5.3 Risks

#### Context overhead

The four-file payload consumes context and may increase input tokens, latency,
or truncation risk. A negative result could reflect the cost of exposure
rather than the absence of useful debugging guidance.

Required treatment:

- record rendered token count;
- record latency and total steps;
- detect truncation;
- preserve cost evidence separately from outcome evidence;
- allow `SKILL_HURTS` only when the run and oracle remain valid.

#### Discoverability is not measured

Static injection gives the agent the intervention without asking it to find
or choose the Skill. This is intentional for the first causal test, but it
does not evaluate:

```text
vague intent
-> capability inference
-> Skill discovery
-> Skill selection
-> Skill use
```

Those belong to a later discovery/routing experiment.

#### Difference from production Skill systems

Many production Skill systems use resource loading, routing, hooks, or
conditional activation. Fixed injection does not estimate their end-to-end
utility. It estimates the utility of the declared source unit under a static,
controlled exposure boundary.

The result must therefore be scoped as:

```text
utility of the four-file source unit under fixed task-start injection
```

It must not be generalized to:

```text
utility of all Skill systems
```

### 5.4 Exposure decision

```yaml
decision: PASS
scope_limit:
  - valid for the first content-utility experiment
  - does not measure discovery, routing, or resource retrieval
  - rendered payload hash and context cost remain required evidence
  - incomplete or rewritten exposure is a protocol failure
```

---

## 6. Final Experiment Confound Register

| Risk | Effect | Mitigation |
| --- | --- | --- |
| Cross-Skill reference | Agent expects a missing TDD or verification workflow and behaves differently for an unavailable dependency | Keep referenced Skills excluded; record unresolved references; classify activation or dependency failure as protocol failure |
| Hidden plugin behavior | Hooks, session startup, or companion Skills add an unplanned treatment | Do not install the full plugin; use fixed payload only; verify the harness has no automatic Skill activation |
| Context length | Skill appears harmful because of token overhead, truncation, or reduced task context | Record rendered token count, truncation, latency, and cost; do not interpret incomplete exposure as Skill utility |
| Workflow lock-in | Agent performs unnecessary investigation or refuses an efficient direct fix | Include low-sensitivity debugging tasks; inspect steps, tool calls, patch revisions, and verification behavior |
| Static exposure bias | Result reflects always-on injection rather than conditional use | Scope the result to fixed task-start injection; defer discoverability and routing to a separate experiment |
| Source snapshot drift | Later runs use different file bytes under the same release label | Resolve from the peeled commit; recompute all file hashes and canonical manifest hash before execution |
| Tag/commit confusion | Annotated tag object or moving branch is mistaken for the source tree identity | Record tag object and peeled commit separately; resolve files from the peeled commit |
| File-order drift | Same files are rendered in a different order and change instruction priority | Freeze the four-file order and include it in the rendered payload hash |
| Wrapper drift | Additional wording changes instruction strength or semantics | Pin wrapper revision; hash the rendered payload; do not add task-specific advice |
| Encoding or line-ending drift | Source identity and agent-visible content diverge silently | Hash raw bytes before normalization; document UTF-8/LF rendering and hash the result |
| Knowledge leakage | Upstream tests, creation logs, examples, or repository facts give the Treatment task-specific information | Exclude upstream test/example materials and inspect the agent-visible payload |
| Tool-surface asymmetry | Treatment receives tools or permissions not available to Control | Keep filesystem, shell, git, test, network, and retry policies identical |
| Oracle asymmetry | Treatment and Control are evaluated with different checks or environments | Use one evaluator revision, one environment, one target/regression procedure |
| License/provenance omission | A local snapshot cannot be audited or loses required attribution | Preserve repository, release, hash, and MIT provenance in the execution record |
| Model ceiling | No Skill already solves all tasks, hiding any intervention effect | Retain task diversity and interpret a neutral result within the frozen model/task scope |
| Model floor | Both arms fail before debugging behavior can matter | Separate model/environment failures from Skill failure and review task sensitivity |
| Trace instrumentation drift | Trace capture changes context, timing, or retries between arms | Use identical instrumentation and record protocol validity |
| Bundled source-unit effect | A positive result is incorrectly attributed to one section | Report the result for the four-file Original Skill; defer section attribution to ablation |
| Provider rewriting | Provider or harness truncates, reorders, or transforms the payload | Record effective rendered payload when possible; classify unobserved rewriting as a readiness issue |
| Manual intervention | Human correction or approval changes one arm's trajectory | Disable or record human intervention identically; exclude unpaired runs |

---

## 7. Final Gate

### 7.1 Artifact status

```yaml
artifact_status: CONDITIONAL APPROVAL
approved_for:
  - engineering integration of the frozen artifact boundary
  - implementation of manifest verification
  - implementation of fixed task-start exposure
  - preparation of paired Control and Treatment runs
not_approved_for:
  - live experiment execution
  - benchmark execution
  - dynamic routing
  - full-plugin installation
  - utility conclusions
```

### 7.2 Conditions for engineering integration

Engineering may integrate the artifact boundary only if it preserves:

1. the exact repository, tag, tag object, and peeled commit;
2. the exact four included files and explicit order;
3. the excluded full-plugin and cross-Skill boundary;
4. raw file, manifest, and rendered payload hashes;
5. fixed task-start exposure;
6. identical Control and Treatment tools, budgets, retries, and evaluator;
7. no hidden source fetching or companion Skill activation;
8. provenance and MIT license records for any local snapshot.

### 7.3 Conditions before live execution

The status cannot advance to live execution until:

- all four source hashes are recomputed;
- the canonical manifest hash is confirmed;
- the rendering wrapper and payload hash are frozen;
- unresolved cross-Skill references are proven inert;
- the harness proves no hidden plugin or tool activation;
- the Treatment payload is complete and not truncated;
- the Control receives no Treatment content;
- the evaluator and trace boundaries are ready.

### 7.4 Gate interpretation

```text
The artifact is sufficiently identifiable and bounded for engineering
integration, but the evidence boundary is not yet sufficient to authorize
live causal runs.
```

This is a conditional artifact approval, not a utility judgment and not a
benchmark authorization.

---

## 8. North Star Alignment Review

```yaml
Lifecycle stage:
  INTERVENE / OBSERVE / DIAGNOSE

Research question:
  Is the external capability intervention sufficiently identifiable and
  bounded to support a causal utility comparison?

Evidence produced:
  - identity acceptance decision
  - source-unit boundary decision
  - provenance and license requirements
  - fixed-exposure assessment
  - final confound register
  - engineering and pre-run acceptance gates

Baseline:
  No Skill

Treatment:
  Four-file Superpowers systematic-debugging source unit at v6.4.1

Decision enabled:
  KEEP / COMPRESS / MODIFY / REPLACE / RETIRE

Gate:
  CONDITIONAL APPROVAL
```

The review remains aligned with the SkillNudge North Star because it freezes
an intervention boundary that can later be observed, diagnosed, evolved, and
retired. It does not optimize for popularity, benchmark score, or the size of
the Skill package.

---

## 9. Scope Record

```text
documentation only: yes
runtime changes: no
dependencies added: no
external Skill downloaded: no
external Skill vendored: no
experiment runner changed: no
contracts changed: no
provider connected: no
benchmark executed: no
live experiment authorized: no
```
