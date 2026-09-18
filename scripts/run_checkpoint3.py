#!/usr/bin/env python3
"""Run Checkpoint 3 from live planning through local evidence hydration."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from skillnudge.candidate_runtime import CandidateAcquisitionRuntime
from skillnudge.planning import InputEnvelope, PlanningRuntime
from skillnudge.planning_model import LiveModelProviderUnavailable, OpenAICompatibleModel


def _default_run_dir(case_id: str | None) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    label = case_id or "planning"
    return Path(__file__).resolve().parents[1] / "runs" / f"{label}-checkpoint3-live-{timestamp}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run SkillNudge Checkpoint 3")
    parser.add_argument("--request", required=True, help="Raw user request")
    parser.add_argument("--database", type=Path, required=True, help="Existing Checkpoint 1 SQLite index")
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--case-id")
    parser.add_argument("--project-context")
    parser.add_argument("--current-stage")
    args = parser.parse_args(argv)

    run_dir = args.run_dir or _default_run_dir(args.case_id)
    model = OpenAICompatibleModel.from_environment()
    planning_runtime = PlanningRuntime(model)
    envelope = InputEnvelope(
        raw_request=args.request,
        project_context=args.project_context,
        current_stage=args.current_stage,
    )
    try:
        planning_result = planning_runtime.run(envelope, run_dir)
        candidate_result = CandidateAcquisitionRuntime(args.database).run(planning_result)
    except LiveModelProviderUnavailable:
        print("LIVE_MODEL_PROVIDER_UNAVAILABLE", file=sys.stderr)
        return 2
    except Exception as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "planning": planning_result.as_dict(),
                "candidate_runtime": candidate_result.as_dict(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

