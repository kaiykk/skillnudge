# SkillNudge

SkillNudge 打通从真实 Agent Session 到可追踪 Skill 版本演化的闭环。

## Why

重要的 Skill 改进通常来自一次真实 Session、明确的用户纠正或可观察反馈。
如果没有持久化的 Session 依据，后续 Skill 变化就会失去原因，也无法复核
或回滚。

## What

SkillNudge 只保留连接以下对象所需的最小控制平面记录：

- Skill identity 与不可变版本；
- 可观察的 Session evidence 与 trace reference；
- 一次外部 evolution operation；
- 带有 Human 决策边界的非活动 candidate version。

## Core Flow

```text
Agent Session
  -> Feedback / Evidence
  -> Evolution Request
  -> External Evolution Operation
  -> Candidate Version
  -> Human Accept / Reject
```

SkillNudge 记录 identity、lineage、provenance 和 decision；它不自己编写或
优化 Skill。

## Principles

- Evolution 从真实使用开始。
- 每个 candidate 都有 provenance。
- Skill version 不可变。
- Candidate 不会自动覆盖 active version。

最小记录边界见 [`docs/core-contract.md`](docs/core-contract.md)。
