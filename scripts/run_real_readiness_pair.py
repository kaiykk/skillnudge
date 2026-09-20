"""Run the bounded Phase 2B.0 real Control/Treatment readiness smoke."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from skillnudge.experiment_runner import (  # noqa: E402
    AgentVisibleTask,
    Condition,
    ExecutionBudget,
    ExecutionPolicy,
    ExperimentRunError,
    PairValidationResult,
    OracleArtifact,
    ExperimentRunner,
    SkillExposureRenderer,
    validate_pair_manifest,
    write_pair_manifest,
)
from skillnudge.real_experiment import (  # noqa: E402
    READINESS_EXPERIMENT_ID,
    REAL_HARNESS_VERSION,
    CodingModelConfig,
    OpenAICompatibleCodingModel,
    ProviderCapabilityProbe,
    ReadinessWorkspaceOracle,
    RealCodingAgentAdapter,
    RealExecutionError,
    create_readiness_task_bundle,
    default_tool_manifest,
    environment_identity,
    fetch_frozen_skill_artifact,
    probe_provider_capabilities,
)


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _blocked_pair(
    *,
    experiment_id: str,
    task_id: str,
    control_run_id: str,
    errors: list[str],
) -> PairValidationResult:
    return PairValidationResult(
        experiment_id=experiment_id,
        task_id=task_id,
        control_run_id=control_run_id,
        treatment_run_id="not-created",
        shared_configuration_identity="not-computed",
        pair_status="PROTOCOL_FAILURE",
        errors=errors,
    )


def _default_run_root() -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return ROOT / "runs" / f"phase2b0-real-readiness-{stamp}"


def _persist_preflight_blocker(
    run_root: Path,
    *,
    blocker: str,
    provider_configuration: object = "unavailable; credentials omitted",
    preflight: dict[str, object] | None = None,
) -> None:
    pair = _blocked_pair(
        experiment_id=READINESS_EXPERIMENT_ID,
        task_id="phase2b0-readiness-discount-001",
        control_run_id="not-created",
        errors=[blocker],
    )
    manifest = pair.as_dict()
    validate_pair_manifest(manifest)
    _write_json(run_root / "pair_manifest.json", manifest)
    _write_json(
        run_root / "shared_preflight.json",
        preflight
        or {
            "status": "FAIL",
            "arms_launched": False,
            "blockers": [blocker],
        },
    )
    _write_json(
        run_root / "readiness_result.json",
        {
            "status": "REAL_EXECUTION_NOT_READY",
            "real_pair_executed": False,
            "shared_preflight": "FAIL",
            "provider_configuration": provider_configuration,
            "blockers": [blocker],
        },
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run one real Control/Treatment readiness smoke, never a utility pilot."
    )
    parser.add_argument("--run-root", type=Path, default=_default_run_root())
    parser.add_argument(
        "--skill-source",
        type=Path,
        default=None,
        help="external directory containing the exact frozen four-file source unit",
    )
    args = parser.parse_args(argv)
    run_root = args.run_root
    if run_root.exists() and any(run_root.iterdir()):
        print(f"Run root must be empty: {run_root}", file=sys.stderr)
        return 2
    run_root.mkdir(parents=True, exist_ok=True)

    bundle = None
    artifact = None
    try:
        artifact = fetch_frozen_skill_artifact(args.skill_source)
        _write_json(run_root / "skill_artifact_preflight.json", artifact.as_dict())
    except (OSError, RealExecutionError, ValueError) as error:
        _persist_preflight_blocker(run_root, blocker=str(error))
        print(json.dumps({"status": "REAL_EXECUTION_NOT_READY", "blockers": [str(error)]}))
        return 0

    if not artifact.verified:
        blocker = artifact.verification_error or "FROZEN_SKILL_ARTIFACT_NOT_VERIFIED"
        _persist_preflight_blocker(
            run_root,
            blocker=blocker,
            preflight={
                "status": "FAIL",
                "order": ["skill_provenance"],
                "skill_provenance": "FAIL",
                "provider_probe": "NOT_RUN",
                "workspace_sanity": "NOT_RUN",
                "oracle_self_test": "NOT_RUN",
                "effective_config_freeze": "NOT_RUN",
                "shared_preflight": "FAIL",
                "arms_launched": False,
                "blockers": [blocker],
            },
        )
        print(json.dumps({"status": "REAL_EXECUTION_NOT_READY", "blockers": [blocker]}))
        return 0

    try:
        model = OpenAICompatibleCodingModel.from_environment()
        probe = probe_provider_capabilities(model.config)
        _write_json(run_root / "provider_probe.json", probe.as_dict())
        if probe.status != "PASS":
            raise RealExecutionError("MODEL_PROVIDER_CAPABILITY_PROBE_FAILED")
        model = model.with_probe(probe)
        model_config = model.config.as_dict()
    except (RealExecutionError, ValueError) as error:
        provider_configuration = (
            model.config.as_dict()
            if "model" in locals()
            else "unavailable; credentials omitted"
        )
        _persist_preflight_blocker(
            run_root,
            blocker=str(error),
            provider_configuration=provider_configuration,
        )
        print(json.dumps({"status": "REAL_EXECUTION_NOT_READY", "blockers": [str(error)]}))
        return 0

    oracle = ReadinessWorkspaceOracle()
    try:
        bundle = create_readiness_task_bundle(run_root)
        _write_json(
            run_root / "task.json",
            AgentVisibleTask.from_task(bundle.task).as_dict(),
        )
        _write_json(
            run_root / "workspace_manifest.json",
            {
                "base_repository": str(bundle.source_repository),
                "base_commit": bundle.task.commit,
                "control_workspace": str(bundle.control_workspace),
                "treatment_workspace": str(bundle.treatment_workspace),
                "same_base_commit": True,
                "workspace_mode": "isolated_clone_from_same_local_repository",
                "oracle_hidden_directory": str(bundle.hidden_oracle_directory),
                "agent_visibility": {
                    "other_arm": "blocked",
                    "oracle_hidden_directory": "blocked",
                    "credentials": "blocked",
                    "network": "disabled",
                },
            },
        )
        oracle_self_test = oracle.self_test(
            OracleArtifact.from_task(bundle.task),
            bundle.source_repository,
        )
        _write_json(run_root / "oracle_self_test.json", oracle_self_test)
        if oracle_self_test["status"] != "PASS":
            raise RealExecutionError("ORACLE_SELF_TEST_FAILED")
        shared_preflight = {
            "status": "PASS",
            "order": [
                "skill_provenance",
                "provider_probe",
                "workspace_sanity",
                "oracle_self_test",
                "effective_config_freeze",
            ],
            "skill_provenance": "PASS",
            "provider_probe": probe.status,
            "workspace_sanity": "PASS",
            "oracle_self_test": oracle_self_test["status"],
            "effective_config_freeze": "PASS",
            "effective_provider_configuration": model_config,
            "shared_preflight": "PASS",
            "arms_launched": False,
            "blockers": [],
        }
        _write_json(run_root / "shared_preflight.json", shared_preflight)
    except (OSError, RealExecutionError, ValueError) as error:
        _persist_preflight_blocker(
            run_root,
            blocker=str(error),
            provider_configuration=model_config,
        )
        print(json.dumps({"status": "REAL_EXECUTION_NOT_READY", "blockers": [str(error)]}))
        return 0

    renderer = None
    control_result = None
    try:
        renderer = artifact.renderer()
        common_kwargs = {
            "model_client": model,
            "renderer": renderer,
            "model_config": model_config,
            "tool_manifest": default_tool_manifest(),
            "execution_budget": ExecutionBudget(
                max_steps=12,
                max_tool_calls=24,
                max_tokens=6_000,
                max_latency_ms=180_000,
            ),
            "environment_hash": environment_identity(),
            "execution_policy": ExecutionPolicy(
                retry_policy={
                    "transport_retry_limit": 0,
                    "tool_failure_retry_limit": 0,
                    "model_error_retry_limit": 0,
                    "task_level_retry_limit": 0,
                },
                termination_policy={
                    "stop_on_completion": True,
                    "stop_on_failure": True,
                    "budget_enforced": True,
                },
            ),
        }
        control_adapter = RealCodingAgentAdapter(
            workspace=bundle.control_workspace,
            **common_kwargs,
        )
        control_result = ExperimentRunner(control_adapter, oracle).run(
            bundle.task,
            experiment_id=READINESS_EXPERIMENT_ID,
            condition=Condition.control(),
            harness_version=REAL_HARNESS_VERSION,
            run_dir=run_root / "control",
        )
    except (ExperimentRunError, RealExecutionError, OSError, ValueError) as error:
        pair = _blocked_pair(
            experiment_id=READINESS_EXPERIMENT_ID,
            task_id=bundle.task.task_id,
            control_run_id="control-failed",
            errors=[str(error)],
        )
        _write_json(run_root / "pair_manifest.json", pair.as_dict())
        shared_preflight["arms_launched"] = True
        shared_preflight["control_status"] = "FAILED"
        shared_preflight["blockers"] = [str(error)]
        _write_json(run_root / "shared_preflight.json", shared_preflight)
        _write_json(
            run_root / "readiness_result.json",
            {
                "status": "REAL_EXECUTION_NOT_READY",
                "real_pair_executed": False,
                "shared_preflight": "PASS",
                "provider_configuration": model_config,
                "control_run": "failed before complete artifact set",
                "blockers": [str(error)],
            },
        )
        print(json.dumps({"status": "REAL_EXECUTION_NOT_READY", "blockers": [str(error)]}))
        return 0

    try:
        treatment_adapter = RealCodingAgentAdapter(
            workspace=bundle.treatment_workspace,
            **common_kwargs,
        )
        treatment_result = ExperimentRunner(treatment_adapter, oracle).run(
            bundle.task,
            experiment_id=READINESS_EXPERIMENT_ID,
            condition=Condition.treatment(),
            harness_version=REAL_HARNESS_VERSION,
            run_dir=run_root / "treatment",
        )
        missing_responses = []
        for name, result in (
            ("control", control_result),
            ("treatment", treatment_result),
        ):
            observations = result.agent_result.result.get(
                "model_response_observations", []
            )
            if not isinstance(observations, list) or not observations:
                missing_responses.append(f"{name} produced no model response")
        if missing_responses:
            pair = _blocked_pair(
                experiment_id=READINESS_EXPERIMENT_ID,
                task_id=bundle.task.task_id,
                control_run_id=control_result.run.run_id,
                errors=missing_responses,
            )
            validate_pair_manifest(pair.as_dict())
            _write_json(run_root / "pair_manifest.json", pair.as_dict())
            shared_preflight["arms_launched"] = True
            shared_preflight["arms_completed"] = True
            shared_preflight["pair_status"] = pair.pair_status
            shared_preflight["blockers"] = missing_responses
            _write_json(run_root / "shared_preflight.json", shared_preflight)
            summary = {
                "status": "REAL_EXECUTION_NOT_READY",
                "real_pair_executed": True,
                "provider_configuration": model_config,
                "provider_probe": probe.as_dict(),
                "artifact_verified": True,
                "shared_preflight": "PASS",
                "pair_status": pair.pair_status,
                "pair_errors": pair.errors,
                "control": {"run_dir": control_result.run_dir},
                "treatment": {"run_dir": treatment_result.run_dir},
                "blockers": missing_responses,
            }
            _write_json(run_root / "readiness_result.json", summary)
            print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
            return 0
        pair = write_pair_manifest(
            run_root / "pair_manifest.json",
            control_result.run,
            treatment_result.run,
            control_task=bundle.task,
            treatment_task=bundle.task,
        )
        shared_preflight["arms_launched"] = True
        shared_preflight["arms_completed"] = True
        shared_preflight["pair_status"] = pair.pair_status
        _write_json(run_root / "shared_preflight.json", shared_preflight)
        status = (
            "REAL_EXECUTION_READY" if pair.pair_status == "VALID" else "REAL_EXECUTION_NOT_READY"
        )
        summary = {
            "status": status,
            "real_pair_executed": True,
            "provider_configuration": model_config,
            "provider_probe": probe.as_dict(),
            "artifact_verified": True,
            "shared_preflight": "PASS",
            "pair_status": pair.pair_status,
            "pair_errors": pair.errors,
            "control": {
                "run_dir": control_result.run_dir,
                "outcome_status": control_result.evidence.outcome.status,
            },
            "treatment": {
                "run_dir": treatment_result.run_dir,
                "outcome_status": treatment_result.evidence.outcome.status,
            },
        }
        _write_json(run_root / "readiness_result.json", summary)
        print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (ExperimentRunError, RealExecutionError, OSError, ValueError) as error:
        pair = _blocked_pair(
            experiment_id=READINESS_EXPERIMENT_ID,
            task_id=bundle.task.task_id,
            control_run_id=control_result.run.run_id,
            errors=[str(error)],
        )
        validate_pair_manifest(pair.as_dict())
        _write_json(run_root / "pair_manifest.json", pair.as_dict())
        shared_preflight["arms_launched"] = True
        shared_preflight["arms_completed"] = False
        shared_preflight["pair_status"] = pair.pair_status
        shared_preflight["blockers"] = [str(error)]
        _write_json(run_root / "shared_preflight.json", shared_preflight)
        _write_json(
            run_root / "readiness_result.json",
            {
                "status": "REAL_EXECUTION_NOT_READY",
                "real_pair_executed": False,
                "shared_preflight": "PASS",
                "provider_configuration": model_config,
                "control_run": control_result.run_dir,
                "blockers": [str(error)],
            },
        )
        print(json.dumps({"status": "REAL_EXECUTION_NOT_READY", "blockers": [str(error)]}))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
