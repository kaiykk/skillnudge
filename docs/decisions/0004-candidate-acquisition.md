# Decision

Candidate Acquisition 采用 local-first，并将候选分为 Stable Catalog、
Validated Cache 和 Current Run / Ephemeral 三个概念层级。

# Context

每次 live discovery 都可能受网络、版本、限流和 source drift 影响。若把
一次 live 结果直接写入稳定 corpus，后续很难解释结果变化。

# Options considered

- 每次都重新搜索所有 source；
- 只维护一个不断增长的全局 corpus；
- 本地候选优先，覆盖不足时定向 live discovery，再经过 normalize 和
  validation 后逐步进入 cache。

# Decision

采用：

```text
live discovery
→ current run
→ validated
→ cache
```

是否进入 Stable Catalog 需要单独的 provenance、license 和 freshness 判断。

# Why

这样可以把“当前发现”与“稳定事实”分开，减少 source drift 对结果解释的
影响。

# Consequences

- Candidate Pool 需要携带 cache level；
- source adapter 需要保留 retrieved time 和版本信息；
- live discovery 不是无成本的默认路径。

# Revisit when

当候选规模、刷新频率或人工核验成本证明三层缓存过于复杂时，再收敛层级。

