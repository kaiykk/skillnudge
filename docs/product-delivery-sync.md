# Product Delivery Sync

This repository is the canonical home for SkillNudge product behavior and
product-facing status. Home Project is the canonical home for governance
research, raw evidence, reviewer receipts and continuity artifacts. The two
repositories are related but are not mirrors.

## Required round header

Every Phase 2+ round must record these fields before work starts:

```yaml
round_id: <stable id>
target_repository: skillnudge | home-project | both
product_behavior_change: YES | NO
product_status_change: YES | NO
implementation_authorized: YES | NO
principal_gate: <receipt or NOT_REQUIRED>
```

`target_repository` is not inferred from the current working directory. The
round packet must name it explicitly.

## Ownership boundary

### SkillNudge repository

Keep only product-owned material here:

- `src/`, CLI and tests;
- product contracts and product-facing phase/status documents;
- README and roadmap statements that a user or contributor needs;
- product implementation receipts and release-facing validation.

### Home Project

Keep governance and research material here:

- DSH raw output and reviewer receipts;
- experiment packets and evidence indexes;
- governance SOPs, OCLA records and OpenSpec continuity;
- hypotheses, bad references and model-track deliberation.

Do not copy the second set wholesale into SkillNudge. Do publish a concise
product-facing status summary when a phase changes.

## End-of-round delivery gate

Before closing a meaningful round, the Manager must produce two separate
receipts when applicable:

1. **Research receipt:** what was observed, what remains uncertain, and the
   evidence boundary. This belongs in Home Project.
2. **Product delivery receipt:** which product files changed, whether runtime
   behavior changed, the commit hash, tests, publish-gate result and push
   result. This belongs in SkillNudge.

No product delivery is complete merely because a research receipt exists. No
research conclusion is complete merely because a README was edited.

## Phase-transition synchronization

When a phase changes, the same round must either update or explicitly verify:

- `docs/current-status.md`;
- `docs/roadmap.md`;
- the relevant README Current Status section;
- `docs/handbook.md` if the active outcome or authority boundary changed.

If product behavior did not change, say so explicitly. A documentation-only
sync is still a valid product commit when it prevents the repository from
reporting a stale phase.

## Pre-push checklist

```text
[ ] The target repository is SkillNudge, not Home Project.
[ ] Product-owned files are listed explicitly.
[ ] Research-only files remain in Home Project.
[ ] Product status distinguishes shipped runtime from research progress.
[ ] No unratified model or reviewer verdict is presented as product behavior.
[ ] Tests and scripts/check_publish_gate.sh pass.
[ ] git status, git log, upstream count and commit hash are recorded.
[ ] git push result is recorded; “Everything up-to-date” is not treated as a
    delivery receipt unless the upstream count was checked first.
```

This gate is a delivery discipline, not a new SkillNudge runtime layer.
