"""D001 Checkpoint 1 runner: local corpus, BM25, RRF, and trace artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .retrieval import (
    BM25Retriever,
    build_index,
    check_d001_coverage,
    fuse_ranked_results,
    to_fts_query,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_QUERY_PLAN = REPO_ROOT / "eval/cases/d001_ui/query_plan.json"
DEFAULT_COVERAGE_TARGET = REPO_ROOT / "eval/cases/d001_ui/coverage_target.json"

CAPABILITY_FIXTURE = {
    "contract": {
        "goal": "Create a better-looking frontend or UI prototype.",
        "stage": "early exploration",
        "blocker": "The user cannot translate vague visual intent into a concrete interface direction.",
        "missing_capabilities": [
            "ui/ux prototyping guidance",
            "design-system guidance",
            "translate visual intent into interface design",
        ],
        "intended_effect": "Turn vague visual intent into a concrete, comparable UI prototype direction.",
        "constraints": [],
        "not_needed": [],
        "uncertainties": [],
    },
    "confidence": "high",
    "clarification_needed": False,
    "clarification_question": None,
}

INTERVENTION_FIXTURE = {
    "decision": "search",
    "targets": [
        {
            "family": "skill",
            "priority": "primary",
            "rationale": "The main gap is instructional capability for translating vague visual intent into a prototype.",
        },
        {
            "family": "resource",
            "priority": "companion",
            "rationale": "References may help compare visual directions after the primary capability is found.",
        },
    ],
    "decision_reason": "The D001 pressure test calls for Skill retrieval with a possible companion Resource.",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_event(path: Path, run_id: str, event: str, stage: str, details: Mapping[str, Any]) -> None:
    record = {
        "schema_version": "trace.event.v0",
        "run_id": run_id,
        "timestamp": _utc_now(),
        "event": event,
        "stage": stage,
        "details": dict(details),
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def run_d001(
    corpus_path: str | Path,
    run_dir: str | Path,
    *,
    query_plan_path: str | Path = DEFAULT_QUERY_PLAN,
    coverage_target_path: str | Path = DEFAULT_COVERAGE_TARGET,
    source_metadata: Mapping[str, Any] | None = None,
    per_query_k: int = 50,
    fused_limit: int = 30,
    rrf_k: int = 60,
) -> dict[str, Any]:
    """Run only Checkpoint 1 and return its reviewable summary."""

    output_dir = Path(run_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    run_id = output_dir.name
    trace_path = output_dir / "trace.jsonl"
    trace_path.write_text("", encoding="utf-8")
    corpus = Path(corpus_path)
    query_plan = json.loads(Path(query_plan_path).read_text(encoding="utf-8"))
    target = json.loads(Path(coverage_target_path).read_text(encoding="utf-8"))

    _write_json(
        output_dir / "00_input.json",
        {
            "schema_version": "checkpoint1.input.v0",
            "run_id": run_id,
            "case_id": "D001",
            "request": "I want to make a better-looking frontend or UI prototype, but I do not know design and do not know how to describe what I want.",
            "stage": "early exploration",
            "source": "frozen D001 golden case",
        },
    )
    _write_json(output_dir / "01_capability_contract.json", CAPABILITY_FIXTURE)
    _write_json(output_dir / "02_intervention_plan.json", INTERVENTION_FIXTURE)
    _write_json(output_dir / "03_query_plan.json", query_plan)
    _write_event(trace_path, run_id, "run_started", "Candidate Acquisition", {"checkpoint": 1})

    coverage = check_d001_coverage(corpus, target)
    _write_event(
        trace_path,
        run_id,
        "d001_coverage_checked",
        "Candidate Acquisition",
        {
            "status": coverage["status"],
            "name_match_count": coverage["name_match_count"],
            "verified_record_ids": coverage["verified_record_ids"],
        },
    )

    source_id_overrides = {
        record_id: {
            "candidate_id": target["candidate_id"],
            "repo": target["repo"],
            "source_url": target.get("source_url", f"https://github.com/{target['repo']}"),
            "license": target.get("license", "unknown"),
            "source": "sra-bench-corpus (identity verified against pinned official file)",
        }
        for record_id in coverage["verified_record_ids"]
    }
    source = dict(source_metadata or {})
    source.setdefault("local_corpus_path", str(corpus))
    index_path = output_dir / "skills.sqlite3"
    stats = build_index(
        corpus,
        index_path,
        metadata={"source": source, "d001_coverage": coverage},
        identity_overrides=source_id_overrides,
    )
    _write_event(trace_path, run_id, "index_built", "Candidate Acquisition", stats.as_dict())

    query_results: dict[str, list[dict[str, Any]]] = {}
    query_evidence: list[dict[str, Any]] = []
    positive_rank_probe: list[dict[str, Any]] = []
    with BM25Retriever(index_path) as retriever:
        for query_item in query_plan["queries"]:
            semantic_query = query_item["semantic_query"]
            fts_query = to_fts_query(semantic_query)
            results = retriever.retrieve(semantic_query, per_query_k)
            query_results[semantic_query] = results
            full_rank_results = retriever.retrieve(semantic_query, stats.imported_record_count)
            full_rank_match = next(
                (result for result in full_rank_results if result["candidate_id"] == target["candidate_id"]),
                None,
            )
            positive_rank_probe.append(
                {
                    "semantic_query": semantic_query,
                    "rank": full_rank_match["rank"] if full_rank_match else None,
                    "raw_bm25_score": full_rank_match["raw_bm25_score"] if full_rank_match else None,
                    "within_retrieval_window": bool(
                        full_rank_match and full_rank_match["rank"] <= per_query_k
                    ),
                }
            )
            query_evidence.append(
                {
                    "family": query_item["family"],
                    "angle": query_item["angle"],
                    "semantic_query": semantic_query,
                    "purpose": query_item["purpose"],
                    "fts_query": fts_query,
                    "top_results": results,
                }
            )
            _write_event(
                trace_path,
                run_id,
                "query_retrieved",
                "Candidate Acquisition",
                {"semantic_query": semantic_query, "fts_query": fts_query, "result_count": len(results)},
            )

    fused = fuse_ranked_results(query_results, limit=fused_limit, rrf_k=rrf_k)
    _write_event(
        trace_path,
        run_id,
        "results_fused",
        "Candidate Acquisition",
        {"method": "rrf", "rrf_k": rrf_k, "fused_count": len(fused)},
    )

    positive = next(
        (item for item in fused if item["candidate_id"] == target["candidate_id"]),
        None,
    )
    best_individual_rank = min(
        (rank for item in query_evidence for rank in [
            next(
                (result["rank"] for result in item["top_results"] if result["candidate_id"] == target["candidate_id"]),
                None,
            )
        ] if rank is not None),
        default=None,
    )
    acquisition = {
        "schema_version": "checkpoint1.candidate_acquisition.v0",
        "run_id": run_id,
        "stage": "Candidate Acquisition",
        "source": source,
        "corpus": {
            "raw_record_count": stats.source_record_count,
            "unique_imported_record_count": stats.imported_record_count,
            "skipped_record_count": stats.skipped_record_count,
            "imported_fields": ["candidate_id", "name", "description", "body", "repo", "source_url", "license", "updated_at", "source"],
            "sqlite_path": str(index_path),
            "fts_table": "skills_fts",
        },
        "d001_coverage": coverage,
        "retrieval": {
            "retriever": "SQLite FTS5 BM25",
            "per_query_k": per_query_k,
            "fts_query_transform": "Unicode word tokens quoted and joined with OR; raw SQLite bm25 score is preserved.",
            "queries": query_evidence,
            "positive_full_rank_probe": positive_rank_probe,
            "rrf": {"method": "reciprocal_rank_fusion", "rrf_k": rrf_k, "limit": fused_limit},
            "fused_top_30": fused,
        },
        "d001_positive": {
            "candidate_id": target["candidate_id"],
            "present_in_corpus": coverage["identity_verified"],
            "retrieved": positive is not None,
            "best_individual_rank": min(
                (probe["rank"] for probe in positive_rank_probe if probe["rank"] is not None),
                default=best_individual_rank,
            ),
            "retrieval_window_k": per_query_k,
            "fused_rank": positive["fused_rank"] if positive else None,
        },
        "not_created": ["05_evidence_packs.json", "06_judgements.json", "07_final_advice.json"],
    }
    _write_json(output_dir / "04_candidate_acquisition.json", acquisition)
    _write_event(
        trace_path,
        run_id,
        "run_completed",
        "Candidate Acquisition",
        {"d001_retrieved": positive is not None, "fused_count": len(fused)},
    )
    return {
        "run_id": run_id,
        "run_dir": str(output_dir),
        "stats": stats.as_dict(),
        "d001_positive": acquisition["d001_positive"],
        "fused_top_30": fused,
        "query_evidence": query_evidence,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run SkillNudge Checkpoint 1 D001 retrieval smoke test")
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--source-repository", default="https://github.com/oneal2000/SR-Agents")
    parser.add_argument("--source-commit", default="277fd8d2bbd7d3b81a5cf4ffa6e87e18c7906e4f")
    parser.add_argument("--corpus-sha256")
    args = parser.parse_args(argv)
    source = {
        "repository": args.source_repository,
        "repository_commit": args.source_commit,
        "corpus_sha256": args.corpus_sha256 or _sha256(args.corpus),
        "license": "MIT",
    }
    try:
        summary = run_d001(args.corpus, args.run_dir, source_metadata=source)
    except Exception as error:
        if hasattr(error, "coverage"):
            print(json.dumps({"error": "CORPUS_COVERAGE_FAILURE", "coverage": error.coverage}, ensure_ascii=False, indent=2))
        else:
            print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 1
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
