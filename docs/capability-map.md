# Capability Map

## Status

- `[FROZEN]` Week 1 / V0 is limited to **Advise**.
- `[FUTURE]` Review, Grow, and Watch are long-term capabilities.
- `[WORKING HYPOTHESIS]` These four capabilities form a useful lifecycle
  boundary without requiring all four in the first release.

## Advise

### Goal

Before the user takes the next action, identify the missing capability, decide
whether intervention is worthwhile, choose the most suitable intervention
surface, and explain the smallest useful option.

### User Problem

The user has a vague task or blockage and cannot tell whether they need a Skill,
Plugin, Tool, Resource, or nothing extra.

### Input

- Raw user request;
- optional project context;
- optional task stage;
- available local candidate sources.

### Output

- Capability framing;
- intervention plan;
- evidence-backed candidate judgement;
- zero to two bounded recommendations;
- readable trace.

### Key Question

> When is an intervention worth adding?

### Example

A user wants a better UI prototype but cannot name the design capability. Advise
should frame the capability first, inspect a small candidate pool, and explain
why a candidate is or is not worth trying.

### V0 Status

`[FROZEN]` This is the only capability in the Week 1 / V0 implementation target.
The runtime is planned, not implemented in this repository.

## Review

### Goal

After an intervention has been used, assess whether it helped the actual task
trajectory.

### User Problem

A Skill or Tool may have been selected and loaded correctly but still fail to
improve the work, or may introduce friction that was not visible beforehand.

### Input

- Advice trace;
- intervention activation and loading events;
- task trajectory;
- user or agent outcome signals;
- project and model context.

### Output

- Post-use utility assessment;
- failure attribution;
- evidence about selection, timing, compatibility, or instruction quality.

### Key Question

> Did this intervention help this task, at this time, in this environment?

### Example

A brainstorming Skill was activated, but the agent still started editing files
before the user had converged. Review would separate selection, trigger timing,
instruction following, and workflow friction.

### V0 Status

`[FUTURE]` Review is outside Week 1 and is not implemented.

## Grow

### Goal

With evidence and user approval, improve a project-local intervention through
optimization, simplification, replay, and evaluation.

### User Problem

A useful intervention may be too broad, too long, stale, or poorly adapted to a
specific project.

### Input

- External Skill or intervention;
- Review evidence;
- replayable traces;
- project constraints;
- user approval.

### Output

- A proposed local Variant or revision;
- comparison evidence;
- an explicit approval decision.

### Key Question

> What is the smallest change that improves utility without adding new
> problems?

### Example

Shorten a Skill, narrow its trigger, or remove a recipe that a newer model
already performs reliably.

### V0 Status

`[FUTURE]` Grow is not a replacement for mature optimization research and is
not implemented.

## Watch

### Goal

Monitor upstream, model, compatibility, and utility changes that may make a
previous intervention stale or harmful.

### User Problem

A Skill that once helped may become redundant after a model upgrade, upstream
change, or project migration.

### Input

- Pinned source and version;
- upstream changes;
- model changes;
- historical Review evidence;
- current project context.

### Output

- A re-evaluation prompt;
- keep, simplify, update, replace, or retire suggestion;
- provenance and freshness notice.

### Key Question

> This intervention used to help. Does it still help now?

### Example

After a model upgrade, Watch flags a long instruction-heavy Skill for a
controlled re-evaluation rather than silently removing it.

### V0 Status

`[FUTURE]` Watch, scheduling, and automatic utility-drift detection are outside
Week 1.
