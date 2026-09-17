# Retrieval

## Status

- `[FROZEN]` V0 is local-first and BM25-first.
- `[FROZEN]` Embedding, vector database, and GPU are not mandatory V0
  dependencies.
- `[WORKING HYPOTHESIS]` Query diversity plus rank fusion can provide a useful
  candidate pool before semantic retrieval is justified.
- `[FUTURE]` Optional embedding, hybrid retrieval, and learned reranking.

这是 SkillNudge 的 V0 retrieval design baseline，不是已经运行的检索系统。

## Lightweight Defaults

V0 明确：

- **NO mandatory embedding model**
- **NO vector database requirement**
- **NO GPU requirement**

默认方向：

```text
CapabilityContract
        ↓
3–5 complementary queries
        ↓
SQLite FTS5 / BM25
        ↓
per-query Top-K
        ↓
Reciprocal Rank Fusion
        ↓
Top 20–30 candidate pool
```

这是一条待实现和验证的 baseline，不是效果承诺。V0 的目标不是 BM25
Top-1 accuracy，而是把值得进一步检查的候选带入一个小而可追溯的
Candidate Pool。

## Retriever Boundary

概念上的抽象为：

```text
Retriever
├── BM25Retriever        # V0 default
├── EmbeddingRetriever   # V1 optional
└── HybridRetriever      # V1 optional
```

Retriever 只回答：

> 哪些候选值得进一步检查？

它不回答：

> 哪个候选值得现在介入？

Embedding 是可选的 capability upgrade，不是安装前提。V0 不在没有产品
闭环证据的情况下重新建设 dense retrieval 研究。

## Query Diversity

Query Planning 不应只生成同一句话的 paraphrase。互补角度可以包括：

- capability；
- problem；
- desired outcome；
- operation；
- professional vocabulary；
- artifact；
- workflow；
- scenario / task stage。

实际数量应由任务复杂度决定，目标范围为 3–5 条。

## Candidate Pool Versus Advice

```text
retrieval relevance
≠
usable intervention
```

完整 body、兼容性、维护状态、许可和任务阶段证据应在后续 Evidence
Hydration 与 Candidate Judgement 中处理。

## No-Intervention Path

如果 Capability Framing 认为用户问题不需要额外能力，retrieval 可以被跳过。
例如一个直接的 Python error 解释请求，不应为了展示检索能力而强行搜索
Skill。

## Future Upgrade Boundary

未来可研究：

- optional embedding retrieval；
- hybrid retrieval；
- learned reranking；
- larger catalog；
- freshness-aware ranking。

这些都需要独立证据，不得因为 retrieval 结果看起来相关，就默认扩大到
V0。只有当产品闭环暴露出 lexical、coverage、query 以外的明确缺口，才
进入该方向。
