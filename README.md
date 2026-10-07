# SkillNudge

SkillNudge connects real Agent sessions to traceable Skill version evolution.

## Why

Important Skill improvements often begin as a real session, a concrete user
correction, or observable feedback. Without a durable reference to that
session, a later Skill change loses its reason and cannot be reviewed or
reversed.

## What

SkillNudge keeps the smallest control-plane record needed to connect:

- a Skill identity and immutable version;
- observable session evidence and trace references;
- an external evolution operation; and
- a non-active candidate with Human decision authority.

## Core Flow

```text
Agent Session
  -> Feedback / Evidence
  -> Evolution Request
  -> External Evolution Operation
  -> Candidate Version
  -> Human Accept / Reject
```

SkillNudge records identity, lineage, provenance, and decisions. It does not
author or optimize Skills itself.

## Principles

- Evolution starts from real usage.
- Every candidate has provenance.
- Skill versions are immutable.
- Candidate versions never replace the active version automatically.

See [`docs/core-contract.md`](docs/core-contract.md) for the minimal record
boundary.
