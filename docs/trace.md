# Trace

## Status

- `[FROZEN]` Trace is a first-class, explicit runtime artifact.
- `[FROZEN]` Trace does not contain private chain-of-thought or secrets.
- `[IMPLEMENTED CHECKPOINT 1]` D001 produces the first five checkpoint artifacts
  plus `trace.jsonl`; later runtime artifacts remain unimplemented.
- `[WORKING HYPOTHESIS]` The proposed artifact boundaries are sufficient for
  diagnosing V0 failures.
- `[FUTURE]` Automated Review, utility attribution, and long-term monitoring.

Trace 是 V0 的可观察性设计。Checkpoint 1 已提供 D001 的局部运行记录系统；
完整 runtime 的记录仍待后续 checkpoint。

## Purpose

Trace 的目标是让后续可以区分：

```text
理解错？
→ route 错？
→ query 错？
→ local corpus coverage 问题？
→ live discovery 问题？
→ evidence hydration 问题？
→ Judge 错？
→ final aggregation 错？
```

如果没有这些边界，系统很容易在事后用一段自然语言解释掩盖真实失败层。

## What to Record

记录系统显式输入、输出和决策对象：

- raw user request；
- optional project context；
- current stage；
- CapabilityContract；
- InterventionPlan；
- QueryPlan；
- source and cache decisions；
- candidate identities；
- evidence packs；
- candidate judgements；
- final advice；
- status；
- errors；
- latency and bounded cost metadata。

不要记录模型 private chain-of-thought。

## Run Artifact Layout

未来每次运行可以保存为：

```text
runs/<run_id>/

00_input.json
01_capability_contract.json
02_intervention_plan.json
03_query_plan.json
04_candidate_acquisition.json
05_evidence_packs.json
06_judgements.json
07_final_advice.json
trace.jsonl
```

`runs/` 默认 gitignored，除非某个脱敏、最小化的 run 被明确选为设计证据。

## Trace Requirements

每个 artifact 应包含：

- schema version；
- run id；
- stage name；
- input references；
- output object；
- timestamp；
- source / model provenance；
- explicit uncertainty；
- error boundary；
- redaction status。

Trace 文件是可复查状态，不是用户隐私的无限制存档。

## Review Protocol

审查一次 run 时，固定按下面顺序：

```text
1. Contract
2. Query / SQL / retrieval request
3. Raw Result
4. System decision
5. Final advice
6. Agent analysis last
```

先看事实和显式产物，再看 Agent 对自身行为的解释。这样可以降低
narrative bias，避免事后叙事掩盖真实失败层。

## Privacy and Security

不得默认保存：

- API key；
- token；
- password；
- cookies；
- browser storage；
- 私人文件原文；
- 模型 private chain-of-thought。

如果输入包含私人项目内容，未来实现必须提供脱敏、最小化和清理策略。

## Status Semantics

Trace 中的最终状态至少应区分：

- `recommendation`
- `no_intervention`
- `insufficient_evidence`
- `needs_clarification`
- `source_error`

公共 source 的空结果不能直接等同于 closed-corpus 的 `no_match`。
