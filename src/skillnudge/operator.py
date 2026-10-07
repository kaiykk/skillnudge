"""Thin external evolution-operator request/result boundary."""

from __future__ import annotations

from typing import Any, Mapping, Protocol

from .skill import validate_skill_version


EVOLUTION_REQUEST_SCHEMA = "skillnudge.evolution-request.v0"
OPERATOR_RESULT_SCHEMA = "skillnudge.operator-result.v0"
_OPERATORS = {"skill_conductor", "darwin", "skillopt", "external"}
_RESULT_STATUSES = {"CANDIDATE", "REJECTED", "FAILED"}


class OperatorContractError(ValueError):
    """Raised when an operator boundary record is invalid."""


class EvolutionOperator(Protocol):
    """Future adapter shape; implementations remain outside this repository."""

    name: str

    def run(self, request: Mapping[str, Any]) -> Mapping[str, Any]: ...


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise OperatorContractError(f"{path} must be an object")
    return value


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OperatorContractError(f"{path} must be a non-empty string")
    return value


def _keys(value: Mapping[str, Any], path: str, required: set[str], allowed: set[str]) -> None:
    missing = sorted(required - set(value))
    extra = sorted(set(value) - allowed)
    if missing:
        raise OperatorContractError(f"{path} missing required fields: {missing}")
    if extra:
        raise OperatorContractError(f"{path} has unexpected fields: {extra}")


def validate_evolution_request(value: Any) -> dict[str, Any]:
    request = _mapping(value, "request")
    fields = {"schema_version", "request_id", "skill_id", "source_version", "objective", "operator", "evidence_refs"}
    _keys(request, "request", fields, fields)
    if request["schema_version"] != EVOLUTION_REQUEST_SCHEMA:
        raise OperatorContractError(f"request.schema_version must be {EVOLUTION_REQUEST_SCHEMA}")
    operator = _string(request["operator"], "request.operator")
    if operator not in _OPERATORS:
        raise OperatorContractError(f"request.operator must be one of {sorted(_OPERATORS)}")
    refs = request["evidence_refs"]
    if not isinstance(refs, list) or not all(isinstance(item, str) and item.strip() for item in refs):
        raise OperatorContractError("request.evidence_refs must be a string list")
    return {
        "schema_version": EVOLUTION_REQUEST_SCHEMA,
        "request_id": _string(request["request_id"], "request.request_id"),
        "skill_id": _string(request["skill_id"], "request.skill_id"),
        "source_version": _string(request["source_version"], "request.source_version"),
        "objective": _string(request["objective"], "request.objective"),
        "operator": operator,
        "evidence_refs": list(refs),
    }

def validate_operator_result(value: Any) -> dict[str, Any]:
    result = _mapping(value, "operator_result")
    fields = {"schema_version", "result_id", "request_id", "operator", "operator_version", "status", "candidate", "native_ref", "provenance_refs"}
    _keys(result, "operator_result", fields, fields)
    if result["schema_version"] != OPERATOR_RESULT_SCHEMA:
        raise OperatorContractError(f"operator_result.schema_version must be {OPERATOR_RESULT_SCHEMA}")
    operator = _string(result["operator"], "operator_result.operator")
    if operator not in _OPERATORS:
        raise OperatorContractError(f"operator_result.operator must be one of {sorted(_OPERATORS)}")
    status = _string(result["status"], "operator_result.status")
    if status not in _RESULT_STATUSES:
        raise OperatorContractError(f"operator_result.status must be one of {sorted(_RESULT_STATUSES)}")
    candidate = result["candidate"]
    normalized_candidate = None if candidate is None else validate_skill_version(candidate, path="operator_result.candidate")
    refs = result["provenance_refs"]
    if not isinstance(refs, list) or not all(isinstance(item, str) and item.strip() for item in refs):
        raise OperatorContractError("operator_result.provenance_refs must be a string list")
    if status == "CANDIDATE" and normalized_candidate is None:
        raise OperatorContractError("CANDIDATE result requires candidate")
    return {
        "schema_version": OPERATOR_RESULT_SCHEMA,
        "result_id": _string(result["result_id"], "operator_result.result_id"),
        "request_id": _string(result["request_id"], "operator_result.request_id"),
        "operator": operator,
        "operator_version": _string(result["operator_version"], "operator_result.operator_version"),
        "status": status,
        "candidate": normalized_candidate,
        "native_ref": _string(result["native_ref"], "operator_result.native_ref"),
        "provenance_refs": list(refs),
    }
