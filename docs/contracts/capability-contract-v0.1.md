# CapabilityContract v0.1

## Status

**FROZEN FOR WEEK 1**

CapabilityContract 记录用户在当前任务阶段的目标、阻塞和可能缺失的行为能力。
它不记录具体 Skill 名称，也不预先决定 intervention。

## Contract

```yaml
CapabilityContract:
  goal: string
  stage: string | null
  blocker: string
  missing_capabilities: list[string] # 0–3
  intended_effect: string
  constraints: list[string]          # optional
  not_needed: list[string]           # optional
  uncertainties: list[string]        # optional

CapabilityFramingResult:
  contract: CapabilityContract
  confidence: high | medium | low
  clarification_needed: bool
  clarification_question: string | null
```

`missing_capabilities` 允许为空列表 `[]`。空数组不表示理解失败，而表示当前
需求可能不存在 capability gap，因此后续可以判断不需要额外 intervention。

## Framing Rules

1. Do not prescribe an intervention.
2. Diagnose the blockage, not merely the topic.
3. Capabilities describe behavioral change.
4. Do not invent a capability gap.

Capability framing 必须先于 candidate retrieval。候选名称、热门程度或搜索
结果不能反向决定用户缺失的 capability。

## Human Pressure Tests

这些案例用于检查合同是否能表达真实阻塞，不把具体候选名称冻结为系统答案。
`confidence` 和澄清问题的具体值不是以下案例额外冻结的行为；需要检查的是
contract 是否忠实表达阻塞，以及空 capability 是否能被保留。

### D001 — UI Vocabulary Gap

#### Scenario

用户想做一个更好看的前端 / UI 原型，但不懂设计，也不知道如何描述自己
想要什么。问题不是单纯出现了 `UI` 这个主题，而是用户缺少把审美目标转成
可执行设计和原型工作的能力与词汇。

#### Pressure-Test Contract

```yaml
contract:
  goal: produce a better-looking UI prototype
  stage: prototyping
  blocker: cannot name the design needs or professional vocabulary
  missing_capabilities:
    - UI / UX framing
    - prototyping guidance
    - design-system guidance
  intended_effect: turn a vague visual goal into actionable design and prototyping direction
```

`missing_capabilities` 不应包含某个候选 Skill 名称。该案例用于检查 vague
intent 是否在搜索前变成可比较的 capability contract。

### D002 — Premature Execution / Thinking Partner

#### Scenario

用户希望面对模糊的概念、需求和方向时，先发散、纠偏、重构问题并逐步收敛，
而不是让 Codex 很快进入 planning 或 coding。表面上它可能像是在寻找
brainstorming Skill，真实阻塞也可能是协作节奏和执行边界。

#### Pressure-Test Contract

```yaml
contract:
  goal: explore and converge on an ambiguous problem before implementation
  stage: problem framing
  blocker: the agent enters planning or coding too quickly
  missing_capabilities:
    - deliberative collaboration
    - problem reframing
    - gradual convergence
  intended_effect: preserve thinking-partner interaction before execution
```

该案例用于检查 framing 不因 SkillNudge 的产品主题而预设 Skill-first 答案，
并保留对 interaction-mode support 的判断空间。

### D003 — No Intervention

#### Scenario

用户只问“这个 Python error 是什么意思？”。在当前信息下，直接解释错误即可，
没有明确的 external capability blocker。

#### Pressure-Test Contract

```yaml
contract:
  goal: understand the meaning of a Python error
  stage: null
  blocker: no external capability blocker identified
  missing_capabilities: []
  intended_effect: understand the error and next step without an additional intervention
```

这里的关键设计修正是 `missing_capabilities` 必须允许 `[]`。它不表示理解
失败；它表示当前需求可能不存在 capability gap，并应允许后续直接进入
`no_intervention` 路径。
