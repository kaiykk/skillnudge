"""Readable validators for the frozen Checkpoint 2 planning contracts."""

from __future__ import annotations

from typing import Any, Mapping


class ContractValidationError(ValueError):
    """Raised when a model response does not match a frozen contract."""

    def __init__(self, contract_name: str, errors: list[str]):
        self.contract_name = contract_name
        self.errors = errors
        message = f"{contract_name} validation failed: " + "; ".join(errors)
        super().__init__(message)


def _mapping(value: Any, contract_name: str, errors: list[str]) -> Mapping[str, Any] | None:
    if not isinstance(value, Mapping):
        errors.append("response must be a JSON object")
        return None
    return value


def _required_string(value: Mapping[str, Any], key: str, errors: list[str]) -> None:
    if key not in value:
        errors.append(f"missing required field: {key}")
    elif not isinstance(value[key], str) or not value[key].strip():
        errors.append(f"{key} must be a non-empty string")


def _nullable_string(value: Mapping[str, Any], key: str, errors: list[str]) -> None:
    if key not in value:
        errors.append(f"missing required field: {key}")
    elif value[key] is not None and not isinstance(value[key], str):
        errors.append(f"{key} must be a string or null")


def _string_list(value: Mapping[str, Any], key: str, errors: list[str], *, required: bool) -> None:
    if key not in value:
        if required:
            errors.append(f"missing required field: {key}")
        return
    items = value[key]
    if not isinstance(items, list):
        errors.append(f"{key} must be a list")
        return
    if any(not isinstance(item, str) or not item.strip() for item in items):
        errors.append(f"{key} must contain only non-empty strings")


def _enum(value: Mapping[str, Any], key: str, allowed: set[str], errors: list[str]) -> None:
    if key not in value:
        errors.append(f"missing required field: {key}")
    elif value[key] not in allowed:
        errors.append(f"{key} must be one of {sorted(allowed)}")


def _unexpected(value: Mapping[str, Any], allowed: set[str], errors: list[str]) -> None:
    unexpected = sorted(set(value) - allowed)
    if unexpected:
        errors.append(f"unexpected fields: {unexpected}")


def validate_input_envelope(value: Any) -> dict[str, Any]:
    """Validate the minimal intake object without changing the raw request."""

    errors: list[str] = []
    data = _mapping(value, "InputEnvelope", errors)
    if data is None:
        raise ContractValidationError("InputEnvelope", errors)
    _required_string(data, "raw_request", errors)
    if "current_stage" in data and data["current_stage"] is not None and not isinstance(data["current_stage"], str):
        errors.append("current_stage must be a string or null")
    _unexpected(data, {"raw_request", "project_context", "current_stage"}, errors)
    if errors:
        raise ContractValidationError("InputEnvelope", errors)
    return dict(data)


def validate_capability_framing(value: Any) -> dict[str, Any]:
    """Validate CapabilityFramingResult without filling omitted optional fields."""

    errors: list[str] = []
    result = _mapping(value, "CapabilityFramingResult", errors)
    if result is None:
        raise ContractValidationError("CapabilityFramingResult", errors)
    contract = result.get("contract")
    contract_errors: list[str] = []
    contract_data = _mapping(contract, "CapabilityContract", contract_errors)
    if contract_data is not None:
        _required_string(contract_data, "goal", contract_errors)
        _nullable_string(contract_data, "stage", contract_errors)
        _required_string(contract_data, "blocker", contract_errors)
        _string_list(contract_data, "missing_capabilities", contract_errors, required=True)
        if isinstance(contract_data.get("missing_capabilities"), list) and len(contract_data["missing_capabilities"]) > 3:
            contract_errors.append("missing_capabilities may contain at most 3 items")
        _required_string(contract_data, "intended_effect", contract_errors)
        for optional_key in ("constraints", "not_needed", "uncertainties"):
            _string_list(contract_data, optional_key, contract_errors, required=False)
        _unexpected(
            contract_data,
            {"goal", "stage", "blocker", "missing_capabilities", "intended_effect", "constraints", "not_needed", "uncertainties"},
            contract_errors,
        )
    errors.extend(f"contract.{error}" for error in contract_errors)

    _enum(result, "confidence", {"high", "medium", "low"}, errors)
    if "clarification_needed" not in result or not isinstance(result.get("clarification_needed"), bool):
        errors.append("clarification_needed must be a boolean")
    _nullable_string(result, "clarification_question", errors)
    if result.get("clarification_needed") is True and (
        not isinstance(result.get("clarification_question"), str)
        or not result["clarification_question"].strip()
    ):
        errors.append("clarification_question must be a non-empty string when clarification_needed is true")
    if result.get("clarification_needed") is False and result.get("clarification_question") is not None:
        errors.append("clarification_question must be null when clarification_needed is false")
    _unexpected(result, {"contract", "confidence", "clarification_needed", "clarification_question"}, errors)
    if errors:
        raise ContractValidationError("CapabilityFramingResult", errors)
    return dict(result)


def validate_intervention_plan(value: Any) -> dict[str, Any]:
    """Validate InterventionPlan and its early-stop invariants."""

    errors: list[str] = []
    plan = _mapping(value, "InterventionPlan", errors)
    if plan is None:
        raise ContractValidationError("InterventionPlan", errors)
    _enum(plan, "decision", {"search", "no_intervention", "clarify"}, errors)
    _required_string(plan, "decision_reason", errors)
    targets = plan.get("targets")
    if not isinstance(targets, list):
        errors.append("targets must be a list")
        targets = []
    if len(targets) > 2:
        errors.append("targets may contain at most 2 items")
    families: set[str] = set()
    primary_count = 0
    for index, target in enumerate(targets):
        target_errors: list[str] = []
        target_data = _mapping(target, f"InterventionPlan.targets[{index}]", target_errors)
        if target_data is not None:
            _enum(target_data, "family", {"skill", "integration", "resource"}, target_errors)
            _enum(target_data, "priority", {"primary", "secondary", "companion"}, target_errors)
            _required_string(target_data, "rationale", target_errors)
            _unexpected(target_data, {"family", "priority", "rationale"}, target_errors)
            if isinstance(target_data.get("family"), str):
                families.add(target_data["family"])
            if target_data.get("priority") == "primary":
                primary_count += 1
        errors.extend(f"targets[{index}].{error}" for error in target_errors)
    if len(families) > 2:
        errors.append("targets may contain at most 2 distinct families")
    if plan.get("decision") in {"no_intervention", "clarify"} and targets:
        errors.append(f"decision={plan.get('decision')} requires targets=[]")
    if plan.get("decision") == "search" and primary_count < 1:
        errors.append("decision=search requires at least one primary target")
    _unexpected(plan, {"decision", "targets", "decision_reason"}, errors)
    if errors:
        raise ContractValidationError("InterventionPlan", errors)
    return dict(plan)


def validate_query_plan(value: Any) -> dict[str, Any]:
    """Validate QueryPlanResult and its early-stop invariants."""

    errors: list[str] = []
    result = _mapping(value, "QueryPlanResult", errors)
    if result is None:
        raise ContractValidationError("QueryPlanResult", errors)
    _enum(result, "status", {"ready", "skipped", "clarify"}, errors)
    queries = result.get("queries")
    if not isinstance(queries, list):
        errors.append("queries must be a list")
        queries = []
    if len(queries) > 5:
        errors.append("queries may contain at most 5 items")
    for index, query in enumerate(queries):
        query_errors: list[str] = []
        query_data = _mapping(query, f"QueryPlanResult.queries[{index}]", query_errors)
        if query_data is not None:
            _enum(query_data, "family", {"skill", "integration", "resource"}, query_errors)
            _enum(query_data, "angle", {"capability", "problem", "outcome", "operation", "professional_vocabulary", "stage"}, query_errors)
            _required_string(query_data, "semantic_query", query_errors)
            _required_string(query_data, "purpose", query_errors)
            _unexpected(query_data, {"family", "angle", "semantic_query", "purpose"}, query_errors)
        errors.extend(f"queries[{index}].{error}" for error in query_errors)
    if result.get("status") in {"skipped", "clarify"} and queries:
        errors.append(f"status={result.get('status')} requires queries=[]")
    if result.get("status") == "ready" and not queries:
        errors.append("status=ready requires at least one query")
    _unexpected(result, {"status", "queries"}, errors)
    if errors:
        raise ContractValidationError("QueryPlanResult", errors)
    return dict(result)
