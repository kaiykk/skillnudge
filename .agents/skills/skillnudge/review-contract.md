# Native Review Contract

Review Mode is a provider-free handoff from the host agent to SkillNudge. The
host performs bounded semantic assessment; SkillNudge validates the envelope,
preserves observable evidence references, and emits a durable result.

The host must send exactly one JSON object with this shape:

```json
{
  "schema_version": "native.review-envelope.v0",
  "experience": {
    "experience_id": "stable-id",
    "source": {"type": "file", "reference": "path:line or event locator"},
    "observable_events": [
      {"event_id": "e1", "kind": "tool_call", "summary": "observable fact", "source_ref": "path:line"}
    ]
  },
  "assessment": {
    "problem": "observable behavior that may be problematic",
    "impact": "low | medium | high | unknown",
    "attribution": {"primary": "agent_lapse | environment | project_fact | capability_candidate | unclear", "alternatives": []},
    "addressability": "plausible | weak | none | unknown",
    "testability": "testable | unclear | not_testable",
    "evidence_refs": ["e1"],
    "uncertainty": ["unresolved point"]
  },
  "intervention_candidate": null,
  "disposition": "TEST | WATCH | NO_INTERVENTION | INSUFFICIENT"
}
```

Rules:

- Every evidence reference must resolve to an event in the same experience.
- There is zero or one intervention candidate, never a portfolio.
- `TEST` and `WATCH` require exactly one candidate. `TEST` additionally
  requires `addressability=plausible` and `testability=testable`.
- `NO_INTERVENTION` and `INSUFFICIENT` require a null candidate.
- Events must contain observable facts and traceable source references.
- Hidden reasoning, chain-of-thought, and private scratchpad fields are not
  accepted. The contract does not claim that a skill was internally consumed.
- `TEST` means “worth validating next”; it does not establish a capability gap,
  skill defect, or intervention effectiveness.

The CLI returns `native.review-result.v0` JSON and writes the envelope, result,
and observable lifecycle trace under the user's SkillNudge data directory.
It never calls a model provider and never imports Home Project state.
