"""Versioned, inspectable prompts for the three planning stages."""

from __future__ import annotations

import json
from typing import Any, Mapping


PROMPT_VERSIONS = {
    "capability": "planning.capability.v0",
    "intervention": "planning.intervention.v0",
    "query": "planning.query.v0",
}


def _json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def capability_prompt(envelope: Mapping[str, Any]) -> str:
    return f"""You are the Capability Framing stage of a planning runtime.

Understand the user's current blockage before deciding whether any intervention
is useful. Diagnose the blockage, not merely the topic. Capabilities must
describe observable behavioral change. Do not prescribe a Skill, plugin, tool,
MCP, bridge, product, or candidate. Do not invent a capability gap: an empty
missing_capabilities list is valid when the current request has no durable
external capability gap.

Return only one JSON object matching this shape. Do not add fields, markdown, or
explanation outside the object:

{{
  "contract": {{
    "goal": "string",
    "stage": "string or null",
    "blocker": "string",
    "missing_capabilities": ["0 to 3 behavioral capability strings"],
    "intended_effect": "string",
    "constraints": ["optional string"],
    "not_needed": ["optional string"],
    "uncertainties": ["optional string"]
  }},
  "confidence": "high | medium | low",
  "clarification_needed": "boolean",
  "clarification_question": "string or null"
}}

If clarification is materially needed before choosing an intervention family,
set clarification_needed to true and provide one concise question. Otherwise
set clarification_needed to false and clarification_question to null.

InputEnvelope:
{_json(envelope)}
"""


def intervention_prompt(capability_result: Mapping[str, Any]) -> str:
    return f"""You are the Intervention Planning stage of a planning runtime.

Decide whether the framed blockage warrants searching and, only at the family
level, where to search. Do not select a concrete candidate or product. Do not
name a Skill, plugin, tool, MCP, bridge, repository, or marketplace entry.
Use at most two distinct families and do not search multiple families merely to
increase recall. Prefer no_intervention when the current agent can answer a
local one-off information request directly. A Skill represents instructions,
procedures, methods, or domain guidance. An integration represents external
systems, runtime behavior, persistent tool access, or an interaction surface.
Plugin, Tool, MCP, and Bridge are all integration at this stage. A resource is
reference, example, catalog, documentation, or inspiration and is normally a
companion.

Return only one JSON object matching this shape:

{{
  "decision": "search | no_intervention | clarify",
  "targets": [
    {{
      "family": "skill | integration | resource",
      "priority": "primary | secondary | companion",
      "rationale": "string"
    }}
  ],
  "decision_reason": "string"
}}

Use targets=[] for no_intervention and clarify. A search decision must have at
least one primary target. Do not emit provider syntax or query strings here.

CapabilityFramingResult:
{_json(capability_result)}
"""


def query_prompt(capability_result: Mapping[str, Any], intervention_plan: Mapping[str, Any]) -> str:
    return f"""You are the Query Planning stage of a planning runtime.

Turn the capability contract and intervention plan into a small set of
complementary semantic search intents. Search the missing capability, blocker,
desired outcome, operation, professional vocabulary, or task stage, not a known
solution. Do not invent or insert product, repository, Skill, plugin, tool, MCP,
bridge, or candidate names. Queries express semantic intent only: do not emit
SQL, FTS MATCH syntax, GitHub syntax, web operators, API parameters, or Top-K.

Use 3-5 queries total when useful, fewer when additional queries would be
redundant. Primary family receives most of the budget. A secondary or companion
family gets queries only when it explores a meaningfully different candidate
space. Resolve an intervention-class uncertainty with clarify rather than by
exploding search breadth.

Return only one JSON object matching this shape:

{{
  "status": "ready | skipped | clarify",
  "queries": [
    {{
      "family": "skill | integration | resource",
      "angle": "capability | problem | outcome | operation | professional_vocabulary | stage",
      "semantic_query": "string",
      "purpose": "string"
    }}
  ]
}}

Use status=clarify and queries=[] when intervention planning requires
clarification. Use status=skipped and queries=[] for no_intervention. Use
status=ready with at least one query only for search.

CapabilityFramingResult:
{_json(capability_result)}

InterventionPlan:
{_json(intervention_plan)}
"""


def repair_prompt(stage: str, original_prompt: str, invalid_response: Any, errors: list[str]) -> str:
    """Ask once for contract repair without changing the semantic task."""

    return f"""The {stage} planning response was not valid JSON for its frozen
contract. Return only a corrected JSON object. Do not add fields, change the
stage's responsibility, invent missing information, or include explanations.

Validation errors:
{json.dumps(errors, ensure_ascii=False)}

Previous response:
{invalid_response}

Original stage instructions:
{original_prompt}
"""
