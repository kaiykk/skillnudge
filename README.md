# SkillNudge

SkillNudge turns a real Agent failure and user feedback into one reviewable
Skill candidate without changing the active Skill.

## Quick Improve

Give the command a Skill and the observable failure/correction:

```bash
skillnudge quick-improve \
  --skill ./SKILL.md \
  --failure "The agent omitted the requested output wrapper." \
  --feedback "Keep the exact wrapper requested by the user."
```

This first call returns a bounded request for the Host Agent's improvement
method. The Host Agent diagnoses one failure and proposes one targeted edit.
It can return that proposal through `--proposal-json` (or a configured
`--proposer-command`):

```json
{
  "diagnosis": "The Skill does not encode the output boundary.",
  "change_summary": "Add one instruction to preserve the requested wrapper.",
  "candidate_content": "...candidate SKILL.md content...",
  "validation_status": "UNVERIFIED",
  "validation_basis": "No independent validation was run."
}
```

For the local Codex Host, use the included thin adapter so the request and
response stay inside one process boundary:

```bash
skillnudge quick-improve \
  --skill ./SKILL.md \
  --failure "The agent omitted the requested output wrapper." \
  --feedback "Keep the exact wrapper requested by the user." \
  --proposer-command "python scripts/codex_quick_improve.py"
```

SkillNudge then prints the unified diff and writes a pending candidate bundle:
`proposed_SKILL.md`, `diff.patch`, `manifest.json`, and `provenance.json`.
The source file is never overwritten. Validation is `UNVERIFIED` unless the
Host Agent supplies a truthful, explicit validation result, and no candidate
is activated automatically.

## Product Boundary

The semantic method stays with the Host Agent. SkillNudge owns the small,
deterministic boundary around it:

- Skill identity, content hash, and parent version.
- Observable Session/feedback references.
- One bounded candidate and a readable diff.
- Candidate staging and the Human `PENDING` decision boundary.

The implementation reuses the useful ideas, rather than copying runtimes:
Skill Conductor's diagnose-before-edit and evidence-bearing improvement flow,
Darwin's one-edit-at-a-time Human checkpoint, and the existing SkillOpt-Sleep
handoff/provenance format. The local `conductor` plugin is an unrelated SEO
MCP and is not used as a Skill evolution engine. Full History Evolution,
automatic evaluation, activation, and external operator integrations remain
out of scope.
