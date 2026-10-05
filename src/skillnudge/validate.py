"""Provider-free Native Validate MVP.

The host performs the two bounded task executions and submits observable arm
records. SkillNudge owns the frozen intervention identity, parity checks, Oracle
evaluation, pair validity, scoped conclusion, and durable receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .bootstrap import default_data_dir


VALIDATION_ENVELOPE_SCHEMA_VERSION = "native.validation-envelope.v0"
VALIDATION_RESULT_SCHEMA_VERSION = "native.validation-result.v0"
TRACE_SCHEMA_VERSION = "trace.event.native-validate.v0"
_DISPOSITIONS = {"TEST"}
_OUTCOMES = {"HELPS", "NEUTRAL", "HURTS", "INCONCLUSIVE", "NOT_EVALUATED"}
_PRIVATE_FIELDS = {"chain_of_thought", "hidden_reasoning", "internal_reasoning", "private_reasoning", "scratchpad"}


class ValidationContractError(ValueError):
    """Raised when a Native Validation Envelope is unsafe or incomplete."""


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValidationContractError(f"{path} must be an object")
    return value


def _keys(value: Mapping[str, Any], path: str, required: set[str], allowed: set[str]) -> None:
    missing = sorted(required - set(value))
    extra = sorted(set(value) - allowed)
    if missing:
        raise ValidationContractError(f"{path} missing required fields: {missing}")
    if extra:
        raise ValidationContractError(f"{path} has unexpected fields: {extra}")


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationContractError(f"{path} must be a non-empty string")
    return value


def _bool(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise ValidationContractError(f"{path} must be boolean")
    return value


def _scan_private(value: Any, path: str = "envelope") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in _PRIVATE_FIELDS:
                raise ValidationContractError(f"{path}.{key} is not allowed")
            _scan_private(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_private(child, f"{path}[{index}]")


def _event_list(value: Any, path: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ValidationContractError(f"{path} must be a non-empty list")
    events: list[dict[str, Any]] = []
    ids: list[str] = []
    for index, raw in enumerate(value):
        event = _mapping(raw, f"{path}[{index}]")
        _keys(event, f"{path}[{index}]", {"event_id", "kind", "summary", "source_ref"}, {"event_id", "kind", "summary", "source_ref"})
        item = {key: _string(event[key], f"{path}[{index}].{key}") for key in ("event_id", "kind", "summary", "source_ref")}
        ids.append(item["event_id"])
        events.append(item)
    if len(ids) != len(set(ids)):
        raise ValidationContractError(f"{path} contains duplicate event_id values")
    return events


def _validate_review_result(value: Any) -> dict[str, Any]:
    review = _mapping(value, "review_result")
    _keys(review, "review_result", {"schema_version", "experience_id", "disposition", "assessment", "evidence", "intervention_candidate", "provider", "run_id", "run_dir"}, {"schema_version", "experience_id", "disposition", "problem", "assessment", "evidence", "intervention_candidate", "provider", "run_id", "run_dir"})
    if review["schema_version"] != "native.review-result.v0":
        raise ValidationContractError("review_result.schema_version must be native.review-result.v0")
    if review["disposition"] not in _DISPOSITIONS:
        raise ValidationContractError("review_result.disposition must be TEST")
    if review["provider"] is not None:
        raise ValidationContractError("review_result.provider must be null for Native Mode")
    assessment = _mapping(review["assessment"], "review_result.assessment")
    _keys(assessment, "review_result.assessment", {"impact", "attribution", "addressability", "testability", "uncertainty"}, {"impact", "attribution", "addressability", "testability", "uncertainty"})
    if assessment["addressability"] != "plausible" or assessment["testability"] != "testable":
        raise ValidationContractError("TEST review result requires plausible addressability and testable validation")
    uncertainty = assessment["uncertainty"]
    if not isinstance(uncertainty, list) or not all(isinstance(item, str) and item.strip() for item in uncertainty):
        raise ValidationContractError("review_result.assessment.uncertainty must be a list of non-empty strings")
    evidence = _mapping(review["evidence"], "review_result.evidence")
    _keys(evidence, "review_result.evidence", {"referenced_event_ids"}, {"referenced_event_ids"})
    evidence_ids = evidence["referenced_event_ids"]
    if not isinstance(evidence_ids, list) or not evidence_ids or not all(isinstance(item, str) and item.strip() for item in evidence_ids):
        raise ValidationContractError("review_result.evidence.referenced_event_ids must be non-empty")
    candidate = _mapping(review["intervention_candidate"], "review_result.intervention_candidate")
    _keys(candidate, "review_result.intervention_candidate", {"title", "target_behavior", "intervention_hypothesis", "evidence_refs"}, {"title", "target_behavior", "intervention_hypothesis", "evidence_refs"})
    refs = candidate["evidence_refs"]
    if not isinstance(refs, list) or not refs or not all(isinstance(item, str) and item.strip() for item in refs):
        raise ValidationContractError("review_result.intervention_candidate.evidence_refs must be non-empty")
    if not set(refs).issubset(set(evidence_ids)):
        raise ValidationContractError("review candidate evidence_refs must resolve in Review result evidence")
    return {"schema_version": review["schema_version"], "experience_id": _string(review["experience_id"], "review_result.experience_id"), "disposition": "TEST", "assessment": dict(assessment), "evidence": {"referenced_event_ids": list(evidence_ids)}, "provider": None, "run_id": _string(review["run_id"], "review_result.run_id"), "run_dir": _string(review["run_dir"], "review_result.run_dir"), "intervention_candidate": {key: (list(candidate[key]) if key == "evidence_refs" else _string(candidate[key], f"review_result.intervention_candidate.{key}")) for key in ("title", "target_behavior", "intervention_hypothesis", "evidence_refs")}}


def _validate_spec(value: Any) -> dict[str, Any]:
    spec = _mapping(value, "validation_spec")
    _keys(spec, "validation_spec", {"frozen_at", "task", "intervention", "oracle", "execution"}, {"frozen_at", "task", "intervention", "oracle", "execution"})
    frozen_at = _timestamp(spec["frozen_at"], "validation_spec.frozen_at")
    task = _mapping(spec["task"], "validation_spec.task")
    _keys(task, "validation_spec.task", {"task_id", "description", "observable_success_condition"}, {"task_id", "description", "observable_success_condition"})
    intervention = _mapping(spec["intervention"], "validation_spec.intervention")
    _keys(intervention, "validation_spec.intervention", {"type", "exact_content", "sha256"}, {"type", "exact_content", "sha256"})
    if intervention["type"] != "instruction":
        raise ValidationContractError("validation_spec.intervention.type must be instruction")
    exact_content = _string(intervention["exact_content"], "validation_spec.intervention.exact_content")
    expected_hash = _string(intervention["sha256"], "validation_spec.intervention.sha256")
    actual_hash = hashlib.sha256(exact_content.encode("utf-8")).hexdigest()
    if expected_hash != actual_hash:
        raise ValidationContractError("validation_spec.intervention.sha256 does not match exact_content")
    oracle = _mapping(spec["oracle"], "validation_spec.oracle")
    _keys(oracle, "validation_spec.oracle", {"type", "field", "expected"}, {"type", "field", "expected"})
    if oracle["type"] != "result_field_equals":
        raise ValidationContractError("validation_spec.oracle.type must be result_field_equals")
    field = _string(oracle["field"], "validation_spec.oracle.field")
    if not isinstance(oracle["expected"], (str, int, float, bool)):
        raise ValidationContractError("validation_spec.oracle.expected must be a scalar")
    execution = _mapping(spec["execution"], "validation_spec.execution")
    _keys(execution, "validation_spec.execution", {"bounded", "mode"}, {"bounded", "mode"})
    if execution["bounded"] is not True or execution["mode"] != "host_observed_arms":
        raise ValidationContractError("validation_spec.execution must be bounded host_observed_arms")
    return {"frozen_at": frozen_at.isoformat(), "task": {key: _string(task[key], f"validation_spec.task.{key}") for key in ("task_id", "description", "observable_success_condition")}, "intervention": {"type": "instruction", "exact_content": exact_content, "sha256": expected_hash}, "oracle": {"type": "result_field_equals", "field": field, "expected": oracle["expected"]}, "execution": {"bounded": True, "mode": "host_observed_arms"}}


def _validate_arm(value: Any, path: str, *, treatment: bool, intervention_sha256: str) -> dict[str, Any]:
    arm = _mapping(value, path)
    required = {"result", "observable_events", "intervention_applied", "intervention_identity", "execution_context", "started_at"}
    allowed = required | {"execution_valid", "execution_errors"}
    _keys(arm, path, required, allowed)
    result = _mapping(arm["result"], f"{path}.result")
    if not result:
        raise ValidationContractError(f"{path}.result must not be empty")
    events = _event_list(arm["observable_events"], f"{path}.observable_events")
    applied = _bool(arm["intervention_applied"], f"{path}.intervention_applied")
    if applied != treatment:
        raise ValidationContractError(f"{path}.intervention_applied does not match condition")
    identity = arm.get("intervention_identity")
    if treatment:
        if identity != intervention_sha256:
            raise ValidationContractError(f"{path}.intervention_identity must match frozen intervention hash")
    elif identity is not None:
        raise ValidationContractError(f"{path}.intervention_identity must be null for control")
    context = _mapping(arm["execution_context"], f"{path}.execution_context")
    context_keys = {"task_id", "reference_host", "model", "harness_version", "tool_manifest", "execution_budget", "environment_hash"}
    _keys(context, f"{path}.execution_context", context_keys, context_keys)
    for key in ("task_id", "reference_host", "model", "harness_version", "environment_hash"):
        _string(context[key], f"{path}.execution_context.{key}")
    if not isinstance(context["tool_manifest"], Mapping) or not isinstance(context["execution_budget"], Mapping):
        raise ValidationContractError(f"{path}.execution_context tool_manifest and execution_budget must be objects")
    started_at = _timestamp(arm["started_at"], f"{path}.started_at")
    execution_valid = arm.get("execution_valid", True)
    if not isinstance(execution_valid, bool):
        raise ValidationContractError(f"{path}.execution_valid must be boolean")
    execution_errors = arm.get("execution_errors", [])
    if not isinstance(execution_errors, list) or not all(isinstance(item, str) and item.strip() for item in execution_errors):
        raise ValidationContractError(f"{path}.execution_errors must be a list of non-empty strings")
    return {"result": dict(result), "observable_events": events, "intervention_applied": applied, "intervention_identity": identity, "execution_context": dict(context), "started_at": started_at.isoformat(), "execution_valid": execution_valid, "execution_errors": list(execution_errors)}


def _timestamp(value: Any, path: str) -> datetime:
    raw = _string(value, path)
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValidationContractError(f"{path} must be an ISO-8601 timestamp") from error
    if parsed.tzinfo is None:
        raise ValidationContractError(f"{path} must include a timezone")
    return parsed


def validate_validation_envelope(value: Any) -> dict[str, Any]:
    _scan_private(value)
    envelope = _mapping(value, "envelope")
    _keys(envelope, "envelope", {"schema_version", "review_result", "validation_spec", "execution"}, {"schema_version", "review_result", "validation_spec", "execution"})
    if envelope["schema_version"] != VALIDATION_ENVELOPE_SCHEMA_VERSION:
        raise ValidationContractError(f"schema_version must be {VALIDATION_ENVELOPE_SCHEMA_VERSION!r}")
    review = _validate_review_result(envelope["review_result"])
    spec = _validate_spec(envelope["validation_spec"])
    execution = _mapping(envelope["execution"], "execution")
    _keys(execution, "execution", {"control", "treatment"}, {"control", "treatment"})
    control = _validate_arm(execution["control"], "execution.control", treatment=False, intervention_sha256=spec["intervention"]["sha256"])
    treatment = _validate_arm(execution["treatment"], "execution.treatment", treatment=True, intervention_sha256=spec["intervention"]["sha256"])
    if control["execution_context"] != treatment["execution_context"]:
        raise ValidationContractError("control and treatment execution_context must match exactly")
    task_id = spec["task"]["task_id"]
    if control["execution_context"]["task_id"] != task_id:
        raise ValidationContractError("arm execution_context.task_id must match frozen validation task")
    frozen_at = datetime.fromisoformat(spec["frozen_at"])
    if any(datetime.fromisoformat(arm["started_at"]) <= frozen_at for arm in (control, treatment)):
        raise ValidationContractError("validation spec and Oracle must be frozen before both arms start")
    return {"schema_version": VALIDATION_ENVELOPE_SCHEMA_VERSION, "review_result": review, "validation_spec": spec, "execution": {"control": control, "treatment": treatment}}


def _oracle(arm: Mapping[str, Any], oracle: Mapping[str, Any]) -> dict[str, Any]:
    field = oracle["field"]
    observed = arm["result"].get(field)
    expected = oracle["expected"]
    success = observed == expected
    return {"evaluator_valid": True, "success": success, "regression": False, "status": "success" if success else "failure", "field": field, "observed": observed, "expected": expected}


def default_validate_run_dir() -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return default_data_dir() / "validate-runs" / f"validate-{timestamp}-{uuid.uuid4().hex[:8]}"


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _trace(path: Path, run_id: str, event: str, details: Mapping[str, Any] | None = None) -> None:
    record = {"schema_version": TRACE_SCHEMA_VERSION, "run_id": run_id, "timestamp": datetime.now(timezone.utc).isoformat(), "event": event, "stage": "Native Validate", "details": dict(details or {})}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def run_validation(envelope: Any, *, run_dir: str | Path | None = None) -> dict[str, Any]:
    validated = validate_validation_envelope(envelope)
    output_dir = Path(run_dir) if run_dir is not None else default_validate_run_dir()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise RuntimeError("VALIDATE_RUN_DIR_EXISTS: choose a new run directory")
    output_dir.mkdir(parents=True, exist_ok=True)
    run_id = output_dir.name
    trace_path = output_dir / "trace.jsonl"
    _write_json(output_dir / "00_validation_envelope.json", validated)
    _trace(trace_path, run_id, "validation_input_received", {"experience_id": validated["review_result"]["experience_id"]})
    _trace(trace_path, run_id, "validation_spec_frozen", {"task_id": validated["validation_spec"]["task"]["task_id"], "intervention_sha256": validated["validation_spec"]["intervention"]["sha256"]})
    _trace(trace_path, run_id, "control_treatment_parity_validated", {"mode": validated["validation_spec"]["execution"]["mode"]})
    control_oracle = _oracle(validated["execution"]["control"], validated["validation_spec"]["oracle"])
    treatment_oracle = _oracle(validated["execution"]["treatment"], validated["validation_spec"]["oracle"])
    control_pass = control_oracle["success"] is True
    treatment_pass = treatment_oracle["success"] is True
    if treatment_pass and not control_pass:
        outcome = "HELPS"
    elif control_pass and not treatment_pass:
        outcome = "HURTS"
    elif control_pass and treatment_pass:
        outcome = "NEUTRAL"
    else:
        outcome = "INCONCLUSIVE"
    pair_status = "VALID" if validated["execution"]["control"]["execution_valid"] and validated["execution"]["treatment"]["execution_valid"] else "INVALID"
    if pair_status == "INVALID":
        outcome = "NOT_EVALUATED"
        control_oracle = {"evaluator_valid": False, "status": "not_evaluated", "diagnostics": validated["execution"]["control"]["execution_errors"]}
        treatment_oracle = {"evaluator_valid": False, "status": "not_evaluated", "diagnostics": validated["execution"]["treatment"]["execution_errors"]}
    _trace(trace_path, run_id, "oracle_evaluated", {"control_success": control_pass, "treatment_success": treatment_pass, "evaluated": pair_status == "VALID"})
    context = validated["execution"]["control"]["execution_context"]
    result = {"schema_version": VALIDATION_RESULT_SCHEMA_VERSION, "run_id": run_id, "experience_id": validated["review_result"]["experience_id"], "task_id": validated["validation_spec"]["task"]["task_id"], "pair_status": pair_status, "validation_result": outcome, "scope": {"task_id": validated["validation_spec"]["task"]["task_id"], "intervention_sha256": validated["validation_spec"]["intervention"]["sha256"], "reference_host": context["reference_host"], "model": context["model"]}, "control": {"oracle": control_oracle, "observable_event_ids": [item["event_id"] for item in validated["execution"]["control"]["observable_events"]]}, "treatment": {"oracle": treatment_oracle, "observable_event_ids": [item["event_id"] for item in validated["execution"]["treatment"]["observable_events"]]}, "limitations": ["One bounded task only.", "Host-observed arm records; no provider or universal utility claim.", "No promotion, rewrite, or lifecycle decision."]}
    _write_json(output_dir / "01_validation_result.json", result)
    _trace(trace_path, run_id, "validation_result_emitted", {"pair_status": pair_status, "validation_result": outcome})
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="skillnudge validate")
    parser.add_argument("--stdin", action="store_true", help="read a Native Validation Envelope from standard input")
    parser.add_argument("--run-dir", type=Path, help="explicit local artifact directory")
    args = parser.parse_args(argv)
    if not args.stdin:
        parser.error("validate requires --stdin")
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            raise ValidationContractError("the validation envelope must not be empty")
        result = run_validation(json.loads(raw), run_dir=args.run_dir)
    except (json.JSONDecodeError, ValidationContractError, RuntimeError, OSError) as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
