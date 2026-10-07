# Roadmap

## Status

这是产品交付方向，不是完整的已实现功能清单。当前 runtime truth 见
[`docs/current-status.md`](current-status.md) 和
[`docs/north-star.md`](north-star.md)。Home Project 的研究材料只提供历史
证据输入，不是 SkillNudge runtime 依赖或当前产品 GPS。

## Current Product Outcome (2026-10-05)

`[IMPLEMENTED_BOUNDED_MVP]` Native Review accepts one real or sanitized,
observable Agent experience from an unrelated working directory through
`skillnudge review --stdin`. It returns exactly one bounded disposition:
`TEST`, `WATCH`, `NO_INTERVENTION`, or `INSUFFICIENT`, with same-experience
event references and explicit uncertainty. It is provider-free and does not
claim hidden skill consumption, utility, or effectiveness.

`[IMPLEMENTED_BOUNDED_MVP]` Validate consumes one `TEST` candidate and one
frozen Validation Envelope. It compares parity-controlled Control/Treatment
records with an observable Oracle and returns a scoped `HELPS`, `NEUTRAL`,
`HURTS`, `INCONCLUSIVE`, or `NOT_EVALUATED` result. It does not promote or
rewrite a Skill.

## Current — Suspended uncertainty WATCH slice (2026-10-06)

`[IMPLEMENTED_BOUNDED_MVP]` One `OPEN` Evidence Need can be persisted with a
candidate identity, unresolved question, evidence role, scope, source
references and an `interesting_future_event`, then loaded by a later process.
The v1 `skillnudge watch --stdin` envelope exposes the exact persisted
`unresolved_question` and `interesting_future_event` to the Host and rejects a
changed condition context. The Host returns `IGNORE`, `WAKE` or `INSUFFICIENT`
with observable event references. A `WAKE` produces a v2 result plus a
persisted, minimal reactivation context that a later Host process can consume
for one bounded continuation step. The Need stays `OPEN`; no utility claim,
lifecycle transition, scheduler, or automatic follow-up is created. This is
one bounded persisted need plus later condition matching and handoff, not a
generic monitoring or aggregation system.

## Evolution Gradient (frozen concept, 2026-10-06)

[`docs/evolution-gradient.md`](evolution-gradient.md) freezes an
evidence-bounded directional signal around evaluation. It separates
`Evaluation Fact`, `Causal Hypothesis`, and future candidate updates without
adding a lifecycle stage, utility score, automatic learning loop, or lifecycle
authority. The current utility round remains
`NOT_EVALUATED_FOR_CANDIDATE_UTILITY`.

## Shipped baseline — ADVISE / REVIEW / VALIDATE

`[FROZEN]` 第一阶段只验证：

- 从模糊用户请求恢复缺失 capability；
- 判断是否值得介入；
- 在 Skill、Plugin、Tool、Companion Resource 和 No intervention 之间保持开放；
- 通过轻量检索构造候选池；
- 通过完整证据进行候选判断；
- 输出少量、可解释的建议；
- 保留可复查 Trace。

这部分是当前 bounded product slice；EVOLVE 已实现为 candidate-only MVP，
仍不会自动晋升。

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

## Historical research input (2026-10-05)

Phase 3 的当前有边界 evidence accumulation and diagnosis campaign 已完成，
结果为没有建立可复用 capability gap。Phase 4A 已进入 controlled
entry-hardening / contract-readiness 工作，但没有授权新的 Variant promotion、
Control/Treatment 执行或产品 evolution runtime。历史研究结论只约束产品边界，
不替代产品 runtime 的 Review / Validate MVP，也不构成 runtime prerequisite。

```yaml
home_project:
  role: HISTORICAL_INPUT_ONLY
  runtime_dependency: NONE
```

## Previous — Principal Review of Validate Receipt

`[SUPERSEDED_BY_EVOLVE_REVISION]` The existing bounded Review → Validate
receipt remains historical evidence. Its pair validity, Oracle, and scoped
outcome remain separate from the EVOLVE lifecycle revision and do not turn one
pair into universal utility.

## Current — EVOLVE / WATCH boundary

`[IMPLEMENTED_BOUNDED_MVP]` EVOLVE 在关联的 Review `TEST`、
`attribution.primary=capability_candidate`、可解析的 observable evidence
和 source CapabilityArtifact 存在时创建 versioned instruction candidate。
`INTERVENTION_ABLATION` 是可选的 pre-EVOLVE evidence-strengthening 路径，
不是普遍前置条件；随后必须用现有 Validate 的 `CAPABILITY_REVISION` 模式
再次比较。WATCH is now a bounded cross-cutting capability:

- EVOLVE：在 Review admission contract 通过后提出 candidate-only 版本；
- Watch：持久化一条 Evidence Need，并在后续 host experience 到来时返回
  `IGNORE`、`WAKE` 或 `INSUFFICIENT`；不做通用 drift aggregation。

Evidence level for the revised direct-admission path:
`HOST_ATTESTED_DIRECT_PATH_DOGFOOD`. The direct path has been exercised once
on a real Native Host task. That receipt proves lifecycle execution only; it
does not establish candidate utility or reusable generalization.

The first Native held-out follow-up evaluated the unchanged candidate v2 on
H1R and H3. Both pairs were `VALID / NEUTRAL`; no held-out improvement was
observed. The bounded round classification is
`NO_NATIVE_UTILITY_OBSERVED`; candidate utility remains
`NOT_ESTABLISHED`. The bounded direction is
`COLLECT_MORE_DISCRIMINATIVE_EVIDENCE`, not automatic evolution or promotion.
See [`docs/product-receipts/first-native-heldout-utility-20261006.md`](product-receipts/first-native-heldout-utility-20261006.md) for the product-owned summary.

The bounded Mechanism-Grounded Autonomous Search Episode 0 then reconstructed
the candidate mechanism and searched existing Native evidence for a natural
discriminative boundary. It stopped at `LOW_MARGINAL_INFORMATION` without a
new Native pair. Candidate utility remains `NOT_ESTABLISHED`; the next action
is `MORE_EVIDENCE` only for a naturally occurring ambiguous task, not a
post-hoc benchmark or automatic evolution. See
[`docs/product-receipts/mechanism-grounded-search-episode-0-20261006.md`](product-receipts/mechanism-grounded-search-episode-0-20261006.md).

Episode 1 ran one matched diagnostic P+/P- pair. Both were `VALID / NEUTRAL`;
the positive probe did not separate v1 and v2, so mechanism support is
`WEAKENED`, not established. Designed probes remain diagnostic evidence only;
natural utility is still `NOT_ESTABLISHED`. The next action is
`WAIT_FOR_NATURAL_EVIDENCE`, not more post-hoc probes or automatic evolution.
See [`docs/product-receipts/mechanism-grounded-search-episode-1-20261006.md`](product-receipts/mechanism-grounded-search-episode-1-20261006.md).

EVOLVE remains candidate-only and Principal-reviewed. WATCH is cross-cutting
and is not a sequential phase.

### Historical Phase 3 research boundary

The completed Phase 3 campaign established an evidence and attribution
boundary but did not establish a reusable capability gap. Its historical
contract is recorded in
[`docs/research/phase3-capability-gap-evidence-gate-v0.1.md`](research/phase3-capability-gap-evidence-gate-v0.1.md).

That historical research result is not a requirement for a product EVOLVE
runtime and does not authorize a Capability Gap Registry, aggregation, or
automatic evolution.

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
