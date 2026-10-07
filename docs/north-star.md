# North Star

SkillNudge is an **evidence-aware control plane for Agent Skill evolution**.

## Core problem

External Skill utility is contextual and non-stationary. Different operators
and models may create or improve a Skill, but a product still needs a stable
identity, version lineage, provenance trail, and Human-owned lifecycle around
those changes.

## Product lifecycle

```text
REGISTER
  -> ACTIVE SKILL
  -> REQUEST EVOLUTION
  -> SELECT OPERATOR
  -> EXTERNAL OPERATOR RUN
  -> CANDIDATE
  -> REVIEW RESULT / PROVENANCE
  -> HUMAN DECISION
  -> ACTIVATE | REJECT | ROLLBACK | RETIRE
```

Validation is an evidence primitive supplied by an operator or Host. It is not
a mandatory universal stage and it never silently activates a candidate.

## Current implementation truth

- Phase 0 repository classification is complete.
- `CapabilityArtifact` identity/version/hash validation is the retained core
  primitive.
- The first operator target is Skill Conductor; integration has not started.
- Earlier Advisor, retrieval, evaluator, and WATCH code is retained as legacy
  material while migration is reviewed.
- Human Principal authority is required for every active Skill mutation.

SkillNudge does not reimplement Skill Conductor, Darwin, or SkillOpt and does
not own a global utility score, benchmark framework, or autonomous evolution
loop.

For the detailed Phase 0 boundary and file classification, see
[`product-reset-phase0-20261007.md`](product-reset-phase0-20261007.md).
