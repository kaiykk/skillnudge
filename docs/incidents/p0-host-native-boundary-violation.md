# P0 Host-Native Boundary Violation

**Severity:** P0

**Status:** CLOSED — external native Codex invocation verified

**Closed:** 2026-09-21

**Discovered:** 2026-09-21 through real unrelated-repository dogfood

## Incident

An explicit `$skillnudge` invocation from an unrelated repository failed with
`LIVE_MODEL_PROVIDER_UNAVAILABLE`. The public Codex Skill delegated the request
to `skillnudge advise`, and that standalone application owns its own live-model
calls. A user therefore needed a separate SkillNudge provider credential even
though the host Agent already had a model.

The user-visible failure was not a retrieval failure. It occurred at the
boundary between the public host Skill and the provider-backed standalone
runtime.

## User Impact

The installed SkillNudge product path was not host-native. Installation and
invocation could be blocked by a second provider configuration, which made the
public integration unavailable in an otherwise working Codex session.

## Original Architecture

```text
Codex host model
  -> installed SKILL.md
  -> skillnudge advise
  -> provider-backed Phase 1 Planning
  -> provider-backed Candidate Judgement and Final Advice
  -> advice
```

The standalone path combined semantic planning, deterministic retrieval, and
semantic judgement behind one CLI command. That composition remains useful for
evaluation, regression, CI, and controlled research, but it is not the public
product boundary.

## Root Cause

The public Skill reused the standalone runtime as its normal execution path.
That made the standalone runtime, rather than the host model, the owner of
semantic reasoning.

Contributing factors:

1. Phase 1 algorithm completion was mistaken for product completion.
2. Dogfood packaging optimized reuse of the standalone runtime instead of
   re-evaluating semantic reasoning ownership.
3. The valid local principle "SKILL.md should not duplicate Phase 1 logic" was
   incorrectly extended into "the standalone runtime should remain the
   semantic execution owner."
4. Reviews verified local call-chain correctness but did not verify the
   product's category and execution ownership inside the host Agent ecosystem.

## Corrected Architecture

### SkillNudge Product

1. **Native Decision Protocol**
   - `.agents/skills/skillnudge/SKILL.md`;
   - focused references only if needed;
   - semantic reasoning executed by the host model.
2. **Capability Core**
   - default bootstrap/index;
   - BM25 retrieval and deterministic RRF;
   - evidence hydration;
   - provenance;
   - schemas and validators.
3. **Capability Registry**
   - bundled corpus;
   - metadata;
   - versions;
   - source identity and hashes.
4. **Host Integration**
   - Codex Skill first;
   - other host adapters only as later, explicit work.

### Outside the Product Architecture

**Standalone Eval Adapter**

- explicit provider allowed;
- existing provider-backed `skillnudge advise` remains available;
- intended for evaluation, regression, CI, and research.

The Standalone Eval Adapter is not a second product architecture.

## Native Decision Protocol

The host model owns:

1. capability framing;
2. intervention choice: `search`, `no_intervention`, or `clarify`;
3. query planning when search is required;
4. evaluation of returned Evidence Packs;
5. final recommendation, no-intervention result, or clarification.

The deterministic core owns only:

1. validating the host-produced planning envelope;
2. locating or bootstrapping the default index;
3. BM25, deterministic RRF, and evidence hydration;
4. returning acquisition and Evidence Pack artifacts.

The minimum Native Mode command is:

```text
skillnudge retrieve --stdin
```

It must not instantiate `OpenAICompatibleModel`, read provider credentials, or
perform semantic judgement or final advice.

## Execution Traces

### Incorrect

```text
Codex
  -> SKILL.md
  -> skillnudge advise
  -> SkillNudge provider
  -> planning
  -> retrieval
  -> SkillNudge provider
  -> judgement/final advice
```

### Correct

```text
Codex host model
  -> SKILL.md Native Decision Protocol
  -> host capability framing/intervention/query planning
  -> skillnudge retrieve --stdin
  -> provider-free bootstrap/index/BM25/RRF/evidence hydration
  -> Evidence Packs
  -> host judgement/final advice
  -> user
```

## Remediation

- [x] Record this canonical P0 incident.
- [x] Add the Host-Native Product Invariant to the handbook.
- [x] Add a provider-free `retrieve --stdin` surface.
- [x] Preserve the provider-backed `skillnudge advise` standalone path.
- [x] Update the public Skill to use the Native Decision Protocol.
- [x] Add provider-free core and public-Skill regression guards.
- [x] Run the real unrelated-repository Native Mode vertical slice.
- [x] Review the returned advice and close the P0 after external evidence.

## Regression-Prevention Rules

1. Public Skill integrations must use the host Agent for semantic reasoning.
2. Native product paths must not read or initialize SkillNudge provider
   configuration.
3. Provider-free Capability Core must not import provider-backed runtime
   modules.
4. `skillnudge advise` is explicit standalone/evaluation behavior and must not
   be the normal public Skill path.
5. Native Mode may reuse deterministic retrieval and evidence contracts, but
   it must not silently add a provider, dynamic routing, or a generic host
   framework.
6. Product closure requires unrelated-repository evidence, not only tests or
   installation checks.

## Provider-Free Core Vertical Slice Evidence

**Run date:** 2026-09-21

**Working repository:** a temporary unrelated Git repository under `/tmp`

**Installed Skill:** `/Users/kai/.agents/skills/skillnudge/SKILL.md`

**Installed CLI:** `/Users/kai/.local/bin/skillnudge`
**Provider configuration:** `DEEPSEEK_API_KEY` and all `SKILLNUDGE_MODEL_*`
variables were unset for the native run

The Codex host model produced a valid planning envelope for this request:

> I am starting a small admin dashboard in this unrelated repository and need
> reusable guidance for accessible interaction, responsive layout, and visual
> hierarchy.

The envelope was then passed to the installed provider-free command from the
unrelated repository without `PYTHONPATH`, `--database`, or a SkillNudge-
specific provider credential. The observed trace was:

```text
Codex host model
  -> installed $skillnudge Skill
  -> skillnudge retrieve --stdin
  -> default bootstrap/index
  -> BM25 + RRF
  -> Evidence Hydration
  -> Evidence Packs
  -> Codex host model advice
```

Observed retrieval result:

- mode: `native`;
- provider: `null`;
- candidate acquisition: `ready`;
- hydrated candidates: `10`;
- top candidate: `ui-ux-pro-max`;
- repository: `nextlevelbuilder/ui-ux-pro-max-skill`;
- top candidate fused rank: `1`;
- trace included planning handoff validation, three query executions, RRF
  fusion, and Evidence Hydration.

The host model's bounded interpretation of the returned evidence was:

> **Recommendation:** `ui-ux-pro-max` is the strongest first capability to
> inspect for this dashboard task because its returned description directly
> covers turning vague interface goals into concrete design and implementation
> decisions, and it ranked first across the complementary retrieval views.

This is provider-free core evidence, not proof of the full public Skill path.
The candidate's provenance was `complete_unverified`; this run did not
independently verify the upstream repository contents or license. The later
external reference-host run below supplies the missing public-product
evidence.

## Closure Criteria

The status can become **CLOSED** only when all of these are true:

- this incident is recorded;
- the handbook invariant is present;
- the Native Decision Protocol exists;
- provider-free `skillnudge retrieve --stdin` works;
- the public Skill no longer delegates Native Mode to `skillnudge advise`;
- Native Mode needs no separate LLM credential;
- standalone/evaluation remains available;
- deterministic retrieval/core is reused;
- existing and new tests pass;
- clean installation remains valid;
- an unrelated-repository `$skillnudge` invocation succeeds;
- the host model returns one real advice.

The evidence above satisfies the provider-free core criteria but not the final
two public-product criteria. Those criteria were subsequently satisfied by the
external reference-host run recorded below.

## Final Closure Evidence

**Run date:** 2026-09-21

**Reference host:** Codex reference host, with the installed Skill invoked from
an unrelated repository

**Representative query:** A normal refactor request in the unrelated
repository. The verbatim user prompt was not retained in this repository
artifact, so this record intentionally does not reconstruct or invent it.

**Observed successful trace:**

```text
Codex host model
  -> installed $skillnudge Skill
  -> native contract
  -> provider-free skillnudge retrieve --stdin
  -> default corpus/index
  -> BM25 + RRF
  -> Evidence Hydration
  -> 10 hydrated candidates
  -> host-model judgement
  -> real Final Advice
```

**Provider:** `null`

No separate SkillNudge LLM provider, API key, or provider credential was
required.

**Advice returned:**

- primary recommendation: `regression-tester`;
- optional supporting companion: `code-reviewer`;
- conditional candidate: `playwright-testing`.

This is the required external product evidence for the reference host: the
installed Skill was discovered and explicitly invoked, the provider-free
SkillNudge core executed, and the host model returned real Phase 1 advice.
The P0 incident is therefore CLOSED for the Codex reference host.
