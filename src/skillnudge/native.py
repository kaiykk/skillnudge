"""Provider-free Native Mode handoff into deterministic retrieval."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .bootstrap import BootstrapResult, bootstrap_default_index
from .candidate_runtime import CandidateAcquisitionRuntime, CandidateRuntimeResult
from .planning_contracts import (
    ContractValidationError,
    validate_capability_framing,
    validate_input_envelope,
    validate_intervention_plan,
    validate_planning_consistency,
    validate_query_plan,
)


NATIVE_RETRIEVAL_SCHEMA_VERSION = "native.retrieve.v0"
NATIVE_PLANNING_SCHEMA_VERSION = "native.planning-envelope.v0"


@dataclass(frozen=True)
class NativePlanningResult:
    """Structural planning result consumed by CandidateAcquisitionRuntime."""

    run_id: str
    run_dir: str
    input_envelope: dict[str, Any]
    capability_framing: dict[str, Any]
    intervention_plan: dict[str, Any]
    query_plan: dict[str, Any]


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _append_trace(
    path: Path,
    run_id: str,
    event: str,
    details: Mapping[str, Any] | None = None,
) -> None:
    record = {
        "schema_version": "trace.event.native.v0",
        "run_id": run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "stage": "Native Retrieval",
        "details": dict(details or {}),
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def validate_native_planning_envelope(value: Any) -> NativePlanningResult:
    """Validate host-produced planning artifacts without loading a provider."""

    errors: list[str] = []
    if not isinstance(value, Mapping):
        raise ContractValidationError(
            "NativePlanningEnvelope",
            ["response must be a JSON object"],
        )
    allowed = {
        "schema_version",
        "input",
        "capability_framing",
        "intervention_plan",
        "query_plan",
    }
    unexpected = sorted(set(value) - allowed)
    if unexpected:
        errors.append(f"unexpected fields: {unexpected}")
    if value.get("schema_version") not in {None, NATIVE_PLANNING_SCHEMA_VERSION}:
        errors.append(
            f"schema_version must be {NATIVE_PLANNING_SCHEMA_VERSION!r} when provided"
        )
    required = (
        "input",
        "capability_framing",
        "intervention_plan",
        "query_plan",
    )
    for key in required:
        if key not in value:
            errors.append(f"missing required field: {key}")
    if errors:
        raise ContractValidationError("NativePlanningEnvelope", errors)

    input_envelope = validate_input_envelope(value["input"])
    capability = validate_capability_framing(value["capability_framing"])
    intervention = validate_intervention_plan(value["intervention_plan"])
    query = validate_query_plan(value["query_plan"])
    validate_planning_consistency(intervention, query)
    return NativePlanningResult(
        run_id="",
        run_dir="",
        input_envelope=input_envelope,
        capability_framing=capability,
        intervention_plan=intervention,
        query_plan=query,
    )


def default_native_run_dir() -> Path:
    """Return a user-data run directory independent of the source checkout."""

    from .bootstrap import default_data_dir

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return (
        default_data_dir()
        / "runs"
        / f"native-retrieve-{timestamp}-{uuid.uuid4().hex[:8]}"
    )


def run_native_retrieval(
    envelope: Any,
    *,
    database_path: str | Path,
    run_dir: str | Path,
) -> CandidateRuntimeResult:
    """Run deterministic acquisition from host-produced planning artifacts."""

    validated = validate_native_planning_envelope(envelope)
    output_dir = Path(run_dir)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise RuntimeError(
            "NATIVE_RUN_DIR_EXISTS: choose a new run directory"
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    run_id = output_dir.name
    planning = NativePlanningResult(
        run_id=run_id,
        run_dir=str(output_dir),
        input_envelope=validated.input_envelope,
        capability_framing=validated.capability_framing,
        intervention_plan=validated.intervention_plan,
        query_plan=validated.query_plan,
    )
    _write_json(
        output_dir / "00_input.json",
        {
            "schema_version": "native.input.v0",
            "run_id": run_id,
            "input": planning.input_envelope,
        },
    )
    _write_json(
        output_dir / "01_capability_contract.json",
        planning.capability_framing,
    )
    _write_json(
        output_dir / "02_intervention_plan.json",
        planning.intervention_plan,
    )
    _write_json(output_dir / "03_query_plan.json", planning.query_plan)
    _append_trace(
        output_dir / "trace.jsonl",
        run_id,
        "planning_handoff_validated",
        {
            "decision": planning.intervention_plan["decision"],
            "query_status": planning.query_plan["status"],
            "provider": None,
        },
    )
    return CandidateAcquisitionRuntime(database_path).run(planning)


def _result_as_dict(
    result: CandidateRuntimeResult,
    *,
    bootstrap: BootstrapResult | None,
) -> dict[str, Any]:
    payload = result.as_dict()
    payload.update(
        {
            "schema_version": NATIVE_RETRIEVAL_SCHEMA_VERSION,
            "mode": "native",
            "provider": None,
            "bootstrap": bootstrap.as_dict() if bootstrap is not None else None,
        }
    )
    return payload


def main(argv: list[str] | None = None) -> int:
    """Read a planning envelope and return deterministic evidence as JSON."""

    import argparse
    import sys

    parser = argparse.ArgumentParser(prog="skillnudge retrieve")
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="read the host-produced planning envelope from standard input",
    )
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--database", type=Path)
    args = parser.parse_args(argv)
    if not args.stdin:
        parser.error("retrieve requires --stdin")

    try:
        raw = sys.stdin.read()
        if not raw.strip():
            raise ValueError("the planning envelope must not be empty")
        envelope = json.loads(raw)
        bootstrap = None
        database_path = args.database
        if database_path is None:
            bootstrap = bootstrap_default_index()
            database_path = Path(bootstrap.database_path)
        result = run_native_retrieval(
            envelope,
            database_path=database_path,
            run_dir=args.run_dir or default_native_run_dir(),
        )
    except Exception as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 1

    print(json.dumps(_result_as_dict(result, bootstrap=bootstrap), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
