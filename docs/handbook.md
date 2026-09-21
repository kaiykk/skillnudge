# SkillNudge Project Handbook

**Status:** Canonical project operating guide
**Last updated:** 2026-09-21

## Active Current Outcome

**Status:** PROVEN / CLOSED

**Milestone:** Phase 1 Native MVP — CLOSED for the Codex reference host

**Outcome:**

From an unrelated repository, the Principal can explicitly invoke
`$skillnudge` in Codex and receive real Phase 1 advice using the host Agent's
existing model, through the installed SkillNudge deterministic core and
default corpus, without configuring a separate SkillNudge LLM provider.

**Acceptance evidence:**

- clean installation succeeds;
- Codex discovers and explicitly invokes `$skillnudge` from an unrelated
  repository;
- host Agent semantic reasoning executes;
- provider-free SkillNudge retrieval/evidence executes;
- 10 candidates are hydrated;
- one actual host-model advice is returned to the Principal.

**Observed reference-host evidence:**

```text
Codex host model
  -> installed $skillnudge
  -> native contract
  -> skillnudge retrieve --stdin
  -> default corpus/index
  -> BM25 + RRF
  -> Evidence Hydration
  -> 10 hydrated candidates
  -> host-model judgement
  -> real Final Advice
```

The returned advice recommended `regression-tester` as primary, with
`code-reviewer` as an optional companion and `playwright-testing` as
conditional. The observed provider was `null`; no separate SkillNudge model
credential was required.

**Resolved for the Codex reference host:**

- provider-free Native Mode completed a real Phase 1 call;
- installed Codex discovery and explicit invocation were demonstrated;
- the default corpus/index produced a real hydrated evidence set.

**No new Current Outcome has been started.** The project remains at the
completed Phase 1 Native MVP boundary while the following items stay in the
Parking Lot: Test 5 meta-workflow / underlying-task capability confusion;
candidate evidence-boundary leakage involving locally known skills; retrieval
top-k relevance drift; `complete_unverified` provenance; corpus coverage gaps;
cross-host validation; and Phase 2 evaluation work.

**Not required for this outcome:**

- Phase 2 paired experiments;
- SWE-bench;
- lifecycle evolution;
- a provider abstraction framework;
- implicit triggering;
- benchmark-level evaluation.

This outcome was the current project GPS coordinate and is now proven for the
Codex reference host. Do not infer a replacement outcome from internal
implementation progress, completed documentation, or passing tests. A new
Current Outcome requires an explicit project decision.

## Host-Native Product Invariant

Public SkillNudge integrations MUST use the host Agent for semantic reasoning.
Installing or invoking SkillNudge MUST NOT require, initialize, or fall back to
a separate SkillNudge LLM provider.

Provider-backed execution is allowed only for explicit standalone evaluation,
testing, CI, or research paths.

### Dependency Invariant

Native product paths may depend on the provider-free Capability Core.
Capability Core MUST NOT depend on provider, standalone-evaluation, or Phase 2
runtime modules.

## Current Outcome Gate

This is a mandatory process-control gate for every new task, proposal, review,
implementation request, and milestone decision in this repository.

### Current Outcome Contract

Every active milestone must have exactly **one** Current Outcome.

A Current Outcome must describe an externally observable result. It must state
what a Principal, user, or external environment can actually do or verify.

Good:

> From an unrelated repo, I can invoke `$skillnudge` and receive a real Phase 1
> advice.

Bad:

- Finish provider abstraction.
- Complete evaluation architecture.
- Improve causal runtime.
- Finish retrieval module.

Internal completeness can support a Current Outcome, but it is not the outcome
itself.

### Task Classification

Before implementation, classify the task as exactly one of:

**A - BLOCKER REMOVAL**

The task directly removes a concrete blocker preventing the Current Outcome.

**B - OUTCOME EVIDENCE**

The task directly produces evidence that the Current Outcome exists or works.

**C - NON-BLOCKING EXPANSION**

The task does neither A nor B. It belongs in the Parking Lot by default.

Default policy:

- A is allowed.
- B is allowed.
- C is parked unless the Principal explicitly overrides.

A C-task may enter the active sprint only with an explicit Principal override.
The override must be recorded in the task plan or review record.

### Mandatory Pre-Task Check

Before executing any new implementation request in this repository, include
the completed gate at the top of the task plan:

```text
Current Outcome:

Task:

Classification: A / B / C

Concrete blocker or evidence:

New externally observable fact after completion:

Could Current Outcome be reached without this task?: YES / NO

Decision: GO / DEFER / PRINCIPAL OVERRIDE
```

Question 5 is a hard prioritization check. If the answer is `YES` and the task
does not itself produce outcome evidence, the default decision is `DEFER`.

### Vertical Slice Rule

Before horizontal hardening:

1. build the thinnest end-to-end path;
2. run it in a realistic external environment;
3. observe an actual failure;
4. harden only the failure that blocks the Current Outcome.

Do not pre-harden hypothetical failure modes unless they are safety-critical.
The current outcome takes priority over subsystem completeness.

### Milestone Closure

A milestone may not be closed only because:

- architecture is complete;
- documentation is complete;
- tests pass;
- contracts are frozen;
- internal modules work;
- a review says `PASS`.

Closure requires the external evidence defined in that milestone's Current
Outcome Contract.

### Review Rule

Every review must check both layers:

**Local Correctness**

> Is this implementation or document correct within its stated scope?

**Global Progress**

> Does this move the Current Outcome forward?

Local correctness cannot compensate for a lack of global progress. A review
must state both judgments, even when the local work is correct.

### Parking Lot Rule

Valid and interesting work is not automatically current work.

The following belong in the Parking Lot when they do not remove a concrete
blocker or produce direct Current Outcome evidence:

- research questions;
- abstractions;
- scalability work;
- generalization;
- future evaluation;
- provider frameworks;
- architecture improvements.

Do not delete parked work. Do not execute it in the active sprint without a
new A/B classification or an explicit Principal override.

### Stop Rule

If two consecutive tasks produce no new external evidence, stop
implementation and re-evaluate:

- the Current Outcome;
- the task classification;
- the active blocker;
- whether the project is accumulating internal completeness instead of
  externally verifiable capability.

## Vertical Slice Development Rhythm

For every active milestone:

1. Define one Current Outcome.
2. Build one minimum vertical slice toward that outcome.
3. Run the slice in the real target environment.
4. Observe the actual failure.
5. Fix only the failure that blocks the Current Outcome.

Internal completeness is not progress unless it produces new externally
observable evidence.

## Phase 2 First-Pair Guardrail

Before the first real valid Control/Treatment pair exists, Phase 2 must not
expand into:

- multi-host support;
- generic experiment runner frameworks;
- provider abstractions;
- provider readiness systems or capability probes;
- benchmark platforms or dataset expansion;
- generalized evaluator frameworks;
- distributed experiment infrastructure;
- lifecycle or Skill evolution;
- SkillNudge Decision Utility;
- automatic capability-selection optimization.

The only objective before the first pair is:

```text
one task
one intervention
one host
one pair
one oracle
one conclusion
```

### First-Pair Necessity Test

Before adding any Phase 2 code, ask:

> If this code did not exist, could the first real Control/Treatment pair
> still be executed and evaluated?

If the answer is yes, the code is presumed out of scope for the current
milestone. An exception requires an explicit Principal decision.

### Measurement Architecture Review Trigger

If Phase 2 adds responsibility for any of the following inside Measurement
Core, stop implementation and trigger an architecture review:

- model or provider client;
- API-key management for Agent execution;
- provider fallback or probing;
- Agent loop, planner, orchestrator, or tool routing;
- Agent retry/recovery lifecycle;
- context or memory management;
- Skill discovery or recommendation;
- duplicate SkillNudge product reasoning;
- custom Agent runtime;
- generic host framework before demonstrated need;
- generic readiness infrastructure.

Measurement observes and compares host executions. Measurement must not become
the host.

## Phase 2 Reference Host

The frozen reference host for the first Phase 2 causal slice is **Codex**.
This is based on the completed Phase 1 Native MVP evidence: Codex already
discovers and invokes the installed SkillNudge Skill, and the provider-free
native path has returned real advice from an unrelated repository.

This is a first-slice freeze, not a claim that Codex is the only or permanent
supported host. Multi-host support remains out of scope until the first valid
pair exists.

The first real task-selection analysis is recorded in
[`docs/research/phase2-first-causal-task-selection-v0.1.md`](research/phase2-first-causal-task-selection-v0.1.md).

## Historical Anti-Patterns

These are explicit lessons from this project:

```text
Phase 1 algorithm complete != SkillNudge installable.
Experiment runtime complete != real paired evidence exists.
SKILL.md installed != Codex actually discovered and invoked $skillnudge.
```

Never infer:

```text
Subsystem complete -> Product milestone complete
```

## Current Scope Boundary

After the Active Current Outcome is reached, work that does not belong to an
explicitly approved new outcome remains parked rather than becoming active by
inference.

The following remain explicitly out of scope until a new Current Outcome is
started by project decision:

- Phase 2 paired experiments;
- SWE-bench;
- lifecycle evolution;
- new provider or harness frameworks;
- implicit SkillNudge triggering;
- large evaluation infrastructure.

This boundary does not delete those ideas. It keeps them in the Parking Lot
until the Current Outcome changes through an explicit project decision.
