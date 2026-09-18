#!/usr/bin/env python3
"""Run the live Checkpoint 2 planning runtime without Candidate Acquisition."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from skillnudge.planning import InputEnvelope, PlanningRuntime
from skillnudge.planning_model import LiveModelProviderUnavailable, OpenAICompatibleModel


def _default_run_dir() -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path(__file__).resolve().parents[1] / "runs" / f"planning-{timestamp}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run SkillNudge Checkpoint 2 planning")
    parser.add_argument("--request", required=True, help="Raw user request")
    parser.add_argument("--run-dir", type=Path, default=_default_run_dir())
    parser.add_argument("--project-context")
    parser.add_argument("--current-stage")
    args = parser.parse_args(argv)

    model = OpenAICompatibleModel.from_environment()
    runtime = PlanningRuntime(model)
    envelope = InputEnvelope(
        raw_request=args.request,
        project_context=args.project_context,
        current_stage=args.current_stage,
    )
    try:
        result = runtime.run(envelope, args.run_dir)
    except LiveModelProviderUnavailable:
        print("LIVE_MODEL_PROVIDER_UNAVAILABLE", file=sys.stderr)
        return 2
    except Exception as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
