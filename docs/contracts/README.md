# SkillNudge V0 Contracts

## DESIGN FREEZE

Frozen V0 contracts may only be reopened by:

1. observed implementation failure;
2. golden-case failure; or
3. a clear contradiction discovered during coding.

They must not be reopened because of speculative architectural improvement.
The default sequence is:

```text
STOP DESIGNING
-> IMPLEMENT
-> OBSERVE FAILURE
-> ONLY THEN REOPEN CONTRACT
```

这些文件是 SkillNudge Week 1 / V0 的 implementation source of truth。
它们只记录已经接受的行为合同和项目边界；待验证假设仍应保存在
`docs/hypotheses.md` 或当前研究 Change 中，不应因为出现在研究材料里就被
写成合同。

## Contract Status

| Contract | Status |
| --- | --- |
| Runtime Map | FROZEN |
| CapabilityContract v0.1 | FROZEN |
| InterventionPlan v0.1 | FROZEN |
| QueryPlan v0.1 | FROZEN |
| JudgeContract v0.1 | FROZEN |
| Candidate Acquisition | IMPLEMENTATION BASELINE |
| Final Advice | MINIMAL BEHAVIOR DEFINED |

本目录未列出的字段、规则或实现细节不因这些文件的存在而自动成立。

## Design Boundary

Runtime Map、CapabilityContract、InterventionPlan、QueryPlan 和 JudgeContract
已冻结，不应因为偏好或提前实现而重新设计。只有观察到 implementation failure
或 golden-case failure，才能重新打开对应合同，并记录失败证据和变更理由。

## Next Stage

```text
WEEK 1 IMPLEMENTATION
```

Checkpoint order is defined in [`../week1-implementation-spec.md`](../week1-implementation-spec.md).
