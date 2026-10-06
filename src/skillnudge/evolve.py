"""Provider-free, candidate-only Native EVOLVE MVP."""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .bootstrap import default_data_dir
from .capability_artifact import CapabilityArtifactError, validate_capability_artifact
from .validate import VALIDATION_RESULT_SCHEMA_VERSION


EVOLVE_ENVELOPE_SCHEMA_VERSION = "native.evolve-envelope.v0"
EVOLVE_RESULT_SCHEMA_VERSION = "native.evolve-result.v0"
TRACE_SCHEMA_VERSION = "trace.event.native-evolve.v0"


class EvolveContractError(ValueError):
    """Raised when an EVOLVE envelope is incomplete or unrelated."""


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise EvolveContractError(f"{path} must be an object")
    return value


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EvolveContractError(f"{path} must be a non-empty string")
    return value


def _keys(value: Mapping[str, Any], path: str, required: set[str], allowed: set[str]) -> None:
    missing = sorted(required - set(value))
    extra = sorted(set(value) - allowed)
    if missing:
        raise EvolveContractError(f"{path} missing required fields: {missing}")
    if extra:
        raise EvolveContractError(f"{path} has unexpected fields: {extra}")


def _validate_review_result(value: Any) -> dict[str, Any]:
    review = _mapping(value, "review_result")
    required = {
        "schema_version", "experience_id", "disposition", "assessment", "evidence",
        "intervention_candidate", "provider", "run_id", "run_dir",
    }
    _keys(review, "review_result", required, required | {"problem"})
    if review["schema_version"] != "native.review-result.v0":
        raise EvolveContractError("review_result.schema_version must be native.review-result.v0")
    if review["disposition"] != "TEST":
        raise EvolveContractError("EVOLVE requires review_result.disposition=TEST")
    if review["provider"] is not None:
        raise EvolveContractError("review_result.provider must be null for Native Mode")
    _string(review["experience_id"], "review_result.experience_id")
    run_id = _string(review["run_id"], "review_result.run_id")
    assessment = _mapping(review["assessment"], "review_result.assessment")
    _keys(assessment, "review_result.assessment", {"impact", "attribution", "addressability", "testability", "uncertainty"}, {"impact", "attribution", "addressability", "testability", "uncertainty"})
    if assessment["addressability"] != "plausible" or assessment["testability"] != "testable":
        raise EvolveContractError("EVOLVE requires a testable Review result")
    attribution = _mapping(assessment["attribution"], "review_result.assessment.attribution")
    if attribution.get("primary") != "capability_candidate":
        raise EvolveContractError("EVOLVE requires review_result.assessment.attribution.primary=capability_candidate")
    evidence = _mapping(review["evidence"], "review_result.evidence")
    _keys(evidence, "review_result.evidence", {"referenced_event_ids"}, {"referenced_event_ids"})
    refs = evidence["referenced_event_ids"]
    if not isinstance(refs, list) or not refs or not all(isinstance(item, str) and item.strip() for item in refs):
        raise EvolveContractError("review_result.evidence.referenced_event_ids must be non-empty")
    candidate = _mapping(review["intervention_candidate"], "review_result.intervention_candidate")
    _keys(candidate, "review_result.intervention_candidate", {"title", "target_behavior", "intervention_hypothesis", "evidence_refs"}, {"title", "target_behavior", "intervention_hypothesis", "evidence_refs"})
    _string(candidate["title"], "review_result.intervention_candidate.title")
    candidate_refs = candidate["evidence_refs"]
    if not isinstance(candidate_refs, list) or not candidate_refs or not all(isinstance(item, str) and item.strip() for item in candidate_refs):
        raise EvolveContractError("review_result.intervention_candidate.evidence_refs must be non-empty")
    if not set(candidate_refs).issubset(set(refs)):
        raise EvolveContractError("review candidate evidence_refs must resolve in Review evidence")
    return {
        "schema_version": "native.review-result.v0",
        "experience_id": review["experience_id"],
        "disposition": "TEST",
        "assessment": review["assessment"],
        "evidence": {"referenced_event_ids": list(refs)},
        "intervention_candidate": review["intervention_candidate"],
        "provider": None,
        "run_id": run_id,
        "run_dir": _string(review["run_dir"], "review_result.run_dir"),
    }


def _validate_validation_result(value: Any) -> dict[str, Any]:
    validation = _mapping(value, "validation_result")
    required = {"schema_version", "run_id", "review_run_id", "experience_id", "task_id", "pair_status", "validation_result", "scope", "control", "treatment", "limitations"}
    _keys(validation, "validation_result", required, required)
    if validation["schema_version"] != VALIDATION_RESULT_SCHEMA_VERSION:
        raise EvolveContractError(f"validation_result.schema_version must be {VALIDATION_RESULT_SCHEMA_VERSION}")
    if validation["pair_status"] != "VALID":
        raise EvolveContractError("EVOLVE requires validation_result.pair_status=VALID")
    for key in ("run_id", "review_run_id", "experience_id", "task_id"):
        _string(validation[key], f"validation_result.{key}")
    scope = _mapping(validation["scope"], "validation_result.scope")
    _string(scope.get("comparison_mode"), "validation_result.scope.comparison_mode")
    if scope["comparison_mode"] != "INTERVENTION_ABLATION":
        raise EvolveContractError("EVOLVE optional validation must use INTERVENTION_ABLATION; CAPABILITY_REVISION runs after EVOLVE")
    return dict(validation)


def _validate_candidate(value: Any) -> tuple[dict[str, str], str]:
    candidate = _mapping(value, "candidate")
    required = {"schema_version", "capability_id", "version", "type", "exact_content", "sha256", "change_summary"}
    _keys(candidate, "candidate", required, required)
    try:
        artifact = validate_capability_artifact({key: candidate[key] for key in required - {"change_summary"}}, path="candidate")
    except CapabilityArtifactError as error:
        raise EvolveContractError(str(error)) from error
    return artifact, _string(candidate["change_summary"], "candidate.change_summary")


def validate_evolve_envelope(value: Any) -> dict[str, Any]:
    envelope = _mapping(value, "envelope")
    fields = {"schema_version", "source", "review_result", "candidate"}
    allowed = fields | {"validation_result"}
    _keys(envelope, "envelope", fields, allowed)
    if envelope["schema_version"] != EVOLVE_ENVELOPE_SCHEMA_VERSION:
        raise EvolveContractError(f"schema_version must be {EVOLVE_ENVELOPE_SCHEMA_VERSION}")
    try:
        source = validate_capability_artifact(envelope["source"], path="source")
    except CapabilityArtifactError as error:
        raise EvolveContractError(str(error)) from error
    review = _validate_review_result(envelope["review_result"])
    validation = None
    if envelope.get("validation_result") is not None:
        validation = _validate_validation_result(envelope["validation_result"])
    candidate, change_summary = _validate_candidate(envelope["candidate"])
    if source["capability_id"] != candidate["capability_id"]:
        raise EvolveContractError("source and candidate capability_id must match")
    if source["version"] == candidate["version"]:
        raise EvolveContractError("source and candidate version must differ")
    if source["sha256"] == candidate["sha256"]:
        raise EvolveContractError("source and candidate sha256 must differ")
    if validation is not None:
        if validation["review_run_id"] != review["run_id"]:
            raise EvolveContractError("validation_result.review_run_id must match review_result.run_id")
        if validation["experience_id"] != review["experience_id"]:
            raise EvolveContractError("validation_result.experience_id must match review_result.experience_id")
        scope = validation["scope"]
        if scope.get("intervention_sha256") != candidate["sha256"]:
            raise EvolveContractError("validation intervention hash must match candidate sha256")
    return {
        "schema_version": EVOLVE_ENVELOPE_SCHEMA_VERSION,
        "source": source,
        "review_result": review,
        "validation_result": validation,
        "candidate": candidate,
        "change_summary": change_summary,
    }


def default_evolve_run_dir() -> Path:
    root = Path(os.environ.get("SKILLNUDGE_EVOLVE_DATA_DIR", str(default_data_dir() / "evolve-runs"))).expanduser()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return root / f"evolve-{timestamp}-{uuid.uuid4().hex[:8]}"


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _trace(path: Path, run_id: str, event: str, details: Mapping[str, Any] | None = None) -> None:
    record = {"schema_version": TRACE_SCHEMA_VERSION, "run_id": run_id, "timestamp": datetime.now(timezone.utc).isoformat(), "event": event, "stage": "Native Evolve", "details": dict(details or {})}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def run_evolve(envelope: Any, *, run_dir: str | Path | None = None) -> dict[str, Any]:
    validated = validate_evolve_envelope(envelope)
    output_dir = Path(run_dir) if run_dir is not None else default_evolve_run_dir()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise RuntimeError("EVOLVE_RUN_DIR_EXISTS: choose a new run directory")
    output_dir.mkdir(parents=True, exist_ok=True)
    run_id = output_dir.name
    trace_path = output_dir / "trace.jsonl"
    _write_json(output_dir / "00_evolve_envelope.json", validated)
    _trace(trace_path, run_id, "evolve_input_received", {"experience_id": validated["review_result"]["experience_id"]})
    validation = validated["validation_result"]
    linkage = {"review_run_id": validated["review_result"]["run_id"]}
    if validation is not None:
        linkage["validation_run_id"] = validation["run_id"]
    _trace(trace_path, run_id, "evidence_linkage_validated", linkage)
    candidate = validated["candidate"]
    result = {
        "schema_version": EVOLVE_RESULT_SCHEMA_VERSION,
        "source": {"capability_id": validated["source"]["capability_id"], "version": validated["source"]["version"], "sha256": validated["source"]["sha256"]},
        "candidate": {**candidate, "parent_sha256": validated["source"]["sha256"]},
        "change": {"summary": validated["change_summary"], "review_run_id": validated["review_result"]["run_id"], "validation_run_id": validation["run_id"] if validation is not None else None, "evidence_refs": validated["review_result"]["evidence"]["referenced_event_ids"]},
        "admission_basis": "REVIEW_PLUS_INTERVENTION_ABLATION" if validation is not None else "REVIEW",
        "lifecycle_status": "CANDIDATE",
        "decision_state": {"status": "PENDING_VALIDATION", "suggested_action": "VALIDATE", "authority": "HUMAN_REQUIRED"},
    }
    _write_json(output_dir / "01_evolve_result.json", result)
    _trace(trace_path, run_id, "candidate_emitted", {"capability_id": candidate["capability_id"], "version": candidate["version"], "lifecycle_status": "CANDIDATE"})
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="skillnudge evolve")
    parser.add_argument("--stdin", action="store_true", help="read a Native EVOLVE Envelope from standard input")
    parser.add_argument("--run-dir", type=Path, help="explicit local artifact directory")
    args = parser.parse_args(argv)
    if not args.stdin:
        parser.error("evolve requires --stdin")
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            raise EvolveContractError("the evolve envelope must not be empty")
        result = run_evolve(json.loads(raw), run_dir=args.run_dir)
    except (json.JSONDecodeError, EvolveContractError, RuntimeError, OSError) as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
