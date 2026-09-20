import json
import hashlib
import os
import sys
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import run_real_readiness_pair  # noqa: E402

from skillnudge.experiment_runner import (  # noqa: E402
    AgentVisibleTask,
    Condition,
    ExecutionBudget,
    ExecutionPolicy,
    ExperimentRunner,
    OracleArtifact,
    SkillExposureRenderer,
    TaskArtifact,
    TraceRecorder,
    FROZEN_SKILL_FILE_SHA256,
    FROZEN_SKILL_HISTORICAL_MANIFEST_SHA256,
    FROZEN_SKILL_MANIFEST_SHA256,
    canonical_skill_manifest_sha256,
    fixture_skill_payload,
)
from skillnudge.real_experiment import (  # noqa: E402
    CodingModelConfig,
    ModelResponse,
    ProviderCapabilityProbe,
    REAL_HARNESS_VERSION,
    ReadinessWorkspaceOracle,
    RealCodingAgentAdapter,
    WorkspaceToolError,
    WorkspaceToolExecutor,
    create_readiness_task_bundle,
    compare_frozen_skill_provenance,
    default_tool_manifest,
    environment_identity,
    fetch_frozen_skill_artifact,
    probe_provider_capabilities,
)


class FakeCodingModel:
    def __init__(self, responses):
        self.config = CodingModelConfig(
            provider_name="fake",
            endpoint_identity="fake://provider/v1",
            model_name="fake-coder",
            model_revision="fake-revision",
            temperature=0.0,
            top_p=1.0,
            seed=None,
            seed_support="unsupported",
            reasoning_configuration=None,
            max_output_tokens=200,
            timeout_seconds=1.0,
            retry_policy={"transport_retry_limit": 0, "model_error_retry_limit": 0},
            api_key="do-not-persist",
        )
        self.responses = list(responses)
        self.messages = []

    def complete(self, messages, *, max_output_tokens, timeout_seconds):
        self.messages.append(list(messages))
        if not self.responses:
            raise AssertionError("fake response exhausted")
        action = self.responses.pop(0)
        return ModelResponse(action=action, output_tokens=10, model_revision="fake-revision")


def _adapter(model, workspace, *, budget=None):
    return RealCodingAgentAdapter(
        model_client=model,
        renderer=SkillExposureRenderer(),
        workspace=workspace,
        model_config=model.config.as_dict(),
        tool_manifest=default_tool_manifest(),
        execution_budget=budget or ExecutionBudget(max_steps=6, max_tool_calls=6),
        environment_hash=environment_identity(),
        execution_policy=ExecutionPolicy(),
    )


class RealExperimentTests(unittest.TestCase):
    def test_provenance_distinguishes_raw_hashes_from_manifest_serialization(self):
        canonical = canonical_skill_manifest_sha256(FROZEN_SKILL_FILE_SHA256)
        legacy_payload = "".join(
            f"{path} {FROZEN_SKILL_FILE_SHA256[path]}\n"
            for path in FROZEN_SKILL_FILE_SHA256
        )
        legacy = hashlib.sha256(legacy_payload.encode("utf-8")).hexdigest()

        self.assertEqual(canonical, FROZEN_SKILL_MANIFEST_SHA256)
        self.assertEqual(legacy, FROZEN_SKILL_HISTORICAL_MANIFEST_SHA256)
        self.assertNotEqual(canonical, legacy)
        comparison = compare_frozen_skill_provenance(FROZEN_SKILL_FILE_SHA256)
        self.assertTrue(comparison["file_hashes_match"])
        self.assertTrue(comparison["verified"])
        self.assertEqual(comparison["mismatched_paths"], [])

    def test_provenance_one_raw_file_mismatch_blocks(self):
        altered = dict(FROZEN_SKILL_FILE_SHA256)
        path = next(iter(altered))
        altered[path] = "0" * 64
        comparison = compare_frozen_skill_provenance(altered)
        self.assertFalse(comparison["file_hashes_match"])
        self.assertFalse(comparison["verified"])
        self.assertEqual(comparison["mismatched_paths"], [path])

    def test_provider_metadata_omits_credentials(self):
        config = CodingModelConfig(
            provider_name="third-party-openai-compatible",
            endpoint_identity="https://example.test/v1",
            model_name="coding-model",
            model_revision=None,
            temperature=0.0,
            top_p=1.0,
            seed=None,
            seed_support="unknown",
            reasoning_configuration=None,
            max_output_tokens=100,
            timeout_seconds=10,
            retry_policy={},
            api_key="secret-value",
        )
        rendered = json.dumps(config.as_dict())
        self.assertNotIn("secret-value", rendered)
        self.assertNotIn("api_key", config.as_dict())

    def test_coding_adapter_supports_official_deepseek_configuration(self):
        from skillnudge import real_experiment

        with (
            mock.patch.object(
                real_experiment,
                "_read_local_provider_env",
                return_value={
                    "DEEPSEEK_API_KEY": "local-secret",
                    "SKILLNUDGE_MODEL": "deepseek-flash",
                    "SKILLNUDGE_MODEL_BASE_URL": "https://api.deepseek.com",
                },
            ),
            mock.patch.dict(os.environ, {}, clear=True),
        ):
            config = CodingModelConfig.from_environment()

        self.assertEqual(config.provider_name, "deepseek")
        self.assertEqual(config.endpoint_identity, "https://api.deepseek.com")
        self.assertEqual(config.model_name, "deepseek-flash")
        self.assertNotIn("api_key", config.as_dict())

    def test_provider_probe_records_supported_and_unsupported_parameters(self):
        class Response:
            status = 200

            def __init__(self, payload):
                self.payload = payload

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, traceback):
                return False

            def read(self):
                return json.dumps(self.payload).encode("utf-8")

        config = CodingModelConfig(
            provider_name="third-party-openai-compatible",
            endpoint_identity="https://example.test/v1",
            model_name="coding-model",
            model_revision=None,
            temperature=0.0,
            top_p=1.0,
            seed=None,
            seed_support="unknown",
            reasoning_configuration=None,
            max_output_tokens=100,
            timeout_seconds=10,
            retry_policy={},
            api_key="secret-value",
        )

        def fake_urlopen(request, timeout):
            body = json.loads(request.data.decode("utf-8"))
            if "seed" in body:
                raise urllib.error.HTTPError(
                    request.full_url,
                    400,
                    "bad request",
                    {},
                    BytesIO(b'{"error":"unknown parameter seed"}'),
                )
            return Response(
                {
                    "model": "observed-coding-model-2026-09",
                    "choices": [
                        {
                            "message": {
                                "content": '{"type":"final","summary":"probe"}'
                            }
                        }
                    ],
                }
            )

        import urllib.error
        import urllib.request

        with mock.patch("urllib.request.urlopen", side_effect=fake_urlopen):
            probe = probe_provider_capabilities(config)

        self.assertEqual(probe.status, "PASS")
        self.assertEqual(probe.parameter_support["seed"], "unsupported")
        self.assertEqual(probe.parameter_support["response_format"], "supported")
        self.assertEqual(
            probe.observed_model_ids,
            ("observed-coding-model-2026-09",),
        )
        serialized = json.dumps(probe.as_dict())
        self.assertNotIn("secret-value", serialized)
        self.assertEqual(probe.as_dict()["response_bodies"], "omitted")

    def test_agent_visible_task_and_oracle_artifact_are_structurally_separate(self):
        task = TaskArtifact(
            task_id="task-boundary",
            repository="local/task",
            commit="base",
            test_command="python3 -m unittest",
            description="visible task",
            visible_test_command="python3 -m unittest discover -s tests -v",
            oracle_target_command="python3 -m unittest discover -s hidden -v",
            oracle_regression_command="python3 -m unittest discover -s regression -v",
        )
        visible = AgentVisibleTask.from_task(task)
        oracle = OracleArtifact.from_task(task)
        self.assertNotIn("oracle_target_command", visible.as_dict())
        self.assertNotIn("oracle_regression_command", visible.as_dict())
        self.assertEqual(oracle.target_command, task.oracle_target_command)
        self.assertEqual(oracle.regression_command, task.oracle_regression_command)

        with tempfile.TemporaryDirectory() as directory:
            bundle = create_readiness_task_bundle(directory)
            model = FakeCodingModel(
                [{"type": "final", "summary": "no-op for boundary test"}]
            )
            adapter = _adapter(model, bundle.control_workspace)
            result = ExperimentRunner(adapter, ReadinessWorkspaceOracle()).run(
                bundle.task,
                experiment_id="boundary-v0",
                condition=Condition.control(),
                run_dir=Path(directory) / "run",
            )
            persisted_task = json.loads(
                (Path(result.run_dir) / "task.json").read_text(encoding="utf-8")
            )
            self.assertNotIn("oracle_target_command", persisted_task)
            self.assertNotIn("oracle_regression_command", persisted_task)
            self.assertTrue(result.oracle_result.evaluator_valid)

    def test_observed_model_identity_is_persisted_per_response(self):
        with tempfile.TemporaryDirectory() as directory:
            model = FakeCodingModel(
                [
                    {"type": "tool_call", "tool": "shell", "arguments": {"command": "pwd"}},
                    {"type": "final", "summary": "done"},
                ]
            )
            adapter = _adapter(model, directory)
            visible = AgentVisibleTask(
                task_id="identity-task",
                repository="local/task",
                commit="base",
                description="inspect",
                visible_test_command="python3 -m unittest",
            )
            trace = TraceRecorder(Path(directory) / "trace.jsonl", "identity-run")
            result = adapter.run(visible, Condition.control(), trace)
            observations = result.result["model_response_observations"]
            self.assertEqual(len(observations), 2)
            self.assertEqual(
                {item["observed_model_id"] for item in observations},
                {"fake-revision"},
            )

    def test_shared_preflight_failure_launches_zero_arms(self):
        artifact = SimpleNamespace(
            verified=True,
            as_dict=lambda: {"verified": True},
        )
        model_config = SimpleNamespace(
            model_name="probe-model",
            config=SimpleNamespace(
                as_dict=lambda: {"model_identifier": "probe-model", "credentials": "omitted"}
            ),
        )
        failed_probe = SimpleNamespace(
            status="FAIL",
            as_dict=lambda: {"status": "FAIL", "credentials": "omitted"},
        )
        with tempfile.TemporaryDirectory() as directory:
            run_root = Path(directory) / "readiness"
            with (
                mock.patch.object(
                    run_real_readiness_pair,
                    "fetch_frozen_skill_artifact",
                    return_value=artifact,
                ),
                mock.patch.object(
                    run_real_readiness_pair.OpenAICompatibleCodingModel,
                    "from_environment",
                    return_value=model_config,
                ),
                mock.patch.object(
                    run_real_readiness_pair,
                    "probe_provider_capabilities",
                    return_value=failed_probe,
                ),
                mock.patch.object(
                    run_real_readiness_pair,
                    "create_readiness_task_bundle",
                ) as create_bundle,
            ):
                exit_code = run_real_readiness_pair.main(
                    ["--run-root", str(run_root)]
                )
            self.assertEqual(exit_code, 0)
            self.assertFalse(create_bundle.called)
            self.assertFalse((run_root / "control").exists())
            self.assertFalse((run_root / "treatment").exists())
            result = json.loads(
                (run_root / "readiness_result.json").read_text(encoding="utf-8")
            )
            self.assertEqual(result["shared_preflight"], "FAIL")
            self.assertFalse(result["real_pair_executed"])

    def test_workspace_tool_blocks_escape_and_python_code_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            executor = WorkspaceToolExecutor(directory, "python3 -m unittest")
            with self.assertRaises(WorkspaceToolError):
                executor.execute("read_file", {"path": "../outside"}, timeout_seconds=1)
            with self.assertRaises(WorkspaceToolError):
                executor.execute(
                    "shell", {"command": "cat ../outside"}, timeout_seconds=1
                )
            with self.assertRaises(WorkspaceToolError):
                executor.execute(
                    "shell", {"command": "python3 -c 'print(1)'"},
                    timeout_seconds=1,
                )

    def test_real_adapter_records_visible_actions_without_oracle_prompt_leakage(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / "src").mkdir()
            (workspace / "src" / "value.py").write_text("VALUE = 1\n", encoding="utf-8")
            model = FakeCodingModel(
                [
                    {
                        "type": "tool_call",
                        "tool": "read_file",
                        "arguments": {"path": "src/value.py"},
                    },
                    {
                        "type": "tool_call",
                        "tool": "write_file",
                        "arguments": {"path": "src/value.py", "content": "VALUE = 2\n"},
                    },
                    {"type": "final", "summary": "patched the value"},
                ]
            )
            adapter = _adapter(model, workspace)
            trace = TraceRecorder(workspace / "trace.jsonl", "run-1")
            task = TaskArtifact(
                task_id="task-1",
                repository="local/task",
                commit="base",
                test_command="python3 -m unittest",
                description="Change VALUE from one to two.",
                oracle_target_command="hidden-target-command",
                oracle_regression_command="hidden-regression-command",
            )
            result = adapter.run(
                AgentVisibleTask.from_task(task),
                Condition.control(),
                trace,
            )

            self.assertEqual(result.result["status"], "completed")
            self.assertEqual(
                (workspace / "src" / "value.py").read_text(encoding="utf-8"),
                "VALUE = 2\n",
            )
            event_names = [event.event for event in trace.events]
            self.assertEqual(
                event_names,
                ["tool_call", "tool_result", "tool_call", "tool_result", "patch_generated"],
            )
            prompt_text = json.dumps(model.messages)
            self.assertNotIn("hidden-target-command", prompt_text)
            self.assertNotIn("hidden-regression-command", prompt_text)
            self.assertNotIn('"role": "tool"', prompt_text)
            self.assertTrue(
                any(
                    message.get("role") == "user"
                    and json.loads(message["content"]).get("type") == "tool_result"
                    for call in model.messages
                    for message in call
                    if isinstance(message, dict)
                    and message.get("role") == "user"
                    and isinstance(message.get("content"), str)
                    and message.get("content", "").startswith("{")
                )
            )

    def test_real_adapter_enforces_step_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            model = FakeCodingModel(
                [
                    {
                        "type": "tool_call",
                        "tool": "shell",
                        "arguments": {"command": "pwd"},
                    },
                    {
                        "type": "tool_call",
                        "tool": "shell",
                        "arguments": {"command": "pwd"},
                    },
                ]
            )
            adapter = _adapter(
                model,
                directory,
                budget=ExecutionBudget(max_steps=1, max_tool_calls=4, max_latency_ms=10_000),
            )
            trace = TraceRecorder(Path(directory) / "trace.jsonl", "run-2")
            task = TaskArtifact(
                task_id="task-2",
                repository="local/task",
                commit="base",
                test_command="python3 -m unittest",
                description="Inspect the repository.",
            )
            result = adapter.run(
                AgentVisibleTask.from_task(task),
                Condition.control(),
                trace,
            )
            self.assertEqual(result.result["termination_reason"], "max_steps")
            self.assertEqual(trace.events[-1].event, "failure")
            self.assertEqual(trace.events[-1].details["category"], "budget")

    def test_readiness_oracle_evaluates_post_agent_workspace(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = create_readiness_task_bundle(directory)
            fixed = (bundle.control_workspace / "src" / "price.py")
            fixed.write_text(
                "def apply_discount(amount, percent):\n"
                "    return round(amount - amount * (percent / 100), 2)\n",
                encoding="utf-8",
            )
            result = ReadinessWorkspaceOracle().evaluate(
                OracleArtifact.from_task(bundle.task),
                {"workspace_reference": str(bundle.control_workspace)},
            )
            self.assertTrue(result.evaluator_valid)
            self.assertTrue(result.success)
            self.assertFalse(result.regression)
            self.assertEqual(result.target_status, "pass")
            self.assertEqual(result.regression_status, "pass")

    def test_frozen_artifact_preflight_does_not_accept_synthetic_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            for path, content in fixture_skill_payload().items():
                target = source / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
            artifact = fetch_frozen_skill_artifact(source)
            self.assertFalse(artifact.verified)
            self.assertEqual(
                artifact.verification_error.split(":", 1)[0],
                "FROZEN_SKILL_FILE_HASH_MISMATCH",
            )
            self.assertEqual(len(artifact.file_hashes), 4)


if __name__ == "__main__":
    unittest.main()
