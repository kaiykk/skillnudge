# SkillNudge V0 Contracts

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
| QueryPlan v0.1 | DESIGNING |
| JudgeContract v0.1 | NOT STARTED |

`query-plan-v0.1.md` 目前只保留占位状态，等待 QueryPlan 内容明确后再填入。
本目录未列出的字段、规则或实现细节不因这些文件的存在而自动成立。

## Design Boundary

Runtime Map、CapabilityContract 和 InterventionPlan 已冻结，不应因为偏好或
提前实现而重新设计。只有真实 implementation failure 证明冻结结构无法工作
时，才重新打开对应合同，并记录失败证据和变更理由。

完成 JudgeContract 后：

```text
STOP DESIGNING
→ CODEX IMPLEMENT WEEK 1
```
