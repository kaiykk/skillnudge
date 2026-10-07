# Core Contract

SkillNudge 的 active product 只保留四类记录。

## Skill identity and version

`skillnudge.skill-version.v0` contains a stable `skill_id`, immutable
`version`, exact `content`, its `sha256`, a source reference, a parent version,
and a lifecycle status of `ACTIVE` or `CANDIDATE`.

## Session evidence

`skillnudge.session-evidence.v0` contains an observable `session_id`, a
`trace_ref`, user or evaluator `feedback_refs`, and a short observed summary.
It deliberately does not contain hidden reasoning or semantic utility claims.

## Operator boundary

`skillnudge.evolution-request.v0` records the source Skill version, objective,
operator identity, and evidence references. `skillnudge.operator-result.v0`
records the operator-native result reference, operator version, candidate
artifact, and provenance references. SkillNudge does not implement the
operator's algorithm.

## Candidate lineage

`skillnudge.candidate.v0` links a candidate version to its source Skill/version,
operator result, and session evidence. Its Human decision is initially
`PENDING` and can become `ACCEPTED`, `REJECTED`, `ROLLED_BACK`, or `RETIRED`.
Changing that decision never mutates the immutable candidate content and never
implicitly overwrites the active version.
