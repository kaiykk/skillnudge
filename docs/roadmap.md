# Roadmap

## Status

这是范围方向，不是已实现功能清单。

## V0 — Discovery / Intervention Advisor

第一阶段只验证：

- 从模糊用户请求恢复缺失 capability；
- 判断是否值得介入；
- 在 Skill、Plugin、Tool、Companion Resource 和 No intervention 之间保持开放；
- 通过轻量检索构造候选池；
- 通过完整证据进行候选判断；
- 输出少量、可解释的建议；
- 保留可复查 Trace。

V0 不包括完整 lifecycle。

## V0.5 — Retrieval Quality / Corpus Freshness

后续可以研究：

- corpus coverage；
- source freshness；
- license / provenance checks；
- candidate cache validation；
- retrieval failure decomposition。

## V1 — Optional Semantic / Hybrid Retrieval

如果 V0 的真实证据显示 lexical retrieval 不足，才考虑：

- optional embedding retrieval；
- hybrid retrieval；
- semantic reranking。

Embedding 仍应是可选能力，不应成为普通开发者的安装前提。

## Later — Review / Grow / Watch

### Review

实际用了以后，检查 intervention 是否真的帮助了任务。

### Grow

在证据支持的前提下，优化、简化或扩展 Variant，而不是只增加 instruction。

### Watch

观察 model、version、source 和 compatibility drift。

这些都不属于 Week 1。

## Future — Skill Utility Drift

随着 foundation model 能力增强：

```text
过去有帮助
→ 模型变强
→ instructions 变成 redundant scaffolding
→ trigger 过宽
→ context pollution / overconstraint
→ utility 下降甚至变成负收益
```

长期问题不应只是：

> 这个 Skill 好不好？

而应是：

> 这个 Skill 对当前 model + task + stage 还值得使用吗？

未来可能的决策包括：

- recommend；
- simplify；
- update；
- replace；
- retire。

当前没有自动化 Utility Drift detection。

## Model-Dependent Design Assumptions

随着模型能力增强，设计需要持续检查：

- 过长的 Skill 描述是否增加选择困难；
- trigger 是否足够明确、窄；
- progressive disclosure 是否优于一次加载全部 instruction；
- elaborate recipe 是否变成 overconstraint；
- AGENTS.md / Skill guidance 是否按需加载；
- 模型升级是否改变 Skill utility。

这些是长期产品假设，不是当前已实现检测能力。

