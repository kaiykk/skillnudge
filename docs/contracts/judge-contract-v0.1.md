# JudgeContract v0.1

## Status

**FROZEN FOR WEEK 1**

## Judge Thesis

Candidate Acquisition 回答：

> Who might be relevant?

Judge 回答：

> Is this intervention actually worth adding now?

Judge 评估的是 incremental intervention utility，而不是 semantic similarity
alone。

核心问题是：

> Compared with doing nothing, is this intervention likely to improve the next
> trajectory enough to justify its cost, friction, and risk?

## Input

Candidate Judge 接收：

```text
CapabilityContract
+
InterventionPlan
+
EvidencePack(candidate)
```

它也可以使用已经在 `InputEnvelope` 中捕获的显式用户 / 项目约束。

Judge 不做以下事情：

- 不重新搜索；
- 不重新生成 `CapabilityContract`；
- 不发明缺失的 source evidence；
- 不选择最终的 Primary recommendation。

## CandidateJudgement Schema

```yaml
CandidateJudgement:
  candidate_id:
    string

  evidence_status:
    sufficient | partial | insufficient

  assessment:

    capability_fit:
      strong | partial | weak | none

    stage_fit:
      now | later | wrong_context | unclear

    mechanism_fit:
      strong | partial | weak

    expected_gain:
      high | medium | low | unknown

    practical_fit:

      compatibility:
        compatible | conditional | incompatible | unknown

      constraint_fit:
        satisfies | partial | violates | unknown

      friction:
        low | medium | high | unknown

    trust:
      strong | adequate | weak | unknown

  matched_capabilities:
    list[string]

  gaps_or_mismatches:
    list[string]

  evidence:
    list[evidence_ref]

  disposition:
    viable
    | companion
    | defer
    | reject
    | insufficient_evidence

  reason:
    string
```

除上述字段外，本合同不增加 V0 numeric score、排序字段或 Primary 选择字段。

## Meaning Of Dimensions

### Capability Fit

Candidate 是否真的解决用户缺失的 capability？

### Stage Fit

Candidate 即使有用，现在是否是合适的使用时机？

### Mechanism Fit

这种 intervention 是否适合解决底层 blocker？

### Expected Gain

相对于什么都不加，预期能带来多少 incremental benefit？

### Practical Fit

结合 compatibility、constraints 和 friction，用户是否现实地用得起来？

### Trust

有多少 external / source evidence 支持其可靠性和判断信心？

## Critical Distinctions

```text
Fit != Gain != Trust != Friction
```

Popularity 不等于 Capability Fit。低 popularity 不应被当作 semantic mismatch
而惩罚。

一个 0-star candidate 仍可能是 high Fit、low Trust、low Friction。一个 popular
candidate 也可能是 high Trust、high Friction、partial Mechanism Fit。

Evidence Status 不等于 Trust：

- 完整的 `SKILL.md` 与 README 可用，但没有 adoption evidence：
  `evidence_status = sufficient`、`trust = weak`；
- 一个著名工具只有一行 metadata 且 README 无法访问：trust 可能较强，但
  `evidence_status` 仍可能是 `insufficient`。

## Expected Gain

Expected Gain 是 SkillNudge 的核心判断之一。V0 只使用：

```text
high | medium | low | unknown
```

不得创建 numerical utility score。当前没有足够 empirical data 支撑如下 fake
precision：

```text
0.72 * fit
+ 0.18 * trust
- 0.35 * friction
```

## Stage Fit

“Not useful now” 不等于 “bad intervention”。允许：

```text
stage_fit = later
disposition = defer
```

例如，一个 specification / workflow Skill 可能在 requirements 稳定后有价值，
但在 early exploration 阶段过早。

## Mechanism Fit

D002 说明 brainstorming Skill 可以有：

```text
capability_fit = strong
mechanism_fit = partial
```

因为真实 blocker 可能位于 interaction / runtime behavior，而不是 instruction
pack 本身。

## Friction

Friction 可以包括：

- setup；
- context load；
- workflow ownership；
- operational instability；
- authentication burden；
- maintenance burden；
- learning cost；
- behavioral intrusion。

即使 intervention 的 capability fit 很高，如果 friction 过高，也可能不值得
推荐。

## Trust

Trust 可以参考：

- official source；
- maintenance；
- adoption；
- documentation；
- repo quality；
- usage evidence；
- update recency。

Stars 不得直接决定 Capability Fit。

## Disposition

- `viable`：candidate 可以进入 Final Advice 的推荐比较；
- `companion`：有支持价值，但不是解决主要 blocker 的 primary intervention；
- `defer`：有用，但不适合当前 stage；
- `reject`：对当前情况不值得使用；
- `insufficient_evidence`：证据不足，不能负责任地判断。

Judge 不选择 `primary` 或 `supporting`。这两个位置属于 Final Advice。

## Hard Gates

默认行为：

```text
evidence_status = insufficient
→ insufficient_evidence

capability_fit = none
→ reject

compatibility = incompatible
→ reject

violates critical user constraint
→ reject

stage_fit = later
→ defer

only auxiliary value
→ companion

otherwise:
may remain viable
```

不得引入 global score。

## Judge Generation Rules

1. Judge incremental value, not topical relevance。
2. Do not reward popularity as capability fit。
3. Do not punish low popularity as semantic mismatch。
4. Prefer `defer` over `reject` when timing is the problem。
5. Every material judgement must be grounded in `EvidencePack` or explicit
   user / project constraints。

如果证据不足，不得猜测。

## Human Pressure Tests

### D001 — UI Vocabulary Gap

#### ui-ux-pro-max Style Candidate

```text
capability_fit = strong
stage_fit = now
mechanism_fit = strong
expected_gain = high
compatibility = compatible
friction = low
trust = adequate
disposition = viable
```

#### awesome-design-md Style Resource

```text
capability_fit = partial
stage_fit = now
mechanism_fit = strong
expected_gain = medium
friction = low
disposition = companion
```

它是 companion，不是解决主要 blocker 的 primary intervention。

#### mono-color Style Candidate

```text
capability_fit = weak
expected_gain = low
gaps_or_mismatches = [scope too narrow]
disposition = reject
```

### D002 — Premature Execution / Thinking Partner

#### Superpowers-like Candidate

```text
capability_fit = strong
trust = strong
friction = high
mechanism_fit = partial
expected_gain = medium
disposition = viable
```

它可能 viable，但不自动优先。`viable` 只表示可以进入 Final Advice comparison，
不表示已经胜出。

#### Lightweight Brainstorm Candidate

```text
capability_fit = strong
trust = weak
friction = low
mechanism_fit = partial
expected_gain = medium
disposition = viable
```

#### Integration / Bridge Candidate

```text
capability_fit = strong
mechanism_fit = strong
expected_gain = high
compatibility = conditional
friction = high
```

它同样不是自动赢家；最终 disposition 必须依据完整 evidence 和 hard gates
生成。

### D003 — No Intervention

Judge 不被调用。

Runtime 应在 retrieval 前 early-stop。

### Stage Defer Edge Test

强 capability、错误 timing：

```text
capability_fit = strong
stage_fit = later
mechanism_fit = strong
expected_gain = medium
disposition = defer
```

这明确表达：

> Good intervention, not now.
