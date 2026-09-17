# Runtime V0

## Status

**FROZEN FOR V0**

这是 V0 的 Runtime 结构合同。除非真实 implementation failure 证明该结构
不成立，否则 V0 不再 speculative redesign Runtime。

## Frozen Runtime

```text
Input
→ Intake / Context
→ Capability Framing
→ Intervention Planning
→ Query Planning
→ Candidate Acquisition
→ Evidence Hydration
→ Candidate Judgement
→ Final Advice
```

Trace 横切全部 Runtime，记录各层之间可复查的显式输入、输出、候选、证据和
决策对象；Trace 不记录模型 private chain-of-thought。

## Layer Contracts

### 1. Intake / Context

#### Goal

接收请求并保留原始事实、任务阶段和可用上下文，避免入口处过早解释。

#### Input

- `Input`：用户的原始请求；
- 可用的项目上下文；
- 可用的任务阶段信息。

#### Output

供后续层使用的输入与上下文记录，同时保留原始表达。

#### Does NOT do

- 不诊断真正缺失的 capability；
- 不搜索 candidate；
- 不提前指定 Skill 或其他 intervention。

### 2. Capability Framing

#### Goal

识别用户在当前任务阶段真正卡住的地方，以及可能缺失的 capability。

#### Input

- Intake / Context 的输入与上下文记录；
- 用户原始表达。

#### Output

`CapabilityFramingResult`，其中包含 `CapabilityContract`、置信度和是否需要
澄清。

#### Does NOT do

- 不指定具体 intervention；
- 不寻找具体 Skill 或 candidate；
- 不使用候选名称倒推 capability；
- 不把主题本身自动当作 capability gap。

### 3. Intervention Planning

#### Goal

决定当前需求应把有限注意力分配到哪些 intervention family，或者明确不需要
额外 intervention。

#### Input

- `CapabilityFramingResult`；
- 任务阶段；
- host 与项目约束。

#### Output

`InterventionPlan`。

#### Does NOT do

- 不决定具体 candidate；
- 不把 soft plan 变成不可调整的 hard route；
- 不因为产品以 Skill 为名就强制选择 Skill；
- 不为提高 recall 而机械搜索所有 family。

### 4. Query Planning

#### Goal

将已确定的 capability 和 intervention 边界转成后续 acquisition 可以执行的
查询计划。

#### Input

- `CapabilityContract`；
- `InterventionPlan`；
- 可用的查询和来源约束。

#### Output

`QueryPlan`。其具体合同仍在设计中，见
[`query-plan-v0.1.md`](query-plan-v0.1.md)。

#### Does NOT do

- 不直接选择具体 candidate；
- 不把查询命中结果当成已验证 capability；
- 不用领域硬编码绕过 Capability Framing 和 Intervention Planning。

### 5. Candidate Acquisition

#### Goal

根据 QueryPlan 在允许的来源中构造有限、可追溯、可进一步检查的候选池。

#### Input

- `QueryPlan`；
- 本地 corpus / catalog；
- 允许的 live-discovery policy。

#### Output

带有 intervention family、身份、来源和可追溯信息的 candidate pool。

#### Does NOT do

- 不直接生成 Final Advice；
- 不无限扩大 live search；
- 不把 live result 自动写入 trusted corpus；
- 不用搜索结果取代完整 evidence 检查。

### 6. Evidence Hydration

#### Goal

把候选从浅层搜索结果补充为 Candidate Judgement 可以检查的证据包。

#### Input

- candidate pool；
- 候选来源适配器；
- 版本、commit 和获取元数据。

#### Output

候选 evidence package，包括能支持判断的完整正文、来源、版本、许可证、兼容
性和新鲜度信息；具体字段以未来实现和相应合同为准。

#### Does NOT do

- 不以 snippet 代替完整证据；
- 不把 README claim 自动升级为 observed capability；
- 不直接生成最终建议。

### 7. Candidate Judgement

#### Goal

判断候选 intervention 是否适合当前需求、阶段和约束，并识别证据不足或不匹配。

#### Input

- evidence package；
- `CapabilityFramingResult`；
- 任务阶段、模型和项目上下文。

#### Output

候选 judgement、适配性与信任说明、摩擦说明，以及拒绝理由或证据不足状态。

#### Does NOT do

- 不只做主题或语义相似度判断；
- 不只看 star 数或其他流行度代理；
- 不把 retrieval relevance 自动当作 utility；
- 不在本合同中预设未冻结的复杂 numeric score。

### 8. Final Advice

#### Goal

把候选判断和不确定性压缩成用户当前可理解、可执行的下一步建议。

#### Input

- candidate judgements；
- evidence；
- 明确的不确定性；
- 原始请求。

#### Output

有边界的 recommendation，必要时附带 rejected alternatives、理由和状态；
也可以输出 `no_intervention`、`insufficient_evidence`、
`needs_clarification` 或 `source_error`。

#### Does NOT do

- 不输出 Top-10 recommendation spam；
- 不隐藏不确定性；
- 不把没有证据统一写成 `no-match`；
- 不为了证明检索能力而强行介入。
