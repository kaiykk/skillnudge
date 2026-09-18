# North Star References

**Status: [RESEARCH BIBLIOGRAPHY]**

This is the canonical bibliography for the SkillNudge North Star. URLs were
checked on 2026-09-18. A verified URL means that the canonical page or
repository resolved during this documentation pass; it does not mean that the
underlying claim has been independently reproduced by SkillNudge.

## Research Map

```text
Agent Skills Primitive
-> Anthropic Agent Skills
-> Agent Skills standard

Skill Evaluation and Evolution
-> Agent Skill Evaluation and Evolution survey
-> SkillOpt
-> Skill Self-Play

Persistent Improvement Evaluation
-> PAST-Bench

Harness Evolution
-> Recursive Harness Self-Improvement
-> ModularRSI

General Self-Improvement Taxonomy
-> Self-Improvements in Modern Agentic Systems survey

Recursive Skill Improvement
-> MetaSkill-Evolve
```

The map is a reading order, not a claim that these projects implement the
same system. It separates the Skill primitive, evaluation, harness evolution,
persistent improvement, and recursive skill evolution layers.

## Source Discipline

Every source is interpreted in three separate ways:

- **SOURCE-SUPPORTED FACT** - what the source itself states or implements;
- **SKILLNUDGE WORKING HYPOTHESIS** - a falsifiable interpretation to test;
- **SKILLNUDGE PRODUCT DECISION** - a local scope or contract choice.

For example:

- Anthropic supports the fact that Skills can package instructions, scripts,
  and resources with progressive disclosure.
- SkillNudge hypothesizes that some cognitive scaffolds will drift toward
  redundancy or harm as models and harnesses improve.
- SkillNudge currently decides that zero intervention is valid.

The external sources do not prove SkillNudge's utility-drift hypotheses.

## Verified Sources

### 1. Anthropic Agent Skills

- **Title:** Equipping agents for the real world with Agent Skills
- **Authors / organization:** Anthropic
- **Date:** 2025-10-16
- **Type:** official engineering blog
- **Canonical identifier:** Anthropic Engineering article
- **Canonical URL:** https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- **Verification status:** verified 2026-09-18
- **Why it matters:** Defines Skills as folders containing instructions,
  scripts, and resources; describes metadata, full-body loading, linked
  resources, progressive disclosure, executable code, and evaluation-first
  authoring.
- **North Star claim supported:** Skills are a capability primitive that can
  package procedural and organizational knowledge, not merely a prompt string.
- **Caution:** This is a vendor engineering article and does not establish
  Skill Utility Drift or a universal Skill evaluation method.

### 2. Anthropic Skills Repository

- **Title:** Skills
- **Authors / organization:** Anthropic
- **Date:** repository state checked 2026-09-18
- **Type:** official GitHub repository
- **Canonical identifier:** `anthropics/skills`
- **Canonical URL:** https://github.com/anthropics/skills
- **Verification status:** verified 2026-09-18
- **Why it matters:** Provides production-oriented examples, `SKILL.md`
  anatomy, templates, a specification directory, and examples spanning
  technical, enterprise, and document workflows.
- **North Star claim supported:** A Skill can be a self-contained package of
  metadata, instructions, scripts, and resources.
- **Caution:** The repository states that some included skills are source
  available rather than open source; inspect each directory and license before
  reuse.

### 3. Agent Skills Standard

- **Title:** Agent Skills
- **Authors / organization:** Agent Skills community
- **Date:** repository state checked 2026-09-18
- **Type:** open specification / GitHub repository
- **Canonical identifier:** `agentskills/agentskills`
- **Canonical URL:** https://github.com/agentskills/agentskills
- **Verification status:** verified 2026-09-18
- **Why it matters:** Specifies a lightweight folder format with `SKILL.md`
  metadata and optional scripts, references, and assets, providing ecosystem
  context for portable capability packages.
- **North Star claim supported:** Capability artifacts can have a portable
  interface separate from any one agent runtime.
- **Caution:** A format standard does not prove that a Skill is useful,
  compatible, safe, or beneficial for a particular model and task.

### 4. OpenAI Agent Architecture Guide

- **Title:** A practical guide to building agents
- **Authors / organization:** OpenAI
- **Date:** 2025 guide; date not re-derived from the PDF during this pass
- **Type:** official guide
- **Canonical identifier:** OpenAI business guide PDF
- **Canonical URL:** https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf
- **Verification status:** verified 2026-09-18
- **Why it matters:** Provides architecture context for agents as model +
  tools + instructions, and discusses workflow execution, tool selection,
  guardrails, and incremental orchestration.
- **North Star claim supported:** Model, tools, instructions, and harness
  behavior are distinct dimensions of an agent capability system.
- **Caution:** This is architecture context only. It is not evidence for Skill
  Utility Drift, Skill evolution, or SkillNudge's product differentiation.

### 5. Recursive Harness Self-Improvement

- **Title:** Recursive Harness Self-Improvement
- **Authors:** Hyunin Lee, Jinglue Xu, Jeffrey Seely, Donghyun Lee, Matei Zaharia, Yujin Tang
- **Date:** 2026-07-17
- **Type:** paper
- **Canonical identifier:** arXiv:2607.15524
- **Canonical URL:** https://arxiv.org/abs/2607.15524
- **Verification status:** verified 2026-09-18
- **Why it matters:** Studies task-specific harness refinement, model-harness
  co-evolution, trace generation, context management, and performance/cost
  trade-offs.
- **North Star claim supported:** Harness-level persistent improvement is a
  legitimate research direction and should be distinguished from model-weight
  updates.
- **Caution:** SkillNudge is not implementing RHI directly. The reported
  experiments are the paper's results and are not SkillNudge evidence.

### 6. ModularRSI

- **Title:** Modular and Generalizable Recursive Harness Self-Improvement
- **Authors:** Siwei Wu, Jincheng Ren, Yizhi Li, Haau-Sing Li, Chengran Yang,
  Yuxuan Zhang, Weicheng Gu, Jian Yang, Riza Batista-Navarro, Chuanyi Zhang,
  Xianglong Liu, Ming Zhou, Bryan Dai, Chenghua Lin
- **Date:** 2026-09-14
- **Type:** paper and GitHub repository
- **Canonical identifier:** arXiv:2609.14857; `IQuestLab/ModularRSI`
- **Canonical URL:** https://arxiv.org/abs/2609.14857
- **Repository URL:** https://github.com/IQuestLab/ModularRSI
- **Verification status:** both URLs verified 2026-09-18
- **Why it matters:** Provides a modular, contrastive, benchmark-disjoint
  approach to harness evolution with restricted module scope and transfer
  evaluation.
- **North Star claim supported:** Future capability evolution should consider
  successful/failed trajectory contrast, modular attribution, benchmark
  separation, and unseen-task transfer.
- **Caution:** The repository is a research implementation with substantial
  infrastructure. Do not import its full harness-evolution scope into Week 1.

### 7. PAST-Bench

- **Title:** PAST-Bench: Benchmarking the Foundations of Recursive
  Self-Improvement in Personal Agents
- **Authors:** Shuhan Xue, Zixin Ding, Yichen Shen, Yinjie Wang, Zhenfei Yin,
  Yingcheng Wu, Yuxin Chen, Mengdi Wang, Ling Yang
- **Date:** 2026-08-04
- **Type:** paper and GitHub benchmark repository
- **Canonical identifier:** arXiv:2608.04003; `Gen-Verse/PAST-Bench`
- **Canonical URL:** https://arxiv.org/abs/2608.04003
- **Repository URL:** https://github.com/Gen-Verse/PAST-Bench
- **Verification status:** both URLs verified 2026-09-18
- **Why it matters:** Tests whether retained experience produces later
  improvement using matched persistence-on/off controls and trace/artifact
  evidence. The public repository describes 26 task families and 204 episodes.
- **North Star claim supported:** Intervention or persistence is not the same
  as demonstrated useful improvement; the pathway must be evaluated and
  attributed.
- **Caution:** Its personal-agent benchmark and infrastructure are not a
  direct SkillNudge benchmark. The repository requires a more substantial
  runtime environment than Week 1.

### 8. Self-Improvements in Modern Agentic Systems

- **Title:** Self-Improvements in Modern Agentic Systems: A Survey
- **Authors:** Zhe Ren, Yimeng Chen, Dandan Guo, Guowei Rong, Tonghui Li,
  R. B. Xiong, Qingfeng Lan, Wenyi Wang, Li Nanbo, Yibo Yang, Mingchen Zhuge,
  Jürgen Schmidhuber
- **Date:** 2026-07-14
- **Type:** paper and survey repository
- **Canonical identifier:** arXiv:2607.13104;
  `selfimproving-agent/awesome-Self-Improving-Agents`
- **Canonical URL:** https://arxiv.org/abs/2607.13104
- **Repository URL:** https://github.com/selfimproving-agent/awesome-Self-Improving-Agents
- **Verification status:** both URLs verified 2026-09-18
- **Why it matters:** Frames an agent as a foundation model coupled with an
  operational scaffold of prompts, memory, tools, and control logic, and
  distinguishes persistent scaffold updates from one-episode correction.
- **North Star claim supported:** Capability lifecycle work should include
  prompts, memory, tools, and control logic, while keeping persistent update
  and evaluation explicit.
- **Caution:** This is a survey and taxonomy, not a SkillNudge implementation
  or proof of the drift hypotheses.

### 9. Agent Skill Evaluation and Evolution

- **Title:** Agent Skill Evaluation and Evolution: Frameworks and Benchmarks
- **Authors:** Kexin Ding, Yang Zhou, Can Jin, Feng Tong, Mu Zhou,
  Dimitris N. Metaxas
- **Date:** 2026-06-09
- **Type:** paper and survey repository
- **Canonical identifier:** arXiv:2606.11435; `Cassie07/AgentSkill_Survey`
- **Canonical URL:** https://arxiv.org/abs/2606.11435
- **Repository URL:** https://github.com/Cassie07/AgentSkill_Survey
- **Verification status:** both URLs verified 2026-09-18
- **Why it matters:** Surveys execution feedback, trajectory distillation,
  compression, reinforcement learning, and skill-centric benchmark
  categories, explicitly emphasizing evaluation-driven Skill evolution.
- **North Star claim supported:** The field treats Skill evaluation and
  evolution as distinct from one-shot Skill creation.
- **Caution:** This is the central survey reference, not independent evidence
  that every listed method works under SkillNudge's target tasks.
- **North Star role:** CORE REFERENCE

### 10. SkillOpt

- **Title:** SkillOpt: Executive Strategy for Self-Evolving Agent Skills
- **Authors:** Yifan Yang, Ziyang Gong, Weiquan Huang, Qihao Yang, Ziwei Zhou,
  Zisu Huang, Yan Li, Xuemei Gao, Qi Dai, Bei Liu, Kai Qiu, Yuqing Yang,
  Dongdong Chen, Xue Yang, Chong Luo
- **Date:** 2026-05-22
- **Type:** paper and GitHub repository
- **Canonical identifier:** arXiv:2605.23904; `microsoft/SkillOpt`
- **Canonical URL:** https://arxiv.org/abs/2605.23904
- **Repository URL:** https://github.com/microsoft/SkillOpt
- **Verification status:** both URLs verified 2026-09-18
- **Why it matters:** Treats Skill text as external state of a frozen agent,
  uses bounded edits, held-out validation, rejected-edit memory, and
  deployable Skill artifacts. The repository also documents the
  SkillOpt-Sleep extension.
- **North Star claim supported:** Capability updates should be evaluation
  gated and should be compared with no-Skill and prior-Skill baselines.
- **Caution:** SkillOpt is a direct neighboring research system, not a
  uniqueness claim for SkillNudge. Its reported metrics and implementation
  behavior require source/version-specific review.
- **North Star role:** CORE REFERENCE

### 11. Skill Self-Play

- **Title:** Skill Self-Play: Pushing the Frontier of LLM Capability with
  Co-Evolving Skills
- **Authors / organization:** Siyuan Huang, Pengyu Cheng, Haotian Liu, Tao
  Chen, Yihao Liu, Jingwei Ni, Shijie Zhou, Ziyi Yang, Gangwei Jiang, Mengyu
  Zhou, Yu Cheng, Xiaoxi Jiang, Guanjun Jiang; Qwen Large Model Application
  Team
- **Date:** 2026-07-24
- **Type:** paper and GitHub repository
- **Canonical identifier:** arXiv:2607.22529; `Qwen-Applications/skill-self-play`
- **Canonical URL:** https://arxiv.org/abs/2607.22529
- **Repository URL:** https://github.com/Qwen-Applications/skill-self-play
- **Verification status:** both URLs verified 2026-09-18
- **Why it matters:** Combines skill-routed task generation, validity checks,
  frontier-based curriculum, and feedback-driven skill refinement, pruning,
  and induction.
- **North Star claim supported:** Skill libraries can participate in a
  feedback and evaluation loop rather than being static prompt bundles.
- **Caution:** The repository focuses on training-time co-evolution and uses
  substantial model-training infrastructure. It is adjacent to, not a
  Week 1 runtime design.
- **North Star role:** ADJACENT / WATCHLIST

### 12. MetaSkill-Evolve

- **Title:** MetaSkill-Evolve: Recursive Self-Improvement of LLM Agents via
  Two-Timescale Meta-Skill Evolution
- **Authors:** Zefeng Wang, Minxi Yan, Jinhe Bi, Sikuan Yan, Volker Tresp,
  Yunpu Ma
- **Date:** 2026-07-06
- **Type:** paper
- **Canonical identifier:** arXiv:2607.05297
- **Canonical URL:** https://arxiv.org/abs/2607.05297
- **Verification status:** paper URL verified 2026-09-18
- **Implementation status:** paper-only; no canonical public implementation URL
  was verified in this pass. `URL_VERIFICATION_PENDING` for any claimed
  implementation repository.
- **Why it matters:** Separates fast task-Skill evolution from slower
  meta-Skill evolution, making the improvement procedure itself an evolvable
  object.
- **North Star claim supported:** Future work may need to distinguish
  capability evolution from evolution of the procedure that performs the
  evolution.
- **Caution:** The reported benchmark improvements are paper results and do
  not establish that recursive evolution is appropriate for SkillNudge's
  product scope.
- **North Star role:** ADJACENT / WATCHLIST

## Proposed SkillNudge Focus

**[WORKING DIFFERENTIATION]**

The sources above increasingly study:

- evolving a known Skill;
- optimizing an agent harness;
- measuring persistent improvement;
- building evolving Skill libraries.

SkillNudge's proposed focus is the lifecycle decision around capability
intervention itself:

```text
Should a capability intervene now?
Did it actually help?
Has its utility drifted?
Which part still contributes?
Should it be compressed, adapted, replaced, or retired?
```

This is a proposed focus, not a claim that no other project studies these
questions.

## Reuse and License Caution

This bibliography records research relevance and URL verification, not blanket
permission to reuse code or Skill content. Before copying code or redistributing
artifacts, inspect the source repository's current license, third-party notices,
dataset terms, and model terms. Papers and repositories may have different
reuse boundaries.
