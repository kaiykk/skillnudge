# Decision

Skill utility 必须被视为 model-dependent、task-dependent 和 time-dependent
的长期问题；Utility Drift 不进入 V0 实现。

# Context

模型能力会变化。一个过去有帮助的 Skill 可能逐渐变成冗余 scaffolding，
trigger 过宽、增加 context pollution，甚至限制更强模型的正常行为。

# Options considered

- 只评估 Skill 的静态质量；
- 只依赖社区 star / activity；
- 在每次当前任务判断中保留 model、task、stage 和 time 维度；
- 立即实现 Review / Grow / Watch 和自动 retire。

# Decision

V0 只保留这个长期假设，不实现自动 drift detection。未来再研究：

- recommend；
- simplify；
- update；
- replace；
- retire。

# Why

先证明“当前介入是否改善下一段轨迹”，再决定是否值得维护完整 lifecycle。

# Consequences

- 不能把一次推荐结果解释为永久质量判断；
- 后续评测需要记录 model、task stage 和时间；
- Review、Grow、Watch 必须保持在 V0 之外。

# Revisit when

当拥有跨时间、跨模型且可验证的使用轨迹后，再决定是否建立 drift 机制。

