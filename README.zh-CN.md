# SkillNudge

SkillNudge 是一个面向 Agent Skill 演化的本地优先 **控制平面**。

它负责持久化 Skill 的：

- canonical identity 和不可变版本 lineage；
- 显式 evolution request；
- 外部 operator 结果导入与 provenance；
- lifecycle state；
- 由 Human 控制的激活、拒绝、回滚和退休。

它不负责 Skill 编写或优化，不拥有自己的 benchmark，不做独立的语义
utility 判断，也不重新实现任何外部 operator。

## 生命周期

```text
REGISTER
  -> ACTIVE SKILL
  -> REQUEST EVOLUTION
  -> SELECT OPERATOR
  -> EXTERNAL OPERATOR RUN
  -> CANDIDATE
  -> REVIEW RESULT / PROVENANCE
  -> HUMAN DECISION
  -> ACTIVATE | REJECT | ROLLBACK | RETIRE
```

共享 artifact 保持最小：

```yaml
schema_version: native.capability-artifact.v0
capability_id: 稳定标识
version: 不可变版本
type: instruction
exact_content: 精确 UTF-8 内容
sha256: exact_content 的 SHA-256
```

## Operator 边界

| Operator | 负责内容 |
| --- | --- |
| Skill Conductor | Skill 创建、review、结构/质量校验、打包 |
| Darwin Skill | 有边界的交互式改进、checkpoint、keep/revert |
| Microsoft SkillOpt | trajectory-driven 和离线优化 |

SkillNudge 是这些系统外部的控制平面。第一集成目标是 Skill Conductor；
Phase 0 不开始任何 operator 集成。

## 当前状态

Phase 0 仓库分类已经完成。仓库中仍保留早期 Advisor、检索、provider
evaluator、Review/Validate 和 WATCH 实现，作为可恢复的 legacy 材料。它们
不是新的 North Star，不能被默认为演化控制平面能力。

参见：

- [架构](docs/architecture.md)
- [生命周期](docs/lifecycle.md)
- [Operator 集成](docs/operator-integrations.md)
- [Phase 0 分类](docs/product-reset-phase0-20261007.md)
- [当前状态](docs/current-status.md)
- [路线图](docs/roadmap.md)

## 安装与开发

```bash
git clone https://github.com/kaiykk/skillnudge.git
cd skillnudge
python3 -m pip install -e .
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m compileall -q src scripts
git diff --check
./scripts/check_publish_gate.sh
```

迁移期间旧 CLI 仍可用于复现历史结果。它的存在不表示检索、Advisor
判断、WATCH 或 provider 实验属于当前 control plane 的职责。

## 产品边界

当前里程碑不包含自动晋升、自动选择 operator、global utility score、
Darwin/SkillOpt 重实现或新的检索系统。任何 active Skill 变更仍必须由
Human Principal 决定。

## License

MIT，见 [LICENSE](LICENSE)。
