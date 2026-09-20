"""Phase 1 Advise runtime and its concise user-facing rendering."""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .candidate_runtime import CandidateAcquisitionError, CandidateAcquisitionRuntime, CandidateRuntimeResult
from .judge import JudgeRunResult, JudgeRuntime
from .planning import InputEnvelope, PlanningRunResult, PlanningRuntime
from .planning_contracts import (
    validate_capability_framing,
    validate_input_envelope,
    validate_intervention_plan,
    validate_planning_consistency,
    validate_query_plan,
)
from .planning_model import PlanningModel


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUNS_DIR = REPO_ROOT / "runs"


class Phase1RuntimeError(RuntimeError):
    """Raised when the composed Phase 1 runtime cannot continue safely."""


def default_run_dir(root: str | Path = REPO_ROOT) -> Path:
    """Return a collision-resistant local run directory."""

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path(root) / "runs" / f"advise-{timestamp}-{uuid.uuid4().hex[:8]}"


def default_database_path(root: str | Path = REPO_ROOT) -> Path:
    """Find a local Checkpoint 1 index without requiring a committed corpus."""

    root_path = Path(root)
    configured = os.environ.get("SKILLNUDGE_DATABASE")
    if configured:
        return Path(configured).expanduser()

    candidates = [
        path
        for path in (root_path / "runs").glob("*/skills.sqlite3")
        if path.is_file()
    ]
    if candidates:
        return max(candidates, key=lambda path: path.stat().st_mtime)
    return root_path / "runs" / "skillnudge.sqlite3"


def _append_trace(
    path: Path,
    run_id: str,
    event: str,
    stage: str,
    details: Mapping[str, Any] | None = None,
) -> None:
    record = {
        "schema_version": "trace.event.phase1.v0",
        "run_id": run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "stage": stage,
        "details": dict(details or {}),
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


@dataclass(frozen=True)
class Phase1RunResult:
    run_id: str
    run_dir: str
    planning: PlanningRunResult
    candidate_runtime: CandidateRuntimeResult
    judge: JudgeRunResult

    @property
    def final_advice(self) -> dict[str, Any]:
        return self.judge.final_advice

    def as_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "run_dir": self.run_dir,
            "planning": self.planning.as_dict(),
            "candidate_runtime": self.candidate_runtime.as_dict(),
            "judge": self.judge.as_dict(),
        }


class Phase1Runtime:
    """Compose the existing Planning, Acquisition, and Judge runtimes."""

    def __init__(self, model: PlanningModel, database_path: str | Path):
        self.model = model
        self.database_path = Path(database_path)

    def run(self, envelope: InputEnvelope, run_dir: str | Path) -> Phase1RunResult:
        output_dir = Path(run_dir)
        if output_dir.exists() and any(output_dir.iterdir()):
            raise Phase1RuntimeError(
                "PHASE1_RUN_DIR_EXISTS: use --resume with the existing run directory"
            )
        output_dir.mkdir(parents=True, exist_ok=True)
        run_id = output_dir.name
        trace_path = output_dir / "trace.jsonl"
        try:
            planning = PlanningRuntime(self.model).run(
                envelope,
                output_dir,
                emit_run_completed=False,
            )
            if (
                planning.intervention_plan["decision"] == "search"
                and planning.query_plan["status"] != "clarify"
                and not self.database_path.is_file()
            ):
                raise CandidateAcquisitionError(
                    "SKILLNUDGE_DATABASE_NOT_FOUND: pass --database or set "
                    "SKILLNUDGE_DATABASE to a local Checkpoint 1 SQLite index"
                )
            candidate_runtime = CandidateAcquisitionRuntime(self.database_path).run(planning)
            judge = JudgeRuntime(self.model).run(output_dir)
            _append_trace(
                trace_path,
                run_id,
                "run_completed",
                "Phase 1 Runtime",
                {
                    "status": judge.final_advice["status"],
                    "candidate_acquisition_status": (
                        candidate_runtime.acquisition or {}
                    ).get("status"),
                    "hydrated_candidate_count": (
                        candidate_runtime.evidence_packs or {}
                    ).get("hydrated_candidate_count", 0),
                    "judged_candidate_count": len(judge.judgements),
                    "judge_call_count": judge.judge_call_count,
                    "resumed_judgement_count": judge.resumed_judgement_count,
                    "final_advice_call_count": judge.final_advice_call_count,
                },
            )
            return Phase1RunResult(
                run_id=run_id,
                run_dir=str(output_dir),
                planning=planning,
                candidate_runtime=candidate_runtime,
                judge=judge,
            )
        except Exception as error:
            if trace_path.exists():
                _append_trace(
                    trace_path,
                    run_id,
                    "run_failed",
                    "Phase 1 Runtime",
                    {
                        "error_type": type(error).__name__,
                        "error": str(error),
                    },
                )
            raise

    def resume(self, run_dir: str | Path) -> Phase1RunResult:
        """Resume Candidate Judgement from an existing Phase 1 artifact set."""

        output_dir = Path(run_dir)
        trace_path = output_dir / "trace.jsonl"
        if not trace_path.exists():
            raise Phase1RuntimeError("PHASE1_RESUME_ARTIFACTS_MISSING: trace.jsonl")
        planning = self._load_planning_result(output_dir)
        acquisition_path = output_dir / "04_candidate_acquisition.json"
        evidence_path = output_dir / "05_evidence_packs.json"
        if planning.intervention_plan["decision"] == "search" and not evidence_path.exists():
            raise Phase1RuntimeError(
                "PHASE1_RESUME_NOT_READY: Evidence Packs are missing; "
                "resume only supports interrupted Candidate Judgement"
            )
        acquisition = (
            json.loads(acquisition_path.read_text(encoding="utf-8"))
            if acquisition_path.exists()
            else None
        )
        evidence = (
            json.loads(evidence_path.read_text(encoding="utf-8"))
            if evidence_path.exists()
            else None
        )
        candidate_runtime = CandidateRuntimeResult(
            run_id=planning.run_id,
            run_dir=str(output_dir),
            acquisition=acquisition,
            evidence_packs=evidence,
        )
        _append_trace(
            trace_path,
            planning.run_id,
            "run_resumed",
            "Phase 1 Runtime",
            {
                "from_stage": "Candidate Judgement",
                "planning_rerun": False,
                "candidate_acquisition_rerun": False,
            },
        )
        try:
            judge = JudgeRuntime(self.model).run(output_dir)
            _append_trace(
                trace_path,
                planning.run_id,
                "run_completed",
                "Phase 1 Runtime",
                {
                    "status": judge.final_advice["status"],
                    "resumed": True,
                    "judged_candidate_count": len(judge.judgements),
                    "judge_call_count": judge.judge_call_count,
                    "resumed_judgement_count": judge.resumed_judgement_count,
                    "final_advice_call_count": judge.final_advice_call_count,
                },
            )
        except Exception as error:
            _append_trace(
                trace_path,
                planning.run_id,
                "run_failed",
                "Phase 1 Runtime",
                {
                    "error_type": type(error).__name__,
                    "error": str(error),
                    "resumed": True,
                },
            )
            raise
        return Phase1RunResult(
            run_id=planning.run_id,
            run_dir=str(output_dir),
            planning=planning,
            candidate_runtime=candidate_runtime,
            judge=judge,
        )

    @staticmethod
    def _load_planning_result(output_dir: Path) -> PlanningRunResult:
        def read(name: str) -> dict[str, Any]:
            path = output_dir / name
            if not path.exists():
                raise Phase1RuntimeError(f"PHASE1_RESUME_ARTIFACTS_MISSING: {name}")
            value = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                raise Phase1RuntimeError(f"{name} must contain a JSON object")
            return value

        input_artifact = read("00_input.json")
        input_data = validate_input_envelope(input_artifact.get("input", input_artifact))
        capability = validate_capability_framing(read("01_capability_contract.json"))
        intervention = validate_intervention_plan(read("02_intervention_plan.json"))
        query = validate_query_plan(read("03_query_plan.json"))
        validate_planning_consistency(intervention, query)
        return PlanningRunResult(
            run_id=output_dir.name,
            run_dir=str(output_dir),
            input_envelope=input_data,
            capability_framing=capability,
            intervention_plan=intervention,
            query_plan=query,
        )


def _display_ref(label: str, value: Mapping[str, Any] | None) -> str | None:
    if value is None:
        return None
    name = value.get("name") or value.get("candidate_id") or "unnamed candidate"
    reason = value.get("reason")
    if isinstance(reason, str) and reason.strip():
        return f"{label}: {name} — {reason}"
    return f"{label}: {name}"


def render_advice(advice: Mapping[str, Any]) -> str:
    """Render Final Advice without exposing internal prompts or chain-of-thought."""

    status = advice.get("status")
    if status == "recommendation":
        lines = ["Recommendation"]
        for label, key in (
            ("Primary", "primary"),
            ("Supporting", "supporting"),
            ("Companion", "companion"),
        ):
            rendered = _display_ref(label, advice.get(key))
            if rendered:
                lines.append(rendered)
        uncertainties = advice.get("uncertainties") or []
        if uncertainties:
            lines.append("Important uncertainties:")
            lines.extend(f"- {item}" for item in uncertainties)
        return "\n".join(lines)
    if status == "no_intervention":
        return "No additional capability appears necessary now."
    if status == "needs_clarification":
        uncertainties = advice.get("uncertainties") or []
        question = uncertainties[0] if uncertainties else "Please clarify the intended capability."
        return f"Needs clarification: {question}"
    if status == "source_error":
        lines = ["I could not evaluate the required intervention source."]
    elif status == "insufficient_evidence":
        lines = ["I do not have enough evidence to make a responsible recommendation."]
    else:
        lines = [f"Final Advice status: {status or 'unknown'}"]
    uncertainties = advice.get("uncertainties") or []
    if uncertainties:
        lines.append("Limitations:")
        lines.extend(f"- {item}" for item in uncertainties)
    return "\n".join(lines)


def render_trace_summary(result: Phase1RunResult) -> str:
    """Return the small trace footer used by ``--trace``."""

    stages = ["planning"]
    if result.candidate_runtime.acquisition is not None:
        stages.append("candidate acquisition")
    if result.candidate_runtime.evidence_packs is not None:
        stages.append("evidence hydration")
    if result.judge.judge_call_count or result.candidate_runtime.acquisition is not None:
        stages.append("candidate judgement")
    stages.append("final advice")
    return "\n".join(
        [
            f"Trace: {result.run_dir}",
            f"Stages: {' -> '.join(stages)} ({result.final_advice['status']})",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    """Run the development CLI."""

    import argparse
    import sys

    parser = argparse.ArgumentParser(prog="skillnudge")
    subparsers = parser.add_subparsers(dest="command", required=True)
    advise = subparsers.add_parser("advise", help="run the Phase 1 capability advisor")
    advise.add_argument("request", nargs="?", help="raw user request")
    advise.add_argument(
        "--stdin",
        action="store_true",
        help="read the raw user request from standard input",
    )
    advise.add_argument("--trace", action="store_true", help="show the local run artifact path")
    advise.add_argument("--run-dir", type=Path, help="explicit local artifact directory")
    advise.add_argument("--database", type=Path, help="local Checkpoint 1 SQLite index")
    advise.add_argument(
        "--resume",
        action="store_true",
        help="resume Candidate Judgement from an existing run directory",
    )
    advise.add_argument("--project-context")
    advise.add_argument("--current-stage")
    advise.add_argument(
        "--json",
        action="store_true",
        help="print the bounded runtime summary as JSON instead of human-readable advice",
    )
    args = parser.parse_args(argv)

    if args.command != "advise":
        parser.error(f"unsupported command: {args.command}")

    if args.request is None and not args.stdin:
        parser.error("provide a request argument or use --stdin")
    if args.request is not None and args.stdin:
        parser.error("request argument and --stdin are mutually exclusive")
    request = sys.stdin.read() if args.stdin else args.request
    if not request or not request.strip():
        parser.error("the raw user request must not be empty")

    if args.resume and args.run_dir is None:
        parser.error("--resume requires --run-dir")
    run_dir = args.run_dir or default_run_dir()
    database_path = args.database or default_database_path()
    envelope = InputEnvelope(
        raw_request=request,
        project_context=args.project_context,
        current_stage=args.current_stage,
    )
    from .planning_model import LiveModelProviderUnavailable, OpenAICompatibleModel

    try:
        runtime = Phase1Runtime(OpenAICompatibleModel.from_environment(), database_path)
        result = runtime.resume(run_dir) if args.resume else runtime.run(envelope, run_dir)
    except LiveModelProviderUnavailable:
        print(
            "LIVE_MODEL_PROVIDER_UNAVAILABLE: configure the ignored "
            "config/provider.local.env or SKILLNUDGE_MODEL_* environment variables.",
            file=sys.stderr,
        )
        return 2
    except Exception as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
    else:
        print(render_advice(result.final_advice))
    if args.trace and not args.json:
        print(render_trace_summary(result))
    elif args.trace and args.json:
        print(f"Trace: {result.run_dir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
