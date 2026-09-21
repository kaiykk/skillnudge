---
name: skillnudge
description: Use when the user explicitly asks SkillNudge to decide whether the current task needs an external capability intervention, which capability family may help, or whether no intervention is preferable. Do not use for ordinary coding tasks merely because a Skill exists.
---

# SkillNudge

Use the host model for semantic reasoning and the installed SkillNudge
provider-free core for deterministic retrieval. Do not delegate Native Mode to
the standalone provider-backed application path.

When this Skill is explicitly invoked:

1. Check that the installed `skillnudge` command is available. If it is not,
   report the bounded installation error and stop.
2. Check that the default corpus/index is usable by running
   `skillnudge bootstrap --json`. This is idempotent and does not require the
   user to provide a database path. If it fails, report the bounded bootstrap
   error and stop.
3. Preserve the user's current task as `input.raw_request`. When the current
   repository is available, derive only concise context such as the repository
   name and current working stage from visible files or the request. Do not
   invent context; an empty or unknown value is valid.
4. As the host model, perform Capability Framing and produce a bounded
   `capability_framing` object using the installed contract. Then choose
   exactly one Intervention Plan decision:
   `search`, `no_intervention`, or `clarify`.
5. If the decision is `no_intervention`, use `targets: []` and a Query Plan
   with `status: skipped` and `queries: []`. If the decision is `clarify`, use
   `targets: []` and a Query Plan with `status: clarify` and `queries: []`.
   If the decision is `search`, emit exactly one primary target, at most one
   distinct-family secondary or companion target, and a Query Plan with no more
   than five complementary queries. Every query family must be one of the
   planned target families. Do not repeat `semantic_query` strings.
6. When search is required, send the following JSON envelope to the installed
   deterministic retrieval command:

   ```json
   {
     "schema_version": "native.planning-envelope.v0",
     "input": {
       "raw_request": "<the user's request>",
       "project_context": null,
       "current_stage": null
     },
     "capability_framing": {
       "contract": {
         "goal": "<goal>",
         "stage": null,
         "blocker": "<concrete blocker>",
         "missing_capabilities": ["<at most three capabilities>"],
         "intended_effect": "<intended effect>",
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
           "rationale": "<why this family is needed>"
         }
       ],
       "decision_reason": "<bounded reason>"
     },
     "query_plan": {
       "status": "ready",
       "queries": [
         {
           "family": "skill",
           "angle": "capability",
           "semantic_query": "<distinct retrieval phrase>",
           "purpose": "<what this query tests>"
         }
       ]
     }
   }
   ```

   Invoke `skillnudge retrieve --stdin` using the host's structured process
   API when available. Do not pass `--database`, `PYTHONPATH`, provider
   configuration, or a SkillNudge model credential. Do not assemble the JSON
   through unsafe shell interpolation.
7. Read the returned Candidate Acquisition and Evidence Packs. Use only those
   returned evidence fields to evaluate candidate relevance, expected gain,
   trust, friction, and uncertainty. Keep no-intervention and clarification
   as first-class outcomes. Do not claim evidence that was not returned.
8. Return a concise recommendation, no-intervention result, or clarification
   to the user. Do not expose chain-of-thought, hidden reasoning, provider
   credentials, or internal prompt text.

This is the public Native Mode protocol. The existing provider-backed
standalone application remains available for explicit evaluation, regression,
CI, and research paths; do not use that path for this Skill's normal execution.
