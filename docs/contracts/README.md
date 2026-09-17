# SkillNudge V0 Contracts

## DESIGN FREEZE

Frozen V0 contracts may only be reopened by observed implementation or
golden-case failure, not by speculative architectural improvement.

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

本目录未列出的字段、规则或实现细节不因这些文件的存在而自动成立。

## Design Boundary

Runtime Map、CapabilityContract、InterventionPlan、QueryPlan 和 JudgeContract
已冻结，不应因为偏好或提前实现而重新设计。只有观察到 implementation failure
或 golden-case failure，才能重新打开对应合同，并记录失败证据和变更理由。

## Next Stage

```text
CODEX IMPLEMENT WEEK 1
```
