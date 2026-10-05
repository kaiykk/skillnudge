"""Provider-free review of one host-observed agent experience.

The host owns semantic interpretation. This module only validates the bounded
review envelope, preserves evidence references, and emits a durable result.
"""

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


REVIEW_ENVELOPE_SCHEMA_VERSION = "native.review-envelope.v0"
REVIEW_RESULT_SCHEMA_VERSION = "native.review-result.v0"
TRACE_SCHEMA_VERSION = "trace.event.native-review.v0"

_MISSING = object()
_PRIVATE_FIELDS = {
    "chain_of_thought",
    "hidden_reasoning",
    "internal_reasoning",
    "private_reasoning",
    "scratchpad",
}
_ATTRIBUTIONS = {
    "agent_lapse",
    "environment",
    "project_fact",
    "capability_candidate",
    "unclear",
}
_DISPOSITIONS = {"TEST", "WATCH", "NO_INTERVENTION", "INSUFFICIENT"}
_IMPACTS = {"low", "medium", "high", "unknown"}
_ADDRESSABILITY = {"plausible", "weak", "none", "unknown"}
_TESTABILITY = {"testable", "unclear", "not_testable"}


class ReviewValidationError(ValueError):
    """Raised when a host envelope violates the public review contract."""


def _require_mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ReviewValidationError(f"{path} must be an object")
    return value


def _require_keys(value: Mapping[str, Any], path: str, required: set[str], allowed: set[str]) -> None:
    missing = sorted(required - set(value))
    unexpected = sorted(set(value) - allowed)
    if missing:
        raise ReviewValidationError(f"{path} missing required fields: {missing}")
    if unexpected:
        raise ReviewValidationError(f"{path} has unexpected fields: {unexpected}")


def _string(value: Any, path: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise ReviewValidationError(f"{path} must be a non-empty string")
    return value


def _string_list(value: Any, path: str) -> list[str]:
    if not isinstance(value, list):
        raise ReviewValidationError(f"{path} must be a list")
    return [_string(item, f"{path}[{index}]") for index, item in enumerate(value)]


def _scan_private_fields(value: Any, path: str = "envelope") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in _PRIVATE_FIELDS:
                raise ReviewValidationError(f"{path}.{key} is not allowed")
            _scan_private_fields(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_private_fields(child, f"{path}[{index}]")


def _validate_event(value: Any, index: int) -> dict[str, Any]:
    event = _require_mapping(value, f"experience.observable_events[{index}]")
    _require_keys(
        event,
        f"experience.observable_events[{index}]",
        {"event_id", "kind", "summary", "source_ref"},
        {"event_id", "kind", "summary", "source_ref"},
    )
    return {
        "event_id": _string(event["event_id"], f"experience.observable_events[{index}].event_id"),
        "kind": _string(event["kind"], f"experience.observable_events[{index}].kind"),
        "summary": _string(event["summary"], f"experience.observable_events[{index}].summary"),
        "source_ref": _string(event["source_ref"], f"experience.observable_events[{index}].source_ref"),
    }


def _validate_experience(value: Any) -> dict[str, Any]:
    experience = _require_mapping(value, "experience")
    _require_keys(
        experience,
        "experience",
        {"experience_id", "source", "observable_events"},
        {"experience_id", "source", "observable_events"},
    )
    source = _require_mapping(experience["source"], "experience.source")
    _require_keys(source, "experience.source", {"type", "reference"}, {"type", "reference"})
    source_type = _string(source["type"], "experience.source.type")
    if source_type not in {"file", "jsonl", "inline", "other"}:
        raise ReviewValidationError("experience.source.type must be file, jsonl, inline, or other")
    events_value = experience["observable_events"]
    if not isinstance(events_value, list) or not events_value:
        raise ReviewValidationError("experience.observable_events must be a non-empty list")
    events = [_validate_event(item, index) for index, item in enumerate(events_value)]
    event_ids = [event["event_id"] for event in events]
    if len(event_ids) != len(set(event_ids)):
        raise ReviewValidationError("experience.observable_events contains duplicate event_id values")
    return {
        "experience_id": _string(experience["experience_id"], "experience.experience_id"),
        "source": {"type": source_type, "reference": _string(source["reference"], "experience.source.reference")},
        "observable_events": events,
    }


def _validate_assessment(value: Any, event_ids: set[str]) -> dict[str, Any]:
    assessment = _require_mapping(value, "assessment")
    _require_keys(
        assessment,
        "assessment",
        {"problem", "impact", "attribution", "addressability", "testability", "evidence_refs", "uncertainty"},
        {"problem", "impact", "attribution", "addressability", "testability", "evidence_refs", "uncertainty"},
    )
    impact = _string(assessment["impact"], "assessment.impact")
    if impact not in _IMPACTS:
        raise ReviewValidationError(f"assessment.impact must be one of {sorted(_IMPACTS)}")
    addressability = _string(assessment["addressability"], "assessment.addressability")
    if addressability not in _ADDRESSABILITY:
        raise ReviewValidationError(f"assessment.addressability must be one of {sorted(_ADDRESSABILITY)}")
    testability = _string(assessment["testability"], "assessment.testability")
    if testability not in _TESTABILITY:
        raise ReviewValidationError(f"assessment.testability must be one of {sorted(_TESTABILITY)}")
    attribution = _require_mapping(assessment["attribution"], "assessment.attribution")
    _require_keys(attribution, "assessment.attribution", {"primary", "alternatives"}, {"primary", "alternatives"})
    primary = _string(attribution["primary"], "assessment.attribution.primary")
    if primary not in _ATTRIBUTIONS:
        raise ReviewValidationError(f"assessment.attribution.primary must be one of {sorted(_ATTRIBUTIONS)}")
    alternatives = _string_list(attribution["alternatives"], "assessment.attribution.alternatives")
    unknown_alternatives = sorted(set(alternatives) - _ATTRIBUTIONS)
    if unknown_alternatives:
        raise ReviewValidationError(f"assessment.attribution.alternatives has invalid values: {unknown_alternatives}")
    refs = _string_list(assessment["evidence_refs"], "assessment.evidence_refs")
    if not refs:
        raise ReviewValidationError("assessment.evidence_refs must contain at least one event_id")
    unknown_refs = sorted(set(refs) - event_ids)
    if unknown_refs:
        raise ReviewValidationError(f"assessment.evidence_refs references unknown event_id values: {unknown_refs}")
    return {
        "problem": _string(assessment["problem"], "assessment.problem"),
        "impact": impact,
        "attribution": {"primary": primary, "alternatives": alternatives},
        "addressability": addressability,
        "testability": testability,
        "evidence_refs": refs,
        "uncertainty": _string_list(assessment["uncertainty"], "assessment.uncertainty"),
    }


def _validate_candidate(value: Any, event_ids: set[str]) -> dict[str, Any] | None:
    if value is None:
        return None
    candidate = _require_mapping(value, "intervention_candidate")
    _require_keys(
        candidate,
        "intervention_candidate",
        {"title", "target_behavior", "intervention_hypothesis", "evidence_refs"},
        {"title", "target_behavior", "intervention_hypothesis", "evidence_refs"},
    )
    refs = _string_list(candidate["evidence_refs"], "intervention_candidate.evidence_refs")
    if not refs:
        raise ReviewValidationError("intervention_candidate.evidence_refs must contain at least one event_id")
    unknown_refs = sorted(set(refs) - event_ids)
    if unknown_refs:
        raise ReviewValidationError(f"intervention_candidate.evidence_refs references unknown event_id values: {unknown_refs}")
    return {
        "title": _string(candidate["title"], "intervention_candidate.title"),
        "target_behavior": _string(candidate["target_behavior"], "intervention_candidate.target_behavior"),
        "intervention_hypothesis": _string(candidate["intervention_hypothesis"], "intervention_candidate.intervention_hypothesis"),
        "evidence_refs": refs,
    }


def validate_review_envelope(value: Any) -> dict[str, Any]:
    """Validate and normalize one host-produced review envelope."""

    _scan_private_fields(value)
    envelope = _require_mapping(value, "envelope")
    _require_keys(
        envelope,
        "envelope",
        {"schema_version", "experience", "assessment", "intervention_candidate", "disposition"},
        {"schema_version", "experience", "assessment", "intervention_candidate", "disposition"},
    )
    if envelope["schema_version"] != REVIEW_ENVELOPE_SCHEMA_VERSION:
        raise ReviewValidationError(f"schema_version must be {REVIEW_ENVELOPE_SCHEMA_VERSION!r}")
    experience = _validate_experience(envelope["experience"])
    event_ids = {event["event_id"] for event in experience["observable_events"]}
    assessment = _validate_assessment(envelope["assessment"], event_ids)
    candidate = _validate_candidate(envelope["intervention_candidate"], event_ids)
    disposition = _string(envelope["disposition"], "disposition")
    if disposition not in _DISPOSITIONS:
        raise ReviewValidationError(f"disposition must be one of {sorted(_DISPOSITIONS)}")
    if disposition in {"TEST", "WATCH"} and candidate is None:
        raise ReviewValidationError(f"{disposition} requires exactly one intervention_candidate")
    if disposition in {"NO_INTERVENTION", "INSUFFICIENT"} and candidate is not None:
        raise ReviewValidationError(f"{disposition} requires intervention_candidate to be null")
    if disposition == "TEST":
        if assessment["addressability"] != "plausible":
            raise ReviewValidationError("TEST requires assessment.addressability=plausible")
        if assessment["testability"] != "testable":
            raise ReviewValidationError("TEST requires assessment.testability=testable")
    return {
        "schema_version": REVIEW_ENVELOPE_SCHEMA_VERSION,
        "experience": experience,
        "assessment": assessment,
        "intervention_candidate": candidate,
        "disposition": disposition,
    }


def default_review_run_dir() -> Path:
    configured = os.environ.get("SKILLNUDGE_REVIEW_DATA_DIR")
    root = Path(configured).expanduser() if configured else default_data_dir() / "review-runs"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return root / f"review-{timestamp}-{uuid.uuid4().hex[:8]}"


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _append_trace(path: Path, run_id: str, event: str, details: Mapping[str, Any] | None = None) -> None:
    record = {
        "schema_version": TRACE_SCHEMA_VERSION,
        "run_id": run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "stage": "Native Review",
        "details": dict(details or {}),
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def run_review(envelope: Any, *, run_dir: str | Path | None = None) -> dict[str, Any]:
    """Validate, persist, and emit a deterministic review result."""

    validated = validate_review_envelope(envelope)
    output_dir = Path(run_dir) if run_dir is not None else default_review_run_dir()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise RuntimeError("REVIEW_RUN_DIR_EXISTS: choose a new run directory")
    output_dir.mkdir(parents=True, exist_ok=True)
    run_id = output_dir.name
    trace_path = output_dir / "trace.jsonl"
    _write_json(output_dir / "00_experience.json", validated["experience"])
    _write_json(output_dir / "01_review_envelope.json", validated)
    _append_trace(trace_path, run_id, "review_input_received", {"experience_id": validated["experience"]["experience_id"]})
    _append_trace(trace_path, run_id, "experience_validated", {"event_count": len(validated["experience"]["observable_events"])})
    _append_trace(trace_path, run_id, "evidence_refs_validated", {"event_ids": validated["assessment"]["evidence_refs"]})
    _append_trace(trace_path, run_id, "review_contract_validated", {"disposition": validated["disposition"]})
    result = {
        "schema_version": REVIEW_RESULT_SCHEMA_VERSION,
        "experience_id": validated["experience"]["experience_id"],
        "disposition": validated["disposition"],
        "problem": validated["assessment"]["problem"],
        "assessment": {
            "impact": validated["assessment"]["impact"],
            "attribution": validated["assessment"]["attribution"],
            "addressability": validated["assessment"]["addressability"],
            "testability": validated["assessment"]["testability"],
            "uncertainty": validated["assessment"]["uncertainty"],
        },
        "evidence": {"referenced_event_ids": validated["assessment"]["evidence_refs"]},
        "intervention_candidate": validated["intervention_candidate"],
        "provider": None,
        "run_id": run_id,
        "run_dir": str(output_dir),
    }
    _write_json(output_dir / "02_review_result.json", result)
    _append_trace(trace_path, run_id, "review_result_emitted", {"disposition": result["disposition"]})
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="skillnudge review")
    parser.add_argument("--stdin", action="store_true", help="read a Review Envelope from standard input")
    parser.add_argument("--run-dir", type=Path, help="explicit local artifact directory")
    args = parser.parse_args(argv)
    if not args.stdin:
        parser.error("review requires --stdin")
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            raise ReviewValidationError("the review envelope must not be empty")
        envelope = json.loads(raw)
        result = run_review(envelope, run_dir=args.run_dir)
    except (json.JSONDecodeError, ReviewValidationError, RuntimeError, OSError) as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
