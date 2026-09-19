# Skill Artifact Manifest Freeze v0.1

**Status:** DESIGN FREEZE FOR FIRST UTILITY EXPERIMENT
**Execution status:** PRE-RUN VERIFICATION REQUIRED
**Scope:** Intervention identity, provenance, file boundary, and rendering
**Date:** 2026-09-19

This document freezes the identity and intended boundary of the first
SkillNudge utility-experiment intervention.

It does not:

- implement runtime code;
- connect a model provider;
- download a dataset;
- run a benchmark or live task;
- vendor the external Skill into this repository;
- add dependencies;
- modify the selected external Skill;
- authorize the Phase 2 experiment.

The artifact is frozen for experiment design. A final pre-run verification of
the source revision, file bytes, rendering, and license record is still
required before any live run.

---

## 1. Freeze Decision

### 1.1 Frozen artifact proposal

```yaml
artifact_id: systematic-debugging-superpowers-v6.4.1-source-unit
name: Superpowers systematic-debugging source unit
source_repository: https://github.com/obra/superpowers
source_directory: skills/systematic-debugging/
release_tag: v6.4.1
tag_object:
  sha: b92c4fa87ea1252077a7f7d3bf420e52325dd25e
  type: annotated_tag
content_commit:
  sha: 5bf4e78011075bcfc0dc295f0724994cd123ee71
  type: peeled_commit
license: MIT
maintainer_or_author: Jesse Vincent / obra
agent_visible_files: 4
full_plugin: excluded
dynamic_routing: false
additional_tools: false
additional_permissions: false
```

The `content_commit` is the identity used for the source file set. The
annotated tag object is recorded separately because an annotated Git tag and
the commit it points to are different Git objects.

The public plugin metadata at this release identifies the package as
Superpowers version `6.4.1`, authored by Jesse Vincent, licensed under MIT,
and containing a broad set of skills. That package identity is provenance
context only. The first experiment does not use the full plugin as its
intervention.

### 1.2 What is frozen

The following are frozen for the first utility experiment:

```text
one source repository
one release tag
one peeled content commit
one four-file source unit
one fixed task-start injection boundary
one deterministic rendering order
one source hash manifest
one rendered-payload hash per execution configuration
```

The frozen object is the **bounded source unit**, not the complete Superpowers
plugin and not an abstract category called "systematic debugging."

### 1.3 What is not claimed

This freeze does not claim that:

- the Skill is useful;
- the Skill is the best debugging procedure;
- the Skill improves any benchmark;
- all references in the source unit are resolved;
- the full Superpowers plugin is appropriate for the experiment;
- the selected source unit should remain unchanged after evidence;
- the source unit should be promoted beyond the tested model, harness, task
  family, and evaluation window.

The freeze makes the intervention identifiable. Utility still requires a
paired No Skill versus Original Skill experiment.

---

## 2. Exact Source Unit

### 2.1 Included files

The agent-visible source unit contains exactly these four files, in this
order:

```text
1. skills/systematic-debugging/SKILL.md
2. skills/systematic-debugging/root-cause-tracing.md
3. skills/systematic-debugging/defense-in-depth.md
4. skills/systematic-debugging/condition-based-waiting.md
```

`SKILL.md` is the entrypoint. The three supporting files are included because
the entrypoint explicitly refers to them as local systematic-debugging
techniques.

### 2.2 File-level manifest

The following values are carried forward from the Artifact Selection Review
v0.2 and are subject to the pre-run verification gate:

| Path | Role | Git blob SHA | SHA-256 |
| --- | --- | --- | --- |
| `skills/systematic-debugging/SKILL.md` | Entry point | `095d194ac041502905f15b01d22d294fb94db8b2` | `808fc5717aa88ad65efff312b11c186294d3e6ee301afb584e2f86599b137787` |
| `skills/systematic-debugging/root-cause-tracing.md` | Supporting technique | Not recorded in v0.2 | `75b933b6a8c40bdb2031b10f21654395b56ec6ab6bc7b018c18d3fe57aeb7fb8` |
| `skills/systematic-debugging/defense-in-depth.md` | Supporting technique | Not recorded in v0.2 | `1e175fb86fc357e58c6aebf5441e481e1b7868b4380c0456b63a17eefbd18ba7` |
| `skills/systematic-debugging/condition-based-waiting.md` | Supporting technique | Not recorded in v0.2 | `e89fec8400d6cd50f43407cec9fab50976ba4d55d0ec2eb51c0bd68036b54c26` |

The previous review also recorded:

```yaml
previous_primary_file_revision:
  commit: c74782ead66b8ded584d9b9cf64dcba95457f320
  interpretation: historical file-provenance record only

previous_manifest_sha256:
  sha256: 92dc8f44a0a729f72e32e1c000f0e37ad8cfb9cbd6346ed4ddbe92694ebe86eb
  input: ordered path-to-content-hash list
  status: carried-forward review value; recompute before execution
```

The source identity is the tag and peeled content commit. The
`previous_primary_file_revision` is not a substitute for the tag commit; it
is retained only because it was recorded in the earlier review and may help
audit how that review established file provenance.

### 2.3 Provenance-only files

Some files may be inspected to establish provenance or licensing but are not
part of the agent-visible treatment:

```text
LICENSE
.codex-plugin/plugin.json
repository README and release metadata
Git tag and commit metadata
```

These files must not be silently concatenated into the Skill payload. Their
role is source identity, license review, or packaging analysis.

---

## 3. Excluded Files and Behaviors

### 3.1 Excluded source paths

The following are excluded from the first treatment:

```text
the complete Superpowers plugin
.codex-plugin/plugin.json as an executable/plugin manifest
plugin hooks
session-start behavior
all other Superpowers Skills
TDD Skills
verification-before-completion Skills
brainstorming and planning Skills
subagent or parallel-execution Skills
code-review and delivery Skills
repository creation logs
upstream tests and fixtures
upstream examples
marketplace or installer behavior
README-only installation instructions
LICENSE text from the agent-visible payload
```

The MIT license remains a provenance and compliance requirement. Excluding its
text from the treatment payload does not remove the obligation to preserve
the license notice if the source is copied or redistributed.

### 3.2 Excluded runtime behaviors

The Treatment must not receive:

- additional executable tools;
- additional filesystem permissions;
- additional network access;
- additional subagents;
- automatic Skill discovery;
- dynamic candidate retrieval;
- dynamic routing;
- hidden companion Skills;
- plugin hooks;
- task-specific adaptation;
- reference patches or hidden tests;
- evaluator-only diagnostics;
- arm-specific retry or recovery logic.

The Control receives the same model, harness, tools, task, environment,
budgets, retries, and evaluator with no source-unit payload.

### 3.3 Cross-Skill references

The source entrypoint contains references to other Superpowers workflows,
including testing and completion-verification procedures. Those referenced
workflows are intentionally excluded.

They must be treated as unresolved external references, not as implicit
dependencies to install. The first experiment must not activate them merely
because the entrypoint mentions them.

If a harness cannot keep those references inert, the run is not a valid
four-file source-unit experiment. It must be classified as a protocol issue,
not silently broadened into a full-plugin treatment.

---

## 4. Source Identity and Provenance

### 4.1 Identity hierarchy

The manifest uses the following identity hierarchy:

```text
repository URL
    ->
release tag
    ->
annotated tag object
    ->
peeled content commit
    ->
ordered source paths
    ->
raw file bytes
    ->
file SHA-256 values
    ->
canonical manifest hash
    ->
rendered payload hash
```

Each level answers a different question:

| Level | Question |
| --- | --- |
| Repository | Which upstream project supplied the source? |
| Tag | Which named release was selected? |
| Tag object | Which Git tag reference was observed? |
| Content commit | Which repository tree supplies the files? |
| Source paths | Which files are in the treatment boundary? |
| Raw file bytes | Did file content change? |
| Manifest hash | Did the ordered file set or any file hash change? |
| Rendered payload hash | Did the agent-visible representation change? |

No single human-readable version string is sufficient for all of these
questions.

### 4.2 Author and license

The source release identifies:

```yaml
author: Jesse Vincent
license: MIT
license_file: LICENSE
license_revision: v6.4.1
```

The MIT notice requires the copyright and permission notice to remain with
copies or substantial portions of the Software. Any future local snapshot,
rendered artifact bundle, or redistribution must preserve the required
attribution and license record.

The repository plugin metadata is not a license substitute. It is recorded
only to explain why the full plugin is excluded from the treatment boundary.
The plugin metadata itself describes capabilities beyond systematic debugging,
including planning, TDD, collaboration, and delivery workflows.

### 4.3 No vendoring decision

This repository does not contain the four source files. It contains only:

- the source identity;
- the selected path manifest;
- hashes;
- rendering rules;
- provenance URLs;
- risks and verification conditions.

A future execution environment may use a read-only local snapshot or a
controlled source fetch, but that snapshot must pass this manifest before it
is exposed to the agent.

---

## 5. Hash Strategy

### 5.1 File hash

For each included file:

1. resolve the file from the peeled content commit;
2. read the exact raw bytes;
3. compute SHA-256 over those raw bytes;
4. record the repository-relative path and digest;
5. reject the artifact if any recorded digest differs.

The raw source hash must be computed before line-ending normalization or
rendering. This keeps source identity separate from prompt representation.

### 5.2 Canonical manifest hash

The manifest hash is computed from a canonical ordered list:

```text
skills/systematic-debugging/SKILL.md <TAB> sha256:<digest>
skills/systematic-debugging/root-cause-tracing.md <TAB> sha256:<digest>
skills/systematic-debugging/defense-in-depth.md <TAB> sha256:<digest>
skills/systematic-debugging/condition-based-waiting.md <TAB> sha256:<digest>
```

The canonical serialization must use:

```text
UTF-8
LF line endings
explicit file order
one record per line
no timestamps
no local absolute paths
no credentials
```

The SHA-256 of this serialization is the `manifest_sha256`.

The carried-forward value is:

```text
92dc8f44a0a729f72e32e1c000f0e37ad8cfb9cbd6346ed4ddbe92694ebe86eb
```

This value is a review artifact, not permission to skip the pre-run
recomputation.

### 5.3 Rendered payload hash

The agent-visible prompt/context payload needs a separate hash because a
stable source can be rendered differently.

The rendered hash must cover:

```text
wrapper revision
file order
file labels
line-ending policy
source contents as rendered
separator format
insertion boundary metadata
```

It must not cover:

- run timestamp;
- run ID;
- API key;
- provider credential;
- mutable task output;
- model response;
- hidden evaluator data.

The source manifest hash and rendered payload hash must both be recorded in a
future run artifact. They answer different questions:

```text
manifest hash:
  Was the selected source unit unchanged?

rendered payload hash:
  Did the agent see the same representation of that source unit?
```

### 5.4 Hash mismatch policy

If any of the following changes, the run must not be presented as the frozen
Original Skill condition:

- repository URL;
- tag or peeled commit;
- included path list;
- raw file hash;
- file order;
- wrapper revision;
- rendering normalization;
- rendered payload hash.

The change requires a new manifest version or a new experiment condition.

---

## 6. Rendering Strategy

### 6.1 Recommended representation

Use a deterministic fixed prompt/context representation at task start.

The conceptual order is:

```text
fixed base instructions
    ->
fixed wrapper
    ->
SKILL.md
    ->
root-cause-tracing.md
    ->
defense-in-depth.md
    ->
condition-based-waiting.md
    ->
fixed task input
```

The source contents must not be rewritten, summarized, paraphrased, or
task-adapted. The wrapper may identify file boundaries and explain that the
payload is a version-pinned external capability intervention, but it must not
add debugging advice that is absent from the selected source unit.

### 6.2 Deterministic rendering rules

The future renderer must:

- use the explicit four-file order;
- decode source bytes as UTF-8;
- apply one documented line-ending policy;
- preserve source text and heading order;
- add stable file-path delimiters;
- use one pinned wrapper revision;
- avoid date, run ID, provider, or task-specific text in the wrapper;
- record the rendered token count when the provider exposes it;
- compute the rendered payload hash after all rendering steps;
- expose the same payload for every Treatment run in the experiment.

The source-level hash must remain the hash of the unmodified raw bytes.

### 6.3 What rendering does not do

Rendering must not:

- resolve or fetch referenced companion Skills;
- activate the Superpowers plugin;
- execute source files;
- alter the model's tool list;
- expand references based on the current task;
- insert hidden task facts;
- remove "unhelpful" sections before evidence;
- add a summary written by the evaluator;
- turn the source unit into a new locally authored Skill.

The full four-file unit is the Original Skill condition. Compression or
section ablation belongs to a later evolution experiment.

### 6.4 Static resource alternative

A later experiment may expose the same four files as a static resource and
measure whether the agent chooses to read them. That would study resource
discoverability and use, not the first causal question.

It is not the v0.1 rendering strategy because it adds a new confound:

```text
Did the intervention help,
or did the agent fail to discover or read the resource?
```

---

## 7. Experimental Risk Register

| Risk | Potential effect | Required control or interpretation |
| --- | --- | --- |
| Unresolved cross-Skill references | The agent may expect TDD or completion-verification procedures that are absent | Keep referenced Skills excluded; record whether the agent reaches an unresolved reference; do not install companions silently |
| Hidden plugin dependencies | Hooks or automatic loading may add capabilities outside the four files | Do not install the full plugin; verify the harness has no hooks, routing, or automatic Skill activation |
| Excessive procedure length | Prompt cost, context pressure, and over-exploration may be mistaken for capability utility | Record rendered token count, steps, latency, and unnecessary procedure signals; allow Skill-neutral or Skill-hurts outcomes |
| Workflow lock-in | Strong procedural language may block a direct correct fix | Include low- and high-sensitivity debugging tasks; inspect verification, recovery, and unnecessary exploration |
| Incomplete source snapshot | A local run may use a different file set or stale branch | Verify tag, peeled commit, paths, per-file hashes, and manifest hash before exposure |
| Tag versus commit confusion | A rerun may use the tag object or a moving branch incorrectly | Record both annotated tag object and peeled content commit; use the peeled commit for file resolution |
| Prompt wrapper drift | A changed wrapper can alter instruction priority or treatment strength | Pin wrapper revision and rendered payload hash |
| Line-ending or encoding drift | Raw source and rendered source may differ without a visible version change | Hash raw bytes first; document UTF-8 and LF rendering policy |
| Task-specific knowledge leakage | The artifact may contain facts about a selected repository or issue | Inspect the bounded source unit; exclude upstream tests, fixtures, creation logs, and task material |
| License/provenance failure | Future copying or redistribution may omit required MIT notice | Preserve `LICENSE` provenance and attribution in any local snapshot or redistribution |
| Upstream version drift | Later executions may silently use a different release | Treat any source or manifest mismatch as a new artifact condition |
| Full-plugin contamination | Planning, TDD, collaboration, or delivery workflows may affect the result | Use only the four-file source unit; reject plugin manifests and hooks from the treatment |
| Model context truncation | The model may not receive the complete source unit | Record payload size and truncation; classify incomplete exposure as protocol failure |
| Provider-specific system behavior | Provider may reorder, truncate, or reinterpret the injected payload | Freeze provider and message boundary separately; record effective rendered input where possible |
| Unsupported local packaging | A local copy may be edited while being prepared for execution | Do not edit source contents; verify hashes after packaging; treat modifications as a new artifact |
| Misclassification of source failure | A bad fetch or malformed rendering may appear as Skill harm | Separate artifact/protocol failure from agent outcome failure |

---

## 8. Pre-Run Verification Gate

Before the first live experiment, a separate implementation or execution
preparation task must produce a verification record containing:

```yaml
artifact_verification:
  repository_url:
  release_tag:
  tag_object_sha:
  content_commit_sha:
  included_paths:
  excluded_paths:
  file_sha256:
  manifest_sha256:
  license_path:
  license_hash:
  wrapper_revision:
  rendered_payload_sha256:
  rendered_token_count:
  unresolved_references:
  verification_timestamp:
  verifier:
```

The gate passes only when:

1. the source resolves to the recorded repository and peeled commit;
2. exactly four included files are present;
3. all four raw SHA-256 values match;
4. the canonical manifest hash matches;
5. no excluded plugin, hook, companion Skill, or extra tool is active;
6. the rendered payload is deterministic and hashable;
7. MIT provenance is retained for any copied or redistributed artifact;
8. the Control receives no treatment payload;
9. the provider and harness do not truncate or rewrite the Treatment
   representation without recording it.

A failed gate blocks live execution. It does not authorize an ad hoc repair or
silent source update.

---

## 9. Remaining Uncertainties

The following remain open after this design freeze:

1. Whether the future harness can inject all four files without context
   truncation or provider-side rewriting.
2. Whether the source unit's cross-Skill references can remain inert in the
   selected harness.
3. Whether the prior supporting-file hashes can be independently re-derived
   from the peeled commit before execution.
4. Whether the final renderer should expose all four files inline or preserve
   a local read-only file boundary while keeping the same agent-visible
   content.
5. What prompt/context overhead is acceptable for the first task slice.
6. Whether low-sensitivity tasks reveal harmful workflow lock-in.
7. Whether the source unit's MIT notice must be embedded in a local execution
   bundle or can remain in a separately linked provenance record.
8. Whether the model/provider exposes enough effective-input metadata to
   verify the rendered payload without recording sensitive content.
9. Whether a later section-level compression experiment can isolate meaningful
   components without changing the causal interpretation of the Original
   Skill baseline.

These uncertainties do not change the frozen source identity. They determine
whether the execution gate can be passed.

---

## 10. North Star Alignment Review

```yaml
Lifecycle stage:
  INTERVENE / OBSERVE / DIAGNOSE

Research question:
  Is the external capability intervention identifiable, reproducible, and
  bounded well enough to test whether it creates measurable utility?

Evidence produced:
  - exact repository, release, tag object, and content commit
  - four-file source-unit manifest
  - included and excluded boundaries
  - source and rendered hash strategy
  - deterministic rendering rules
  - unresolved reference and provenance risks
  - pre-run verification gate

Decision enabled:
  KEEP / COMPRESS / MODIFY / REPLACE / RETIRE

Gate:
  CONDITIONAL PASS
```

### Gate interpretation

The artifact identity is frozen for experiment design:

```text
obra/superpowers
skills/systematic-debugging/
v6.4.1
peeled content commit 5bf4e780...
four explicitly listed files
fixed task-start context boundary
```

The execution gate remains conditional because the final local snapshot,
supporting-file hashes, rendering behavior, unresolved references, and
provider/harness exposure must still be verified immediately before a live
run.

This document does not establish utility, authorize benchmark execution, or
permit the full Superpowers plugin to enter the treatment.

---

## 11. Scope Record

```text
documentation only: yes
runtime changes: no
provider connection: no
dependency changes: no
dataset download: no
benchmark execution: no
external Skill vendored: no
external Skill modified: no
full plugin selected: no
```

---

## 12. Source References

The source identity and provenance references are:

- Repository: https://github.com/obra/superpowers
- Release tag: https://github.com/obra/superpowers/tree/v6.4.1
- Entry point: https://github.com/obra/superpowers/blob/v6.4.1/skills/systematic-debugging/SKILL.md
- Root-cause tracing: https://github.com/obra/superpowers/blob/v6.4.1/skills/systematic-debugging/root-cause-tracing.md
- Defense in depth: https://github.com/obra/superpowers/blob/v6.4.1/skills/systematic-debugging/defense-in-depth.md
- Condition-based waiting: https://github.com/obra/superpowers/blob/v6.4.1/skills/systematic-debugging/condition-based-waiting.md
- Plugin metadata, provenance only: https://github.com/obra/superpowers/blob/v6.4.1/.codex-plugin/plugin.json
- License, provenance only: https://github.com/obra/superpowers/blob/v6.4.1/LICENSE
