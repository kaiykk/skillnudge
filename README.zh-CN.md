<div align="center">
  <p>
    <a href="README.md">English</a>
    ·
    <a href="README.zh-CN.md">简体中文</a>
  </p>
  <p>
    <a href="#快速开始">快速开始</a>
    ·
    <a href="#为什么是-skillnudge">为什么是 SkillNudge</a>
    ·
    <a href="#north-star">North Star</a>
    ·
    <a href="#文档">文档</a>
  </p>
  <p>
    <a href="https://github.com/kaiykk/skillnudge/blob/main/LICENSE">
      <img src="https://img.shields.io/github/license/kaiykk/skillnudge?style=flat-square" alt="MIT License">
    </a>
    <a href="https://github.com/kaiykk/skillnudge/stargazers">
      <img src="https://img.shields.io/github/stars/kaiykk/skillnudge?style=flat-square" alt="GitHub stars">
    </a>
    <a href="https://github.com/kaiykk/skillnudge/commits/main">
      <img src="https://img.shields.io/github/last-commit/kaiykk/skillnudge?style=flat-square" alt="Last commit">
    </a>
  </p>
</div>

<!-- Week 1 官方 Hero 图片。 -->
<p align="center">
  <img src="./assets/hero.png" alt="SkillNudge" width="100%">
</p>

SkillNudge 是一个面向 AI Agent 的本地优先能力介入建议工具。

它试图回答一个仅靠 Skill 搜索无法回答的问题：

> **当前真正缺少什么能力？现在增加任何介入，究竟是否值得？**

## 为什么是 SkillNudge？

### Relevant ≠ Useful

搜索可以告诉你哪些东西看起来相关。

SkillNudge 进一步追问：

> **增加这个能力，真的会改善下一段任务轨迹吗？**

- 对更强的模型来说，一个相关 Skill 可能已经没有必要。
- 同一种能力在不同任务阶段，可能有帮助，也可能造成负担。
- 合适的介入可能是 Plugin、Tool 或 Resource，而不是 Skill。
- 有时候最好的答案就是不介入。

更完整的背景见[产品命题](docs/product-thesis.md)。

## 它做什么？

### 01 — Understand

从模糊请求或任务阻塞中识别能力缺口。

### 02 — Discover

寻找最小的可行介入，而不是默认增加更多能力。

### 03 — Judge

把语义相关性与预期收益、信任、摩擦和阶段适配度分开判断。

### 04 — Advise

返回 0–2 个有边界的建议，也可以明确建议不介入。

这些是 V0 的目标能力。当前仓库已经包含 planning、本地检索、Evidence
Hydration 以及 Candidate Judgement / Final Advice 的运行时实现；最后阶段的
provider-backed 验证仍在进行。

## 快速开始

### Development Preview

当前仓库提供直接运行的 Python 开发流程，还不是打包后的终端用户 CLI。

```bash
git clone https://github.com/kaiykk/skillnudge.git
cd skillnudge
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py' -v
```

要运行当前的本地检索 smoke path，请准备兼容的 Skill corpus：

```bash
PYTHONPATH=src python3 scripts/run_d001.py \
  --corpus /path/to/corpus.json \
  --run-dir runs/d001-checkpoint1
```

运行结果会写入 `runs/` 下的可复查产物。这是工程 smoke path，不是推荐质量
benchmark。

实时 planning 和 judgement 需要显式配置 OpenAI-compatible provider。请参阅
[`docs/provider-configuration.md`](docs/provider-configuration.md) 中的本地配置
说明。不要提交或粘贴 provider 凭据。

## 示例场景

> “我想做一个更好的 frontend/UI 原型，但我不懂设计，也不知道该怎样描述
> 自己想要什么。”

在当前实现层面，D001 的流程是：

```text
能力缺口
  -> 设计 framing 与 UI 决策支持
介入面
  -> Skill
候选发现
  -> 能力候选
证据
  -> 候选正文 + 检索证据 + 明确的 provenance 缺口
Judge
  -> 运行时已实现；provider-backed 验证进行中
```

这里不会虚构某个推荐结果。D001 是有边界的设计探针，不是写死的答案。详见
[`docs/golden-cases.md`](docs/golden-cases.md)。

## 产品原则

> **最小的有效介入优先。**

> **不介入也是合法结果。**

> **先有证据，再给建议。**

## North Star

SkillNudge 现在从能力介入建议工具开始。

更长期的方向可以分成三层：

```text
Capability Control Plane
  -> Eval / Utility Layer
  -> Capability Evolution Loop
```

长期问题不只是“我应该使用哪个 Skill”，还包括：

> **这个能力在当前模型、当前 harness、当前任务上，是否仍然有帮助？**

完整方向见 [North Star](docs/north-star.md)。这不代表 Eval 或能力演化今天已经
实现。

## 当前状态

### 当前可用

- Capability Framing
- Intervention Planning
- Query Planning
- 本地 SQLite FTS5 / BM25 检索
- Evidence Hydration
- 可观察的 Runtime Trace
- Candidate Judgement 与最小 Final Advice 运行时代码

### 正在进行

- Candidate Judgement 与 Final Advice 的 provider-backed 验证
- 当前 Week 1 advisor loop 的完成复核

### 尚未提供

- 打包后的生产 CLI
- 自动安装
- Utility 评估与 Skill Utility Drift 检测
- 能力演化
- Review、Grow、Watch

当前仓库是早期实现基线，还不是完整产品，也不是产品质量 benchmark。

## 文档

四个入口覆盖主要项目背景：

- [North Star](docs/north-star.md)
- [Architecture & Runtime](docs/architecture.md)
- [Contracts](docs/contracts/README.md)
- [Research](docs/research/README.md)

[浏览全部文档](docs/)。

## Roadmap

### Now

能力介入：

```text
understand -> discover -> judge -> advise
```

### Next

测量介入是否真的改善了下游任务轨迹。

### Later

检测 Skill Utility Drift，并评估是否需要演化、压缩、替换或退役某种能力。

这些是方向阶段，不是已经完成的功能。

## 参与贡献

SkillNudge 仍处于早期开源阶段。提交变更前，请先阅读当前文档，并明确区分已实现
行为和提议行为。

欢迎范围窄、可以证伪、尊重证据与不确定性，并且符合本地优先 Week 1 边界的贡献。

本地验证：

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m compileall -q src scripts
git diff --check
./scripts/check_publish_gate.sh
```

## 许可证

SkillNudge 使用 [MIT License](LICENSE) 发布。
