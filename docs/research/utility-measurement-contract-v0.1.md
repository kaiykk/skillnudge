# Utility Measurement Contract v0.1

**Status:** RESEARCH DESIGN / NOT PHASE 2 IMPLEMENTATION AUTHORIZATION
**Date:** 2026-09-19
**Scope:** Utility evidence, interpretation, and lifecycle decision support

This document defines the minimum evidence contract for the first SkillNudge
Phase 2 utility experiment.

The first experiment compares:

```text
Control:
  No Skill

Treatment:
  Original Systematic Debugging Skill
```

This is a research evidence contract. It is not:

- a runtime or API contract;
- a benchmark runner specification;
- a universal Skill score;
- an automatic promotion or retirement policy;
- permission to implement Phase 2 runtime;
- permission to execute the benchmark.

The contract must remain compatible with the existing research design reviews:

- North Star Gate v0.1;
- Skill Utility Drift Experiment Card v0.2;
- Skill Artifact Selection Review v0.2;
- Dataset Artifact Selection Review v0.2;
- Task Slice Selection Protocol v0.1;
- Model/Harness Freeze Review v0.1.

---

## 1. Purpose and North Star Alignment

### 1.1 North Star question

SkillNudge is a Capability Lifecycle Control Plane. Its core question is:

> When should an external capability intervention exist?

The first Phase 2 experiment is not intended to build a Skill benchmark or
rank Skills by a single number. It is intended to produce evidence that can
support a bounded lifecycle decision:

```text
KEEP
COMPRESS
MODIFY
REPLACE
RETIRE
```

The relevant causal comparison is:

```text
same model
same harness
same tools
same task
same environment
same evaluator

No Skill
vs
Original Systematic Debugging Skill
```

The evidence must explain not only whether the result changed, but also how
the visible trajectory changed, what cost was introduced, whether harm was
created, and whether the effect transfers beyond the development examples.

### 1.2 What this contract prevents

This contract prevents the following substitutions:

```text
benchmark rank             for intervention utility
one successful run          for repeatable evidence
final answer quality       for trajectory understanding
model confidence           for verified outcome
more steps                 for better reasoning
lower cost                 for better utility
retrieval relevance        for lifecycle value
hidden reasoning claims    for observable evidence
```

It also keeps protocol failure separate from Skill failure. If the treatment
and control do not receive comparable execution conditions, the result is not
evidence that the Skill helps, is neutral, or hurts.

### 1.3 Scope of a conclusion

Every utility conclusion must name its evidence scope:

```text
model
harness
tool surface
provider configuration
task family
repository scope
environment
Skill revision
evaluation window
```

No result from the first task slice should be presented as a universal claim
about all models, harnesses, repositories, or future Skill versions.

### 1.4 Evidence chain

The required reasoning chain is:

```text
intervention
    -> observable trajectory
    -> verified outcome
    -> cost and risk profile
    -> diagnosis
    -> lifecycle decision
```

The chain is incomplete when any of the following is missing:

- a valid No Skill comparison;
- a verifiable task oracle;
- an observable trajectory;
- a diagnosis of a non-neutral result;
- enough valid evidence to distinguish noise from a meaningful pattern;
- transfer evidence when the proposed decision exceeds the development scope.

---

## 2. Utility Definition

### 2.1 Utility is multidimensional evidence

Skill Utility is not a single scalar. It is the set of evidence showing how
an external capability intervention changes outcomes, observable work,
resource use, risk, and transfer under a declared experimental scope.

For this experiment:

```text
utility(intervention) =
  outcome evidence
  + trajectory evidence
  + cost evidence
  + risk evidence
  + transfer evidence
```

The plus signs mean that the dimensions must be considered together. They do
not define an additive formula and must not be converted into an arbitrary
universal score.

An intervention may:

- improve outcome while increasing cost;
- preserve outcome while reducing wasted work;
- improve difficult task families while adding overhead on simple tasks;
- create no measurable outcome change but expose a useful diagnostic pattern;
- harm one task family while helping another;
- appear neutral because the baseline already reaches a ceiling;
- appear harmful because the task or environment is invalid.

The evidence record must preserve these distinctions.

### 2.2 Outcome Utility

**Question:**

> Did the intervention improve the verified task result?

Possible observable dimensions:

- target acceptance checks;
- required regression checks;
- patch correctness;
- behavioral constraint compliance;
- evaluator validity;
- transfer-task success;
- preservation of source behavior.

Outcome Utility is not established by a plausible patch, a confident answer,
or one visible test. Primary success requires a valid oracle and the declared
acceptance conditions.

### 2.3 Trajectory Utility

**Question:**

> Did the intervention improve the observable way the agent reached the result?

Possible observable dimensions:

- earlier localization of the relevant fault region;
- more useful hypothesis and test transitions when the agent emits them;
- fewer repeated failed edits;
- better target and regression verification;
- more effective recovery after a failed attempt;
- fewer low-value exploration actions;
- more direct movement from evidence to a verified patch.

Trajectory Utility must be based on actions, tool calls, emitted summaries,
tests, edits, failures, and other observable events. It must not claim access
to hidden chain-of-thought.

A longer trajectory can be better if it contains productive investigation. A
shorter trajectory can be worse if it skips verification or introduces a
regression.

### 2.4 Cost Utility

**Question:**

> What additional resources did the intervention consume, and was that cost
> justified by the observed result?

Possible observable dimensions:

- model output tokens;
- input or context tokens when available;
- agent steps;
- tool calls;
- wall-clock time;
- provider cost when reliably available;
- retries;
- patch revisions;
- files touched;
- context overhead introduced by the Skill.

Cost Utility must be reported alongside outcome and risk. Lower cost alone is
not utility if it comes from an invalid or under-verified result.

### 2.5 Risk Utility

**Question:**

> Did the intervention introduce harmful or unsafe behavior?

Possible observable dimensions:

- regression introduction;
- unnecessary procedure execution;
- over-engineering;
- excessive repository exploration;
- repeated edits after adequate evidence was available;
- failure to stop when the task was solved;
- tool misuse;
- violation of task constraints;
- increased sensitivity to irrelevant instructions;
- patch growth without corresponding outcome benefit.

Risk is not the same as raw step count. The review must distinguish productive
investigation from wasteful procedure overhead.

### 2.6 Transfer Utility

**Question:**

> Does the observed capability effect generalize beyond the examples used to
> develop or inspect the intervention?

Possible observable dimensions:

- held-out task success;
- held-out regression safety;
- transfer across debugging families;
- transfer across repositories;
- transfer across issue shapes;
- consistency of trajectory changes;
- preservation of neutral or low-sensitivity cases;
- absence of a newly introduced failure mode.

Transfer evidence is required before a development result is treated as a
promotion or broad retention decision. A development-only effect is evidence
for further research, not proof of general utility.

### 2.7 Neutrality and inconclusiveness

The following are distinct:

```text
SKILL_NEUTRAL:
  a valid comparison found no material benefit or harm within scope

INCONCLUSIVE:
  evidence is insufficient to distinguish benefit, neutrality, harm, or
  protocol failure

PROTOCOL_FAILURE:
  the comparison conditions or evaluator were invalid
```

Missing evidence must not be silently converted into `SKILL_NEUTRAL`.

---

## 3. Evidence Model

### 3.1 Evidence units

The minimum evidence unit is a valid paired task comparison:

```text
same task
same repository snapshot
same model and provider configuration
same harness
same tool surface
same evaluator
same budget and retry policy

No Skill run
paired with
Original Skill run
```

The full evidence set is organized at several levels:

| Unit | Purpose |
| --- | --- |
| Task | Defines the requested debugging problem and acceptance condition |
| Run | Records one execution under one condition |
| Pair | Compares No Skill and Original Skill on the same task and protocol |
| Task family | Tests whether an effect is limited to a debugging pattern |
| Experiment | Aggregates valid pairs under one frozen environment |
| Lifecycle review | Converts scoped evidence into a keep, change, or retirement decision |

One run cannot replace a paired comparison. One pair cannot support an
unscoped universal claim.

### 3.2 Evidence artifacts

The experiment should preserve the following artifacts:

```text
Task Artifact
    describes the task, repository snapshot, inputs, and oracle

Trace Artifact
    records observable model turns, tool calls, edits, tests, failures,
    recoveries, termination, and resource usage

Oracle Artifact
    records task acceptance, regression checks, constraints, and evaluator
    validity

Diagnostic Artifact
    records the observable failure or success mechanism and its evidence

Evolution Decision Evidence
    records the lifecycle action supported by the scoped evidence
```

These artifacts are related but not interchangeable. A trace does not prove
success. An oracle does not explain why success occurred. A diagnosis does
not establish transfer. A decision record must preserve the evidence scope.

### 3.3 Directly observable data

Direct data is recorded from the run or oracle without an interpretive claim:

- condition: No Skill or Original Skill;
- task and repository identifiers;
- model, harness, tool, and environment identities;
- Skill source revision and content hash for treatment;
- task input and agent-visible context;
- model turns and tool calls;
- files read, edited, created, or deleted;
- shell commands and exit results;
- tests invoked and reported results;
- patch or final artifact;
- termination reason;
- step, tool-call, token, retry, and wall-clock counts;
- target test result;
- regression test result;
- constraint checks;
- evaluator validity;
- human intervention record;
- protocol deviation record.

Direct data must remain distinguishable from analyst interpretation.

### 3.4 Diagnostic evidence

Diagnostic evidence is an explicit interpretation grounded in direct
observations. Every diagnostic claim should point to the relevant observable
events, such as:

```text
event range or trace reference
observed behavior
diagnostic category
why the evidence supports the category
alternative explanations considered
```

Diagnostics may use agent-emitted summaries, hypotheses, or explanations only
as observable outputs. They must not reconstruct or request hidden reasoning.

### 3.5 Validity evidence

Before interpreting utility, the review must report:

- valid runs by condition;
- paired task coverage;
- environment failures;
- evaluator failures;
- protocol deviations;
- missing trace fields;
- missing oracle fields;
- invalid or excluded tasks;
- incomplete runs;
- provider or transport failures.

Validity failures are findings about experiment readiness. They are not Skill
failures.

### 3.6 Research review record

The following is an illustrative review shape, not a runtime schema and not a
scoring formula:

```yaml
utility_review:
  scope:
    model:
    harness:
    tools:
    environment:
    task_family:
    skill_revision:
    evaluation_window:
  validity:
    paired_comparison:
    oracle_valid:
    trace_sufficient:
    protocol_deviations:
    environment_failures:
  outcome_evidence:
    control:
    treatment:
    paired_changes:
    regression_safety:
  trajectory_evidence:
    helpful_changes:
    harmful_changes:
    uncertainty:
  cost_evidence:
    control:
    treatment:
    tradeoffs:
  risk_evidence:
    observed_harms:
    protected_behaviors:
  transfer_evidence:
    development:
    held_out:
    scope_limit:
  diagnosis:
    categories:
    evidence_refs:
    alternative_explanations:
  lifecycle_decision:
  decision_scope:
  evidence_gaps:
```

Empty or unknown fields must remain explicit. They must not be filled with
assumptions merely to complete the record.

---

## 4. Metric Taxonomy

### 4.1 Direct metrics

Direct metrics are automatically measurable or directly extractable from
declared run and oracle artifacts.

#### Outcome metrics

- target test pass/fail;
- regression test pass/fail;
- patch accepted/rejected;
- task success/failure/invalid;
- constraint check pass/fail;
- evaluator validity;
- held-out task result.

#### Process and cost metrics

- agent steps;
- model turns;
- tool calls;
- shell commands;
- test invocations;
- retries;
- wall-clock time;
- model output tokens;
- context or input tokens when available;
- provider usage and cost when available;
- files touched;
- patch size;
- reverted edits;
- human interventions.

#### Risk and protocol metrics

- destructive or disallowed command attempts;
- regression introduction;
- timeout;
- budget exhaustion;
- missing verification;
- evaluator failure;
- environment failure;
- protocol deviation;
- information leakage;
- termination reason.

Direct metrics are necessary but not sufficient. A lower tool-call count does
not prove better debugging, and a higher test count does not prove productive
verification.

### 4.2 Diagnostic metrics

Diagnostic metrics require trace analysis. They should be reported as
evidence-backed categories, not collapsed into arbitrary points.

#### Localization

```text
correct localization
wrong localization
late localization
localization not observable
```

Evidence may include the files or symbols inspected, the first relevant
failure interpretation, the patch location, and the subsequent verification
result.

#### Hypothesis formation

```text
useful hypothesis emitted and tested
hypothesis changed after disconfirming evidence
unsupported hypothesis persisted
no observable hypothesis
```

Only hypotheses that the agent actually emits or operationalizes are
observable. Hidden internal reasoning is excluded.

#### Verification discipline

```text
target behavior verified
regression behavior verified
verification delayed but completed
verification missing
verification contradicted by result
```

#### Recovery

```text
failed edit followed by evidence-based correction
repeated failure without strategy change
rollback after a harmful change
stalled or budget-exhausted recovery
```

#### Exploration efficiency

```text
productive exploration
repeated low-value exploration
unnecessary procedure overhead
insufficient investigation
```

Exploration must be interpreted against task difficulty and outcome. The same
number of repository reads can be productive for a cross-component bug and
wasteful for a direct assertion failure.

#### Intervention interaction

When observable, record:

- whether the Skill's procedure was used;
- which named section or instruction was operationalized;
- whether a section was ignored;
- whether the intervention caused a strategy change;
- whether the intervention created a conflict with task evidence;
- whether the intervention was redundant with the baseline behavior.

This does not require private reasoning access. It requires only visible
actions and outputs that can be tied to the version-pinned intervention.

### 4.3 Invalid evidence

The following cannot prove utility by themselves:

| Invalid evidence | Why it is insufficient |
| --- | --- |
| One successful treatment run | Could be luck, task artifact, or environment state |
| Final answer quality only | Does not show outcome validity, trajectory, cost, or mechanism |
| Benchmark rank | Compares systems without isolating the intervention |
| Model confidence | Confidence is not an oracle and may be miscalibrated |
| Hidden chain-of-thought | It is not an allowed observable evidence source |
| More reasoning steps | Extra work may be productive or wasteful |
| Fewer tokens | Short output may omit investigation or verification |
| Prompt adherence alone | Following the Skill does not prove it improved the task |
| A plausible patch | Plausibility is not acceptance or regression safety |
| One visible test | Does not establish complete task correctness |
| Historical trajectory without control | Does not provide a causal counterfactual |
| Different tools or model settings | Confounds intervention with environment |
| Aggregate average without task pairs | Can hide task-family reversal and outliers |
| Development-only success | Does not establish transfer |

Invalid evidence may still be useful as a diagnostic clue. It must not be
presented as lifecycle proof.

### 4.4 No chain-of-thought collection

The experiment must not collect, request, reconstruct, or require hidden
chain-of-thought.

Allowed evidence includes:

- visible model messages;
- declared tool calls and results;
- file and patch changes;
- test and evaluator output;
- explicit short summaries when produced by the agent;
- termination and resource events;
- human-visible corrections or interventions.

The absence of hidden reasoning access is an explicit observation boundary, not
a reason to invent internal-state metrics.

---

## 5. Diagnostic Categories

The initial taxonomy should remain small and reusable:

| Code | Category | Observable interpretation |
| --- | --- | --- |
| `F1` | Wrong localization | The agent focused on the wrong file, symbol, component, or causal region |
| `F2` | Insufficient hypothesis | The agent did not form, revise, or test a useful explanation in observable behavior |
| `F3` | Missing verification | The agent edited or concluded without adequate target or regression checks |
| `F4` | Over-exploration | The agent spent substantial effort on low-value search or investigation |
| `F5` | Regression introduction | The target appeared fixed but required surrounding behavior broke |
| `F6` | Unnecessary procedure overhead | The intervention added steps, context, or tool calls without corresponding benefit |

Multiple categories may apply to one run. A category is not a score and must
not be assigned solely from an aggregate metric.

### 5.1 Skill-attributable versus non-Skill failure

The review must separate:

```text
skill_gap:
  the intervention lacks, misstates, or poorly bounds useful guidance

agent_lapse:
  the intervention contains relevant guidance, but the agent did not follow it

environment:
  provider, permission, dependency, filesystem, network, or tool failure

project_fact:
  a fact specific to one repository, task, path, or dataset

evaluator:
  oracle or evaluation failure

protocol:
  control and treatment were not comparable

unclear:
  evidence is insufficient for attribution
```

Only a well-supported intervention-related diagnosis can support modifying or
retiring the Skill. Environment, evaluator, and protocol failures must be
fixed or excluded before lifecycle interpretation.

### 5.2 Diagnostic evidence requirement

For every non-neutral conclusion, the review must identify:

1. the affected task or task family;
2. the direct observations;
3. the diagnostic category;
4. the alternative explanations considered;
5. why the evidence supports an intervention-related interpretation;
6. the scope in which the diagnosis is valid.

If this chain cannot be produced, classify the result as `INCONCLUSIVE` or
`PROTOCOL_FAILURE`, not as `SKILL_HURTS` or `SKILL_HELPS`.

---

## 6. Lifecycle Decision Rules

These rules guide research review. They are not automatic runtime behavior and
do not publish, promote, modify, or retire a Skill without human review.

### 6.1 General decision preconditions

Before any lifecycle decision other than `INCONCLUSIVE` or `PROTOCOL_FAILURE`,
the evidence should show:

- a valid paired No Skill versus Original Skill comparison;
- a valid oracle for the relevant outcome;
- sufficient valid trials to state the uncertainty;
- observable trajectory evidence for a non-neutral result;
- no unresolved environment or evaluator failure that explains the result;
- a declared scope for the conclusion;
- held-out or transfer evidence when the decision exceeds development scope.

No arbitrary numerical threshold is frozen by this document. "Sufficient",
"meaningful", and "acceptable" must be interpreted against the task slice,
risk tolerance, and declared evaluation design before live results are read.

### 6.2 KEEP

Support `KEEP` when the evidence shows:

- meaningful verified outcome improvement, or a predeclared efficiency
  improvement that preserves the required outcome;
- acceptable additional cost for the tested scope;
- no unacceptable regression, constraint violation, or safety problem;
- a repeatable pattern across valid paired trials or a declared uncertainty
  analysis that supports the conclusion;
- transfer within the scope in which retention is proposed.

`KEEP` means retain the current intervention for the tested model, harness,
task family, environment, and evidence window. It does not mean keep it
globally or forever.

### 6.3 COMPRESS

Support `COMPRESS` when:

- only a named section, step, or instruction contributes to the observed
  benefit;
- the remaining content creates measurable cost or procedure overhead;
- removing or shortening the named content preserves verified outcome and
  regression safety;
- the comparison identifies the removed content as redundant or unnecessary;
- the compressed version is evaluated as a new intervention version.

Compression is not justified by length preference alone. The removed material
must be linked to an observed redundancy or cost mechanism.

### 6.4 MODIFY

Support `MODIFY` when:

- a useful capability effect is visible;
- the current form creates a reproducible, diagnosable failure, ambiguity, or
  unnecessary restriction;
- the proposed change is bounded and preserves the capability hypothesis;
- the change can be versioned and compared against the Original Skill;
- held-out evaluation is planned before treating the change as promoted.

The modification must not be used to retroactively reinterpret the Original
Skill result.

### 6.5 REPLACE

Support `REPLACE` when:

- another bounded intervention addresses the same capability need;
- the alternative produces stronger verified utility, lower material harm, or
  better transfer under comparable conditions;
- the comparison keeps baseline, tool surface, model, harness, and evaluator
  aligned;
- the alternative's provenance and intervention boundary are auditable.

A more popular, newer, or shorter Skill is not automatically a replacement.

### 6.6 RETIRE

Support `RETIRE` within a declared scope when:

- no meaningful utility is observed in a valid comparison, or consistent harm
  persists;
- the result is not explained by environment, evaluator, or protocol failure;
- protected task families and known use cases have been considered;
- better alternatives are absent or have been separately evaluated;
- rollback or reintroduction evidence is preserved.

Retirement from one model, harness, task family, or evidence window is not
global retirement unless broader evidence supports that scope.

### 6.7 INCONCLUSIVE

Use `INCONCLUSIVE` when:

- the task set or valid trial coverage cannot separate effect from noise;
- the trace is insufficient to diagnose the outcome;
- the oracle is incomplete or ambiguous;
- transfer has not been tested for a decision that claims transfer;
- multiple explanations remain equally compatible with the evidence;
- a task family is too insensitive to expose the capability;
- a baseline ceiling or floor prevents meaningful comparison.

`INCONCLUSIVE` is a valid research result. It should lead to a protocol,
task-slice, instrumentation, or readiness correction rather than a forced
lifecycle action.

### 6.8 PROTOCOL_FAILURE

Use `PROTOCOL_FAILURE` when:

- the No Skill and Original Skill arms received different tools, model
  settings, budgets, permissions, or environment state;
- agent-visible task or evaluator information leaked into one arm;
- an evaluator or provider failure invalidated the comparison;
- the Skill payload was not the declared revision;
- human coaching or arm-specific recovery occurred;
- the run cannot be reconstructed sufficiently for comparison.

Protocol failure is preserved for audit and excluded from utility conclusions.

---

## 7. Failure Interpretation

This section prevents common interpretation errors.

### 7.1 Skill improves success rate

Incorrect conclusion:

```text
Skill is useful.
```

Required follow-up:

- Was the improvement verified by the declared oracle?
- Was the control and treatment environment identical?
- Did the Skill increase tokens, steps, tool calls, latency, or patch size?
- Did regression or constraint failures change?
- Did the improvement transfer to held-out tasks?
- Which observable behavior changed?
- Could task selection or baseline variance explain the result?

The correct result may be `KEEP`, `COMPRESS`, `MODIFY`, or `INCONCLUSIVE`.
Success-rate improvement alone does not select the lifecycle action.

### 7.2 Skill does not improve final success

Incorrect conclusion:

```text
Skill is useless.
```

Required follow-up:

- Did the baseline already solve the tasks reliably?
- Were the tasks sensitive to systematic debugging behavior?
- Did the Skill improve localization, recovery, or verification without
  changing the final outcome?
- Did it help only one task family?
- Did cost or risk increase despite unchanged success?
- Was the trace or oracle too incomplete to observe the effect?
- Was the treatment actually inserted at the declared boundary?

The result may be neutral within scope, a compression opportunity, or
inconclusive. It is not automatically `RETIRE`.

### 7.3 Skill increases reasoning or agent steps

Incorrect conclusion:

```text
Skill is harmful.
```

Required follow-up:

- Were the extra steps productive investigation?
- Did they improve localization or verification?
- Did they reduce repeated failed edits?
- Did they introduce unnecessary procedure overhead?
- Did the task require deeper investigation?
- Did the extra work produce a better or safer result?

Step count is a cost signal, not a direct harm label.

### 7.4 Skill is followed but utility is not observed

Following the procedure is not the same as benefiting from it. The review
should distinguish:

```text
procedure followed
    + outcome improved
    + cost acceptable
    -> possible utility

procedure followed
    + outcome unchanged
    + cost increased
    -> possible compression or retirement evidence

procedure not followed
    + outcome failed
    -> agent-lapse or intervention-delivery question, not immediate Skill failure
```

The final diagnosis must remain grounded in visible behavior and verified
outcomes.

### 7.5 Baseline ceiling and task sensitivity

A neutral result may arise because:

- the No Skill baseline already reaches the task ceiling;
- the task has a direct, low-sensitivity failure mode;
- the task slice lacks the failure families targeted by the Skill;
- the model does not use the intervention;
- the intervention is redundant with the model and harness;
- the observed sample is too small.

These explanations require different next actions. The review must not merge
them into one claim that the Skill has no value.

### 7.6 Cost and risk tradeoffs

Every non-neutral outcome must be read as a vector:

```text
outcome
trajectory
cost
risk
transfer
```

Examples:

```text
better success
  + large uncompensated overhead
  -> not automatically KEEP
```

```text
same success
  + better verification
  + lower regression risk
  -> possible KEEP or MODIFY
```

```text
same success
  + repeated unnecessary procedure
  -> possible COMPRESS or RETIRE
```

```text
lower success
  + environment timeout in treatment only
  -> PROTOCOL_FAILURE, not SKILL_HURTS
```

---

## 8. Experiment Readiness Gate

This contract is ready for implementation review only when the following
conditions are explicit and reviewable:

### 8.1 Scope and intervention

- the model, provider, harness, tool surface, and environment are frozen;
- the Original Skill source, revision, file set, license, and hashes are
  recorded;
- the No Skill and Original Skill boundaries are explicit;
- no dynamic routing or treatment-only tool is introduced;
- the task slice and held-out policy are recorded before outcome analysis.

### 8.2 Oracle and outcome

- target acceptance checks are defined;
- regression checks are defined;
- evaluator validity is distinguishable from task failure;
- constraint and safety checks are declared;
- invalid, incomplete, and protocol-failed runs are classified separately.

### 8.3 Trace and observability

- visible model turns and tool calls are captured;
- file and patch changes are reconstructable;
- tests and command results are captured;
- resource and termination events are captured;
- trace capture does not add arm-specific context or tools;
- no hidden chain-of-thought is collected.

### 8.4 Interpretation

- direct metrics and diagnostic metrics remain separate;
- diagnostic categories and attribution labels are defined;
- lifecycle decisions are scoped to the evidence;
- no arbitrary universal score is introduced;
- transfer evidence is required for decisions that claim transfer;
- a process exists for recording alternative explanations and uncertainty.

### 8.5 Gate result

The evidence contract is sufficiently specified for a separate implementation
review when the above conditions are satisfied. Passing this gate does not
authorize benchmark execution, live model runs, or Skill promotion.

---

## 9. Remaining Uncertainties

The following remain open and must not be silently resolved by this document:

1. What exact held-out task count and task-family coverage are sufficient for
   the first transfer claim?
2. Which observable trace events are available in the final Harness without
   changing model context or treatment exposure?
3. How should provider token accounting be normalized across the authorized
   endpoint and any fallback provider?
4. What material cost increase is unacceptable for each task family?
5. Which regression and constraint failures are protected cases for the first
   Systematic Debugging Skill experiment?
6. How should uncertainty be summarized for a small paired task slice without
   overstating population-level conclusions?
7. Which sections of the Original Skill can be isolated for a valid future
   compression experiment?
8. What evidence is needed before comparing a second model or harness?
9. When a Skill helps only a subset of task families, should the decision be
   conditional routing, scoped retention, or a variant experiment?
10. How will evaluator failures and provider failures be surfaced consistently
    in the final run artifacts?

These are experiment-readiness questions. They are not reasons to invent a
runtime architecture in this documentation change.

---

## North Star Alignment Review

```yaml
Lifecycle stage:
  EVALUATE

Research question:
  What evidence is sufficient to decide whether an external capability
  intervention should continue, change, or retire?

Evidence produced:
  - multidimensional utility definition
  - direct metric taxonomy
  - observable diagnostic taxonomy
  - invalid-evidence boundaries
  - lifecycle decision rules
  - failure interpretation rules
  - experiment readiness conditions

Decision enabled:
  KEEP / COMPRESS / MODIFY / REPLACE / RETIRE

Gate:
  CONDITIONAL PASS
```

The gate is conditional because the evidence contract is documented, but the
runtime, final task slice, live provider configuration, trace capture, oracle
implementation, and benchmark execution remain outside this task.

---

## Scope Record

```text
documentation only: yes
runtime changes: no
dependency changes: no
CLI changes: no
Phase 1 changes: no
retrieval changes: no
Judge changes: no
benchmark execution: no
dataset download: no
external repository vendoring: no
```
