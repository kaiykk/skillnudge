# InterventionPlan v0.1

## Status

**FROZEN FOR WEEK 1**

InterventionPlan 决定当前需求应“去哪里找”，不决定“找哪个 candidate”。
它是有限的、可解释的 soft allocation，不是具体产品或候选的硬路由。

## Contract

```yaml
InterventionPlan:
  decision:
    search | no_intervention | clarify

  targets:
    max_items: 2
    item:
      family:
        skill | integration | resource
      priority:
        primary | secondary | companion
      rationale:
        string

  decision_reason:
    string
```

`targets.item` 表示目标条目的结构；目标总数最多为两个。对于
`no_intervention`，可以不产生目标条目；对于 `clarify`，应先获得必要澄清，
再决定是否搜索。

## Planning Rules

- InterventionPlan 决定“去哪里找”，不决定“找哪个 candidate”。
- 不允许在这里出现具体产品名。
- Plugin / Tool / MCP / Bridge 在本层统一属于 `integration`。
- 具体是 Plugin 还是 Tool，留给 Candidate Acquisition。
- 最多两个 family。
- 不为提高 recall 而机械搜索所有 family。
- `no_intervention` 是一等结果。

因此，`integration` 是本层的干预类别，不是对具体实现形态的提前判断。
Candidate Acquisition 才负责在该类别内发现和检查具体候选。

## Human Pressure Tests

这些 pressure tests 只冻结 intervention family、优先级和停止边界，不冻结
具体产品名或 candidate。

### D001 — UI Vocabulary Gap

用户缺少把模糊 UI 目标转成设计和原型行动的能力。合理的计划是：

```text
Skill primary + Resource companion
```

Resource 用于补充术语、案例或参考材料；它不是在本层被选定的具体资源。

### D002 — Premature Execution / Thinking Partner

用户的核心阻塞可能是交互方式和执行边界，而不只是缺少一组 Skill 指令。
合理的计划是：

```text
Integration primary + Skill secondary
```

`integration` 可以覆盖 Plugin、Tool、MCP 或 Bridge，但本层不决定具体是哪一
种；Skill 作为次要探索面保留。

### D003 — No Intervention

对直接询问 Python error 含义的需求，合理的计划是：

```text
No intervention
```

该决定应在 retrieval 前直接停止，不应为了展示搜索能力而构造候选池。
