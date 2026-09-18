# `src/skillnudge`

This package contains the Week 1 Phase 1 runtime:

- capability framing, intervention planning, and query planning;
- local SQLite FTS5 storage, raw BM25 retrieval, and deterministic RRF;
- Evidence Hydration;
- Candidate Judgement and bounded Final Advice;
- a composed development entry point:
  `PYTHONPATH=src python3 -m skillnudge advise "<request>" --trace`.

It does not implement live discovery, automatic installation, Review, Grow,
Watch, embeddings, reranking, or capability self-evolution.
