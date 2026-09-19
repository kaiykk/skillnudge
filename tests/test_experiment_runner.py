import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from skillnudge.experiment_runner import (
    AgentExecutionContext,
    ExecutionBudget,
    Condition,
    ExperimentRun,
    ExperimentRunError,
    ExperimentRunner,
    ExperimentSchemaError,
    FixtureAgent,
    FixtureAgentAdapter,
    FixtureOracle,
    OracleResult,
    SkillExposureRenderer,
    SYSTEMATIC_DEBUGGING_SKILL,
    TaskArtifact,
    TraceRecorder,
    FROZEN_SKILL_ARTIFACT_ID,
    FROZEN_SKILL_MANIFEST_SHA256,
    FROZEN_SKILL_SOURCE_PATHS,
    fixture_skill_payload,
    validate_experiment_run,
    validate_trace_event,
    validate_utility_evidence,
)


class TestFixtureOracle:
    def __init__(self, result: OracleResult):
        self.result = result

    def evaluate(self, task: TaskArtifact, result):
        return self.result


class CapturingOracle:
    oracle_version = "capturing-oracle-v0"

    def __init__(self):
        self.seen_result = None

    def evaluate(self, task: TaskArtifact, result):
        self.seen_result = result
        return OracleResult(
            success=True,
            regression=False,
            diagnostics=["captured visible result"],
            tests_passed=1,
            evaluator_valid=True,
        )


def _task() -> TaskArtifact:
    return TaskArtifact(
        task_id="task-001",
        repository="example/project",
        commit="abc123",
        test_command="python -m unittest",
    )


class ExperimentRunnerTests(unittest.TestCase):
    def _run(self, root: str, condition: Condition, *, oracle: OracleResult | None = None):
        agent = FixtureAgent(
            result={"patch": "visible patch artifact"},
            steps=4,
            tokens=123,
            latency_ms=45.5,
            events=(
                ("tool_call", {"tool": "shell", "command": "python -m unittest"}),
                ("tool_result", {"tool": "shell", "exit_code": 1}),
                ("test_execution", {"command": "python -m unittest", "passed": 2}),
                ("patch_generated", {"files": ["src/example.py"]}),
                ("verification", {"kind": "regression", "passed": True}),
            ),
        )
        adapter = FixtureAgentAdapter(
            execution_agent=agent,
            renderer=SkillExposureRenderer(fixture_skill_payload()),
            model="fixture-model",
            harness_version="fixture-harness-v0",
            tool_manifest={"filesystem": "isolated", "shell": "fixture"},
            execution_budget=ExecutionBudget(),
            environment_hash="env-sha256",
        )
        return ExperimentRunner(
            adapter,
            TestFixtureOracle(
                oracle
                or OracleResult(
                    success=True,
                    regression=False,
                    diagnostics=["target and regression checks passed"],
                    tests_passed=2,
                )
            ),
        ).run(
            _task(),
            experiment_id="skill-utility-v0.1",
            condition=condition,
            model="fixture-model",
            harness_version="fixture-harness-v0",
            environment_hash="env-sha256",
            tool_manifest={"filesystem": "isolated", "shell": "fixture"},
            run_dir=Path(root) / condition.name,
        )

    def test_control_run_persists_control_condition_and_outcome_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self._run(directory, Condition.control())

            self.assertIsNone(result.run.condition.skill)
            self.assertEqual(result.evidence.outcome.status, "success")
            self.assertTrue((Path(directory) / "control/experiment_run.json").exists())
            evidence = json.loads(
                (Path(directory) / "control/utility_evidence.json").read_text()
            )
            self.assertEqual(evidence["condition"], {"skill": None})
            self.assertNotIn("utility_score", evidence)

    def test_treatment_run_persists_only_the_supported_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self._run(directory, Condition.treatment())

            self.assertEqual(result.run.condition.skill, SYSTEMATIC_DEBUGGING_SKILL)
            self.assertEqual(result.run.skill_version, SYSTEMATIC_DEBUGGING_SKILL)
            self.assertEqual(
                json.loads(
                    (Path(directory) / "treatment/experiment_run.json").read_text()
                )["condition"]["skill"],
                SYSTEMATIC_DEBUGGING_SKILL,
            )

    def test_trace_generation_allows_only_observable_events(self):
        with tempfile.TemporaryDirectory() as directory:
            trace_path = Path(directory) / "trace.jsonl"
            trace = TraceRecorder(trace_path, "run-1")
            trace.emit("tool_call", {"tool": "shell", "command": "pytest"})
            trace.emit("verification", {"passed": True})

            records = [
                json.loads(line)
                for line in trace_path.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual([record["event"] for record in records], ["tool_call", "verification"])
            self.assertEqual(len(trace.events), 2)
            with self.assertRaises(ExperimentSchemaError):
                trace.emit("tool_call", {"chain_of_thought": "must not persist"})

    def test_evidence_generation_keeps_dimensions_separate(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self._run(
                directory,
                Condition.control(),
                oracle=OracleResult(
                    success=False,
                    regression=True,
                    diagnostics=["regression detected"],
                    tests_passed=1,
                ),
            )

            evidence = result.evidence.as_dict()
            self.assertEqual(evidence["outcome"]["status"], "failure")
            self.assertEqual(evidence["outcome"]["tests_passed"], 1)
            self.assertEqual(evidence["trajectory"]["steps"], 4)
            self.assertEqual(evidence["trajectory"]["tool_calls"], 1)
            self.assertEqual(evidence["trajectory"]["verification_count"], 2)
            self.assertEqual(evidence["cost"]["tokens"], 123)
            self.assertEqual(evidence["cost"]["latency_ms"], 45.5)
            self.assertNotIn("score", evidence)
            validate_utility_evidence(evidence)

    def test_schema_validation_rejects_invalid_condition_and_run(self):
        with self.assertRaises(ExperimentSchemaError):
            Condition.from_value({"skill": "other-skill"})

        valid = ExperimentRun(
            run_id="run-1",
            experiment_id="experiment-1",
            task_id="task-001",
            condition=Condition.control(),
            model="fixture-model",
            harness_version="fixture-harness-v0",
            skill_version=None,
            tool_manifest={"shell": "fixture"},
            environment_hash="env-sha256",
            timestamp="2026-09-19T00:00:00+00:00",
        ).as_dict()
        invalid = {**valid, "skill_version": SYSTEMATIC_DEBUGGING_SKILL}
        with self.assertRaises(ExperimentSchemaError):
            validate_experiment_run(invalid)

        with self.assertRaises(ExperimentSchemaError):
            validate_trace_event(
                {
                    "schema_version": "trace.event.experiment.v0",
                    "run_id": "run-1",
                    "timestamp": "now",
                    "event": "hidden_thought",
                    "details": {},
                }
            )

    def test_existing_run_directory_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory) / "existing"
            run_dir.mkdir()
            (run_dir / "sentinel").write_text("keep", encoding="utf-8")
            runner = ExperimentRunner(
                FixtureAgent(), TestFixtureOracle(OracleResult(None, None, ["unknown"]))
            )
            with self.assertRaises(ExperimentRunError):
                runner.run(
                    _task(),
                    experiment_id="experiment-1",
                    condition=Condition.control(),
                    model="fixture-model",
                    harness_version="fixture-harness-v0",
                    environment_hash="env-sha256",
                    run_dir=run_dir,
                )
            self.assertEqual((run_dir / "sentinel").read_text(), "keep")

    def test_skill_renderer_exposes_only_the_frozen_four_file_unit(self):
        renderer = SkillExposureRenderer(fixture_skill_payload())
        control = renderer.render(Condition.control())
        treatment = renderer.render(Condition.treatment())

        self.assertEqual(control.visible_context, "")
        self.assertIsNone(control.payload_hash)
        self.assertEqual(treatment.skill_identity, FROZEN_SKILL_ARTIFACT_ID)
        self.assertEqual(
            treatment.skill_identity,
            "systematic-debugging-superpowers-v6.4.1-source-unit",
        )
        self.assertEqual(treatment.skill_version, "v6.4.1")
        self.assertEqual(treatment.file_paths, FROZEN_SKILL_SOURCE_PATHS)
        self.assertTrue(treatment.payload_hash)
        self.assertTrue(treatment.manifest_hash)
        self.assertNotEqual(treatment.manifest_hash, FROZEN_SKILL_MANIFEST_SHA256)
        for path in FROZEN_SKILL_SOURCE_PATHS:
            self.assertIn(path, treatment.visible_context)

        with self.assertRaises(ValueError):
            SkillExposureRenderer(
                {
                    **fixture_skill_payload(),
                    "skills/other/SKILL.md": "must not be included",
                }
            )

    def test_empty_renderer_supports_control_but_blocks_treatment(self):
        renderer = SkillExposureRenderer()
        self.assertEqual(renderer.render(Condition.control()).visible_context, "")
        with self.assertRaises(ExperimentRunError):
            renderer.render(Condition.treatment())

    def test_treatment_cannot_bypass_the_static_skill_adapter(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = ExperimentRunner(
                FixtureAgent(),
                TestFixtureOracle(
                    OracleResult(
                        success=True,
                        regression=False,
                        diagnostics=["fixture"],
                    )
                ),
            )
            with self.assertRaisesRegex(
                ExperimentRunError, "treatment requires an AgentAdapter"
            ):
                runner.run(
                    _task(),
                    experiment_id="causal-fixture-v0.1",
                    condition=Condition.treatment(),
                    model="fixture-model",
                    harness_version="fixture-harness-v0",
                    environment_hash="env-sha256",
                    run_dir=Path(directory) / "treatment",
                )

    def test_agent_adapter_context_and_manifest_differ_only_by_skill(self):
        execution_agent = FixtureAgent(result={"patch": "fixture patch"})
        adapter = FixtureAgentAdapter(
            execution_agent=execution_agent,
            renderer=SkillExposureRenderer(fixture_skill_payload()),
            model="fixture-model",
            harness_version="fixture-harness-v0",
            tool_manifest={"filesystem": "isolated", "shell": "fixture"},
            execution_budget=ExecutionBudget(max_steps=7, max_tool_calls=9),
            environment_hash="env-sha256",
        )
        control_context = adapter.context_for(Condition.control())
        treatment_context = adapter.context_for(Condition.treatment())

        self.assertIsInstance(control_context, AgentExecutionContext)
        self.assertEqual(control_context.visible_context, "")
        self.assertIsNone(control_context.skill_payload_hash)
        self.assertEqual(treatment_context.skill_identity, FROZEN_SKILL_ARTIFACT_ID)
        self.assertNotEqual(treatment_context.skill_payload_hash, None)
        self.assertEqual(control_context.model, treatment_context.model)
        self.assertEqual(
            control_context.harness_version, treatment_context.harness_version
        )
        self.assertEqual(control_context.tool_manifest, treatment_context.tool_manifest)
        self.assertEqual(
            control_context.execution_budget, treatment_context.execution_budget
        )
        self.assertEqual(
            control_context.environment_hash, treatment_context.environment_hash
        )

        with tempfile.TemporaryDirectory() as directory:
            runner = ExperimentRunner(
                adapter,
                FixtureOracle(),
                clock=lambda: "2026-09-19T00:00:00+00:00",
            )
            control = runner.run(
                _task(),
                experiment_id="causal-fixture-v0.1",
                condition=Condition.control(),
                run_dir=Path(directory) / "control",
            )
            treatment = runner.run(
                _task(),
                experiment_id="causal-fixture-v0.1",
                condition=Condition.treatment(),
                run_dir=Path(directory) / "treatment",
            )
            control_manifest = json.loads(
                (Path(control.run_dir) / "experiment_run.json").read_text()
            )
            treatment_manifest = json.loads(
                (Path(treatment.run_dir) / "experiment_run.json").read_text()
            )
            for key in (
                "model",
                "harness_version",
                "tool_manifest",
                "environment_hash",
                "oracle_version",
                "execution_budget",
            ):
                self.assertEqual(control_manifest[key], treatment_manifest[key])
            self.assertIsNone(control_manifest["skill_identity"])
            self.assertIsNone(control_manifest["skill_manifest_hash"])
            self.assertEqual(
                treatment_manifest["skill_identity"], FROZEN_SKILL_ARTIFACT_ID
            )
            self.assertTrue(treatment_manifest["skill_manifest_hash"])
            self.assertIsNone(control_manifest["skill_payload_hash"])
            self.assertTrue(treatment_manifest["skill_payload_hash"])
            self.assertEqual(
                control_manifest,
                json.loads(
                    (Path(control.run_dir) / "run_manifest.json").read_text()
                ),
            )

    def test_oracle_receives_visible_result_but_not_hidden_reasoning_or_context(self):
        oracle = CapturingOracle()
        adapter = FixtureAgentAdapter(
            execution_agent=FixtureAgent(
                result={
                    "patch": "observable patch",
                    "summary": "visible action summary",
                }
            ),
            renderer=SkillExposureRenderer(fixture_skill_payload()),
            model="fixture-model",
            harness_version="fixture-harness-v0",
            tool_manifest={"filesystem": "isolated"},
            execution_budget=ExecutionBudget(),
            environment_hash="env-sha256",
        )
        with tempfile.TemporaryDirectory() as directory:
            ExperimentRunner(adapter, oracle).run(
                _task(),
                experiment_id="causal-fixture-v0.1",
                condition=Condition.treatment(),
                run_dir=Path(directory) / "treatment",
            )

        self.assertEqual(
            oracle.seen_result,
            {"patch": "observable patch", "summary": "visible action summary"},
        )
        self.assertNotIn("visible_context", oracle.seen_result)
        self.assertNotIn("chain_of_thought", oracle.seen_result)
        self.assertNotIn("hidden_reasoning", oracle.seen_result)

    def test_skill_manifest_and_payload_hashes_are_reproducible(self):
        renderer = SkillExposureRenderer(fixture_skill_payload())
        first = renderer.render(Condition.treatment())
        second = renderer.render(Condition.treatment())

        self.assertEqual(first.manifest_hash, second.manifest_hash)
        self.assertEqual(first.payload_hash, second.payload_hash)
        self.assertEqual(first.visible_context, second.visible_context)

        with self.assertRaises(ExperimentRunError):
            SkillExposureRenderer(
                fixture_skill_payload(),
                expected_manifest_sha256=(
                    "92dc8f44a0a729f72e32e1c000f0e37ad8cfb9cbd6346ed4ddbe92694ebe86eb"
                ),
            ).render(Condition.treatment())


if __name__ == "__main__":
    unittest.main()
