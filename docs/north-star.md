# SkillNudge North Star

**Status:** canonical product direction
**Updated:** 2026-10-05

The user-facing experience reference is [`north-star-experience.md`](north-star-experience.md).

## 1. Core Problem / Thesis

External capability utility is contextual and non-stationary.

SkillNudge exists to build an evidence-driven capability lifecycle for AI
Agents. A Skill, prompt, workflow, integration, memory strategy, or other
external capability is useful only relative to the conditions in which it is
used:

```text
Capability Utility =
f(capability, model, harness, task, task_stage, environment, time)
```

This is a product model, not a universal score or a mathematically validated
equation. A capability that helps one task or model may be redundant,
over-constraining, stale, or harmful under different conditions.

SkillNudge is therefore not primarily a Skill marketplace, generic
observability platform, generic experiment framework, prompt rewriting tool,
or autonomous self-improving agent. Its product question is:

> When an Agent experience suggests an external capability may help, what
> evidence is sufficient to test, change, and govern that capability?

No intervention is a valid outcome. Relevance is not utility, and a bad case
is not by itself proof of a capability gap.

## 2. Product Lifecycle

The canonical lifecycle is:

```text
ADVISE
  -> REVIEW
  -> EVOLVE
  -> VALIDATE (candidate v2 vs current capability v1)
  -> DECIDE (Human-owned lifecycle action)
```

`INTERVENTION_ABLATION` may be used between REVIEW and EVOLVE when additional
mechanism or attribution evidence is useful, but it is optional and is not a
universal `VALIDATE HELPS` prerequisite. The post-EVOLVE comparison is the
bounded `VALIDATE` evidence step.

`WATCH` is a cross-cutting capability. It detects new evidence or possible
utility drift and may trigger Review or Validate; it is not a sequential phase
between the lifecycle stages.

### ADVISE

Ask whether introducing an external capability is worthwhile for the current
task. Advise may recommend a bounded capability, ask for clarification, or
recommend no intervention.

### REVIEW

Inspect one real or sanitized observable Agent trajectory and identify what, if
anything, is worth testing as an intervention. Review preserves evidence
references and uncertainty. It does not prove a capability gap, Skill defect,
or intervention effectiveness.

### INTERVENTION_ABLATION (optional pre-EVOLVE evidence)

Compare the exact bounded intervention against its Control condition on the
same tested scope. Keep task, host, model, harness, tools, budget, environment,
and observable Oracle explicit. A valid pair may return `HELPS`, `NEUTRAL`,
`HURTS`, or `INCONCLUSIVE`; an invalid pair is `NOT_EVALUATED`.

### EVOLVE

Review evidence may justify proposing a versioned capability candidate when it
passes the EVOLVE Admission Contract: `TEST`, primary
`capability_candidate` attribution, observable evidence references, source
artifact identity, and a host-proposed candidate. The Host may supply semantic
proposal content; SkillNudge must preserve source identity, parent lineage,
exact content, and evidence linkage. Optional `INTERVENTION_ABLATION` can
strengthen admission but is not universally required. EVOLVE creates a
candidate, not a promoted capability.

### VALIDATE

Compare candidate v2 with the current capability under the same bounded
validation discipline. A candidate must be revalidated before any lifecycle
decision.

### HUMAN LIFECYCLE AUTHORITY

The Human Principal owns the final decision to promote, keep, reject, roll back,
retire, or watch a capability. `PROMOTION_CANDIDATE` is not a lifecycle
endpoint and is never equivalent to `PROMOTED`, `CURRENT`, `ACTIVE`, or
`DEFAULT`.

## 3. Current Implementation Truth and Scope

```yaml
ADVISE:
  status: IMPLEMENTED_AND_PROVEN

REVIEW:
  status: IMPLEMENTED_BOUNDED_MVP
  native_e2e_dogfood: PASS

VALIDATE:
  status: IMPLEMENTED_BOUNDED_MVP
  evidence_level: HOST_ATTESTED_BOUNDED_COMPARISON

EVOLVE:
  status: IMPLEMENTED_BOUNDED_MVP
  scope: CANDIDATE_ONLY_INSTRUCTION_ARTIFACT
  evidence_level: HOST_ATTESTED_DIRECT_PATH_DOGFOOD
  optional_pre_evolve_validation: INTERVENTION_ABLATION
AUTO_PROMOTION:
  status: NOT_IMPLEMENTED

WATCH:
  status: FUTURE_CROSS_CUTTING
```

The shipped Native product is provider-free: the Host Agent owns semantic
reasoning and SkillNudge owns deterministic contract validation, evidence
linkage, parity checks, Oracle execution, persistence, and bounded results.

Current Review and Validate results are scoped to their observed experience or
tested pair. They do not establish universal utility, a reusable capability
gap, production promotion, or automatic Skill mutation.

The bounded EVOLVE MVP accepts a linked Review `TEST` with primary
`capability_candidate` attribution, observable evidence, source artifact
identity, and host-proposed instruction content. A linked
`INTERVENTION_ABLATION` result may strengthen admission but is not universally
required and need not be `HELPS` merely to create a candidate. It creates a
versioned, non-active candidate and requires `CAPABILITY_REVISION` before any
Human lifecycle decision. No candidate is installed, activated, overwritten,
promoted, rolled back, or retired automatically.

The following remain outside the current product runtime boundary:

- automatic promotion, rollback, retirement, or Skill directory mutation;
- multi-session aggregation, Candidate Portfolio, or Capability Gap Registry;
- Plugin, Tool, Memory, multi-file package, or cross-model evolution;
- Darwin, SkillOpt, a new provider, DSH, or Home Project runtime;
- a global utility score, Watch daemon, or generic marketplace.

The product direction is intentionally smaller than a complete autonomous
evolution system. Each lifecycle step must first produce an externally
observable, evidence-bounded result before the next step is authorized.
