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

1. Preserve the user's current task as the raw request.
2. Send that request to the installed CLI through stdin:

   ```bash
   printf '%s' '<the current user task>' | skillnudge advise --stdin --trace
   ```

   Replace the placeholder with the actual current task. Prefer the stdin form
   so shell quoting does not alter the request.
3. Report the CLI's actual Final Advice, including `No additional capability
   appears necessary now.` when the runtime returns `no_intervention`.
4. If the CLI fails, report the bounded error and do not invent a Skill
   recommendation.

This adapter is intentionally explicit for the Phase 1.1 dogfood milestone.
It does not install Skills, invoke Phase 2 experiment code, perform dynamic
routing, or access a database path supplied by the user.
