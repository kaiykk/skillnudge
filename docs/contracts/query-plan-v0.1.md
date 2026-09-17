# QueryPlan v0.1

## Status

**FROZEN FOR WEEK 1**

## Purpose

QueryPlan 只回答：

> 应该从哪些互补的语义角度寻找 candidate？

它不负责：

- provider selection；
- SQL；
- API syntax；
- Top-K；
- BM25 weighting；
- live-search trigger；
- candidate selection；
- fallback logic。

## Runtime Boundary

```text
CapabilityContract
+
InterventionPlan
↓
QueryPlan
↓
Candidate Acquisition
↓
actual SQL / API / BM25 / web request
```

## Contract

```yaml
QueryPlanResult:
  status:
    ready | skipped | clarify

  queries:
    max_items: 5

    item:
      family:
        skill | integration | resource

      angle:
        capability
        | problem
        | outcome
        | operation
        | professional_vocabulary
        | stage

      semantic_query:
        string

      purpose:
        string
```

## Global Query Budget

3–5 queries 是总预算，不是每个 intervention family 各自拥有 3–5 条。

Primary family 通常获得大多数 query。只有在 secondary 或 companion family
确实覆盖不同 candidate space 时，才为它生成 query。

简单案例可以少于 3 条 query。不得为了满足数量配额而凭空增加 query。

## Hard Rules

### 1. Queries Must Be Complementary

Queries 必须互补，不能只是 paraphrase。

Bad：

```text
ui prototype
frontend prototype
ui design
interface design
frontend UI
```

### 2. Search the Capability, Not the Known Solution

除非用户明确提供，否则不得把已知 candidate 名称放入 query generation。
这样可以避免 gold leakage。

### 3. QueryPlan Expresses Semantic Intent

QueryPlan 表达语义意图，不表达 provider syntax。不得输出 SQL、FTS syntax、
GitHub syntax、`skills.sh` parameters 或 web search operators；这些属于
Candidate Acquisition。

### 4. Do Not Explode Search Breadth to Resolve Uncertainty

不应通过无限扩大搜索宽度来解决 uncertainty。如果某个 uncertainty 会改变
intervention family，应优先澄清，而不是同时搜索 Skill、Integration 和
Resource。

## Pressure Tests

### D001 — UI Vocabulary Gap

Intervention：

```text
Skill primary
Resource companion
```

Example QueryPlan：

```yaml
- family: skill
  angle: capability
  semantic_query: ui ux prototyping guidance
  purpose: Find instructional capabilities that help users turn vague product ideas into UI prototypes.

- family: skill
  angle: problem
  semantic_query: translate vague visual intent into interface design
  purpose: Search around the actual blocker rather than generic frontend development.

- family: skill
  angle: professional_vocabulary
  semantic_query: design system wireframe prototype interaction design
  purpose: Introduce professional vocabulary the user did not know, improving lexical recall.

- family: resource
  angle: outcome
  semantic_query: ui design references interface patterns examples
  purpose: Find companion references that help users express and compare visual directions.
```

不得把以下已知 candidate 放入 query generation：

- `ui-ux-pro-max`；
- `awesome-design-md`；
- `mono-color-skill`。

### D002 — Premature Execution / Thinking Partner

Intervention：

```text
Integration primary
Skill secondary
```

Example semantic search space：

Integration：

- Codex deliberative conversation interaction；
- Codex premature planning execution discussion mode；
- Codex thinking partner gradual problem framing。

Skill：

- deliberative brainstorming problem reframing；
- challenge assumptions discuss before implementation。

不得 hardcode known candidates。

### D003 — No Intervention

InterventionPlan：

```yaml
decision: no_intervention
```

因此：

```yaml
status: skipped
queries: []
```

不得执行 BM25 search。

## Clarify Edge Case

如果 `CapabilityFramingResult` 表示需要澄清，并且答案会改变 intervention
family：

```yaml
status: clarify
queries: []
```

不得在澄清前进行 broad search。
