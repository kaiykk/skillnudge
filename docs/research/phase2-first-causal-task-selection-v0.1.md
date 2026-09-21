# Phase 2 First Causal Task Selection v0.1

**Status:** Candidate review; first TaskArtifact not frozen

**Scope:** Select one real task and one task-specific Oracle for the first
Control/Treatment pair.

This document records a bounded selection review. It does not implement the
causal slice, run a real pair, delete the existing readiness code, or start a
new Current Outcome.

## 1. Current Outcome Gate

```text
Current Outcome:
  For one real task, one real capability intervention, and one fixed reference
  host, SkillNudge Measurement Plane can produce one valid Control/Treatment
  pair with observable trajectories, compare them using one task-specific
  oracle, and output one scoped utility conclusion.

Part A classification:
  C - NON-BLOCKING EXPANSION / PRINCIPAL OVERRIDE

Part B/C classification:
  A - BLOCKER REMOVAL / GO

Measurement boundary:
  Measurement Plane must not own the Agent runtime, model provider, or
  SkillNudge product reasoning.
```

The repository handbook now records the permanent development rhythm and the
first-pair guardrail. The first-pair task selection remains a research review,
not implementation authorization.

## 2. Frozen Reference Host

```yaml
reference_host: Codex
reason:
  - Phase 1 Native MVP was externally demonstrated on Codex.
  - The installed SkillNudge Skill is already discoverable there.
  - The native retrieval/evidence path is provider-free.
scope:
  - first Phase 2 causal slice only
not_claimed:
  - permanent host support
  - multi-host comparability
```

No second host is selected.

## 3. Candidate Task 1: Native Planning Contract Discoverability Repair

### Task

Reproduce the real SkillNudge maintenance task completed by commit
`869484c`: make the native planning contract visible to the host and keep the
documented enum set aligned with the Python validator. The bounded change is
the focused contract document, the native Skill reference, validator enum
exports, and the regression test that compares the two.

### Repository / initial state

```yaml
repository: SkillNudge
source: /Users/kai/Desktop/Work/github/kaiykk/skillnudge
initial_commit: 865bfdf191ce5d6be1aa3451e7767f063705c0ef
target_change_commit: 869484cf19bd7589c7981e96f5417687166773bc
changed_files_in_reference_change:
  - .agents/skills/skillnudge/SKILL.md
  - .agents/skills/skillnudge/native-contract.md
  - src/skillnudge/planning_contracts.py
  - tests/test_native.py
```

The initial state is reconstructable from Git history. The target commit is
provenance for task construction only; its patch must not be exposed to the
Agent during execution.

### Capability intervention

Treatment receives the frozen four-file
`systematic-debugging-superpowers-v6.4.1-source-unit` through the Codex
host-native treatment boundary. Control receives no external capability
payload. Both arms receive the same repository snapshot, task request, model,
tools, budget, and Oracle.

### Why capability might help

The task is a compact multi-file contract failure with an observed invalid
host-produced structure. Systematic debugging could change the trajectory by
encouraging failure localization, validator-to-document comparison, focused
reproduction, and regression verification. It is not guaranteed to help: the
task may be solved directly from the error and existing tests.

### Control feasibility

Control can inspect the validator and failing contract boundary and can run the
existing tests. The task is not designed so that only Treatment can act.

### Treatment exposure

The host receives the exact frozen source unit at task start through the
Codex-native capability exposure. No new tools, permissions, provider, or
hidden task information are added.

### Task-specific Oracle

The Oracle must be frozen before execution and must evaluate behavior, not
whether the Agent reproduced the historical patch text. It should include:

- the native contract document contains every required enum and required-field
  rule used by the validator;
- the validator accepts a compact valid envelope containing each documented
  enum family;
- invalid enum values are rejected;
- the native regression test passes;
- the full existing test suite passes with no regression.

The exact evaluator script and its clean base-environment record are still
missing. Therefore this candidate is reviewable but not implementation-ready.

### Counterfactual cleanliness

The intended difference is the treatment capability payload only. The
historical target patch is not supplied to either arm. The task is small
enough to keep the same host and tool surface, but it is internal to
SkillNudge, so familiarity with the repository can reduce external
generalization.

### Potential confounds

- contract documentation and validator changes can be solved by direct schema
  inspection without systematic debugging;
- the task touches the public Skill contract boundary, so host instruction
  discoverability may interact with the treatment exposure;
- the four-file change is still a maintenance task, not a general debugging
  workload;
- a test-only success could hide an incomplete documentation boundary unless
  the Oracle checks both accepted and rejected structures.

### External nondeterminism

None is required after the repository snapshot and Codex configuration are
frozen. The host itself remains the principal execution nondeterminism.

### Expected experiment cost

Low to medium. The task is small, the Oracle is deterministic in principle,
and the repository snapshot is available locally.

### Missing assets

- a frozen task artifact containing the initial snapshot identity and visible
  task text;
- a separate Oracle script/configuration with hidden checks;
- a clean-environment hash and exact test-command record;
- a pre-run decision on whether internal SkillNudge maintenance is acceptable
  as the first external-validity slice.

## 4. Candidate Task 2: Host-Native Boundary Restoration

### Task

Reproduce the real host-native boundary repair recorded by commit `865bfdf`:
move the public Skill path to host-owned semantic reasoning and deterministic
retrieval, with installation and native-path regression coverage.

### Repository / initial state

```yaml
repository: SkillNudge
initial_commit: 1d979e4
target_change_commit: 865bfdf191ce5d6be1aa3451e7767f063705c0ef
reference_change_size:
  files: 9
  insertions: 862
```

The exact changed files are available in Git history, but the change is too
large for the first pair.

### Capability intervention

The same systematic-debugging source unit would be exposed to Treatment only.

### Why capability might help

The incident began with a real boundary failure and requires tracing the
execution path across Skill, CLI, deterministic core, and provider ownership.
That is plausibly sensitive to disciplined diagnosis.

### Control feasibility

Control can attempt the repair, but the surface spans installer, native Skill,
CLI, runtime modules, and tests. A failure in either arm would be difficult to
attribute to the intervention rather than task size.

### Treatment exposure

Fixed task-start host-native exposure, with identical tools and permissions.

### Task-specific Oracle

Possible checks include provider-free installation, no standalone delegation,
native retrieval, and the native regression suite. The exact hidden Oracle,
clean base snapshot, and bounded task decomposition are not frozen.

### Counterfactual cleanliness and confounds

The intended intervention difference is clear in principle, but the task also
changes the product boundary being used by the host. Large architectural
scope, installation state, and multiple failure boundaries make the first pair
hard to interpret.

### External nondeterminism and cost

No external service is required after setup, but the task is high-cost and
high-confound. It is not recommended for the first pair.

### Missing assets

- a smaller bounded task slice extracted from the incident;
- a frozen Oracle independent of the historical patch;
- an execution-isolated base snapshot.

## 5. Rejected Existing Fixture: Readiness Discount

### Task

Fix the whole-number percentage discount behavior in the generated local
repository `phase2b0-readiness-discount-001`.

### Repository / initial state

```yaml
repository: generated local fixture
task_id: phase2b0-readiness-discount-001
base_commit: 4661a80ac4b8c2ffeff8da6510911e286893737c
visible_test_command: python3 -m unittest discover -s tests -v
```

The fixture is generated by `create_readiness_task_bundle` in
`src/skillnudge/real_experiment.py` and has a hidden target and regression
check.

### Assessment

Its Oracle boundary is comparatively strong and the Control/Treatment
workspace split is already represented. However, the task repository, bug, and
tests were invented by the readiness implementation. It is not a real
repository task and therefore is not a serious candidate for the first real
causal evidence.

It remains valid as a protocol/integration fixture only. The existing
`pair_status: VALID` records do not establish utility evidence; earlier runs
also show model/provider failures with no observed Agent trajectory.

### Missing assets

None for fixture plumbing. It is nevertheless ineligible for the first real
causal task because its provenance is synthetic.

## 6. Comparison

| Candidate | Reality | Oracle strength | Repeatability | Counterfactual cleanliness | Control feasibility | Intervention plausibility | Nondeterminism | Complexity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Native contract discoverability repair | real historical repository work | potentially strong, not frozen | high from Git snapshot | conditional; internal contract boundary | high | medium | low | low-medium |
| Host-native boundary restoration | real historical repository work | possible but broad | high from Git snapshot | weak for first pair | medium-low | medium-high | low-medium | high |
| Synthetic readiness fixture (rejected) | synthetic | strong plumbing Oracle | high | good plumbing, invalid causal provenance | high | low/unknown | low | low |

The comparison is about measurement-path quality, not expected Skill win rate.

## 7. Recommended First Candidate

**Candidate 1: Native Planning Contract Discoverability Repair** is the one
candidate recommended for Principal review.

It is the smallest real historical maintenance task currently available, has a
reconstructable Git base, a plausible but non-guaranteed systematic-debugging
fit, and a deterministic Oracle shape. It is recommended because it can test
the measurement path with limited task and environment variance, not because
Treatment is expected to outperform Control.

This is a recommendation for review, not a frozen TaskArtifact. The task is
not ready for implementation until the missing Oracle and task artifact are
created and the internal-repository confound is explicitly accepted.

## 8. Missing Inputs

Only these concrete inputs are missing before implementation:

1. `task.json` for Candidate 1, including the immutable initial commit,
   agent-visible task text, repository identity, and environment identity.
2. A separate task-specific Oracle script/configuration for Candidate 1,
   including hidden checks and evaluator version.
3. A frozen Codex execution manifest covering model, tools, budget, and trace
   import boundary.
4. Principal decision on whether a SkillNudge-internal maintenance task is
   acceptable for the first causal slice, or whether an external repository
   snapshot must be supplied instead.

No dataset download, provider connection, benchmark run, or runtime change is
authorized by this review.

## 9. Next Step

```yaml
decision: BLOCKED_BY_MISSING_CONCRETE_ARTIFACT
reason: Candidate 1 is reviewable, but its task artifact and independent Oracle are not frozen.
implementation_started: false
real_pair_run: false
```
