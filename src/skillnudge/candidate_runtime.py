"""Checkpoint 3 Candidate Acquisition and minimal Evidence Hydration."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .planning import PlanningRunResult
from .planning_contracts import (
    ContractValidationError,
    validate_intervention_plan,
    validate_planning_consistency,
    validate_query_plan,
)
from .retrieval import BM25Retriever, fuse_ranked_results, to_fts_query


PER_QUERY_K = 50
FUSED_LIMIT = 30
HYDRATION_LIMIT = 10
RRF_K = 60
SUPPORTED_ACQUISITION_FAMILIES = frozenset({"skill"})


class CandidateAcquisitionError(RuntimeError):
    """Raised when a planning result cannot be consumed safely."""


@dataclass(frozen=True)
class CandidateRuntimeResult:
    run_id: str
    run_dir: str
    acquisition: dict[str, Any] | None
    evidence_packs: dict[str, Any] | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "run_dir": self.run_dir,
            "candidate_acquisition": self.acquisition,
            "evidence_packs": self.evidence_packs,
        }


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _append_trace(
    path: Path,
    run_id: str,
    event: str,
    stage: str,
    details: Mapping[str, Any] | None = None,
) -> None:
    record = {
        "schema_version": "trace.event.checkpoint3.v0",
        "run_id": run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "stage": stage,
        "details": dict(details or {}),
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def _body_sha256(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _provenance(
    record: Mapping[str, Any],
    *,
    verification_basis: str | None = None,
) -> tuple[str, list[str]]:
    fields = ("repo", "source_url", "license", "updated_at", "source")
    gaps = [field for field in fields if not record.get(field)]
    if len(gaps) == len(fields):
        return "unknown", [f"missing_{field}" for field in gaps]
    if gaps:
        return "partial", [f"missing_{field}" for field in gaps]
    if verification_basis:
        return "verified", []
    return "complete_unverified", []


class CandidateAcquisitionRuntime:
    """Consume a real PlanningRunResult and stop after local evidence hydration."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        per_query_k: int = PER_QUERY_K,
        fused_limit: int = FUSED_LIMIT,
        hydration_limit: int = HYDRATION_LIMIT,
        rrf_k: int = RRF_K,
    ):
        if per_query_k != PER_QUERY_K:
            raise ValueError("Checkpoint 3 fixes per-query retrieval at Top-50")
        if fused_limit != FUSED_LIMIT:
            raise ValueError("Checkpoint 3 fixes the fused candidate pool at Top-30")
        if hydration_limit != HYDRATION_LIMIT:
            raise ValueError("Checkpoint 3 fixes evidence hydration at Top-10")
        if rrf_k != RRF_K:
            raise ValueError("Checkpoint 3 fixes RRF k at 60")
        self.database_path = Path(database_path)
        self.per_query_k = per_query_k
        self.fused_limit = fused_limit
        self.hydration_limit = hydration_limit
        self.rrf_k = rrf_k

    def run(self, planning_result: PlanningRunResult) -> CandidateRuntimeResult:
        output_dir = Path(planning_result.run_dir)
        run_id = planning_result.run_id
        trace_path = output_dir / "trace.jsonl"
        intervention = validate_intervention_plan(planning_result.intervention_plan)
        query_plan = validate_query_plan(planning_result.query_plan)
        validate_planning_consistency(intervention, query_plan)

        if intervention["decision"] in {"no_intervention", "clarify"} or query_plan["status"] in {
            "skipped",
            "clarify",
        }:
            _append_trace(
                trace_path,
                run_id,
                "early_stop",
                "Candidate Acquisition",
                {
                    "decision": intervention["decision"],
                    "query_status": query_plan["status"],
                    "reason": "planning stopped before candidate acquisition",
                },
            )
            return CandidateRuntimeResult(run_id, str(output_dir), None, None)

        return self._acquire(
            output_dir=output_dir,
            trace_path=trace_path,
            run_id=run_id,
            intervention=intervention,
            query_plan=query_plan,
        )

    def _acquire(
        self,
        *,
        output_dir: Path,
        trace_path: Path,
        run_id: str,
        intervention: Mapping[str, Any],
        query_plan: Mapping[str, Any],
    ) -> CandidateRuntimeResult:
        targets = intervention.get("targets", [])
        planned_families = [
            target["family"]
            for target in targets
            if isinstance(target, Mapping) and isinstance(target.get("family"), str)
        ]
        queries = list(query_plan.get("queries", []))
        _append_trace(
            trace_path,
            run_id,
            "stage_start",
            "Candidate Acquisition",
            {
                "family": "skill",
                "planned_families": planned_families,
                "query_count": len(queries),
                "database_path": str(self.database_path),
            },
        )

        warnings: list[dict[str, Any]] = []
        supported_queries: list[tuple[str, Mapping[str, Any]]] = []
        query_records: list[dict[str, Any]] = []
        for index, query in enumerate(queries, start=1):
            if not isinstance(query, Mapping):
                raise CandidateAcquisitionError(f"QueryPlan query {index} is not an object")
            query_id = f"q{index}"
            family = query.get("family")
            base = {
                "query_id": query_id,
                "family": family,
                "angle": query.get("angle"),
                "semantic_query": query.get("semantic_query"),
                "purpose": query.get("purpose"),
                "top_k": self.per_query_k,
            }
            if family not in SUPPORTED_ACQUISITION_FAMILIES:
                warning = {
                    "code": "unsupported_family_surface",
                    "family": family,
                    "query_id": query_id,
                    "message": "No Week 1 acquisition surface exists for this family.",
                    "action": "not_acquired",
                }
                warnings.append(warning)
                base.update(
                    {
                        "status": "unsupported_family_surface",
                        "actual_fts_query": None,
                        "results": [],
                    }
                )
                query_records.append(base)
                _append_trace(
                    trace_path,
                    run_id,
                    "family_unsupported",
                    "Candidate Acquisition",
                    warning,
                )
                continue
            supported_queries.append((query_id, query))

        if not supported_queries:
            status = "unsupported_family_surface"
            acquisition = self._acquisition_artifact(
                run_id=run_id,
                status=status,
                planned_families=planned_families,
                query_records=query_records,
                fused=[],
                corpus={},
                warnings=warnings,
            )
            _write_json(output_dir / "04_candidate_acquisition.json", acquisition)
            _append_trace(
                trace_path,
                run_id,
                "stage_complete",
                "Candidate Acquisition",
                {"status": status, "fused_count": 0},
            )
            return CandidateRuntimeResult(run_id, str(output_dir), acquisition, None)

        results_by_query: dict[str, list[dict[str, Any]]] = {}
        query_by_id: dict[str, dict[str, Any]] = {}
        with BM25Retriever(self.database_path) as retriever:
            corpus = self._corpus_identity(retriever)
            for query_id, query in supported_queries:
                semantic_query = str(query["semantic_query"])
                fts_query = to_fts_query(semantic_query)
                results = retriever.retrieve(semantic_query, self.per_query_k)
                results_by_query[query_id] = results
                query_by_id[query_id] = {
                    "query_id": query_id,
                    "family": query["family"],
                    "angle": query["angle"],
                    "semantic_query": semantic_query,
                    "purpose": query["purpose"],
                    "top_k": self.per_query_k,
                    "status": "retrieved",
                    "actual_fts_query": fts_query,
                    "results": [
                        {
                            **result,
                            "rrf_contribution": 1.0 / (self.rrf_k + int(result["rank"])),
                        }
                        for result in results
                    ],
                }
                _append_trace(
                    trace_path,
                    run_id,
                    "query_execution",
                    "Candidate Acquisition",
                    {
                        "query_id": query_id,
                        "family": query["family"],
                        "semantic_query": semantic_query,
                        "actual_fts_query": fts_query,
                        "result_count": len(results),
                    },
                )

            query_records.extend(query_by_id.values())
            fused = fuse_ranked_results(
                results_by_query,
                limit=self.fused_limit,
                rrf_k=self.rrf_k,
            )
            fused = [self._with_query_hits(item, query_by_id) for item in fused]
            _append_trace(
                trace_path,
                run_id,
                "fusion",
                "Candidate Acquisition",
                {
                    "method": "reciprocal_rank_fusion",
                    "rrf_k": self.rrf_k,
                    "fused_limit": self.fused_limit,
                    "fused_count": len(fused),
                },
            )

            status = "ready" if not warnings else "partial_unsupported_family_surface"
            acquisition = self._acquisition_artifact(
                run_id=run_id,
                status=status,
                planned_families=planned_families,
                query_records=query_records,
                fused=fused,
                corpus=corpus,
                warnings=warnings,
            )
            _write_json(output_dir / "04_candidate_acquisition.json", acquisition)
            _append_trace(
                trace_path,
                run_id,
                "stage_complete",
                "Candidate Acquisition",
                {"status": status, "fused_count": len(fused)},
            )

            evidence = self._hydrate(
                output_dir=output_dir,
                trace_path=trace_path,
                run_id=run_id,
                retriever=retriever,
                fused=fused,
                query_by_id=query_by_id,
                corpus=corpus,
            )
        return CandidateRuntimeResult(run_id, str(output_dir), acquisition, evidence)

    @staticmethod
    def _corpus_identity(retriever: BM25Retriever) -> dict[str, Any]:
        metadata = retriever.build_metadata()
        source = metadata.get("source")
        if not isinstance(source, Mapping):
            source = {}
        return {
            "database_path": str(retriever.database_path),
            "identity": source.get("repository") or source.get("local_corpus_path"),
            "version": source.get("repository_commit") or source.get("corpus_sha256"),
            "source_metadata": dict(source),
            "build_metadata": metadata,
        }

    @staticmethod
    def _with_query_hits(
        fused_item: Mapping[str, Any],
        query_by_id: Mapping[str, Mapping[str, Any]],
    ) -> dict[str, Any]:
        item = dict(fused_item)
        hits = []
        for query_id, rank in fused_item.get("query_ranks", {}).items():
            query = query_by_id.get(query_id, {})
            hits.append(
                {
                    "query_id": query_id,
                    "semantic_query": query.get("semantic_query"),
                    "angle": query.get("angle"),
                    "rank": rank,
                    "raw_bm25_score": fused_item.get("raw_bm25_scores", {}).get(query_id),
                    "rrf_contribution": fused_item.get("rrf_contributions", {}).get(query_id),
                }
            )
        item["query_hits"] = hits
        return item

    @staticmethod
    def _acquisition_artifact(
        *,
        run_id: str,
        status: str,
        planned_families: list[str],
        query_records: list[dict[str, Any]],
        fused: list[dict[str, Any]],
        corpus: Mapping[str, Any],
        warnings: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return {
            "schema_version": "checkpoint3.candidate_acquisition.v0",
            "run_id": run_id,
            "stage": "Candidate Acquisition",
            "status": status,
            "family": "skill" if "skill" in planned_families else None,
            "planned_families": planned_families,
            "acquired_families": ["skill"] if any(
                query.get("family") == "skill" and query.get("status") == "retrieved"
                for query in query_records
            ) else [],
            "corpus": dict(corpus),
            "retrieval": {
                "per_query_k": PER_QUERY_K,
                "rrf": {
                    "method": "reciprocal_rank_fusion",
                    "rrf_k": RRF_K,
                    "limit": FUSED_LIMIT,
                },
                "queries": query_records,
                "fused_top_30": fused,
            },
            "warnings": warnings,
        }

    def _hydrate(
        self,
        *,
        output_dir: Path,
        trace_path: Path,
        run_id: str,
        retriever: BM25Retriever,
        fused: list[dict[str, Any]],
        query_by_id: Mapping[str, Mapping[str, Any]],
        corpus: Mapping[str, Any],
    ) -> dict[str, Any]:
        top_10 = fused[: self.hydration_limit]
        records = retriever.fetch_candidates([item["candidate_id"] for item in top_10])
        records_by_id = {record["candidate_id"]: record for record in records}
        _append_trace(
            trace_path,
            run_id,
            "stage_start",
            "Evidence Hydration",
            {"requested_count": len(top_10), "family": "skill"},
        )
        packs: list[dict[str, Any]] = []
        for item in top_10:
            candidate_id = item["candidate_id"]
            record = records_by_id.get(candidate_id)
            if record is None:
                _append_trace(
                    trace_path,
                    run_id,
                    "candidate_hydration",
                    "Evidence Hydration",
                    {
                        "candidate_id": candidate_id,
                        "fused_rank": item.get("fused_rank"),
                        "provenance_status": "unknown",
                        "status": "missing_local_record",
                    },
                )
                continue
            body = record.get("body") or ""
            provenance_status, evidence_gaps = _provenance(record)
            pack = {
                "candidate_id": candidate_id,
                "family": "skill",
                "identity": {
                    "name": record.get("name"),
                    "repo": record.get("repo"),
                    "source_url": record.get("source_url"),
                    "source": record.get("source"),
                    "license": record.get("license"),
                    "updated_at": record.get("updated_at"),
                },
                "content": {
                    "description": record.get("description"),
                    "body": body,
                    "body_sha256": _body_sha256(body),
                    "body_length": len(body.encode("utf-8")),
                },
                "retrieval": {
                    "fused_rank": item.get("fused_rank"),
                    "rrf_score": item.get("rrf_score"),
                    "query_hits": item.get("query_hits", []),
                },
                "provenance_status": provenance_status,
                "evidence_gaps": evidence_gaps,
                "corpus": {
                    "identity": corpus.get("identity"),
                    "version": corpus.get("version"),
                },
            }
            packs.append(pack)
            _append_trace(
                trace_path,
                run_id,
                "candidate_hydration",
                "Evidence Hydration",
                {
                    "candidate_id": candidate_id,
                    "fused_rank": item.get("fused_rank"),
                    "provenance_status": provenance_status,
                    "body_length": len(body.encode("utf-8")),
                },
            )
        evidence = {
            "schema_version": "checkpoint3.evidence_packs.v0",
            "run_id": run_id,
            "stage": "Evidence Hydration",
            "family": "skill",
            "hydration_limit": self.hydration_limit,
            "requested_candidate_count": len(top_10),
            "hydrated_candidate_count": len(packs),
            "packs": packs,
        }
        _write_json(output_dir / "05_evidence_packs.json", evidence)
        _append_trace(
            trace_path,
            run_id,
            "stage_complete",
            "Evidence Hydration",
            {"requested_count": len(top_10), "hydrated_count": len(packs)},
        )
        return evidence
