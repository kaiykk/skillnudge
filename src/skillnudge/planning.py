"""Checkpoint 2 planning runtime: framing, intervention, and query planning."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from .planning_contracts import (
    ContractValidationError,
    validate_capability_framing,
    validate_input_envelope,
    validate_intervention_plan,
    validate_query_plan,
)
from .planning_model import PlanningModel
from .prompts import (
    PROMPT_VERSIONS,
    capability_prompt,
    intervention_prompt,
    query_prompt,
    repair_prompt,
)


class PlanningStageError(RuntimeError):
    """A planning stage failed after its allowed repair attempt."""


@dataclass(frozen=True)
class InputEnvelope:
    """Minimal intake boundary; raw_request is preserved exactly."""

    raw_request: str
    project_context: Any = None
    current_stage: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "raw_request": self.raw_request,
            "project_context": self.project_context,
            "current_stage": self.current_stage,
        }


@dataclass(frozen=True)
class PlanningRunResult:
    run_id: str
    run_dir: str
    input_envelope: dict[str, Any]
    capability_framing: dict[str, Any]
    intervention_plan: dict[str, Any]
    query_plan: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "run_dir": self.run_dir,
            "input": self.input_envelope,
            "capability_framing": self.capability_framing,
            "intervention_plan": self.intervention_plan,
            "query_plan": self.query_plan,
        }


class _TraceWriter:
    def __init__(self, path: Path, run_id: str):
        self.path = path
        self.run_id = run_id
        self.path.write_text("", encoding="utf-8")

    def emit(self, event: str, stage: str, details: Mapping[str, Any] | None = None) -> None:
        record = {
            "schema_version": "trace.event.planning.v0",
            "run_id": self.run_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "stage": stage,
            "details": dict(details or {}),
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _parse_model_response(response: Any) -> dict[str, Any]:
    if isinstance(response, Mapping):
        return dict(response)
    if not isinstance(response, str):
        raise ValueError("model response must be a JSON object or JSON text")
    parsed = json.loads(response)
    if not isinstance(parsed, Mapping):
        raise ValueError("model JSON must be an object")
    return dict(parsed)


def _error_details(error: Exception) -> dict[str, Any]:
    return {"error_type": type(error).__name__, "error": str(error)}


class PlanningRuntime:
    """Run only the frozen planning stages and stop before Candidate Acquisition."""

    def __init__(self, model: PlanningModel):
        self.model = model

    def run(self, envelope: InputEnvelope, run_dir: str | Path) -> PlanningRunResult:
        input_data = validate_input_envelope(envelope.as_dict())
        output_dir = Path(run_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        run_id = output_dir.name
        trace = _TraceWriter(output_dir / "trace.jsonl", run_id)
        trace.emit("run_started", "Planning Runtime", {"checkpoint": 2})
        _write_json(
            output_dir / "00_input.json",
            {"schema_version": "checkpoint2.input.v0", "run_id": run_id, "input": input_data},
        )

        capability_result = self._model_stage(
            trace=trace,
            stage="Capability Framing",
            prompt_version=PROMPT_VERSIONS["capability"],
            prompt=capability_prompt(input_data),
            validator=validate_capability_framing,
        )
        _write_json(output_dir / "01_capability_contract.json", capability_result)

        if capability_result["clarification_needed"]:
            intervention_result = self._derived_stage(
                trace=trace,
                stage="Intervention Planning",
                value={
                    "decision": "clarify",
                    "targets": [],
                    "decision_reason": "Clarification is required before choosing an intervention family.",
                },
                validator=validate_intervention_plan,
                reason="capability framing requires clarification",
            )
            _write_json(output_dir / "02_intervention_plan.json", intervention_result)
            query_result = self._derived_stage(
                trace=trace,
                stage="Query Planning",
                value={"status": "clarify", "queries": []},
                validator=validate_query_plan,
                reason="intervention planning stopped for clarification",
            )
            trace.emit("early_stop", "Query Planning", {"status": "clarify"})
        else:
            intervention_result = self._model_stage(
                trace=trace,
                stage="Intervention Planning",
                prompt_version=PROMPT_VERSIONS["intervention"],
                prompt=intervention_prompt(capability_result),
                validator=validate_intervention_plan,
            )
            _write_json(output_dir / "02_intervention_plan.json", intervention_result)
            if intervention_result["decision"] == "no_intervention":
                query_result = self._derived_stage(
                    trace=trace,
                    stage="Query Planning",
                    value={"status": "skipped", "queries": []},
                    validator=validate_query_plan,
                    reason="intervention plan selected no_intervention",
                )
                trace.emit("early_stop", "Query Planning", {"status": "skipped"})
            elif intervention_result["decision"] == "clarify":
                query_result = self._derived_stage(
                    trace=trace,
                    stage="Query Planning",
                    value={"status": "clarify", "queries": []},
                    validator=validate_query_plan,
                    reason="intervention plan selected clarify",
                )
                trace.emit("early_stop", "Query Planning", {"status": "clarify"})
            else:
                query_result = self._model_stage(
                    trace=trace,
                    stage="Query Planning",
                    prompt_version=PROMPT_VERSIONS["query"],
                    prompt=query_prompt(capability_result, intervention_result),
                    validator=validate_query_plan,
                )
        _write_json(output_dir / "03_query_plan.json", query_result)
        trace.emit("run_completed", "Planning Runtime", {"candidate_acquisition_invoked": False})
        return PlanningRunResult(
            run_id=run_id,
            run_dir=str(output_dir),
            input_envelope=input_data,
            capability_framing=capability_result,
            intervention_plan=intervention_result,
            query_plan=query_result,
        )

    def _model_stage(
        self,
        *,
        trace: _TraceWriter,
        stage: str,
        prompt_version: str,
        prompt: str,
        validator: Callable[[Any], dict[str, Any]],
    ) -> dict[str, Any]:
        trace.emit("stage_start", stage, {"prompt_version": prompt_version})
        current_prompt = prompt
        invalid_response: Any = None
        errors: list[str] = []
        for repair_attempt in range(2):
            started = time.perf_counter()
            try:
                response = self.model.generate_structured(
                    stage=stage,
                    prompt=current_prompt,
                    prompt_version=prompt_version,
                )
            except Exception as error:
                trace.emit(
                    "model_call",
                    stage,
                    {
                        "provider": getattr(self.model, "provider_name", "unknown"),
                        "model": getattr(self.model, "model_name", "unknown"),
                        "prompt_version": prompt_version,
                        "repair_attempt": repair_attempt,
                        "success": False,
                        "latency_ms": round((time.perf_counter() - started) * 1000, 2),
                    },
                )
                trace.emit("error", stage, _error_details(error))
                raise
            trace.emit(
                "model_call",
                stage,
                {
                    "provider": getattr(self.model, "provider_name", "unknown"),
                    "model": getattr(self.model, "model_name", "unknown"),
                    "prompt_version": prompt_version,
                    "repair_attempt": repair_attempt,
                    "success": True,
                    "latency_ms": round((time.perf_counter() - started) * 1000, 2),
                },
            )
            invalid_response = response
            try:
                parsed = _parse_model_response(response)
                validated = validator(parsed)
            except (ContractValidationError, ValueError) as error:
                errors = error.errors if isinstance(error, ContractValidationError) else [str(error)]
                trace.emit(
                    "validation_result",
                    stage,
                    {"valid": False, "repair_attempt": repair_attempt, "errors": errors},
                )
                if repair_attempt == 0:
                    current_prompt = repair_prompt(stage, prompt, invalid_response, errors)
                    continue
                final_error = PlanningStageError(
                    f"{stage} remained invalid after one repair attempt: {'; '.join(errors)}"
                )
                trace.emit("error", stage, _error_details(final_error))
                raise final_error from error
            trace.emit(
                "validation_result",
                stage,
                {"valid": True, "repair_attempt": repair_attempt},
            )
            trace.emit("stage_complete", stage, {"repair_attempt": repair_attempt})
            return validated
        raise AssertionError("unreachable")

    @staticmethod
    def _derived_stage(
        *,
        trace: _TraceWriter,
        stage: str,
        value: dict[str, Any],
        validator: Callable[[Any], dict[str, Any]],
        reason: str,
    ) -> dict[str, Any]:
        trace.emit("stage_start", stage, {"source": "early_stop"})
        try:
            validated = validator(value)
        except ContractValidationError as error:
            trace.emit("validation_result", stage, {"valid": False, "errors": error.errors})
            trace.emit("error", stage, _error_details(error))
            raise
        trace.emit("validation_result", stage, {"valid": True, "source": "early_stop"})
        trace.emit("stage_complete", stage, {"source": "early_stop", "reason": reason})
        return validated
