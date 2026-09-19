import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from skillnudge.experiment_runner import (
    Condition,
    ExperimentRun,
    ExperimentRunError,
    ExperimentRunner,
    ExperimentSchemaError,
    FixtureAgent,
    OracleResult,
    SYSTEMATIC_DEBUGGING_SKILL,
    TaskArtifact,
    TraceRecorder,
    validate_experiment_run,
    validate_trace_event,
    validate_utility_evidence,
)


class FixtureOracle:
    def __init__(self, result: OracleResult):
        self.result = result

    def evaluate(self, task: TaskArtifact, result):
        return self.result


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
        return ExperimentRunner(
            agent,
            FixtureOracle(
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
            runner = ExperimentRunner(FixtureAgent(), FixtureOracle(OracleResult(None, None, ["unknown"])))
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


if __name__ == "__main__":
    unittest.main()
