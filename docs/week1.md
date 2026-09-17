# Week 1

## Status

这是 Week 1 的实现边界建议，不代表当前已经开始实现。

## Goal

建立一个轻量的 **Intervention Advisor V0**，先验证产品边界和最小可用闭环。

## Definition of Done

### G1

未来实现后，能够运行：

```bash
skillnudge advise "<vague request>"
```

当前仓库不提供这个命令。

### G2

默认运行不依赖：

- GPU；
- embedding；
- vector database。

### G3

D001 可以从真实 corpus 找到合理的 Skill candidate。

### G4

D002 不会强制选择 Skill；Tool 或 Plugin 可以成为更合适的 intervention。

### G5

D003 允许 `no_intervention`。

### G6

每次运行都有完整 observable trace。

## Week 1 Non-Goals

Week 1 不做：

- frontend / GUI；
- mandatory embedding；
- vector DB；
- reranker training；
- Skill-specific fine tuning；
- Review；
- Grow；
- Watch；
- personalization；
- automatic installation；
- massive ToolHub；
- multi-agent；
- background scheduler；
- exhaustive benchmark；
- 完整 Skill lifecycle。

## Working Discipline

实现阶段应保持：

- 先验证 source coverage，再调 query；
- 先记录 evidence boundary，再写 recommendation；
- 先区分 intervention type，再决定候选；
- 先保证 no-intervention 合法，再追求推荐数量；
- 不把 README 或模型推断写成 confirmed capability。

