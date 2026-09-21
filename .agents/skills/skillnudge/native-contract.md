# Native Planning Contract

This is the compact host-facing contract for the provider-free Native Mode
handoff. Python validators remain the enforcement source. The host must emit
only the structures and values documented here.

## Envelope

The JSON envelope has these fields:

| Field | Required | Shape |
| --- | --- | --- |
| `schema_version` | Optional | If present, exactly `native.planning-envelope.v0` |
| `input` | Required | Input object below |
| `capability_framing` | Required | Capability Framing object below |
| `intervention_plan` | Required | Intervention Plan object below |
| `query_plan` | Required | Query Plan object below |

Unknown envelope fields are invalid.

## Input

| Field | Required | Rule |
| --- | --- | --- |
| `raw_request` | Required | Non-empty string; preserve the user's request |
| `project_context` | Optional | Any JSON value; use `null` when unknown |
| `current_stage` | Optional | String or `null` |

Unknown input fields are invalid.

## Capability Framing

`capability_framing` contains:

| Field | Required | Rule |
| --- | --- | --- |
| `contract` | Required | Object described below |
| `confidence` | Required | `high`, `medium`, or `low` |
| `clarification_needed` | Required | Boolean |
| `clarification_question` | Required | String or `null`; non-empty when clarification is needed, otherwise `null` |

`contract` contains:

| Field | Required | Rule |
| --- | --- | --- |
| `goal` | Required | Non-empty string |
| `stage` | Required | String or `null` |
| `blocker` | Required | Non-empty string |
| `missing_capabilities` | Required | List of 0 to 3 non-empty strings |
| `intended_effect` | Required | Non-empty string |
| `constraints` | Optional | List of non-empty strings |
| `not_needed` | Optional | List of non-empty strings |
| `uncertainties` | Optional | List of non-empty strings |

Unknown fields are invalid.

## Intervention Plan

| Field | Required | Rule |
| --- | --- | --- |
| `decision` | Required | `search`, `no_intervention`, or `clarify` |
| `targets` | Required | List with at most 2 target objects |
| `decision_reason` | Required | Non-empty string |

Each target contains:

| Field | Required | Rule |
| --- | --- | --- |
| `family` | Required | `skill`, `integration`, or `resource` |
| `priority` | Required | `primary`, `secondary`, or `companion` |
| `rationale` | Required | Non-empty string |

Additional invariants:

- `no_intervention` and `clarify` require `targets: []`.
- `search` requires exactly one `primary` target.
- Target families must be unique.
- If a second target exists, its priority must be `secondary` or `companion`.

## Query Plan

| Field | Required | Rule |
| --- | --- | --- |
| `status` | Required | `ready`, `skipped`, or `clarify` |
| `queries` | Required | List with at most 5 query objects |

Each query contains:

| Field | Required | Rule |
| --- | --- | --- |
| `family` | Required | `skill`, `integration`, or `resource` |
| `angle` | Required | `capability`, `problem`, `outcome`, `operation`, `professional_vocabulary`, or `stage` |
| `semantic_query` | Required | Non-empty string; do not duplicate another query |
| `purpose` | Required | Non-empty string |

Early-stop and cross-stage invariants:

- `ready` requires at least one query.
- `skipped` and `clarify` require `queries: []`.
- Every query family must exist in `intervention_plan.targets`.
- `no_intervention` requires Query Plan `status: skipped`.
- `clarify` requires Query Plan `status: clarify`.
- `search` must not use Query Plan `status: skipped`; `search -> clarify` is allowed.

## Compact Valid Example

```json
{
  "schema_version": "native.planning-envelope.v0",
  "input": {
    "raw_request": "Find reusable guidance for an accessibility review.",
    "project_context": null,
    "current_stage": "implementation"
  },
  "capability_framing": {
    "contract": {
      "goal": "Improve the accessibility review",
      "stage": "implementation",
      "blocker": "The task needs reusable accessibility guidance.",
      "missing_capabilities": ["accessibility review guidance"],
      "intended_effect": "Make the review steps concrete and repeatable.",
      "constraints": [],
      "not_needed": [],
      "uncertainties": []
    },
    "confidence": "medium",
    "clarification_needed": false,
    "clarification_question": null
  },
  "intervention_plan": {
    "decision": "search",
    "targets": [
      {
        "family": "skill",
        "priority": "primary",
        "rationale": "A reusable skill is the direct capability gap."
      }
    ],
    "decision_reason": "Search the skill family for reusable guidance."
  },
  "query_plan": {
    "status": "ready",
    "queries": [
      {
        "family": "skill",
        "angle": "capability",
        "semantic_query": "accessibility review keyboard focus contrast guidance",
        "purpose": "Find reusable accessibility review guidance."
      },
      {
        "family": "skill",
        "angle": "professional_vocabulary",
        "semantic_query": "WCAG accessibility audit interaction patterns",
        "purpose": "Search using professional accessibility vocabulary."
      }
    ]
  }
}
```

## Validator-Comparison Data

The regression test compares this machine-readable mapping with the exported
enum values used directly by the Python validators.

```json
{
  "capability_framing.confidence": ["high", "low", "medium"],
  "intervention_plan.decision": ["clarify", "no_intervention", "search"],
  "intervention_plan.targets[].family": ["integration", "resource", "skill"],
  "intervention_plan.targets[].priority": ["companion", "primary", "secondary"],
  "query_plan.status": ["clarify", "ready", "skipped"],
  "query_plan.queries[].family": ["integration", "resource", "skill"],
  "query_plan.queries[].angle": ["capability", "operation", "outcome", "problem", "professional_vocabulary", "stage"]
}
```
