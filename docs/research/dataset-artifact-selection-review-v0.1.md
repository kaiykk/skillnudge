# Dataset Artifact Selection Review v0.1

**Status:** RESEARCH REVIEW / NOT A DATASET FREEZE
**Date:** 2026-09-19
**Scope:** Evidence collection and decision support only

This document reviews candidate artifacts for the first SkillNudge Phase 2
utility experiment.

It does not:

- implement an evaluation runtime;
- download or vendor datasets;
- create benchmark code;
- select the final dataset;
- freeze Experiment Card v0.2;
- start Phase 2 coding.

The review is intentionally about artifact suitability, not leaderboard
position.

---

## 1. Decision Context

### Phase 2 research question

> When should an external capability intervention exist?

### Intervention candidate

```text
Systematic Debugging Skill
```

### Intended first comparison

```text
Control:
  Agent without external capability intervention

Treatment:
  Agent with Systematic Debugging Skill
```

The dataset artifact must therefore support more than a final pass rate. It
must make it possible to compare the two conditions on:

- verified task outcome;
- investigation and localization;
- hypothesis formation;
- verification behavior;
- recovery from failed attempts;
- trajectory cost;
- regression or constraint failure;
- reasons for keep, compress, modify, replace, or retire.

### Review boundary

The candidate is not being asked to prove that the Skill is useful. It is being
asked whether it can support a falsifiable intervention comparison.

The review distinguishes three possible artifact roles:

| Role | Meaning |
| --- | --- |
| Task and oracle substrate | Defines the task, environment, acceptance checks, and reproducible success signal |
| Debugging structure | Makes bug type, fault localization, repair precision, or debugging behavior explicit |
| Trajectory diagnostic source | Provides historical action sequences and failure patterns that can inform observation and diagnosis |

No single candidate is assumed to provide all three roles.

---

## 2. Review Method

### Evidence hierarchy

Evidence was checked in this order:

1. official repository or dataset card;
2. official benchmark or maintainer documentation;
3. original paper or official report;
4. adjacent trajectory or evaluation resources;
5. secondary descriptions only to locate a primary source.

Repository README claims are recorded as claims about the artifact. They are
not treated as evidence that the artifact is suitable for SkillNudge.

### Retrieval and availability boundary

The review was performed on 2026-09-19. No dataset was downloaded. Public
availability means that the artifact was visible through its official
repository, dataset host, or paper page at review time. It does not mean that
all environments, task repositories, container images, or historical
dependencies were locally verified.

### Scoring scale

Each dimension is scored from 0 to 5:

```text
0 = absent or unusable for this question
1 = very weak
2 = limited
3 = usable with material caveats
4 = strong with bounded caveats
5 = directly supports the experiment
```

The scores are evidence-organizing aids, not a benchmark leaderboard and not a
mechanical winner selection.

---

## 3. Candidate A: SWE-bench Lite

### 3.1 Artifact identity

| Field | Review |
| --- | --- |
| Name | SWE-bench Lite |
| Repository | [SWE-bench/SWE-bench](https://github.com/SWE-bench/SWE-bench) |
| Dataset artifact | [SWE-bench/SWE-bench_Lite](https://huggingface.co/datasets/SWE-bench/SWE-bench_Lite) |
| Paper | [SWE-bench: Can Language Models Resolve Real-World GitHub Issues?](https://openreview.net/forum?id=VTF8yNQM66) |
| License | Official repository reports MIT. Underlying repository and task contents retain their own provenance and license considerations; verify per task before redistribution. |
| Version / release | Public `SWE-bench_Lite` split; 300 test Issue-Pull Request pairs. No semantic dataset version was identified in the reviewed sources. Pin an immutable dataset revision before use. |
| Maintainer | SWE-bench team, with Princeton and Stanford contributors; the repository lists Carlos E. Jimenez and John Yang as contacts. |
| Availability | Public repository and public Hugging Face dataset. No data download performed in this review. |
| Evidence status | Confirmed for public identity, task count, task family, and official evaluation description. Exact current revision remains to be pinned. |

The official dataset card describes Lite as a 300-instance subset of
SWE-bench, with real GitHub issue and pull-request pairs from popular Python
repositories. The official repository documents Docker-based evaluation and
the `SWE-bench_Lite` dataset alias. [1][2]

### 3.2 Task structure

**Input**

```text
repository identifier
+ base commit
+ GitHub issue title/body
+ repository environment
```

The agent is expected to work from the repository state before the reference
fix. The dataset card exposes fields such as `instance_id`, `repo`,
`base_commit`, `problem_statement`, `version`, `environment_setup_commit`,
`FAIL_TO_PASS`, and `PASS_TO_PASS`.

**Output**

```text
agent-generated repository patch
+ final response or submission status
```

**Environment**

- repository-level Python projects;
- Docker-based evaluation harness;
- task-specific environment setup and version metadata;
- a local or cloud execution environment with substantial storage and CPU
  requirements.

The official repository warns that full evaluation is resource intensive and
that support for ARM64 is experimental. This matters for a small local
experiment because environment failure can be mistaken for intervention
failure.

**Oracle**

The reference pull request contributes:

- `FAIL_TO_PASS`: tests expected to fail before the fix and pass after it;
- `PASS_TO_PASS`: tests expected to remain passing;
- a test patch and evaluation script.

**Evaluation method**

Apply the agent patch to the base repository and run the task's unit-test
evaluation. A successful patch is one that satisfies the defined test
conditions.

Conceptual task unit:

```text
repository + issue
+ agent patch
+ task environment
+ target and regression tests
```

### 3.3 Fit for Skill Utility Experiment

| Dimension | Score | Reason |
| --- | ---: | --- |
| A. Debugging relevance | 4/5 | Real repository issue resolution includes debugging, but also feature work, API changes, refactoring, and repository navigation |
| B. Intervention sensitivity | 4/5 | A systematic procedure could plausibly affect localization, test use, hypothesis checking, and recovery |
| C. Trajectory observability | 2/5 | The artifact defines tasks and oracles, but does not itself provide the No Skill and Skill trajectories; those must be collected separately |
| D. Oracle quality | 4/5 | Task-specific tests and `FAIL_TO_PASS`/`PASS_TO_PASS` provide a useful automated signal, but test mismatch and hidden assumptions remain risks |
| E. Reproducibility | 4/5 | Docker and pinned commits help, but the environment is heavy and local hardware/platform differences remain material |

### 3.4 Bias analysis

Potential ways Lite could mislead SkillNudge:

1. **Repository complexity bias**
   A failure may reflect codebase size, dependency structure, or issue
   ambiguity rather than debugging procedure.
2. **Task-family impurity**
   Not every issue is a debugging task. Some are feature requests,
   maintenance tasks, or broad changes.
3. **Test-oracle mismatch**
   Passing the supplied tests may not prove the intended behavior, while a
   correct patch may fail an overly specific test.
4. **Historical contamination**
   Public issues, patches, and repositories may have been present in model
   training data.
5. **Environment failure**
   Dependency setup, image build, or platform failure may be attributed to the
   Skill unless excluded explicitly.
6. **Lite selection effect**
   The subset is intended to be less costly to evaluate, so its task
   distribution should not be assumed to represent all repository-level
   debugging.

### 3.5 North Star alignment

**Lifecycle stage:**

```text
OBSERVE / DIAGNOSE
```

**Research question:**

Does a repository-level issue-resolution artifact allow SkillNudge to determine
whether Systematic Debugging Skill changes a real task trajectory?

**Baseline support:**

Yes, in principle. The same task snapshot and evaluator can be run under No
Skill and Systematic Debugging Skill. The artifact does not provide this
counterfactual automatically; SkillNudge must create the paired runs.

**Trajectory visibility:**

Partial. The task and final test outcome are visible, but investigation,
hypothesis formation, verification ordering, and recovery are not part of the
dataset artifact. They must be captured by the experiment harness.

**Future evolution:**

Results could support:

- keep the Skill for a bounded task family;
- compress a redundant search or planning section;
- modify verification guidance;
- replace a rigid procedure;
- retire the Skill if it adds cost or harm without outcome gain.

### 3.6 Interim judgment

Lite is a credible repository-level task and oracle substrate, but it is not a
complete utility-evaluation artifact. It is useful as a source of candidate
tasks, not as automatic evidence that a debugging Skill has been evaluated.

---

## 4. Candidate B: SWE-bench Verified

### 4.1 Artifact identity

| Field | Review |
| --- | --- |
| Name | SWE-bench Verified |
| Repository | [SWE-bench/SWE-bench](https://github.com/SWE-bench/SWE-bench) |
| Dataset artifact | [SWE-bench/SWE-bench_Verified](https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified) |
| Paper | Original SWE-bench paper; the Verified subset is documented in the [official OpenAI report](https://openai.com/index/introducing-swe-bench-verified/) rather than a separate peer-reviewed benchmark paper in the sources reviewed |
| License | Official SWE-bench repository reports MIT. Underlying repositories and task artifacts retain their own provenance and license considerations. |
| Version / release | 500 human-validated test Issue-Pull Request pairs. No semantic dataset version was identified in the reviewed sources; pin the dataset revision and task-image revision before use. |
| Maintainer | SWE-bench team in collaboration with OpenAI for the human-validation campaign. |
| Availability | Public GitHub repository, Hugging Face dataset, and Docker-oriented evaluation tooling. No data download performed in this review. |
| Evidence status | Confirmed for public identity, 500-row size, human-validation description, task fields, and unit-test evaluation. Current benchmark-status interpretation requires caution. |

The dataset card identifies Verified as a 500-sample human-validated subset of
the SWE-bench test set. It describes repository issue resolution using the
pre-issue base commit and unit-test verification tied to the reference
solution. [3]

The official validation report says the campaign screened issue
specification, test relevance, and environment problems with professional
software developers. It also states that Verified superseded the original
SWE-bench and Lite test sets at the time of release. [4]

That historical claim should not be read as permanent evidence that Verified
is a current frontier-model measure. Later public discussion and reporting
raise contamination, benchmark aging, and task-quality concerns. For
SkillNudge, this makes Verified useful as a candidate task substrate, but not
as an unquestioned external definition of capability.

### 4.2 Task structure

**Input**

```text
repository identifier
+ base commit
+ issue statement
+ task-specific environment
```

**Output**

```text
agent-generated patch
+ final agent submission
```

**Environment**

- real Python repositories;
- task-specific installation and environment metadata;
- Docker-based evaluation harness;
- official task images or build procedures.

**Oracle**

The dataset card exposes:

- gold patch;
- `FAIL_TO_PASS`;
- `PASS_TO_PASS`;
- test patch;
- evaluation script;
- environment setup commit;
- version and image metadata.

The human-validation process is an additional artifact-quality signal, not a
replacement for running the task oracle.

**Evaluation method**

Run the agent patch against the pinned task environment and execute the
task-specific tests. Record setup failure separately from patch failure.

### 4.3 Fit for Skill Utility Experiment

| Dimension | Score | Reason |
| --- | ---: | --- |
| A. Debugging relevance | 4/5 | Real issue resolution is closer to work performed by a debugging agent than snippet benchmarks, but the set is not debugging-pure |
| B. Intervention sensitivity | 4/5 | A systematic debugging procedure could influence investigation, verification, regression avoidance, and recovery |
| C. Trajectory observability | 2/5 | The artifact is outcome- and task-centered; intervention traces must be generated separately |
| D. Oracle quality | 5/5 | Human screening plus task-specific tests and regression checks make it the strongest of the reviewed repository-level candidates, while not eliminating all oracle risk |
| E. Reproducibility | 4/5 | Public tasks, commits, images, and Docker tooling are strong foundations; full reproduction remains resource intensive and platform-sensitive |

### 4.4 Bias analysis

Potential ways Verified could mislead SkillNudge:

1. **Human validation is not debugging validation**
   Screening for issue clarity and test quality does not prove that the task
   measures systematic debugging rather than general software engineering.
2. **Repository-level confounding**
   Success may depend more on navigation, library knowledge, or codebase
   familiarity than on the intervention.
3. **Contamination and memorization**
   Public issue text, repositories, and patches may be present in training
   data. A high score may reflect recall rather than process quality.
4. **Difficulty distribution**
   Human filtering changes the task distribution. Easier or clearer tasks may
   make treatment effects harder to detect because the baseline already solves
   them.
5. **Binary outcome compression**
   Test pass/fail does not distinguish a disciplined trajectory from a lucky
   patch with blind retries or missing verification.
6. **Benchmark-status drift**
   A dataset accepted as a quality improvement in 2024 may not remain an
   adequate proxy for frontier model capability in 2026.

### 4.5 North Star alignment

**Lifecycle stage:**

```text
OBSERVE / DIAGNOSE
```

**Research question:**

Does a human-screened repository-level task substrate allow SkillNudge to
compare the downstream effect of No Skill versus Systematic Debugging Skill?

**Baseline support:**

Yes. The same task and environment can be paired across control and treatment.
The pairing must be created by SkillNudge, not inferred from leaderboard
results.

**Trajectory visibility:**

Partial. Verified provides a stronger task/oracle boundary than Lite but does
not itself expose the intervention trajectory. A separate trace capture layer
is required.

**Future evolution:**

The resulting evidence could support:

- keep the Skill for task families where it improves verified outcomes;
- compress sections that add steps without improving success;
- modify verification or recovery instructions;
- replace the procedure when it creates over-constraint;
- retire it when held-out utility disappears or harm persists.

### 4.6 Interim judgment

Verified is the strongest reviewed repository-level substrate for a small,
audited utility experiment, but it should be treated as a source of task
artifacts rather than as a ready-made SkillNudge benchmark. The first use
should be a manually selected and independently audited slice, not an
assumption that all 500 tasks are equally suitable.

---

## 5. Candidate C: DebugBench / BugBench Family

Candidate C is a family review, not one stable artifact. The names refer to
different generations and purposes:

1. **DebugBench** is an LLM debugging benchmark described in a 2024 paper.
2. **BugBench** is an older C/C++ bug benchmark suite for evaluating bug
   detection tools.
3. Other bug corpora such as BugsJS, Defects4J, QuixBugs, and newer precise
   debugging benchmarks solve related but different measurement problems.

They must not be merged into one dataset identity without checking the exact
artifact, license, and task protocol.

### 5.1 Artifact identity: DebugBench representative

| Field | Review |
| --- | --- |
| Name | DebugBench: Evaluating Debugging Capability of Large Language Models |
| Repository | No official repository was confirmed from the primary sources inspected in this review. Do not infer a GitHub repository from secondary references. |
| Paper | [arXiv:2401.04621](https://arxiv.org/abs/2401.04621) |
| License | Dataset/artifact license was not confirmed in the sources inspected. The paper being publicly readable does not establish a data redistribution license. |
| Version / release | 4,253 instances described in the paper; no stable public release revision was verified in this review. |
| Maintainer | Paper authors led by Runchu Tian; artifact maintenance status is unresolved. |
| Availability | Paper and benchmark description are public. Dataset and executable benchmark availability remain unresolved without direct artifact verification. No data download performed. |
| Evidence status | Confirmed for paper-level task description and reported scale; unconfirmed for reproducible data package, repository, and license. |

The paper describes 4,253 instances across C++, Java, and Python, with four
major bug categories and 18 minor types. It constructs buggy code by
collecting LeetCode solutions and injecting bugs with GPT-4, followed by
automatic filtering and manual inspection. The paper also reports that
runtime feedback can affect performance and is not always helpful. [5]

### 5.2 Artifact identity: BugBench legacy family

| Field | Review |
| --- | --- |
| Name | BugBench: Benchmarks for Evaluating Bug Detection Tools |
| Repository | Historical source references include a University of Chicago BugBench page; no current artifact identity or maintained canonical repository was frozen in this review. |
| Paper | [BugBench: Benchmarks for Evaluating Bug Detection Tools](https://www.people.cs.uchicago.edu/~shanlu/papers/bugbench.pdf) |
| License | Not confirmed in the reviewed source. |
| Version / release | Historical C/C++ suite; the cited source describes 17 applications. Current reproducible release status is unresolved. |
| Maintainer | Historical research project; current maintainer is unresolved. |
| Availability | Historical descriptions are public; current setup, source snapshots, and license need direct verification. |
| Evidence status | Useful as historical context for real bug programs, not yet a confirmed candidate artifact for SkillNudge. |

BugBench was designed for bug detection tools rather than an agent performing
an issue-resolution trajectory. That distinction is decisive for this review:
bug detection, diagnosis, repair, and repository-level software engineering are
not interchangeable tasks.

### 5.3 Task structure

#### DebugBench

**Input**

```text
buggy code snippet
+ task or test context
+ possibly runtime feedback
```

**Output**

```text
corrected code or debugging answer
```

**Environment**

- C++, Java, and Python execution settings;
- snippet-level or problem-level runtime;
- exact packaging and environment reproducibility not confirmed here.

**Oracle**

The paper reports pass-rate evaluation and compares debugging performance by
bug category and language. The exact public test harness, hidden tests, and
artifact-level oracle need direct inspection before use.

**Evaluation method**

Run the model or agent on the buggy instance and check whether the resulting
code passes the task tests. Runtime feedback may be exposed or withheld as an
experimental condition.

#### BugBench

**Input**

```text
buggy C/C++ application or known defect
+ detection or analysis task
```

**Output**

Depending on the benchmark version, the output is a detected bug report,
diagnostic result, or tool finding. A repository patch and a debugging
trajectory are not guaranteed.

**Environment and oracle**

The historical suite is oriented toward evaluating bug detection tools over
real programs. Its test and ground-truth structure may support fault
detection, but it does not automatically provide a controlled Skill
intervention task with a patch-level success oracle.

### 5.4 Fit for Skill Utility Experiment

| Dimension | Score | Reason |
| --- | ---: | --- |
| A. Debugging relevance | 5/5 | DebugBench directly targets debugging capability; BugBench directly targets bug detection and related analysis |
| B. Intervention sensitivity | 4/5 | A systematic procedure could change diagnosis, hypothesis testing, runtime feedback use, and verification |
| C. Trajectory observability | 1/5 | The benchmark instances do not provide historical agent trajectories; a new harness would still be required |
| D. Oracle quality | 3/5 | Pass-rate and bug-ground-truth signals are promising, but exact artifact-level evaluator, hidden tests, and redistribution status are unresolved |
| E. Reproducibility | 3/5 | Synthetic construction can make task generation repeatable, but public packaging and environment details are not sufficiently confirmed; legacy BugBench adds maintenance risk |

### 5.5 Bias analysis

Potential ways this family could mislead SkillNudge:

1. **Synthetic task distribution**
   DebugBench injects bugs into LeetCode solution snippets. This can measure
   controlled bug-type response without representing repository debugging.
2. **Bug injection artifacts**
   The injected defect may have unnatural locality, wording, or repair
   pattern, making a procedural Skill appear more effective than it is on
   real issues.
3. **Code generation confound**
   Snippet repair can be solved by regenerating a correct answer rather than
   investigating and verifying a fault.
4. **Missing repository navigation**
   A Skill that helps search, localize, and recover across a codebase cannot be
   evaluated fairly on a single snippet.
5. **Feedback-policy confound**
   Runtime feedback may be a stronger treatment than the Skill itself unless
   tool and feedback conditions are fixed.
6. **Artifact availability risk**
   If the dataset, tests, or license cannot be independently verified, a
   paper-level description cannot serve as the experiment substrate.
7. **Legacy BugBench purpose mismatch**
   A bug-detection benchmark may answer whether a tool identifies a defect,
   not whether an agent can carry out a complete debugging trajectory.

### 5.6 North Star alignment

**Lifecycle stage:**

```text
OBSERVE / DIAGNOSE
```

**Research question:**

Does a debugging-focused artifact make the effect of Systematic Debugging Skill
more visible than a general software-engineering benchmark?

**Baseline support:**

Potentially yes for DebugBench, if the public task and evaluator can be
verified. The same buggy instance can be run under No Skill and Skill.
BugBench's baseline support is unresolved because its task may be detection,
not patching.

**Trajectory visibility:**

Weak by default. SkillNudge would need to capture investigation,
hypothesis/testing, and recovery trajectories itself.

**Future evolution:**

If task-level and process-level evidence are available, the family could help
decide whether to:

- retain debugging-specific verification guidance;
- compress generic explanation or planning content;
- replace a rigid procedure with a more local diagnosis strategy;
- retire a procedure that does not change outcomes or creates over-editing.

### 5.7 Interim judgment

DebugBench is the strongest candidate for testing debugging specificity, but it
is not yet a fully verified artifact for this project. Its value is as a
possible complementary slice or diagnostic probe, not as an automatic
replacement for a repository-level task substrate.

---

## 6. Candidate D: Agent Trajectory Datasets

Candidate D is exploratory only. These resources are valuable because they
expose agent behavior, but a historical trajectory corpus is not automatically
a counterfactual intervention dataset.

### 6.1 Concrete artifact D1: SWE-agent trajectories

| Field | Review |
| --- | --- |
| Name | `nebius/SWE-agent-trajectories` |
| Repository | Upstream agent: [SWE-agent/SWE-agent](https://github.com/SWE-agent/SWE-agent); dataset: [Hugging Face dataset](https://huggingface.co/datasets/nebius/SWE-agent-trajectories) |
| Paper | [SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering](https://arxiv.org/abs/2405.15793); dataset documentation also points to Nebius collection reports |
| License | Dataset card reports CC BY 4.0, while each source repository retains its own license. The card also includes a model-license notice for some generated outputs. |
| Version / release | Public train split with 80,036 trajectories at review time; no immutable revision was frozen in this document. |
| Maintainer | Nebius for the trajectory dataset; SWE-agent upstream is maintained by the SWE-agent research project. |
| Availability | Public Hugging Face dataset; approximately 1.11 GB according to the dataset page. No download performed. |
| Evidence status | Confirmed for schema, scale, license statement, and historical outcome fields. Suitability as a counterfactual experiment artifact is not confirmed. |

The dataset card reports trajectories generated by a SWE-agent framework over
GitHub issue-resolution instances, with fields including model name, target
success, trajectory, exit status, generated patch, and evaluation logs. It
also reports aggregate differences in steps, context length, edits, and
correct-step rates between resolved and unresolved trajectories. [6]

### 6.2 Concrete artifact D2: OpenHands trajectories

| Field | Review |
| --- | --- |
| Name | `nebius/SWE-rebench-openhands-trajectories` |
| Repository | Agent framework: [OpenHands/OpenHands](https://github.com/OpenHands/OpenHands); dataset: [Hugging Face dataset](https://huggingface.co/datasets/nebius/SWE-rebench-openhands-trajectories) |
| Paper | Dataset card cites a 2025 Nebius report, [OpenHands Trajectories with Qwen3-Coder-480B-A35B-Instruct](https://nebius.com/blog/posts/openhands-trajectories-with-qwen3-coder-480b) |
| License | Dataset card reports CC BY 4.0; source repositories and task repositories retain their own license obligations. |
| Version / release | Public train split with 67,074 trajectories at review time; trajectories were collected with OpenHands v0.54.0 and Qwen3-Coder-480B-A35B-Instruct according to the dataset card. |
| Maintainer | Nebius for the dataset; OpenHands project for the agent framework. |
| Availability | Public Hugging Face dataset; approximately 2.08 GB according to the dataset page. No download performed. |
| Evidence status | Confirmed for schema, collection configuration, scale, and license statement. It remains an exploratory diagnostic source, not a frozen SkillNudge benchmark. |

The dataset exposes complete multi-turn trajectories with system, assistant,
user, and tool messages, along with tools, model patch, exit status, resolved
indicator, and generated-test fields. This is unusually useful for studying
investigation, tool use, verification, and recovery. [7]

### 6.3 Adjacent diagnostic artifact D3: AgentLens-Bench

AgentLens-Bench is relevant as a trajectory-analysis reference rather than as
the primary task dataset:

| Field | Review |
| --- | --- |
| Name | AgentLens-Bench / `code-agent-state-trajectories` |
| Repository | [Microsoft code-agent-state-trajectories](https://github.com/microsoft/code-agent-state-trajectories) |
| Paper | [AgentLens: Revealing the Lucky Pass Problem in SWE-Agent Evaluation](https://arxiv.org/abs/2605.12925) |
| License | Not confirmed in the sources inspected for this review; check the repository before reuse. |
| Version / release | Paper reports 1,815 annotated trajectories from a larger set of OpenHands runs over 60 SWE-bench Verified tasks. |
| Maintainer | Microsoft research authors and repository maintainers. |
| Availability | Paper states that an anonymized project repository and benchmark are released; exact current repository contents and license require direct inspection. |
| Evidence status | Confirmed for the paper-level trajectory-analysis result; repository and license still require verification. |

The paper is especially relevant to SkillNudge because it argues that binary
test pass/fail can hide “lucky pass” behavior such as regression cycles, blind
retries, missing verification, or disordered exploration and implementation.
It reports a trajectory-level benchmark with quality, waste, divergence, and
process-reference signals. [8]

### 6.4 Task structure

**Input**

Historical trajectory datasets generally contain:

```text
repository issue instance
+ model and scaffold identity
+ agent messages
+ tool calls
+ environment observations
+ final patch
+ historical evaluation result
```

**Output**

```text
trajectory record
+ generated patch
+ exit status
+ historical success or test logs
```

**Environment**

The original collection environment may include:

- a specific agent harness;
- a specific model;
- a particular tool interface;
- a task-repository snapshot;
- a particular evaluation image.

These conditions are part of the data-generating process. They cannot be
silently replaced with SkillNudge's future harness.

**Oracle**

The resources may include target labels, resolved flags, test logs, or
generated-test checks. These are historical outcome records, not a fresh oracle
for a new No Skill versus Skill run.

**Evaluation method**

The primary use in this review is offline trajectory analysis:

- classify investigation and verification behavior;
- identify recovery and waste patterns;
- design process metrics;
- compare historical traces under known but non-counterfactual conditions.

### 6.5 Fit for Skill Utility Experiment

| Dimension | Score | Reason |
| --- | ---: | --- |
| A. Debugging relevance | 3/5 | The tasks are real issue-resolution tasks, but not all trajectories isolate debugging |
| B. Intervention sensitivity | 2/5 | Existing trajectories were generated under different models/scaffolds and do not provide a clean Skill intervention counterfactual |
| C. Trajectory observability | 5/5 | Complete or near-complete action, tool, observation, patch, and evaluation records are the strongest reviewed evidence source for process analysis |
| D. Oracle quality | 4/5 | Historical target and evaluation fields are useful, but their evaluator and collection context must be preserved |
| E. Reproducibility | 2/5 | Large artifacts, model/provider dependence, harness versions, source-repository licenses, and historical environments make exact reproduction difficult |

### 6.6 Bias analysis

Potential ways trajectory resources could mislead SkillNudge:

1. **No counterfactual**
   A historical success under one agent scaffold does not show what would
   happen with the same task and model without the Skill.
2. **Behavior leakage**
   The trajectories may contain the very procedural behavior that a future
   Systematic Debugging Skill would prescribe. Using them to design the Skill
   and evaluate the Skill can create leakage.
3. **Model and harness confounding**
   Differences may be caused by model, prompt, tool interface, or scaffold,
   not by the presence of an external capability.
4. **Selection bias**
   The corpus may overrepresent tasks and runs selected for training or
   successful completion.
5. **Historical evaluator drift**
   Test logs and target labels may reflect an older image, dependency state, or
   test policy.
6. **License and privacy boundaries**
   Source repository license obligations and model-output restrictions may
   differ by task.
7. **Post-hoc diagnosis risk**
   A reviewer may infer a clean reasoning process from a trace that is only a
   record of tool actions and model text.

### 6.7 North Star alignment

**Lifecycle stage:**

```text
OBSERVE / DIAGNOSE
```

**Research question:**

Can trajectory resources help SkillNudge understand why an intervention
changed, failed to change, or harmed an agent trajectory?

**Baseline support:**

Not by themselves. They can support process-metric design and failure
taxonomy, but a new paired No Skill versus Skill run is required for causal
utility evidence.

**Trajectory visibility:**

Strongest of the candidates. They directly expose investigation, hypothesis
proxies, tool usage, verification, retries, and recovery artifacts, subject to
the exact schema and privacy/license boundary.

**Future evolution:**

They can support:

- identifying redundant or harmful Skill sections;
- designing ablations;
- defining recovery and verification metrics;
- diagnosing why a treatment helped or failed;
- deciding whether a procedure should be compressed, modified, or retired.

They should not, by themselves, authorize promotion or retirement.

### 6.8 Interim judgment

Trajectory resources are best treated as diagnostic references and metric-design
inputs. They are not a substitute for a controlled task artifact because they
do not provide the required intervention counterfactual.

---

## 7. Cross-Candidate Comparison

### 7.1 Score matrix

| Candidate | Debugging relevance | Intervention sensitivity | Trajectory observability | Oracle quality | Reproducibility |
| --- | ---: | ---: | ---: | ---: | ---: |
| A. SWE-bench Lite | 4 | 4 | 2 | 4 | 4 |
| B. SWE-bench Verified | 4 | 4 | 2 | 5 | 4 |
| C. DebugBench / BugBench family | 5 | 4 | 1 | 3 | 3 |
| D. Agent trajectory resources | 3 | 2 | 5 | 4 | 2 |

These scores summarize the evidence in this review. They are not additive
utility scores and must not be used to declare a winner.

### 7.2 Structural comparison

| Question | SWE-bench Lite | SWE-bench Verified | DebugBench / BugBench | Trajectory resources |
| --- | --- | --- | --- | --- |
| Real repository context | Strong | Strong | Weak for DebugBench; mixed for BugBench | Strong in source tasks |
| Pure debugging focus | Partial | Partial | Stronger | Partial |
| Fresh control/treatment possible | Yes | Yes | Potentially | No, not from historical data alone |
| Native trajectory data | No | No | No | Yes |
| Automated oracle | Strong but imperfect | Strongest reviewed repository oracle | Promising but artifact status unclear | Historical logs and labels |
| Environment reproducibility | Docker, heavy | Docker, heavy | Unclear or language-specific | Collection environment-specific |
| Good primary artifact? | Possible | Possible with audit | Not yet confirmed | No |
| Good diagnostic supplement? | Yes | Yes | Yes | Yes |

### 7.3 What each candidate can and cannot prove

| Candidate | Can help establish | Cannot establish by itself |
| --- | --- | --- |
| SWE-bench Lite | Whether a Skill changes outcomes on a small real-issue slice | That the Skill is useful for debugging specifically or across models |
| SWE-bench Verified | Whether a Skill changes outcomes on more carefully screened real issues | That a high score reflects process quality, current frontier ability, or low contamination |
| DebugBench / BugBench | Whether a Skill changes performance on controlled or historical bug tasks | That the effect transfers to repository-level agent work |
| Trajectory resources | Which investigation, verification, recovery, and waste signals are observable | A causal No Skill versus Skill utility effect |

---

## 8. North Star Alignment Review

This review is itself an `OBSERVE / DIAGNOSE` research artifact under
[the mandatory North Star Gate](../north-star-gate.md).

### Lifecycle stage

```text
OBSERVE / DIAGNOSE
```

The artifact selection work observes what each candidate can expose and
diagnoses where it would create confounding or evidence gaps.

### Research question

> Does the candidate artifact help determine whether a capability intervention
> should exist, rather than merely whether a benchmark task can be solved?

### Capability decision evidence

The review does not yet decide keep, compress, modify, replace, or retire. It
identifies which candidate can support those decisions and what additional
evidence is required.

The strongest lifecycle use is:

```text
task/oracle substrate
+ controlled No Skill vs Skill runs
+ trajectory observation
+ diagnosis
-> keep / compress / modify / replace / retire evidence
```

### Baseline support

- SWE-bench Lite: supports a paired baseline in principle.
- SWE-bench Verified: supports a paired baseline in principle and has the
  strongest reviewed repository-level oracle.
- DebugBench: potentially supports a paired baseline if the artifact and
  license are verified.
- Trajectory resources: do not provide the counterfactual by themselves.

### Trajectory visibility

- SWE-bench artifacts expose task and evaluation metadata but require new
  trajectory capture.
- DebugBench exposes debugging task structure but not agent process.
- Trajectory resources expose the process but preserve historical confounds.

### Future evolution

The selected research design must allow a result to lead to:

```text
keep
compress
modify
replace
retire
or conditional intervention
```

If a candidate only produces a leaderboard number, it fails the North Star
Gate as a complete Phase 2 artifact.

---

## 9. Recommended Direction

### Current evidence suggests

Current evidence suggests a **two-layer artifact strategy** is stronger than
choosing one unmodified dataset:

1. Use a **small, manually audited repository-level slice derived from the
   SWE-bench Verified task/oracle structure** as the primary task substrate.
2. Use **DebugBench-style bug categories** only as a diagnostic labeling or
   coverage lens, after confirming that any artifact and license are actually
   available.
3. Use **SWE-agent/OpenHands trajectory resources** to design trajectory
   observation fields and failure analysis, not as the causal benchmark itself.

This is a recommended direction, not a final dataset choice.

The reason is structural:

- Verified offers the clearest reviewed path to real repository tasks,
  reproducible environments, and automated acceptance checks;
- DebugBench is more debugging-specific but weaker on repository context,
  trajectory visibility, and artifact verification;
- trajectory datasets are rich in process evidence but lack the clean
  No-Skill counterfactual needed for intervention utility.

The first artifact should therefore probably be a **small derived slice** with
its own audit record, not a blind commitment to all 500 Verified tasks, all
300 Lite tasks, or a large historical trajectory corpus.

### What this direction deliberately does not say

It does not say:

- SWE-bench Verified is the permanent SkillNudge benchmark;
- SWE-bench Lite is invalid;
- DebugBench is inferior as a debugging research benchmark;
- trajectory data should be discarded;
- benchmark leaderboard numbers are sufficient evidence;
- the final task set should be selected before manual inspection.

---

## 10. Remaining Uncertainty

The following questions remain unresolved:

1. Which specific Verified or Lite tasks are genuinely debugging-dominant
   rather than feature, navigation, or general maintenance tasks?
2. Can a small derived slice preserve enough repository and bug-family
   diversity to expose intervention effects?
3. Which test failures are due to environment setup, evaluator mismatch, or
   agent patch behavior?
4. What is the contamination status of candidate tasks for the selected model?
5. Can DebugBench's public data and test oracle be verified, licensed, and
   executed without reconstructing undocumented packaging?
6. Which DebugBench bug categories map to systematic debugging behaviors rather
   than code regeneration?
7. Which trajectory fields are reliable proxies for hypothesis formation when
   the model's internal reasoning is not directly observable?
8. How should tool calls, retries, verification, and recovery be normalized
   across SWE-agent and OpenHands formats?
9. Can historical trajectory outputs be reused for research under the
   per-instance repository and model-license constraints?
10. What minimum repetition and held-out split is needed to separate Skill
    effect from task and model variance?

---

## 11. Additional Evidence Needed Before Freezing Experiment Card v0.2

Before freezing the next experiment card, complete these evidence steps:

1. **Artifact identity lock**
   - choose the exact source artifact or derived slice;
   - record immutable dataset revision;
   - record task repository commits and image revisions;
   - verify maintainer, license, and redistribution boundaries.
2. **Task audit**
   - inspect candidate tasks manually;
   - classify debugging, feature, maintenance, and environment-dominated tasks;
   - remove or separately label tasks with ambiguous acceptance criteria.
3. **Oracle audit**
   - confirm target tests and regression tests;
   - run reference patches or equivalent golden checks;
   - separate setup failures from task failures.
4. **Trajectory protocol**
   - define the minimum observable events for investigation,
     hypothesis/testing, verification, and recovery;
   - define how tool calls and retries are counted;
   - define what remains unknown.
5. **Contamination and leakage review**
   - inspect issue age, public patches, model cutoff assumptions, and possible
     benchmark exposure;
   - prevent trajectory resources from leaking the intervention wording or
     expected strategy into agent prompts.
6. **Paired-run design**
   - freeze the No Skill and Systematic Debugging Skill conditions;
   - hold model, harness, tools, environment, budget, and evaluator constant;
   - define repeated trials and held-out tasks before interpreting results.
7. **Evolution gate**
   - define what evidence would justify keep, compress, modify, replace, or
     retire;
   - define rollback and protected-case rules.

Until these steps are complete, the project should not describe the candidate
as the final Phase 2 dataset or begin Phase 2 coding.

---

## 12. Decision Status

```text
Task:
  Dataset Artifact Selection Review v0.1

Decision:
  research direction recommended

Final dataset frozen:
  no

Dataset downloaded:
  no

Evaluation runtime implemented:
  no

Phase 2 coding started:
  no

Next required step:
  manual artifact and task audit before Experiment Card v0.2 freeze
```

---

## Sources

1. SWE-bench repository and evaluation documentation:
   [github.com/SWE-bench/SWE-bench](https://github.com/SWE-bench/SWE-bench)
2. SWE-bench Lite dataset card:
   [huggingface.co/datasets/SWE-bench/SWE-bench_Lite](https://huggingface.co/datasets/SWE-bench/SWE-bench_Lite)
3. SWE-bench Verified dataset card:
   [huggingface.co/datasets/SWE-bench/SWE-bench_Verified](https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified)
4. OpenAI, “Introducing SWE-bench Verified”:
   [openai.com/index/introducing-swe-bench-verified](https://openai.com/index/introducing-swe-bench-verified/)
5. Tian et al., “DebugBench: Evaluating Debugging Capability of Large Language Models”:
   [arxiv.org/abs/2401.04621](https://arxiv.org/abs/2401.04621)
6. Nebius, `SWE-agent-trajectories` dataset card:
   [huggingface.co/datasets/nebius/SWE-agent-trajectories](https://huggingface.co/datasets/nebius/SWE-agent-trajectories)
7. Nebius, `SWE-rebench-openhands-trajectories` dataset card:
   [huggingface.co/datasets/nebius/SWE-rebench-openhands-trajectories](https://huggingface.co/datasets/nebius/SWE-rebench-openhands-trajectories)
8. Sahoo et al., “AgentLens: Revealing the Lucky Pass Problem in SWE-Agent Evaluation”:
   [arxiv.org/abs/2605.12925](https://arxiv.org/abs/2605.12925)
9. SWE-agent repository:
   [github.com/SWE-agent/SWE-agent](https://github.com/SWE-agent/SWE-agent)
10. OpenHands repository:
    [github.com/OpenHands/OpenHands](https://github.com/OpenHands/OpenHands)
