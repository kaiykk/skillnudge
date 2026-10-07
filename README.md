# SkillNudge

SkillNudge is a local-first **control plane for Agent Skill evolution**.

It owns the durable facts around a Skill:

- canonical identity and immutable version lineage;
- explicit evolution requests;
- external operator result import and provenance;
- lifecycle state; and
- Human-controlled activation, rejection, rollback, and retirement.

It does not author or optimize Skills, run its own benchmark framework, make
independent semantic utility judgements, or reimplement an external operator.

## Lifecycle

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

The shared artifact is intentionally small:

```yaml
schema_version: native.capability-artifact.v0
capability_id: stable identifier
version: immutable version
type: instruction
exact_content: exact UTF-8 content
sha256: SHA-256(exact_content)
```

## Operator boundary

| Operator | Owns |
| --- | --- |
| Skill Conductor | Skill creation, review, structure/quality validation, packaging |
| Darwin Skill | bounded interactive improvement, checkpoints, keep/revert |
| Microsoft SkillOpt | trajectory-driven and offline optimization |

SkillNudge is the control plane around these systems. The first integration
target is Skill Conductor; no operator integration is started in Phase 0.

## Current status

Phase 0 repository classification is complete. The repository still contains
the earlier Advisor, retrieval, provider-backed evaluator, Review/Validate,
and WATCH implementations as recoverable legacy material. They are not the new
North Star and are not silently presented as an evolution control plane.

See:

- [Architecture](docs/architecture.md)
- [Lifecycle](docs/lifecycle.md)
- [Operator integrations](docs/operator-integrations.md)
- [Phase 0 classification](docs/product-reset-phase0-20261007.md)
- [Current status](docs/current-status.md)
- [Roadmap](docs/roadmap.md)

## Install and development

```bash
git clone https://github.com/kaiykk/skillnudge.git
cd skillnudge
python3 -m pip install -e .
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m compileall -q src scripts
git diff --check
./scripts/check_publish_gate.sh
```

The legacy CLI remains available during migration for reproducibility. Its
presence does not imply that retrieval, Advisor judgement, WATCH, or provider
experiments are active control-plane responsibilities.

## Product boundary

No automatic promotion, autonomous operator routing, global utility score,
Darwin reimplementation, SkillOpt reimplementation, or new retrieval system is
part of the current milestone. Human Principal authority remains required for
any active Skill mutation.

## License

MIT. See [LICENSE](LICENSE).
