# Final Advice

## Status

**MINIMAL BEHAVIOR DEFINED FOR V0**

This is a behavior boundary, not a new elaborate contract. Candidate judgement
remains the source of truth for candidate-level decisions.

## Input

Final Advice receives `CandidateJudgements` after candidate acquisition and
judgement. It does not treat retrieval order or retrieval cost as a
recommendation decision.

## Output Shape

```yaml
FinalAdvice:
  status:
    recommendation
    | no_intervention
    | insufficient_evidence
    | needs_clarification
    | source_error

  primary:
    optional

  supporting:
    optional

  companion:
    optional

  deferred:
    optional

  uncertainties:
    optional
```

## Rules

- Filter rejected and insufficient candidates.
- Compare viable candidates.
- Produce zero to two primary actions.
- The preferred result has one Primary action.
- The maximum recommendation is Primary plus Supporting.
- Include at most one Companion when it adds distinct support value.
- Mention a Deferred candidate only when the timing distinction is useful.
- Zero recommendations is valid.
- Do not create Top-10 recommendation lists.
- Do not choose a candidate merely because retrieval already paid its cost.

Final Advice must preserve uncertainty, clarification, source error, and
no-intervention as distinct outcomes. It does not add numerical ranking fields
to `CandidateJudgement`.
