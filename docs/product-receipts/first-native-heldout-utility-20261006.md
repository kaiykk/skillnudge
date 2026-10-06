# First Native Held-Out Utility Evidence

**Date:** 2026-10-06  
**Scope:** frozen `structured-record-transformation` candidate v2 versus v1

## Result

Two new sibling tasks were evaluated through real Codex Reference Host/model
arms. Both pairs were valid and neutral:

```yaml
H1R:
  pair_status: VALID
  validation_result: NEUTRAL
H3:
  pair_status: VALID
  validation_result: NEUTRAL
```

The source task S previously returned `VALID / HELPS`, but neither held-out
task improved over a successful v1 baseline. The bounded reusable utility
classification therefore remains:

```yaml
candidate_utility: NOT_ESTABLISHED
round_classification: NOT_EVALUATED
evolution_gradient: COLLECT_MORE_DISCRIMINATIVE_EVIDENCE
```

## Evidence boundary

The exact v1 and v2 capability hashes were frozen before execution. All four
final arms retained observable Host trajectories and ran the independent task
Oracle. The old H1 remains permanently invalid and was not rewritten; H1R is a
new task identity, and H3 is a pristine sibling.

This receipt does not establish universal utility, a reusable capability gap,
a Skill gap, promotion, or Darwin/SkillOpt readiness. No v3, candidate update,
automatic lifecycle transition, or product runtime change occurred.

The complete freeze manifest, trajectories, validation outputs, shadow
hypotheses, and gradient synthesis remain in the separate Home Project packet:
`gpt-review/skillnudge-first-native-heldout-utility-20261006/`.

## Operational note

The arm launch wrapper attempted to assign a zsh read-only variable named
`status` after each Codex process completed. The wrapper consequently returned
code 1, but each persisted trajectory ended with `turn.completed`, each output
artifact existed, and each Oracle check passed. The wrapper defect is retained
in the Home Project receipt and must be fixed before any future run.
