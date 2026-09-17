# Candidate Acquisition

## Status

这是 V0 的数据与候选获取设计，不是已实现的 source adapter。

## Local First

SkillNudge 默认不让每次查询都访问所有互联网 source。

逻辑基线：

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

## Skill Source

默认轻量方向：

```text
public Skill corpus
→ normalize
→ SQLite
→ FTS5 / BM25
```

设计上应能支撑未来十万或几十万级 metadata，但运行时不把完整 corpus
加载进内存。

可以参考已有公开 corpus、registry 或 benchmark，但不能把第三方项目的
coverage 或 quality claim 直接当作事实。

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

未来可以增加：

```text
official marketplace
    + user personal marketplace
    + project/team marketplace
```

但这些不是当前实现承诺。

## Tool Source

V0 不预建一个巨大的 ToolHub。

当以下任一条件成立时，才考虑定向 live discovery：

- Capability framing 显示 Tool 可能更合适；
- Skill / Plugin 候选较弱；
- 现有本地 catalog 覆盖不足。

只对少量候选进行：

```text
2–3 targeted web queries
→ hydrate top few candidates
→ normalize
→ judge
```

## Candidate Cache Levels

live result 不应自动污染稳定 corpus。概念上区分：

### L0 Stable Catalog

经过固定版本、来源和许可核验的稳定 catalog。

### L1 Validated Cache

曾经被验证过、但仍需要 freshness 管理的候选缓存。

### L2 Current Run / Ephemeral

只属于当前运行的 live 候选，不自动升级为稳定数据。

候选流转方向：

```text
live discovery
→ current run
→ validated
→ cache
```

是否从 L1 进入 L0，需要后续单独决策。

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

Candidate Pool 不等于 Recommendation List。

