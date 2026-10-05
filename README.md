<div align="center">
  <p>
    <a href="README.md">English</a>
    ·
    <a href="README.zh-CN.md">简体中文</a>
  </p>
  <p>
    <a href="#quick-start">Quick Start</a>
    ·
    <a href="#why-skillnudge">Why SkillNudge</a>
    ·
    <a href="#north-star">North Star</a>
    ·
    <a href="#docs">Docs</a>
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

<!-- Official SkillNudge hero image. -->
<p align="center">
  <img src="./assets/hero.png" alt="SkillNudge" width="100%">
</p>

SkillNudge is a local-first, evidence-driven capability lifecycle for AI
agents.

It helps answer a question that Skill search alone cannot:

> **What capability is actually missing now — and is adding any intervention
> worth it at all?**

## Why SkillNudge?

### Relevant ≠ Useful

Search can tell you what looks related.

SkillNudge asks a harder question:

> **Will adding this capability actually improve the next trajectory?**

- A relevant Skill may be unnecessary for a stronger model.
- The same capability may help at one task stage and hurt at another.
- The right intervention may be a Plugin, Tool, or resource rather than a Skill.
- Sometimes no intervention is the best answer.

Read the [product thesis](docs/product-thesis.md) for the deeper framing.

## What It Does

### 01 — Understand

Find the capability gap behind a vague request or a blocked task.

### 02 — Discover

Search for the smallest plausible intervention instead of adding more
capability by default.

### 03 — Judge

Separate semantic relevance from expected gain, trust, friction, and stage fit.

### 04 — Advise

Return zero to two bounded recommendations, or explicitly recommend nothing.

These are the target V0 capabilities. The current repository contains the
planning, local retrieval, evidence hydration, Candidate Judgement / Final
Advice runtime surfaces, and a composed development `advise` CLI. Phase 1
release-readiness validation is complete within the current bounded product
envelope.

## Quick Start

### Install for Codex

```bash
git clone https://github.com/kaiykk/skillnudge.git
cd skillnudge
./scripts/install_codex.sh
export PATH="$HOME/.local/bin:$PATH"
```

The installer creates the `skillnudge` command, builds the bundled Phase 1
corpus into a per-user SQLite/FTS5 index, and installs the explicit Codex Skill
at `$HOME/.agents/skills/skillnudge`.

Open any unrelated repository in Codex and invoke:

```text
$skillnudge
```

The Skill passes the current request to the installed Phase 1 runtime. It can
return a recommendation, clarification, source error, insufficient evidence,
or `No additional capability appears necessary now.` The default index lives
outside the current repository and is versioned by the installer bootstrap.

The installed CLI also exposes the bounded commands:

```bash
skillnudge --help
skillnudge bootstrap
skillnudge advise "I want to build a better UI prototype but do not know how to describe it"
skillnudge review --stdin
skillnudge validate --stdin
```

`review --stdin` is the provider-free Native Review MVP. From any unrelated
working directory, the host Agent can submit one real or sanitized observable
experience and receive `TEST`, `WATCH`, `NO_INTERVENTION`, or `INSUFFICIENT`
with event references and explicit uncertainty. Review does not infer hidden
skill consumption or claim intervention effectiveness.

`validate --stdin` consumes one `TEST` result and a frozen Validation Envelope,
then evaluates the same bounded task with and without the exact instruction
intervention. It returns `HELPS`, `NEUTRAL`, `HURTS`, `INCONCLUSIVE`, or
`NOT_EVALUATED` together with `pair_status`. Results are scoped to that task,
host, model, and intervention; they do not promote or rewrite a Skill.

Phase 1 planning and judgement require an explicitly configured
OpenAI-compatible provider through the `SKILLNUDGE_MODEL_*` environment
variables. See [`docs/provider-configuration.md`](docs/provider-configuration.md)
for the provider boundary. Never commit or paste provider credentials.

### Development Tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The repository also provides a clean-install check:

```bash
./scripts/smoke_install_codex.sh
```

## Example Use Case

> “I want to build a good frontend/UI prototype, but I do not understand
> design and do not know how to describe what I want.”

At the current implementation level, the D001 flow is:

```text
Capability gap
  -> design framing and UI decision support
Intervention
  -> Skill
Discovery
  -> candidate capabilities
Evidence
  -> candidate body + retrieval evidence + explicit provenance gaps
Judge
  -> bounded provider-free Native Review / Validate product surface
```

No recommendation is fabricated here. D001 is a bounded design probe, not a
hard-coded answer. See [`docs/golden-cases.md`](docs/golden-cases.md).

## Product Principles

> **The smallest useful intervention wins.**

> **No intervention is a valid outcome.**

> **Evidence before recommendation.**

## North Star

SkillNudge is an evidence-driven capability lifecycle:

```text
ADVISE -> REVIEW -> VALIDATE -> EVOLVE -> VALIDATE AGAIN
       -> PROMOTE / ROLLBACK / RETIRE
```

The current shipped slice ends at bounded REVIEW and VALIDATE. EVOLVE is not
implemented. Read the [North Star](docs/north-star.md) and the
[North Star Experience Reference](docs/north-star-experience.md) for the
canonical product direction and user-facing meaning.

## Current Status

**Product status as of 2026-10-05:** the provider-free Native Review MVP is the
current shipped product outcome, alongside the Phase 1 Native advisor baseline.
From an unrelated working directory, a host Agent can submit one observable
experience to `skillnudge review --stdin` and receive an evidence-referenced
bounded disposition. Phase 3/4 research remains historical input to the product
contract; it did not establish a reusable capability gap or Skill defect. See
[`docs/current-status.md`](docs/current-status.md) and
[`docs/product-delivery-sync.md`](docs/product-delivery-sync.md).

### Working today

- Capability Framing
- Intervention Planning
- Query Planning
- Local SQLite FTS5 / BM25 retrieval
- Evidence Hydration
- Observable runtime traces
- Provider-free Native Review of one observable Agent experience
- Provider-free Native Validate of one bounded TEST candidate
- Composed Phase 1 `advise` development CLI with bounded early stops and resume
- Candidate Judgement and minimal Final Advice runtime code

### Phase 1 status

- Phase 1 D001 / D002 / D003 release-readiness validation is complete

### Research track status

- Phase 2 measurement remains scoped to its tested conditions; no universal
  utility conclusion is established
- Phase 3 diagnosis is complete for the current bounded evidence campaign;
  `reusable_capability_gap=INSUFFICIENT`
- Phase 4A entry hardening is in progress as static contract/readiness work

### Not yet shipped

- Utility evaluation and Skill Utility Drift detection
- Capability evolution
- Multi-experience aggregation and capability-gap registry
- EVOLVE, multi-experience aggregation, capability-gap registry, and Watch
- Phase 4A runtime execution, Variant promotion, or Darwin/SkillOpt evolution

The repository is an early implementation baseline, not a complete product or
a product-quality benchmark.

## Docs

Four entry points cover the main project context:

- [North Star](docs/north-star.md)
- [North Star Experience Reference](docs/north-star-experience.md)
- [Architecture & Runtime](docs/architecture.md)
- [Contracts](docs/contracts/README.md)
- [Research](docs/research/README.md)

[Browse all documentation](docs/).

## Roadmap

### Now

```text
ADVISE -> REVIEW -> VALIDATE
```

The bounded Native Review and Validate MVPs are shipped and scoped to their
observed experience or tested pair.

### Next

Define and implement candidate-only EVOLVE behavior only after the required
product contract and Principal review. It must preserve lineage and use the
existing bounded Validate surface again.

### Later

Validate candidate versions again, then support Human-owned promote, rollback,
or retire decisions and cross-cutting utility-drift observation.

## Contributing

SkillNudge is an early open-source project. Before opening a change, read the
current documentation and keep implemented behavior separate from proposed
behavior.

Good contributions are narrow, falsifiable, evidence-aware, and compatible
with the current bounded product boundary.

For local validation:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m compileall -q src scripts
git diff --check
./scripts/check_publish_gate.sh
```

## License

SkillNudge is released under the [MIT License](LICENSE).
