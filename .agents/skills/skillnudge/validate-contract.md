# Native Validate Contract

Validate Mode consumes one `TEST` result from Review Mode and evaluates that
exact intervention on one bounded task. The host owns the two observable task
executions. SkillNudge owns strict contract validation, intervention identity,
parity checks, a deterministic Oracle, pair validity, and persistence.

The input is one JSON object:

```json
{
  "schema_version": "native.validation-envelope.v0",
  "review_result": {
    "schema_version": "native.review-result.v0",
    "experience_id": "exp-001",
    "disposition": "TEST",
    "problem": "Observable behavior requiring validation.",
    "assessment": {
      "impact": "medium",
      "attribution": {"primary": "capability_candidate", "alternatives": ["agent_lapse"]},
      "addressability": "plausible",
      "testability": "testable",
      "uncertainty": ["One episode does not establish reuse."]
    },
    "evidence": {"referenced_event_ids": ["e1"]},
    "intervention_candidate": {
      "title": "Small check scaffold",
      "target_behavior": "Check the prerequisite before acting.",
      "intervention_hypothesis": "The instruction may improve this task.",
      "evidence_refs": ["e1"]
    },
    "provider": null,
    "run_id": "review-run-001",
    "run_dir": "/user-data/review-runs/review-run-001"
  },
  "validation_spec": {
    "frozen_at": "2026-10-05T12:00:00+00:00",
    "task": {
      "task_id": "task-001",
      "description": "Complete one bounded task.",
      "observable_success_condition": "Result field equals true."
    },
    "intervention": {
      "type": "instruction",
      "exact_content": "Check the prerequisite before acting.",
      "sha256": "<sha256 of exact_content>"
    },
    "oracle": {"type": "result_field_equals", "field": "success", "expected": true},
    "execution": {"bounded": true, "mode": "host_observed_arms"}
  },
  "execution": {
    "control": {
      "result": {"success": true},
      "observable_events": [{"event_id": "c1", "kind": "completion", "summary": "...", "source_ref": "..."}],
      "intervention_applied": false,
      "intervention_identity": null,
      "execution_context": {"task_id": "task-001", "reference_host": "Codex", "model": "host-model", "harness_version": "host-v1", "tool_manifest": {}, "execution_budget": {"max_steps": 4}, "environment_hash": "env"},
      "started_at": "2026-10-05T12:01:00+00:00"
    },
    "treatment": {
      "result": {"success": true},
      "observable_events": [{"event_id": "t1", "kind": "completion", "summary": "...", "source_ref": "..."}],
      "intervention_applied": true,
      "intervention_identity": "<same sha256>",
      "execution_context": "<exactly the same object as control>",
      "started_at": "2026-10-05T12:02:00+00:00"
    }
  }
}
```

The specification and Oracle must be frozen before either arm starts. Control
and Treatment must have exactly identical execution context: task, host, model,
harness, tools, budget, and environment. A Treatment identity is the SHA-256
of the exact instruction bytes; Control carries `null`.

`pair_status=VALID` allows the Oracle to return `HELPS`, `NEUTRAL`, `HURTS`, or
`INCONCLUSIVE`. An arm marked `execution_valid=false` yields
`pair_status=INVALID` and `validation_result=NOT_EVALUATED`; it is never weak
utility evidence. The result is scoped to this task/intervention/host/model and
does not establish a reusable capability gap, promotion, or evolution.
