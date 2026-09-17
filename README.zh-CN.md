# SkillNudge

**The right capability, only when it helps.**

SkillNudge 是一个面向 AI coding agent 的开源、本地优先的能力介入建议工具。

它关注的问题不只是：

> “我应该安装哪些 Skill？”

而是：

> 在当前任务的这个阶段，真正缺少什么能力？现在增加任何介入是否值得？

未来 SkillNudge 可能会考虑：

- Agent Skill
- Plugin
- 外部 Tool
- Companion Resource
- 或者不介入

当前仓库仍处于 **Design / V0 baseline** 阶段，产品尚未实现。

## 为什么需要 SkillNudge

Agent Skill 生态正在快速增长，但问题已经不只是“如何找到更多 Skill”：

- 用户经常说不清自己缺少的能力，也不知道应该搜索什么；
- 同一个介入在不同任务阶段的价值可能不同；
- 语义相关不代表现在值得介入；
- 过多 instruction 会增加上下文负担、触发错误，或过度约束已经很强的模型；
- 随着模型变强，旧 Skill 提供的能力可能已经被模型原生覆盖；
- 用户真正需要的可能是 Plugin 或 Tool，而不是 Skill；
- 不做任何介入也应该是合法答案。

核心产品命题是：

> **Skill utility is contextual, not static.**
>
> Skill 的效用取决于上下文，而不是静态属性。

概念上可以写成：

```text
Utility = f(
  intervention,
  task,
  task_stage,
  model,
  project_context,
  time
)
```

这只是设计模型，不是 V0 的评分公式。

## 产品原则

SkillNudge 不以最大化安装数量或生成 Top-10 列表为目标。它遵循的核心原则是：

> **找到一个能够真正改善下一段任务轨迹的最小介入。**

建议输出保持克制：

- 0 个推荐是合法结果；
- 理想情况下只有 1 个 primary；
- 最多是 primary + supporting；
- Companion Resource 单独呈现；
- 必要时解释为什么拒绝其他候选；
- 不输出推荐垃圾列表。

## 概念流程

```text
用户问题
    ↓
缺失能力
    ↓
介入类型
    ↓
候选对象
    ↓
基于证据的判断
```

当前概念模型包含 Skill、Plugin、Tool、Companion Resource 和 No intervention。
V0 不一定对每种类型提供同等深度的支持。

## V0 设计基线

已经冻结的 V0 Runtime Map 是：

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

Trace 横切整个 Runtime。
```

设计基线详见：

- [`docs/runtime.md`](docs/runtime.md)
- [`docs/candidate-acquisition.md`](docs/candidate-acquisition.md)
- [`docs/retrieval.md`](docs/retrieval.md)
- [`docs/trace.md`](docs/trace.md)

## Local-First 与轻量默认

V0 的目标是在普通开发者笔记本上运行：

- 不强制安装 embedding model；
- 不要求 vector database；
- 不要求 GPU；
- 默认采用本地 SQLite + FTS5 / BM25 的检索方向；
- 只有本地证据或覆盖不足时才进行定向 live discovery；
- 只对小候选池获取完整正文。

GitHub 主要用于已知候选的源代码获取、provenance 和 freshness check，
不把它默认当作完整 Skill universe 的搜索索引。

## 设计案例

最初的三个案例有意覆盖不同问题：

- **D001 — UI Vocabulary Gap：** 用户想做设计和原型，但不知道专业词汇。
- **D002 — Premature Execution / Thinking Partner：** 最合适的介入可能是
  协作模式、Plugin、Tool 或 model bridge，而不是 Skill。
- **D003 — No Intervention：** 一个直接的问题可能不需要增加任何能力。

详见 [`docs/golden-cases.md`](docs/golden-cases.md)。这些案例是设计探针，
不是写死到系统里的答案。

## 当前状态

**Design / V0 baseline。**

当前仓库包含：

- 产品与 Runtime 设计文档；
- 决策记录；
- Golden Cases；
- 为后续 source 和测试代码预留的占位文件。

当前**不宣称**已经提供：

- 可运行的 `skillnudge advise` 命令；
- BM25 或 FTS5 实现；
- 已下载的 Skill corpus；
- embedding 或 reranking backend；
- 自动安装；
- Review、Grow 或 Watch；
- 自动化 Skill Utility Drift 检测；
- benchmark 结果或优于其他产品的结论。

## Roadmap

计划按阶段推进：

1. **V0：** Discovery / Intervention Advisor。
2. **V0.5：** 检索质量与 corpus freshness。
3. **V1：** 可选 semantic / hybrid retrieval。
4. **Later：** Review、Grow、Watch。
5. **Future：** Skill Utility Drift，包括 simplify、update、replace 和
   retire。

这些是 roadmap 方向，不代表已经实现。

## 设计文档

- [`docs/runtime.md`](docs/runtime.md) — V0 Runtime Map 与各层职责。
- [`docs/candidate-acquisition.md`](docs/candidate-acquisition.md) — 本地
  source、live fallback、标准化与缓存层级。
- [`docs/retrieval.md`](docs/retrieval.md) — 轻量检索基线。
- [`docs/trace.md`](docs/trace.md) — 不记录 private chain-of-thought 的可观察运行产物。
- [`docs/golden-cases.md`](docs/golden-cases.md) — D001、D002、D003。
- [`docs/roadmap.md`](docs/roadmap.md) — 分阶段范围与 utility drift。
- [`docs/week1.md`](docs/week1.md) — 第一阶段实现边界建议。
- [`docs/decisions/`](docs/decisions/) — 历史决策记录。

## 参与贡献

项目仍处于早期设计阶段。提出实现前，请先阅读设计文档，并明确区分：

- 设计目标与已经实现的行为；
- 证据与假设；
- Skill、Plugin、Tool、Companion Resource 与 No intervention；
- 检索相关性与介入效用。

优先接受小范围、可证伪的提案，而不是一次性加入完整平台能力。

## 许可证

SkillNudge 使用 [MIT License](LICENSE) 发布。

