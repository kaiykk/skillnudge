# SkillNudge Repository Rules

SkillNudge is a control plane connecting real Agent Session evidence to
traceable Skill version evolution.

## Active product boundary

The active tree owns only:

- Skill identity, exact content, hash, and immutable version records;
- observable Session evidence and trace references;
- a thin external evolution-operator request/result boundary;
- candidate lineage and Human accept/reject/rollback/retire decisions.

It does not own search, retrieval, advisor planning, semantic utility
judgement, benchmark/evaluator frameworks, WATCH, Evidence Need, or operator
algorithms.

## Engineering invariants

- Every candidate must point to a source Skill/version, operator result, and
  evidence references.
- Candidate content is immutable and never automatically replaces an active
  Skill.
- Do not store hidden reasoning in Session evidence.
- Keep operator-native algorithms and result semantics outside SkillNudge;
  normalize only identity, lineage, provenance, and lifecycle fields.
- Human authority is required for every active Skill mutation.
- Prefer narrow, deterministic record validation and atomic persistence.

## Scope gate

Before adding a file or feature, answer:

```text
Does this directly serve Session -> Skill Evolution?
What observable capability exists after the change?
Does it introduce a new lifecycle stage, semantic judge, search system, or
operator algorithm? If yes, stop and request Principal review.
```

External operator integration is not part of the Repository Reset. Do not start
Skill Conductor, Darwin, or SkillOpt integration in the reset commit.

## Validation

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m compileall -q src scripts
git diff --check
./scripts/check_publish_gate.sh
```
