# Decision

V0 采用 local-first、轻量 lexical retrieval；embedding 作为可选的 V1 能力。

# Context

SkillNudge 面向普通开发者本地运行。强制 embedding、vector database 或
GPU 会提高安装和维护成本，也会在没有证据时提前扩大架构。

# Options considered

- 强制 embedding + vector database；
- 每次都访问所有 live source；
- 本地 SQLite FTS5 / BM25，覆盖不足时再定向 live discovery；
- 先做纯 embedding benchmark。

# Decision

采用：

```text
Local corpus
→ SQLite FTS5 / BM25
→ per-query Top-K
→ RRF
→ targeted live fallback when needed
```

# Why

这条路线容易在普通笔记本上运行，也便于固定 corpus、版本和 evidence。
它还允许在真实失败后再判断是否需要 semantic retrieval。

# Consequences

- 需要认真处理 vocabulary mismatch；
- local corpus coverage 成为显式设计对象；
- GitHub 不再被默认当作完整 universe search；
- dense retrieval 仍需要未来独立验证。

# Revisit when

当固定 corpus 上的真实案例持续显示 lexical retrieval 无法恢复关键候选，
并且 failure 不是 source coverage 或 query planning 问题时，再评估 V1。

