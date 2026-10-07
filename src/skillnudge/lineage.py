"""Candidate lineage and Human decision boundary."""

from __future__ import annotations

from typing import Any, Mapping

from .skill import validate_skill_version


CANDIDATE_SCHEMA = "skillnudge.candidate.v0"
_DECISIONS = {"PENDING", "ACCEPTED", "REJECTED", "ROLLED_BACK", "RETIRED"}


class LineageValidationError(ValueError):
    """Raised when a candidate lineage record is invalid."""


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise LineageValidationError(f"{path} must be an object")
    return value


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LineageValidationError(f"{path} must be a non-empty string")
    return value


def _keys(value: Mapping[str, Any], path: str, required: set[str], allowed: set[str]) -> None:
    missing = sorted(required - set(value))
    extra = sorted(set(value) - allowed)
    if missing:
        raise LineageValidationError(f"{path} missing required fields: {missing}")
    if extra:
        raise LineageValidationError(f"{path} has unexpected fields: {extra}")


def validate_candidate(value: Any) -> dict[str, Any]:
    candidate = _mapping(value, "candidate")
    fields = {"schema_version", "candidate_id", "source_skill_id", "source_version", "candidate_skill", "operator_result_id", "evidence_refs", "human_decision"}
    _keys(candidate, "candidate", fields, fields)
    if candidate["schema_version"] != CANDIDATE_SCHEMA:
        raise LineageValidationError(f"candidate.schema_version must be {CANDIDATE_SCHEMA}")
    skill = validate_skill_version(candidate["candidate_skill"], path="candidate.candidate_skill")
    if skill["lifecycle_status"] != "CANDIDATE":
        raise LineageValidationError("candidate.candidate_skill.lifecycle_status must be CANDIDATE")
    if skill["skill_id"] != candidate["source_skill_id"]:
        raise LineageValidationError("candidate skill_id must match source_skill_id")
    if skill["parent_version"] != candidate["source_version"]:
        raise LineageValidationError("candidate parent_version must match source_version")
    refs = candidate["evidence_refs"]
    if not isinstance(refs, list) or not all(isinstance(item, str) and item.strip() for item in refs):
        raise LineageValidationError("candidate.evidence_refs must be a string list")
    decision = _string(candidate["human_decision"], "candidate.human_decision")
    if decision not in _DECISIONS:
        raise LineageValidationError(f"candidate.human_decision must be one of {sorted(_DECISIONS)}")
    return {
        "schema_version": CANDIDATE_SCHEMA,
        "candidate_id": _string(candidate["candidate_id"], "candidate.candidate_id"),
        "source_skill_id": _string(candidate["source_skill_id"], "candidate.source_skill_id"),
        "source_version": _string(candidate["source_version"], "candidate.source_version"),
        "candidate_skill": skill,
        "operator_result_id": _string(candidate["operator_result_id"], "candidate.operator_result_id"),
        "evidence_refs": list(refs),
        "human_decision": decision,
    }


def apply_human_decision(value: Any, decision: str) -> dict[str, Any]:
    """Return a new record; never mutates or activates the candidate."""

    normalized = validate_candidate(value)
    decision = _string(decision, "human_decision").upper()
    if decision not in _DECISIONS - {"PENDING"}:
        raise LineageValidationError("human_decision must be ACCEPTED, REJECTED, ROLLED_BACK, or RETIRED")
    normalized["human_decision"] = decision
    return normalized
