# Golden Cases

## Status

这些是 V0 的真实设计探针，不是未来系统中的硬编码答案。

它们用于检查 SkillNudge 是否能够：

- 从模糊表达恢复 capability；
- 在不同 intervention type 之间保持开放；
- 合法地选择不介入。

## D001 — UI Vocabulary Gap

### User Intent

用户大意：

> 我想做一个好的前端 / UI 原型，但我不懂设计，也不知道怎么描述自己
> 想要什么。

### Expected Capability Framing

- UI / UX framing；
- prototyping guidance；
- design-system guidance。

### Expected Intervention Tendency

倾向于检查 Skill primary。

### Known Useful Candidate

`ui-ux-pro-max`

### Companion Candidate

`awesome-design-md`

它应作为 Companion Resource 单独处理，不自动计入 Skill positive /
negative。

### Known Mismatch

`mono-color-skill` 对主需求过窄。

### Design Question

用户不知道 professional vocabulary 时，系统能否不依赖原始 lexical match
而恢复足够准确的 capability framing？

## D002 — Premature Execution / Thinking Partner

### User Intent

用户大意：

> Codex 越来越像执行者。面对模糊概念、需求和方向时，它总是很快进入
> planning / coding。我希望它像 ChatGPT 一样，先和我发散、纠偏，慢慢收敛。

### Expected Capability Framing

- deliberative collaboration；
- problem reframing；
- gradual convergence；
- interaction-mode support。

### Candidate Surfaces

可能出现：

- brainstorming Skill；
- lightweight brainstorm Skill；
- Socratic guidance；
- ChatGPT / Codex Plugin；
- model / browser bridge；
- collaboration Tool。

### Design Question

SkillNudge 能否意识到：

> Skill may be the wrong intervention class.

不能因为产品名里有 Skill，就强行输出 Skill。

## D003 — No Intervention

### User Intent

例如：

> 这个 Python error 是什么意思？

### Expected Advice

允许：

```text
no_intervention
```

系统不应为了展示检索能力而强行推荐 debugging Skill。

## Use of Golden Cases

Golden Case 只约束要检查的问题，不冻结具体候选名称或最终输出。未来的
评测需要同时记录：

- 任务理解；
- 是否选对 intervention type；
- 是否过度推荐；
- 是否解释不确定性；
- 用户是否认为建议改善了下一步工作。

