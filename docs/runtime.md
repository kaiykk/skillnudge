# Runtime Map

## Status

- `[FROZEN]` The eight-layer V0 Runtime Map below.
- `[FROZEN]` Trace crosses every layer.
- `[WORKING HYPOTHESIS]` Explicit intermediate artifacts will provide enough
  diagnostic value to justify their recording cost.
- `[FUTURE]` Review, Grow, Watch, personalization, and lifecycle automation.

This is a design baseline, not an implemented Runtime.

## Frozen Flow

```text
Raw User Request
        │
        ▼
1. Intake / Context
        │
        ▼
2. Capability Framing
        │
        ▼
3. Intervention Planning
        │
        ▼
4. Query Planning
        │
        ▼
5. Candidate Acquisition
        ├── Local Retrieval
        └── Conditional Live Discovery
        │
        ▼
6. Evidence Hydration
        │
        ▼
7. Candidate Judgement
        │
        ▼
8. Final Advice

Trace crosses the entire runtime.
```

除非发现明显的内部矛盾，否则后续实现不应重新设计这张图。

## Layer Responsibilities

### 1. Intake / Context

#### Goal

保留原始事实，避免在入口处过早解释。

#### Input

- 用户原始输入；
- 可选 project context；
- 可选 current stage。

#### Output

`InputEnvelope`（概念对象）。

#### Does NOT do

- 解释用户真正需要什么；
- 搜索 candidate；
- 提前指定 Skill。

### 2. Capability Framing

#### Goal

理解用户为什么在当前任务阶段推进不下去，以及真正缺失的 capability。

#### Input

- `InputEnvelope`；
- 用户原始表达。

#### Output

`CapabilityContract`（概念对象），并保留不确定性和原始措辞。

#### Does NOT do

- 寻找具体 Skill；
- 使用候选结果倒推答案；
- 做最终推荐。

Capability Framing 必须在搜索前完成，避免把候选名称误写进 capability。

### 3. Intervention Planning

#### Goal

决定搜索预算应该分给哪些 intervention surface，例如 Skill primary、
Tool secondary，或 Plugin primary、Skill secondary。

#### Input

- `CapabilityContract`；
- task stage；
- host 和 project constraints。

#### Output

`InterventionPlan`（概念对象）。

#### Does NOT do

- 把软路由变成 hard route；
- 直接宣布最终答案；
- 因为产品名是 SkillNudge 就强制选择 Skill。

### 4. Query Planning

#### Goal

把 `CapabilityContract` 转成 3-5 个互补 query。

#### Input

- `CapabilityContract`；
- `InterventionPlan`。

#### Output

`QueryPlan`（概念对象）。

Query angle 可以包括 capability、problem、desired outcome、operation、
professional vocabulary、artifact、workflow 和 scenario/stage。

#### Does NOT do

- 生成 8 个近义词 query；
- 通过 `if ui`、`if debug` 等领域 hardcode 直接写答案；
- 把 query 结果当成已验证 capability。

### 5. Candidate Acquisition

#### Goal

形成可进一步检查的 `CandidatePool`。

#### Input

- `QueryPlan`；
- local corpus / catalog；
- live-discovery policy。

#### Output

带有 intervention type、身份、来源和 cache level 的候选池。

#### Does NOT do

- 直接给出 Final Advice；
- 把 local corpus 当作整个世界；
- 无限进行 live search；
- 自动把 live result 写入 trusted corpus。

默认顺序是 LOCAL FIRST，然后才是 CONDITIONAL LIVE DISCOVERY。

### 6. Evidence Hydration

#### Goal

把候选从“搜索结果”变成 Judge 能判断的 evidence package。

#### Input

- `CandidatePool`；
- source adapters；
- version / commit / retrieval metadata。

#### Output

概念上的 evidence package，例如：

- Skill：name、description、完整 body、repo、source、license、
  compatibility、updated_at；
- Tool：README evidence、installation、supported host、maintenance、repo、
  trust signals。

#### Does NOT do

- 以 snippet 代替完整证据；
- 把 README claim 自动升级为 observed capability；
- 直接生成最终建议。

### 7. Candidate Judgement

#### Goal

判断 intervention 是否值得在当前 stage 介入。

#### Input

- evidence packages；
- `CapabilityContract`；
- task stage、model 和 project context。

#### Output

候选 judgement、fit/trust/friction 说明、拒绝理由或证据不足状态。

#### Does NOT do

- 只做 semantic similarity；
- 只看 star 数；
- 在 V0 预设复杂 numeric score；
- 把 retrieval relevance 当作 utility。

### 8. Final Advice

#### Goal

把判断压缩成用户现在可执行、可理解的下一步建议。

#### Input

- candidate judgements；
- evidence；
- explicit uncertainty；
- original request。

#### Output

0-2 个主要 recommendation，必要时附 companion resource、rejected
alternatives 和 status。

#### Does NOT do

- 输出 Top-10 recommendation spam；
- 隐藏不确定性；
- 把没有证据统一写成 `no-match`；
- 为了体现检索能力而强行介入。

概念上的 final status 至少区分：

- `recommendation`
- `no_intervention`
- `insufficient_evidence`
- `needs_clarification`
- `source_error`

## Cross-Cutting Rules

### Trace

Trace 记录显式输入、输出、候选、证据和决策对象，但不记录模型 private
chain-of-thought。

### Evidence Boundary

设计文档、模型推断、README 声明和候选名称不能自动升级为已确认能力。
需要把 claimed、observed、validated 和 unknown 分开。

### Intervention Boundary

Skill 是主要入口，但不能因为产品以 Skill 为名，就强制把所有问题都归为
Skill 问题。

### Scope Boundary

Watch、Review、Grow、personalization、自动安装和完整 lifecycle 不属于
V0 Runtime。
