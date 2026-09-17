# Week 1

## Status

- `[FROZEN]` Week 1 is CLI-first and Advise-only.
- `[IMPLEMENTED CHECKPOINT 1]` Local corpus indexing, BM25/RRF raw retrieval,
  and D001 trace artifacts are implemented.
- `[FROZEN]` Week 1 excludes Review, Grow, Watch, semantic retrieval, and
  automatic installation.
- `[WORKING HYPOTHESIS]` A lightweight end-to-end loop can validate the product
  boundary before a larger platform is justified.

这是 Week 1 的实现边界与当前 checkpoint 状态。

## Goal

建立一个轻量的 **Intervention Advisor V0**，先验证产品边界和最小可用闭环：

```text
Input
→ Capability
→ Intervention
→ Query
→ Candidate Acquisition
→ Evidence
→ Judge
→ Advice
```

默认 CLI 方向为：

```bash
skillnudge advise "<request>" --trace
```

当前仓库尚未提供完整的 `skillnudge advise` 命令；Checkpoint 1 通过
`scripts/run_d001.py` 提供局部 smoke path。

## Definition of Done

### G1 — Runtime

未来实现后，CLI 能够运行完整的 Advise runtime，且每一层有可检查边界。

### G2 — Laptop

普通 laptop 可运行，默认不依赖：

- GPU；
- embedding；
- vector database。

### G3 — D001

D001 能从一个真实、可追溯的 corpus 找到合理 Skill candidate，并解释
vocabulary mismatch。

### G4 — D002

D002 不会强制选择 Skill，且能保留 non-Skill intervention 作为更合适的
方向。

### G5 — D003

D003 能输出 `no_intervention`。

### G6 — Trace

每次运行产生可读、脱敏、能定位失败层的 observable trace。

## Week 1 Non-Goals

Week 1 不做：

- frontend / GUI；
- mandatory embedding；
- vector DB；
- reranker training；
- Skill-specific fine tuning；
- Review；
- Grow；
- Watch；
- personalization；
- automatic installation；
- massive ToolHub；
- multi-agent；
- background scheduler；
- exhaustive benchmark；
- 完整 Skill lifecycle。

## Working Discipline

实现阶段应保持：

- 先验证 source coverage，再调 query；
- 先记录 evidence boundary，再写 recommendation；
- 先区分 intervention type，再决定候选；
- 先保证 no-intervention 合法，再追求推荐数量；
- 不把 README 或模型推断写成 confirmed capability。

## Timebox

Week 1 的目标是五个工作日内验证最小闭环，而不是完成完整生态。若
corpus/source、host compatibility 或 evidence hydration 在最小范围内仍
无法得到可复查结果，应记录为边界问题并缩小范围，不用增加平台基础设施
来掩盖验证失败。
