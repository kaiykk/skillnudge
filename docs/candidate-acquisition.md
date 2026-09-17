# Candidate Acquisition

## Status

- `[FROZEN]` Local corpus is a default source, not the whole world.
- `[FROZEN]` Candidate Acquisition constructs a Candidate Pool and does not
  produce Final Advice.
- `[WORKING HYPOTHESIS]` Local-first plus bounded live fallback is sufficient
  for the first product loop.
- `[FUTURE]` Large-scale source adapters, stable snapshot publishing, and a
  broad ToolHub.

这是 V0 的数据与候选获取设计，不是已实现的 source adapter。

## Local First

SkillNudge 默认不让每次查询都访问所有互联网 source。

```text
Query Plan
   ↓
Local Candidate Acquisition
   ↓
Is evidence / coverage sufficient?
   ├── yes → continue
   └── no  → targeted live discovery
                   ↓
              normalize
                   ↓
                cache
                   ↓
              candidate pool
```

Local-first 的目的不是拒绝互联网，而是控制：

- 网络延迟；
- source drift；
- 重复抓取；
- 不可复查的候选变化；
- 把一次 live 结果误当成稳定 corpus 的风险。

## Candidate Pool Sources

Local corpus != the whole world. Candidate Pool 可以来自：

- stable local corpus；
- official catalog；
- live discovery；
- user-provided URL / repo；
- local installed Skills / Plugins。

Candidate Pool 不等于 Recommendation List。

## Skill Source

默认轻量方向：

```text
public Skill corpus
→ normalize
→ SQLite
→ FTS5 / BM25
```

设计上应能支撑未来 10k、50k、100k+ 级 metadata，但运行时不把完整 corpus
加载进内存。正确的边界是：

```text
Disk corpus
→ SQLite index
→ BM25
→ Top candidates
```

而不是 `load all Skills into Python memory`。

如果本地 coverage 或 evidence 不够，再触发 Skill live discovery。优先
复用成熟 registry / search service，不在 V0 自己重做互联网爬虫。前期
D001 的 GitHub live code search 失败记录见
[`research/github-search-failure.md`](research/github-search-failure.md)。

### GitHub Boundary

GitHub 更适合：

```text
已知 candidate
→ fetch source
→ hydrate SKILL.md
→ freshness / provenance check
```

当前不把裸 GitHub code search 视为整个 Skill universe 的 primary
discovery backend。

### Registry / Catalog Boundary

V0 可以优先研究成熟 registry 或 catalog：

- Skill registry 用于 source coverage；
- official plugin marketplace 用于 Plugin catalog；
- personal / project marketplace 作为未来扩展。

不要在 V0 自己构建 PluginHub。

## Plugin Source

Plugin 采用 catalog-first 的概念：

```text
official plugin marketplace
→ normalize
→ local / lightweight index
→ periodic refresh
```

未来可以增加 official marketplace、personal marketplace 和
project/team marketplace，但这些不是当前实现承诺。

## Tool Source

V0 不预建一个巨大的 ToolHub。

只有当以下任一条件成立时，才考虑定向 live discovery：

- Capability Framing 显示 Tool 可能更合适；
- Skill / Plugin 候选较弱；
- 现有本地 catalog 覆盖不足。

搜索预算必须有限：

```text
2–3 targeted web queries
→ hydrate top few candidates
→ normalize
→ judge
```

这不是 general knowledge search，也不是无限 web research。

## Companion Resource

Resource 不是 V0 核心 candidate class，可以作为 Companion Resource，例如：

- reference collection；
- design gallery；
- documentation。

不要因此扩展成 general knowledge search engine。

## Candidate Data Lifecycle

候选的 L0/L1/L2 生命周期、标准化字段和 provenance 规则集中记录在
[`data-layer.md`](data-layer.md)。这里仅保留 acquisition 相关边界：

```text
live discovery
→ current run
→ validated
→ cache
```

live result 不能自动进入 trusted corpus。

## Candidate Pool Contract

每个候选至少应能追溯到：

- intervention type；
- canonical identity；
- source URL 或 local source；
- version / commit / retrieved time；
- license；
- evidence location；
- current cache level；
- source confidence；
- compatibility uncertainty。
