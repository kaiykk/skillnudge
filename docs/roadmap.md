# Roadmap

## Status

这是范围方向，不是完整的已实现功能清单。除当前 Product Outcome 外，运行时功能仍按 `[FUTURE]` 或
`[WORKING HYPOTHESIS]` 标记；当前研究轨迹状态见
[`docs/current-status.md`](current-status.md)，不能把研究完成误写成 runtime
完成。

## Current Product Outcome (2026-10-05)

`[IMPLEMENTED_BOUNDED_MVP]` Native Review accepts one real or sanitized,
observable Agent experience from an unrelated working directory through
`skillnudge review --stdin`. It returns exactly one bounded disposition:
`TEST`, `WATCH`, `NO_INTERVENTION`, or `INSUFFICIENT`, with same-experience
event references and explicit uncertainty. It is provider-free and does not
claim hidden skill consumption, utility, or effectiveness.

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

## Research track position (2026-10-05)

Phase 3 的当前有边界 evidence accumulation and diagnosis campaign 已完成，
结果为没有建立可复用 capability gap。Phase 4A 已进入 controlled
entry-hardening / contract-readiness 工作，但没有授权新的 Variant promotion、
Control/Treatment 执行或产品 evolution runtime。历史研究结论只约束产品边界，
不替代产品 runtime 的 Review MVP。

## Next — Validate

`[FUTURE]` Validate 将在 Review 输出基础上验证一个候选介入是否值得继续，
但需要独立的任务、Oracle 和 Principal 授权；Review 本身不会启动验证。

## Later — Grow / Watch

`[FUTURE]` Grow、Watch 属于长期能力地图：

- Grow：在证据和用户批准下改进、简化或扩展 local Variant；
- Watch：观察 model、version、source 和 compatibility drift。

这些都不属于 Week 1。

### Phase 3 Model Track Gate

Before implementing Validate/Grow behavior, Phase 3 must first establish a
scenario-aware Capability Gap Registry from real experience evidence. Its
output is an evidence-backed evolution hypothesis, not a modified Skill or
Variant. The minimum semantic contract, Discovery Oracle boundary, stop
conditions, and Phase 4/Darwin boundary are recorded in
[`docs/research/phase3-capability-gap-evidence-gate-v0.1.md`](research/phase3-capability-gap-evidence-gate-v0.1.md).

This gate intentionally does not freeze a minimum sample count, confidence
threshold, aggregation formula, automatic stop algorithm, Variant schema, or
lifecycle threshold.

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
