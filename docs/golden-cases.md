# Golden Cases

## Status

- `[HISTORICAL EVIDENCE]` D001-D003 come from real user scenarios and
  exploration.
- `[FROZEN]` The cases test capability framing, intervention-class openness,
  and the legitimacy of no intervention.
- `[WORKING HYPOTHESIS]` Three contrasting cases are enough to expose the first
  product boundary.
- `[FUTURE]` A larger benchmark and formal labels.

这些是 V0 的设计测试集，不是未来系统中的硬编码答案。

## D001 — UI Vocabulary Gap

### Raw User Request

用户大意：

> 我想做一个更好看的前端 / UI 原型，但我不懂设计，也不知道怎么描述
> 自己想要什么。

### Why It Is Hard

这是 vocabulary mismatch：用户不知道 UI/UX、design system、wireframe、
prototype 等专业词，直接 lexical search 可能找不到合适候选。

### Expected Capability Framing

- UI / UX framing；
- prototyping guidance；
- design-system guidance。

### Expected Intervention Tendency

倾向于检查 Skill primary，但不能提前把某个 Skill 名称写进 capability。

### Known Candidate Examples

- Useful candidate: `ui-ux-pro-max`
- Companion candidate: `awesome-design-md`
- Narrow mismatch: `mono-color-skill`

这些候选来自历史探针，只是检查用例，不是产品应写死的答案。

### Known Traps

- 把用户原话当作完整搜索词；
- 只返回和 UI 相关但能力过窄的候选；
- 把 Companion Resource 当成 Skill positive；
- 因为找不到术语就直接宣称没有候选。

### What Failure Would Look Like

系统没有恢复 design/prototyping capability，或只返回 superficially-related
候选，却没有解释 fit 和 mismatch。

### Why This Case Matters

它验证 vague intent 是否能在搜索前转成可比较的 capability contract。

## D002 — Premature Execution / Thinking Partner

### Raw User Request

用户大意：

> Codex 越来越像执行者。面对模糊概念、需求和方向时，它总是很快进入
> planning / coding。我希望它像 ChatGPT 一样，先和我发散、纠偏，慢慢收敛。

### Why It Is Hard

这是 intervention-class mismatch。表面请求可能是“找一个 brainstorm Skill”，
真实需求却可能是改变交互节奏和执行边界。

### Expected Capability Framing

- deliberative collaboration；
- problem reframing；
- gradual convergence；
- interaction-mode support。

### Expected Intervention Tendency

Skill 可以作为一个候选 surface，但 Plugin、Tool、model bridge 或 no
intervention 也必须保持开放。

### Known Candidate Examples

可能出现：

- Superpowers brainstorming；
- lightweight brainstorm Skill；
- Socratic guidance；
- ChatGPT / Codex Plugin；
- model / browser bridge；
- collaboration Tool。

这些名称是历史候选表面，不是冻结的推荐。

### Known Traps

- 因为产品名是 SkillNudge 就强行选 Skill；
- 把高 fit 与高 trust 混为一谈；
- 忽略重型 workflow 的 friction；
- 把“先讨论”误解为“多装一个 instruction pack”。

### What Failure Would Look Like

系统只给出一个 Skill 名称，却没有判断 interaction mode 是否更合适，
也没有说明 setup、context、workflow friction。

### Why This Case Matters

它验证系统是否真正是 Capability Intervention Advisor，而不是换名后的
Skill Directory。

## D003 — No Intervention

### Raw User Request

例如：

> 这个 Python error 是什么意思？

### Why It Is Hard

它看起来很容易，但推荐系统往往会因为有候选就强行推荐。

### Expected Capability Framing

直接解释错误即可，当前没有明确的 external capability gap。

### Expected Intervention Tendency

优先判断 `no_intervention`，而不是为了展示检索能力而搜索。

### Known Candidate Examples

通常没有必要的 Skill、Plugin 或 Tool。

### Known Traps

- recommendation addiction；
- 把“没有候选”与“不需要介入”混淆；
- 输出一个泛化 debugging Skill 但不说明增量价值。

### What Failure Would Look Like

系统为了填满结果位而推荐一个 generic Skill，或把 source 空结果写成
`no_match`。

### Why This Case Matters

它把“0 intervention 是合法答案”变成可检查的设计约束。

## Use of Golden Cases

Golden Case 只约束要检查的问题，不冻结具体候选名称或最终输出。未来评测
至少应记录：

- 任务理解；
- 是否选对 intervention type；
- 是否过度推荐；
- 是否解释不确定性；
- 用户是否认为建议改善了下一步工作；
- 失败属于 framing、acquisition、evidence、judge 还是 advice。
