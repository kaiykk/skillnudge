# Roadmap

## Status

这是范围方向，不是已实现功能清单。所有未来阶段都是 `[FUTURE]` 或
`[WORKING HYPOTHESIS]`，不应写成当前能力。

## V0 — Lightweight Intervention Advisor

`[FROZEN]` 第一阶段只验证：

- 从模糊用户请求恢复缺失 capability；
- 判断是否值得介入；
- 在 Skill、Plugin、Tool、Companion Resource 和 No intervention 之间保持开放；
- 通过轻量检索构造候选池；
- 通过完整证据进行候选判断；
- 输出少量、可解释的建议；
- 保留可复查 Trace。

V0 不包括完整 lifecycle。

## V0.5 — Retrieval Quality / Corpus Freshness

`[WORKING HYPOTHESIS]` 后续可以研究：

- corpus coverage；
- source freshness；
- license / provenance checks；
- candidate cache validation；
- retrieval failure decomposition；
- query and rank-fusion improvements。

## V1 — Optional Semantic / Hybrid Retrieval

`[FUTURE]` 只有当 V0 的真实证据显示 lexical retrieval 不足，且失败不是
source coverage 或 query planning 问题时，才考虑：

- optional embedding retrieval；
- hybrid retrieval；
- semantic reranking。

Embedding 仍应是可选能力，不应成为普通开发者的安装前提。

## Later — Review / Grow / Watch

`[FUTURE]` Review、Grow、Watch 属于长期能力地图：

- Review：判断一次 intervention 是否真的帮助了任务；
- Grow：在证据和用户批准下改进、简化或扩展 local Variant；
- Watch：观察 model、version、source 和 compatibility drift。

这些都不属于 Week 1。

## Long-Term — Skill Utility Drift

`[FUTURE]` 随着 foundation model 能力增强：

```text
过去有帮助
→ 模型变强
→ instructions 变成 redundant scaffolding
→ trigger 过宽
→ context pollution / overconstraint
→ utility 下降甚至变成负收益
```

未来可能的决策包括 recommend、simplify、update、replace 和 retire。当前
没有自动化 Utility Drift detection。

## Model-Dependent Design Assumptions

`[WORKING HYPOTHESIS]` 后续需要持续检查：

- 过长的 Skill 描述是否增加选择困难；
- trigger 是否足够明确、窄；
- progressive disclosure 是否优于一次加载全部 instruction；
- elaborate recipe 是否变成 overconstraint；
- AGENTS.md / Skill guidance 是否按需加载；
- 模型升级是否改变 Skill utility。
