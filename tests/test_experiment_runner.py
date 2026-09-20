import json
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from skillnudge.experiment_runner import (
    AgentExecutionContext,
    ExecutionBudget,
    ExecutionPolicy,
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
    validate_pair_manifest,
    validate_paired_runs,
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
                    evaluator_valid=True,
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

    def _paired_results(self, root: str):
        agent = FixtureAgent(
            result={"patch": "fixture patch"},
            steps=2,
            tokens=50,
            latency_ms=5.0,
            events=(("verification", {"kind": "target", "passed": True}),),
        )
        adapter = FixtureAgentAdapter(
            execution_agent=agent,
            renderer=SkillExposureRenderer(fixture_skill_payload()),
            model="fixture-model",
            harness_version="fixture-harness-v0",
            tool_manifest={"filesystem": "isolated", "shell": "fixture"},
            execution_budget=ExecutionBudget(max_steps=8, max_tool_calls=16),
            environment_hash="fixture-environment-sha256",
            execution_policy=ExecutionPolicy(
                retry_policy={"transport_retry_limit": 1},
                termination_policy={"stop_on_completion": True},
            ),
        )
        runner = ExperimentRunner(adapter, FixtureOracle())
        control = runner.run(
            _task(),
            experiment_id="paired-experiment-v0",
            condition=Condition.control(),
            run_dir=Path(root) / "control",
        )
        treatment = runner.run(
            _task(),
            experiment_id="paired-experiment-v0",
            condition=Condition.treatment(),
            run_dir=Path(root) / "treatment",
        )
        return control, treatment

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

    def test_oracle_validity_is_preserved_and_invalid_evaluator_cannot_be_success(self):
        with tempfile.TemporaryDirectory() as directory:
            invalid = self._run(
                directory,
                Condition.control(),
                oracle=OracleResult(
                    success=True,
                    regression=False,
                    diagnostics=["evaluator crashed after producing a provisional result"],
                    evaluator_valid=False,
                ),
            )
            self.assertEqual(invalid.evidence.evidence_validity, "PROTOCOL_FAILURE")
            self.assertEqual(invalid.evidence.outcome.status, "protocol_failure")
            self.assertEqual(invalid.evidence.outcome.target_status, "pass")
            self.assertEqual(invalid.evidence.outcome.regression_status, "pass")
            self.assertFalse(invalid.evidence.outcome.evaluator_valid)

            unknown = self._run(
                directory,
                Condition.treatment(),
                oracle=OracleResult(
                    success=None,
                    regression=None,
                    diagnostics=["evaluator state unavailable"],
                    evaluator_valid=None,
                ),
            )
            self.assertEqual(unknown.evidence.evidence_validity, "INCONCLUSIVE")
            self.assertEqual(unknown.evidence.outcome.status, "unknown")

    def test_oracle_evaluation_is_not_agent_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            zero_agent = FixtureAgent(
                result={"patch": "fixture"},
                events=(),
            )
            zero_adapter = FixtureAgentAdapter(
                execution_agent=zero_agent,
                renderer=SkillExposureRenderer(fixture_skill_payload()),
                model="fixture-model",
                harness_version="fixture-harness-v0",
                tool_manifest={"shell": "fixture"},
                execution_budget=ExecutionBudget(),
                environment_hash="env-sha256",
            )
            zero = ExperimentRunner(zero_adapter, FixtureOracle()).run(
                _task(),
                experiment_id="verification-boundary-v0",
                condition=Condition.control(),
                run_dir=Path(directory) / "zero",
            )
            self.assertEqual(zero.evidence.trajectory.verification_count, 0)
            trace = (Path(zero.run_dir) / "trace.jsonl").read_text(encoding="utf-8")
            self.assertEqual(trace.count('"event": "oracle_evaluation"'), 1)

            two_agent = FixtureAgent(
                result={"patch": "fixture"},
                events=(
                    ("verification", {"kind": "target", "passed": True}),
                    ("verification", {"kind": "regression", "passed": True}),
                ),
            )
            two_adapter = replace(zero_adapter, execution_agent=two_agent)
            two = ExperimentRunner(two_adapter, FixtureOracle()).run(
                _task(),
                experiment_id="verification-boundary-v0",
                condition=Condition.control(),
                run_dir=Path(directory) / "two",
            )
            self.assertEqual(two.evidence.trajectory.verification_count, 2)

    def test_adapter_is_the_authoritative_metadata_source(self):
        mismatches = (
            ("model", "different-model"),
            ("harness_version", "different-harness"),
            ("tool_manifest", {"shell": "different"}),
            ("environment_hash", "different-environment"),
            ("execution_budget", ExecutionBudget(max_steps=999)),
            (
                "execution_policy",
                ExecutionPolicy(
                    retry_policy={"transport_retry_limit": 99},
                    termination_policy={"stop_on_completion": False},
                ),
            ),
        )
        for field_name, value in mismatches:
            with self.subTest(field=field_name), tempfile.TemporaryDirectory() as directory:
                adapter = FixtureAgentAdapter(
                    execution_agent=FixtureAgent(),
                    renderer=SkillExposureRenderer(fixture_skill_payload()),
                    model="fixture-model",
                    harness_version="fixture-harness-v0",
                    tool_manifest={"shell": "fixture"},
                    execution_budget=ExecutionBudget(max_steps=8),
                    environment_hash="env-sha256",
                    execution_policy=ExecutionPolicy(),
                )
                kwargs = {
                    "model": "fixture-model",
                    "harness_version": "fixture-harness-v0",
                    "tool_manifest": {"shell": "fixture"},
                    "execution_budget": ExecutionBudget(max_steps=8),
                    "environment_hash": "env-sha256",
                    "execution_policy": ExecutionPolicy(),
                }
                kwargs[field_name] = value
                with self.assertRaisesRegex(
                    ExperimentRunError, field_name
                ):
                    ExperimentRunner(adapter, FixtureOracle()).run(
                        _task(),
                        experiment_id="adapter-authority-v0",
                        condition=Condition.control(),
                        run_dir=Path(directory) / "run",
                        **kwargs,
                    )

    def test_paired_fixture_is_valid_and_has_explicit_synthetic_treatment(self):
        with tempfile.TemporaryDirectory() as directory:
            control, treatment = self._paired_results(directory)
            pair = validate_paired_runs(
                control.run,
                treatment.run,
                control_task=_task(),
                treatment_task=_task(),
            )
            self.assertEqual(pair.pair_status, "VALID")
            self.assertEqual(pair.errors, [])
            validate_pair_manifest(pair.as_dict())
            self.assertEqual(
                treatment.run.artifact_verification["mode"], "synthetic_fixture"
            )
            self.assertFalse(treatment.run.artifact_verification["verified"])
            self.assertEqual(
                control.run.artifact_verification["mode"], "none"
            )

    def test_pair_validator_rejects_each_load_bearing_mismatch(self):
        mismatch_values = (
            ("model", "other-model"),
            ("harness_version", "other-harness"),
            ("tool_manifest", {"shell": "other"}),
            ("environment_hash", "other-environment"),
            ("execution_budget", {"max_steps": 999}),
            (
                "execution_policy",
                {
                    "retry_policy": {"transport_retry_limit": 9},
                    "termination_policy": {"stop_on_completion": True},
                },
            ),
            ("oracle_version", "other-oracle"),
            ("trace_instrumentation", "other-trace"),
        )
        for field_name, value in mismatch_values:
            with self.subTest(field=field_name), tempfile.TemporaryDirectory() as directory:
                control, treatment = self._paired_results(directory)
                mutated = treatment.run.as_dict()
                mutated[field_name] = value
                result = validate_paired_runs(
                    control.run.as_dict(),
                    mutated,
                    control_task=_task(),
                    treatment_task=_task(),
                )
                self.assertEqual(result.pair_status, "PROTOCOL_FAILURE")
                self.assertTrue(
                    any(field_name in error for error in result.errors),
                    result.errors,
                )

    def test_pair_validator_rejects_task_identity_and_missing_treatment_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            control, treatment = self._paired_results(directory)
            missing_task_identity = validate_paired_runs(control.run, treatment.run)
            self.assertEqual(missing_task_identity.pair_status, "PROTOCOL_FAILURE")
            self.assertIn(
                "task artifact identity is required for paired validation",
                missing_task_identity.errors,
            )

            different_task = TaskArtifact(
                task_id="task-002",
                repository="example/project",
                commit="abc123",
                test_command="python -m unittest",
            )
            result = validate_paired_runs(
                control.run,
                treatment.run,
                control_task=_task(),
                treatment_task=different_task,
            )
            self.assertEqual(result.pair_status, "PROTOCOL_FAILURE")
            self.assertIn("task artifact identity mismatch", result.errors)

            missing_skill = treatment.run.as_dict()
            missing_skill.update(
                {
                    "condition": {"skill": None},
                    "skill_version": None,
                    "skill_identity": None,
                    "skill_manifest_hash": None,
                    "skill_payload_hash": None,
                    "artifact_verification": {
                        "mode": "none",
                        "verified": True,
                        "expected_manifest_sha256": None,
                        "actual_manifest_sha256": None,
                    },
                }
            )
            result = validate_paired_runs(
                control.run,
                missing_skill,
                control_task=_task(),
                treatment_task=_task(),
            )
            self.assertEqual(result.pair_status, "PROTOCOL_FAILURE")
            self.assertIn(
                "treatment condition must use the declared systematic debugging Skill",
                result.errors,
            )

    def test_frozen_artifact_mode_requires_verified_manifest_hash(self):
        with self.assertRaises(ValueError):
            SkillExposureRenderer(
                fixture_skill_payload(),
                artifact_mode="frozen_verified_artifact",
            )
        with self.assertRaises(ExperimentRunError):
            SkillExposureRenderer(
                fixture_skill_payload(),
                artifact_mode="frozen_verified_artifact",
                expected_manifest_sha256="wrong-hash",
            ).render(Condition.treatment())

    def test_pair_validator_rejects_wrong_verified_treatment_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            control, treatment = self._paired_results(directory)
            mutated = treatment.run.as_dict()
            mutated["artifact_verification"] = {
                "mode": "frozen_verified_artifact",
                "verified": True,
                "expected_manifest_sha256": "wrong-hash",
                "actual_manifest_sha256": "wrong-hash",
            }
            result = validate_paired_runs(
                control.run,
                mutated,
                control_task=_task(),
                treatment_task=_task(),
            )
            self.assertEqual(result.pair_status, "PROTOCOL_FAILURE")
            self.assertIn("frozen treatment manifest hash is not verified", result.errors)

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
                    evaluator_valid=True,
                ),
            )

            evidence = result.evidence.as_dict()
            self.assertEqual(evidence["outcome"]["status"], "failure")
            self.assertEqual(evidence["evidence_validity"], "VALID")
            self.assertTrue(evidence["outcome"]["evaluator_valid"])
            self.assertEqual(evidence["outcome"]["tests_passed"], 1)
            self.assertEqual(evidence["trajectory"]["steps"], 4)
            self.assertEqual(evidence["trajectory"]["tool_calls"], 1)
            self.assertEqual(evidence["trajectory"]["verification_count"], 1)
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
                        evaluator_valid=True,
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
        self.assertEqual(
            control_context.execution_policy, treatment_context.execution_policy
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
                "execution_policy",
                "trace_instrumentation",
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
