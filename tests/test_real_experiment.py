import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from skillnudge.experiment_runner import (  # noqa: E402
    Condition,
    ExecutionBudget,
    ExecutionPolicy,
    SkillExposureRenderer,
    TaskArtifact,
    TraceRecorder,
    fixture_skill_payload,
)
from skillnudge.real_experiment import (  # noqa: E402
    CodingModelConfig,
    ModelResponse,
    REAL_HARNESS_VERSION,
    ReadinessWorkspaceOracle,
    RealCodingAgentAdapter,
    WorkspaceToolError,
    WorkspaceToolExecutor,
    create_readiness_task_bundle,
    default_tool_manifest,
    environment_identity,
    fetch_frozen_skill_artifact,
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
            result = adapter.run(task, Condition.control(), trace)

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
            result = adapter.run(task, Condition.control(), trace)
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
                bundle.task,
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
                artifact.verification_error.split(": ", 1)[0],
                "FROZEN_SKILL_MANIFEST_MISMATCH",
            )
            self.assertEqual(len(artifact.file_hashes), 4)


if __name__ == "__main__":
    unittest.main()
