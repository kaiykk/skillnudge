---
name: skillnudge
description: Use when the user explicitly asks SkillNudge to decide whether the current task needs an external capability intervention, which capability family may help, or whether no intervention is preferable. Do not use for ordinary coding tasks merely because a Skill exists.
---

# SkillNudge

Use the installed SkillNudge Phase 1 runtime as the source of truth for this
decision. Do not infer a recommendation from the request alone and do not
reimplement Capability Framing, Intervention Planning, Retrieval, Judge, or
Final Advice in this Skill.

When this Skill is explicitly invoked:

1. Check that the installed `skillnudge` command is available. If it is not,
   report the bounded installation error and stop.
2. Check that the default corpus/index is usable by running
   `skillnudge bootstrap --json`. This is idempotent and does not require the
   user to provide a database path. If it fails, report the bounded bootstrap
   error and stop.
3. Preserve the user's current task as the raw request. When the current
   repository is available, derive only concise context such as the repository
   name and current working stage from visible files or the request. Do not
   invent context; an empty or unknown value is valid.
4. Invoke the installed CLI with the raw request on standard input and pass
   `--project-context` and `--current-stage` only when their values are known:

   ```bash
   printf '%s' "$RAW_REQUEST" | skillnudge advise \
     --stdin \
     --project-context "$PROJECT_CONTEXT" \
     --current-stage "$CURRENT_STAGE" \
     --trace
   ```

   Use the host's structured argument or process API when available so neither
   the request nor optional context is assembled through unsafe shell
   interpolation. Omit an optional flag rather than passing a guessed value.
5. Report the CLI's actual Final Advice, including `No additional capability
   appears necessary now.` when the runtime returns `no_intervention`.
6. If the CLI fails, report the bounded error and do not invent a Skill
   recommendation.

This adapter is intentionally explicit for the Phase 1.1 dogfood milestone.
It does not install Skills, invoke Phase 2 experiment code, perform dynamic
routing, or access a database path supplied by the user.
