"""Generate one deterministic Control/Treatment plumbing fixture."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from skillnudge.experiment_runner import (
    Condition,
    ExecutionBudget,
    ExperimentRunner,
    FixtureAgent,
    FixtureAgentAdapter,
    FixtureOracle,
    SkillExposureRenderer,
    TaskArtifact,
    fixture_skill_payload,
    write_pair_manifest,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate the local non-benchmark causal experiment fixture"
    )
    parser.add_argument(
        "--run-root",
        type=Path,
        default=Path("runs/causal-runtime-fixture-v0.1"),
    )
    args = parser.parse_args()

    task = TaskArtifact(
        task_id="fixture-debug-task-001",
        repository="fixture/example-project",
        commit="fixture-base-commit",
        test_command="python -m unittest",
    )
    adapter = FixtureAgentAdapter(
        execution_agent=FixtureAgent(
            result={
                "patch": "fixture-visible-patch",
                "summary": "fixture agent completed the visible task",
            },
            steps=4,
            tokens=128,
            latency_ms=12.0,
            events=(
                ("tool_call", {"tool": "shell", "command": "python -m unittest"}),
                ("tool_result", {"tool": "shell", "exit_code": 0}),
                ("test_execution", {"command": "python -m unittest", "passed": 1}),
                ("patch_generated", {"files": ["src/example.py"]}),
                ("verification", {"kind": "target", "passed": True}),
            ),
        ),
        renderer=SkillExposureRenderer(
            fixture_skill_payload(),
            artifact_mode="synthetic_fixture",
        ),
        model="fixture-model",
        harness_version="fixture-harness-v0",
        tool_manifest={
            "filesystem": "isolated-fixture",
            "shell": "fixture",
            "git": "fixture",
            "test_runner": "python -m unittest",
        },
        execution_budget=ExecutionBudget(
            max_steps=8,
            max_tool_calls=16,
            max_tokens=4_000,
            max_latency_ms=30_000,
        ),
        environment_hash="fixture-environment-sha256",
    )
    runner = ExperimentRunner(
        adapter,
        FixtureOracle(),
        clock=lambda: "2026-09-19T00:00:00+00:00",
    )

    results = {}
    run_results = {}
    for condition in (Condition.control(), Condition.treatment()):
        result = runner.run(
            task,
            experiment_id="causal-runtime-fixture-v0.1",
            condition=condition,
            run_dir=args.run_root / condition.name,
        )
        run_results[condition.name] = result
        results[condition.name] = {
            "run_dir": result.run_dir,
            "condition": result.run.condition.as_dict(),
            "skill_payload_hash": result.run.skill_payload_hash,
            "outcome_status": result.evidence.outcome.status,
        }

    pair = write_pair_manifest(
        args.run_root / "pair_manifest.json",
        run_results["control"].run,
        run_results["treatment"].run,
        control_task=task,
        treatment_task=task,
    )
    results["pair"] = {
        "pair_manifest": str(args.run_root / "pair_manifest.json"),
        "pair_status": pair.pair_status,
        "errors": pair.errors,
    }
    print(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
