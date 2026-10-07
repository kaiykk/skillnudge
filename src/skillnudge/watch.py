"""Provider-free WATCH for one persisted Evidence Need and one experience."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .bootstrap import default_data_dir
from .evidence_need import EvidenceNeedError, load_evidence_need


WATCH_ENVELOPE_SCHEMA_VERSION = "native.watch-envelope.v1"
WATCH_RESULT_SCHEMA_VERSION = "native.watch-result.v1"
TRACE_SCHEMA_VERSION = "trace.event.native-watch.v0"
_DISPOSITIONS = {"IGNORE", "WAKE", "INSUFFICIENT"}
_EXPERIENCE_ROLES = {"NATIVE_HOST_EXPERIENCE", "WATCH_ROUTING_TEST_EVIDENCE"}
_PRIVATE_FIELDS = {"chain_of_thought", "hidden_reasoning", "internal_reasoning", "private_reasoning", "scratchpad"}


class WatchValidationError(ValueError):
    """Raised when a host WATCH envelope violates the public contract."""


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise WatchValidationError(f"{path} must be an object")
    return value


def _keys(value: Mapping[str, Any], path: str, required: set[str], allowed: set[str]) -> None:
    missing = sorted(required - set(value))
    extra = sorted(set(value) - allowed)
    if missing:
        raise WatchValidationError(f"{path} missing required fields: {missing}")
    if extra:
        raise WatchValidationError(f"{path} has unexpected fields: {extra}")


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise WatchValidationError(f"{path} must be a non-empty string")
    return value


def _string_list(value: Any, path: str, *, non_empty: bool = True) -> list[str]:
    if not isinstance(value, list):
        raise WatchValidationError(f"{path} must be a list")
    if non_empty and not value:
        raise WatchValidationError(f"{path} must be non-empty")
    return [_string(item, f"{path}[{index}]") for index, item in enumerate(value)]


def _scan_private(value: Any, path: str = "envelope") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in _PRIVATE_FIELDS:
                raise WatchValidationError(f"{path}.{key} is not allowed")
            _scan_private(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_private(child, f"{path}[{index}]")


def _validate_subject(value: Any, expected: Mapping[str, str]) -> dict[str, str]:
    subject = _mapping(value, "experience.subject")
    _keys(subject, "experience.subject", {"capability_id", "candidate_version", "candidate_sha256"}, {"capability_id", "candidate_version", "candidate_sha256"})
    normalized = {key: _string(subject[key], f"experience.subject.{key}") for key in ("capability_id", "candidate_version", "candidate_sha256")}
    if normalized != dict(expected):
        raise WatchValidationError("experience.subject does not match the persisted Evidence Need")
    return normalized


def _validate_experience(value: Any, need: Mapping[str, Any]) -> tuple[dict[str, Any], set[str]]:
    experience = _mapping(value, "experience")
    _keys(experience, "experience", {"experience_id", "evidence_role", "subject", "execution_context", "observable_events"}, {"experience_id", "evidence_role", "subject", "execution_context", "observable_events"})
    role = _string(experience["evidence_role"], "experience.evidence_role")
    if role not in _EXPERIENCE_ROLES:
        raise WatchValidationError(f"experience.evidence_role must be one of {sorted(_EXPERIENCE_ROLES)}")
    subject = _validate_subject(experience["subject"], need["subject"])
    context = _mapping(experience["execution_context"], "experience.execution_context")
    _keys(context, "experience.execution_context", {"model", "harness", "task_family"}, {"model", "harness", "task_family"})
    normalized_context = {key: _string(context[key], f"experience.execution_context.{key}") for key in ("model", "harness", "task_family")}
    if normalized_context != dict(need["scope"]):
        raise WatchValidationError("experience.execution_context does not match the Evidence Need scope")
    events = experience["observable_events"]
    if not isinstance(events, list) or not events:
        raise WatchValidationError("experience.observable_events must be a non-empty list")
    normalized_events: list[dict[str, str]] = []
    event_ids: set[str] = set()
    for index, raw in enumerate(events):
        event = _mapping(raw, f"experience.observable_events[{index}]")
        _keys(event, f"experience.observable_events[{index}]", {"event_id", "kind", "summary", "source_ref"}, {"event_id", "kind", "summary", "source_ref"})
        item = {key: _string(event[key], f"experience.observable_events[{index}].{key}") for key in ("event_id", "kind", "summary", "source_ref")}
        if item["event_id"] in event_ids:
            raise WatchValidationError("experience.observable_events contains duplicate event_id values")
        event_ids.add(item["event_id"])
        normalized_events.append(item)
    return {"experience_id": _string(experience["experience_id"], "experience.experience_id"), "evidence_role": role, "subject": subject, "execution_context": normalized_context, "observable_events": normalized_events}, event_ids


def validate_watch_envelope(value: Any, need: Mapping[str, Any]) -> dict[str, Any]:
    _scan_private(value)
    envelope = _mapping(value, "envelope")
    _keys(envelope, "envelope", {"schema_version", "need_id", "need_context", "experience", "assessment"}, {"schema_version", "need_id", "need_context", "experience", "assessment"})
    if envelope["schema_version"] != WATCH_ENVELOPE_SCHEMA_VERSION:
        raise WatchValidationError(f"schema_version must be {WATCH_ENVELOPE_SCHEMA_VERSION!r}")
    need_id = _string(envelope["need_id"], "need_id")
    if need_id != need["need_id"]:
        raise WatchValidationError("need_id does not match the loaded Evidence Need")
    need_context = _mapping(envelope["need_context"], "need_context")
    _keys(need_context, "need_context", {"unresolved_question", "interesting_future_event"}, {"unresolved_question", "interesting_future_event"})
    normalized_need_context = {
        key: _string(need_context[key], f"need_context.{key}")
        for key in ("unresolved_question", "interesting_future_event")
    }
    expected_need_context = {
        key: need[key] for key in ("unresolved_question", "interesting_future_event")
    }
    if normalized_need_context != expected_need_context:
        raise WatchValidationError("need_context does not match the persisted Evidence Need")
    experience, event_ids = _validate_experience(envelope["experience"], need)
    assessment = _mapping(envelope["assessment"], "assessment")
    _keys(assessment, "assessment", {"disposition", "rationale", "evidence_refs"}, {"disposition", "rationale", "evidence_refs"})
    disposition = _string(assessment["disposition"], "assessment.disposition")
    if disposition not in _DISPOSITIONS:
        raise WatchValidationError(f"assessment.disposition must be one of {sorted(_DISPOSITIONS)}")
    refs = _string_list(assessment["evidence_refs"], "assessment.evidence_refs", non_empty=disposition != "INSUFFICIENT")
    unknown_refs = sorted(set(refs) - event_ids)
    if unknown_refs:
        raise WatchValidationError(f"assessment.evidence_refs references unknown event_id values: {unknown_refs}")
    return {
        "schema_version": WATCH_ENVELOPE_SCHEMA_VERSION,
        "need_id": need_id,
        "need_context": normalized_need_context,
        "experience": experience,
        "assessment": {
            "disposition": disposition,
            "rationale": _string(assessment["rationale"], "assessment.rationale"),
            "evidence_refs": refs,
        },
    }


def default_watch_run_dir(data_dir: str | Path | None = None) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    root = Path(data_dir).expanduser() if data_dir is not None else default_data_dir()
    return root / "watch-runs" / f"watch-{timestamp}-{uuid.uuid4().hex[:8]}"


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _append_trace(path: Path, run_id: str, event: str, details: Mapping[str, Any] | None = None) -> None:
    record = {"schema_version": TRACE_SCHEMA_VERSION, "run_id": run_id, "timestamp": datetime.now(timezone.utc).isoformat(), "event": event, "stage": "Native Watch", "details": dict(details or {})}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def run_watch(envelope: Any, *, data_dir: str | Path | None = None, run_dir: str | Path | None = None) -> dict[str, Any]:
    """Load one OPEN need, validate one experience, and persist a WATCH receipt."""

    raw = _mapping(envelope, "envelope")
    need_id = _string(raw.get("need_id"), "need_id")
    try:
        need = load_evidence_need(need_id, data_dir=data_dir, require_open=True)
    except EvidenceNeedError as error:
        raise WatchValidationError(str(error)) from error
    validated = validate_watch_envelope(envelope, need)
    output_dir = Path(run_dir) if run_dir is not None else default_watch_run_dir(data_dir)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise RuntimeError("WATCH_RUN_DIR_EXISTS: choose a new run directory")
    output_dir.mkdir(parents=True, exist_ok=True)
    run_id = output_dir.name
    trace_path = output_dir / "trace.jsonl"
    _write_json(output_dir / "00_watch_envelope.json", validated)
    _append_trace(trace_path, run_id, "evidence_need_loaded", {"need_id": need_id, "status": need["status"]})
    _append_trace(
        trace_path,
        run_id,
        "interesting_future_event_loaded",
        {"need_id": need_id, "interesting_future_event": validated["need_context"]["interesting_future_event"]},
    )
    _append_trace(trace_path, run_id, "experience_validated", {"experience_id": validated["experience"]["experience_id"], "evidence_role": validated["experience"]["evidence_role"]})
    _append_trace(trace_path, run_id, "evidence_refs_validated", {"event_ids": validated["assessment"]["evidence_refs"]})
    _append_trace(trace_path, run_id, "watch_disposition_recorded", {"disposition": validated["assessment"]["disposition"]})
    result = {
        "schema_version": WATCH_RESULT_SCHEMA_VERSION,
        "need_id": need_id,
        "need_context": validated["need_context"],
        "experience_id": validated["experience"]["experience_id"],
        "disposition": validated["assessment"]["disposition"],
        "rationale": validated["assessment"]["rationale"],
        "evidence": {"referenced_event_ids": validated["assessment"]["evidence_refs"]},
        "experience_role": validated["experience"]["evidence_role"],
        "provider": None,
        "utility_claim": False,
        "lifecycle_transition": None,
        "need_status": "OPEN",
        "run_id": run_id,
        "run_dir": str(output_dir),
    }
    _write_json(output_dir / "01_watch_result.json", result)
    _append_trace(trace_path, run_id, "watch_result_emitted", {"disposition": result["disposition"], "utility_claim": False, "lifecycle_transition": None})
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="skillnudge watch")
    parser.add_argument("--stdin", action="store_true", help="read a WATCH envelope from standard input")
    parser.add_argument("--data-dir", type=Path, help="override the per-user SkillNudge data directory")
    parser.add_argument("--run-dir", type=Path, help="explicit local artifact directory")
    args = parser.parse_args(argv)
    if not args.stdin:
        parser.error("watch requires --stdin")
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            raise WatchValidationError("the WATCH envelope must not be empty")
        result = run_watch(json.loads(raw), data_dir=args.data_dir, run_dir=args.run_dir)
    except (json.JSONDecodeError, WatchValidationError, RuntimeError, OSError) as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
