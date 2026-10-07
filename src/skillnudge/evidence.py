"""Minimal references from real Agent sessions to Skill evolution."""

from __future__ import annotations

from typing import Any, Mapping


SESSION_EVIDENCE_SCHEMA = "skillnudge.session-evidence.v0"
_PRIVATE_FIELDS = {"chain_of_thought", "hidden_reasoning", "internal_reasoning", "scratchpad"}


class EvidenceValidationError(ValueError):
    """Raised when a Session Evidence reference is invalid."""


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise EvidenceValidationError(f"{path} must be an object")
    return value


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EvidenceValidationError(f"{path} must be a non-empty string")
    return value


def _keys(value: Mapping[str, Any], path: str, required: set[str], allowed: set[str]) -> None:
    missing = sorted(required - set(value))
    extra = sorted(set(value) - allowed)
    if missing:
        raise EvidenceValidationError(f"{path} missing required fields: {missing}")
    if extra:
        raise EvidenceValidationError(f"{path} has unexpected fields: {extra}")


def _scan_private(value: Any, path: str = "evidence") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in _PRIVATE_FIELDS:
                raise EvidenceValidationError(f"{path}.{key} is not allowed")
            _scan_private(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_private(child, f"{path}[{index}]")


def validate_session_evidence(value: Any, *, path: str = "evidence") -> dict[str, Any]:
    """Validate one observable session/feedback reference without judging it."""

    _scan_private(value, path)
    evidence = _mapping(value, path)
    fields = {"schema_version", "evidence_id", "session_id", "trace_ref", "feedback_refs", "observed_summary"}
    _keys(evidence, path, fields, fields)
    if evidence["schema_version"] != SESSION_EVIDENCE_SCHEMA:
        raise EvidenceValidationError(f"{path}.schema_version must be {SESSION_EVIDENCE_SCHEMA}")
    refs = evidence["feedback_refs"]
    if not isinstance(refs, list) or not refs or not all(isinstance(item, str) and item.strip() for item in refs):
        raise EvidenceValidationError(f"{path}.feedback_refs must be a non-empty string list")
    return {
        "schema_version": SESSION_EVIDENCE_SCHEMA,
        "evidence_id": _string(evidence["evidence_id"], f"{path}.evidence_id"),
        "session_id": _string(evidence["session_id"], f"{path}.session_id"),
        "trace_ref": _string(evidence["trace_ref"], f"{path}.trace_ref"),
        "feedback_refs": list(refs),
        "observed_summary": _string(evidence["observed_summary"], f"{path}.observed_summary"),
    }
