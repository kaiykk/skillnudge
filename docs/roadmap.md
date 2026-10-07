# Roadmap

This roadmap follows the SkillNudge control-plane North Star. Historical
Advisor, evaluator, and Home Project research material is not a product
dependency or a current lifecycle stage.

## Complete — Phase 0: repository boundary

The repository inventory and KEEP/ADAPT/REMOVE_FROM_ACTIVE_TREE classification
are recorded in
[`product-reset-phase0-20261007.md`](product-reset-phase0-20261007.md).
No runtime migration or operator integration started in this phase.

## Next — Skill Conductor interop MVP

Given one registered Skill and an explicit evolution request, SkillNudge should
be able to:

1. preserve the source identity and version;
2. invoke or receive one Skill Conductor result;
3. import one non-active candidate;
4. preserve operator-native result references and provenance; and
5. leave activation to the Human Principal.

Success means the control plane can carry one candidate across the boundary. It
does not mean SkillNudge can author or judge Skills itself.

## Later — Darwin, then SkillOpt

Darwin is the second adapter for bounded interactive improvement. SkillOpt is
the later adapter for trajectory-driven/offline optimization. Neither should
be integrated before the first adapter establishes the shared artifact and
Human decision boundary.

## Explicitly out of scope

- automatic operator selection;
- automatic promotion, rollback, or retirement;
- global utility scores or fixed thresholds;
- a new retrieval or benchmark system;
- reimplementation of Skill Conductor, Darwin, or SkillOpt;
- reactivating WATCH/Evidence Need as V0 lifecycle stages without a concrete
  operator workflow that requires them.
