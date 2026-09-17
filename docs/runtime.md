# Runtime Map

## Status

这是 SkillNudge 的 V0 design baseline，不是已实现的 Runtime。

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
        │
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

Trace 横切整个 Runtime。
```

除非发现明显的内部矛盾，否则后续实现不应重新设计这张图。

## Layer Responsibilities

### 1. Intake / Context

保存：

- 用户原始输入；
- 可选 project context；
- 可选 current stage。

这一层不负责解释用户真正需要什么。

### 2. Capability Framing

判断用户当前可能缺少的 capability，并形成
`CapabilityContract`。

这一层：

- 可以使用模型进行抽象；
- 必须保留不确定性；
- SHALL 在搜索候选前完成；
- 不得读取候选结果来反向写答案。

### 3. Intervention Planning

判断搜索预算应该分配给哪些 intervention surface，例如：

- Skill primary；
- Plugin secondary；
- Tool candidate；
- Companion Resource；
- No intervention。

这不是 hard route，也不直接决定最终答案。

### 4. Query Planning

从 `CapabilityContract` 生成 3–5 个互补 query。

Query angles 可以包括：

- capability；
- outcome；
- operation；
- professional vocabulary；
- artifact；
- workflow。

Query Planning 不应通过领域 `if/else` 直接写出某个行业的答案。

### 5. Candidate Acquisition

构造 `CandidatePool`，而不是直接做最终推荐。

Candidate Acquisition 包含：

- Local Acquisition；
- Conditional Live Discovery。

默认顺序是先检查本地 evidence / coverage，再按需访问 live source。

### 6. Evidence Hydration

获取候选的完整证据包，例如：

- 完整 Skill body；
- README；
- metadata；
- provenance；
- compatibility；
- maintenance；
- license。

检索相关性不等于可用性。

### 7. Candidate Judgement

回答：

> 这个 intervention 是否值得在用户当前状态介入？

长期需要关注：

- capability fit；
- stage fit；
- intervention-type fit；
- compatibility；
- trust；
- friction。

V0 暂不设计复杂数学 score。

### 8. Final Advice

压缩成：

- 0–2 个主要 recommendation；
- why now；
- why this；
- relevant uncertainty；
- 必要时列出 rejected alternatives。

Final status 至少概念上区分：

- `recommendation`
- `no_intervention`
- `insufficient_evidence`
- `needs_clarification`
- `source_error`

不要把所有没有推荐的情况统一称为 `no-match`。

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

