#!/usr/bin/env python3
"""Run Checkpoint 4 from preserved Evidence Packs through Final Advice."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from skillnudge.judge import JudgeRuntime
from skillnudge.planning_model import LiveModelProviderUnavailable, OpenAICompatibleModel


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run SkillNudge Checkpoint 4")
    parser.add_argument(
        "--run-dir",
        type=Path,
        required=True,
        help="Existing Checkpoint 3 run directory; planning and retrieval are not rerun",
    )
    args = parser.parse_args(argv)

    model = OpenAICompatibleModel.from_environment()
    try:
        result = JudgeRuntime(model).run(args.run_dir)
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
