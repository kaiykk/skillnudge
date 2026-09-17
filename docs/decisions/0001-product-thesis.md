# Decision

SkillNudge 定义为 Capability Intervention Advisor，而不只是 Skill search
或 Skill directory。

# Context

用户经常只能描述模糊问题，且缺少专业词汇。即使某个 Skill 与用户问题
语义相关，也不代表它适合当前任务阶段，更不代表它值得增加上下文负担。

此外，合适的介入可能是 Plugin、Tool、Companion Resource，或者不介入。

# Options considered

- 构建一个更大的 Skill directory；
- 只做 Skill search / installer；
- 把所有问题路由到 Skill；
- 先理解缺失能力，再判断 intervention type 和是否值得介入。

# Decision

采用：

```text
User problem
→ Missing capability
→ Intervention type
→ Candidate
→ Evidence-based judgement
```

# Why

这能保留 No intervention，并避免把“搜索相关对象”误当成“现在值得
介入的能力”。

# Consequences

- 输出数量应保持克制；
- 需要显式记录不确定性和拒绝理由；
- Retrieval 不再等于最终 recommendation；
- Skill 只是主要入口，不是唯一答案。

# Revisit when

当真实任务证明 intervention type 判断没有增量，或用户始终只需要一个
纯 Skill directory 时，重新检查产品边界。

