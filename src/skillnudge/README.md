# `src/skillnudge`

This package is in a controlled migration from the earlier Advisor runtime to
the SkillNudge Skill-evolution control plane. The target active runtime owns
artifact identity, version lineage, lifecycle state, operator-result
provenance, and Human decisions.

The current checkout still contains the legacy bounded runtime:

- capability framing, intervention planning, and query planning;
- local SQLite FTS5 storage, raw BM25 retrieval, and deterministic RRF;
- Evidence Hydration;
- Candidate Judgement and bounded Final Advice;
- provider-free Native Review of one observable Agent experience;
- provider-free Native Validate of one bounded TEST candidate;
- provider-free Native EVOLVE candidate creation from a qualifying Review result,
  with optional linked INTERVENTION_ABLATION evidence;
- a composed development entry point:
  `PYTHONPATH=src python3 -m skillnudge advise "<request>" --trace`.

These modules remain for reproducibility while Phase 0 classification is
reviewed. They are not evidence that the new control-plane operator adapters
already exist. It does not implement automatic installation, automatic
promotion, autonomous operator selection, or capability self-evolution.

See [`../../docs/product-reset-phase0-20261007.md`](../../docs/product-reset-phase0-20261007.md)
for the KEEP/ADAPT/REMOVE_FROM_ACTIVE_TREE decision.
