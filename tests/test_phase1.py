import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from skillnudge.phase1 import Phase1Runtime, Phase1RuntimeError, render_advice
from skillnudge.planning import InputEnvelope
from skillnudge.planning_model import DeterministicFakeModel, ModelProviderError
from skillnudge.retrieval import build_index


def _capability(*, missing: list[str], clarification_needed: bool = False) -> dict:
    return {
        "contract": {
            "goal": "Make progress on the current task",
            "stage": "exploration",
            "blocker": "The current request does not yet have a concrete next step.",
            "missing_capabilities": missing,
            "intended_effect": "Make the next task step clearer.",
            "constraints": [],
            "not_needed": [],
            "uncertainties": [],
        },
        "confidence": "high",
        "clarification_needed": clarification_needed,
        "clarification_question": (
            "Which security capability do you mean?"
            if clarification_needed
            else None
        ),
    }


def _search_plan() -> dict:
    return {
        "decision": "search",
        "targets": [
            {
                "family": "skill",
                "priority": "primary",
                "rationale": "A reusable instructional capability is the main gap.",
            }
        ],
        "decision_reason": "Search the primary capability family.",
    }


def _query_plan() -> dict:
    return {
        "status": "ready",
        "queries": [
            {
                "family": "skill",
                "angle": "capability",
                "semantic_query": "design system prototyping guidance",
                "purpose": "Find reusable prototyping guidance.",
            },
            {
                "family": "skill",
                "angle": "problem",
                "semantic_query": "translate vague visual intent into interface decisions",
                "purpose": "Search for the underlying design blockage.",
            },
        ],
    }


def _judgement(candidate_id: str) -> dict:
    return {
        "candidate_id": candidate_id,
        "evidence_status": "sufficient",
        "assessment": {
            "capability_fit": "strong",
            "stage_fit": "now",
            "mechanism_fit": "strong",
            "expected_gain": "high",
            "practical_fit": {
                "compatibility": "compatible",
                "constraint_fit": "satisfies",
                "friction": "low",
            },
            "trust": "unknown",
        },
        "matched_capabilities": ["prototyping guidance"],
        "gaps_or_mismatches": [],
        "evidence": ["content.body", "content.description"],
        "disposition": "viable",
        "reason": "The body directly supports the missing capability.",
    }


def _advice(candidate_id: str, name: str = "prototype-guidance") -> dict:
    return {
        "status": "recommendation",
        "primary": {
            "candidate_id": candidate_id,
            "name": name,
            "reason": "It addresses the current capability gap.",
        },
        "supporting": None,
        "companion": None,
        "deferred": [],
        "uncertainties": [],
    }


class Phase1RuntimeTests(unittest.TestCase):
    def _database(self, directory: str, *, record_count: int = 1) -> Path:
        records = [
            {
                "candidate_id": "candidate-1",
                "name": "prototype-guidance",
                "description": "Design system and prototype guidance",
                "body": "Use design systems and prototypes to make visual decisions.",
                "repo": "example/prototype-guidance",
                "source_url": "https://example.test/prototype-guidance",
                "license": "MIT",
                "updated_at": "2026-09-18",
                "source": "test-fixture",
            }
        ]
        if record_count == 2:
            records.append(
                {
                    "candidate_id": "candidate-2",
                    "name": "prototype-guidance-companion",
                    "description": "Prototype planning examples",
                    "body": "Compare prototype examples before choosing a visual direction.",
                    "repo": "example/prototype-guidance-companion",
                    "source_url": "https://example.test/prototype-guidance-companion",
                    "license": "MIT",
                    "updated_at": "2026-09-18",
                    "source": "test-fixture",
                }
            )
        corpus = Path(directory) / "corpus.json"
        corpus.write_text(json.dumps(records), encoding="utf-8")
        database = Path(directory) / "skills.sqlite3"
        build_index(corpus, database, metadata={"source": {"repository": "test-fixture"}})
        return database

    def test_composed_runtime_writes_full_path_and_one_overall_completion(self):
        with tempfile.TemporaryDirectory() as directory:
            database = self._database(directory)
            fake = DeterministicFakeModel(
                [
                    _capability(missing=["prototyping guidance"]),
                    _search_plan(),
                    _query_plan(),
                    _judgement("candidate-1"),
                    _advice("candidate-1"),
                ]
            )
            run_dir = Path(directory) / "advise"
            result = Phase1Runtime(fake, database).run(
                InputEnvelope("Help me make a better UI prototype."),
                run_dir,
            )

            self.assertEqual(result.final_advice["status"], "recommendation")
            self.assertTrue(
                all(
                    (run_dir / filename).exists()
                    for filename in (
                        "00_input.json",
                        "01_capability_contract.json",
                        "02_intervention_plan.json",
                        "03_query_plan.json",
                        "04_candidate_acquisition.json",
                        "05_evidence_packs.json",
                        "06_judgements.json",
                        "07_final_advice.json",
                        "trace.jsonl",
                    )
                )
            )
            events = [
                json.loads(line)
                for line in (run_dir / "trace.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            completions = [event for event in events if event["event"] == "run_completed"]
            self.assertEqual(len(completions), 1)
            self.assertEqual(completions[0]["stage"], "Phase 1 Runtime")
            self.assertEqual(completions[0]["details"]["status"], "recommendation")
            self.assertEqual(result.judge.judge_call_count, 1)
            self.assertEqual(result.judge.final_advice_call_count, 1)

    def test_d003_skips_acquisition_and_judge_with_missing_database(self):
        with tempfile.TemporaryDirectory() as directory:
            fake = DeterministicFakeModel(
                [
                    _capability(missing=[]),
                    {
                        "decision": "no_intervention",
                        "targets": [],
                        "decision_reason": "This is a local explanation request.",
                    },
                ]
            )
            run_dir = Path(directory) / "d003"
            result = Phase1Runtime(
                fake,
                Path(directory) / "does-not-exist.sqlite3",
            ).run(InputEnvelope("What does KeyError mean?"), run_dir)

            self.assertEqual(result.final_advice["status"], "no_intervention")
            self.assertEqual(result.judge.judge_call_count, 0)
            self.assertEqual(fake.calls, [
                {"stage": "Capability Framing", "prompt_version": "planning.capability.v1"},
                {"stage": "Intervention Planning", "prompt_version": "planning.intervention.v1"},
            ])
            self.assertFalse((run_dir / "04_candidate_acquisition.json").exists())
            self.assertFalse((run_dir / "05_evidence_packs.json").exists())
            self.assertFalse((run_dir / "06_judgements.json").exists())
            self.assertTrue((run_dir / "07_final_advice.json").exists())

    def test_optional_project_context_and_current_stage_are_persisted(self):
        with tempfile.TemporaryDirectory() as directory:
            fake = DeterministicFakeModel(
                [
                    _capability(missing=[]),
                    {
                        "decision": "no_intervention",
                        "targets": [],
                        "decision_reason": "The current task is a direct explanation.",
                    },
                ]
            )
            run_dir = Path(directory) / "context"
            result = Phase1Runtime(
                fake,
                Path(directory) / "does-not-exist.sqlite3",
            ).run(
                InputEnvelope(
                    "Explain this local error.",
                    project_context="SkillNudge repository",
                    current_stage="debugging",
                ),
                run_dir,
            )

            self.assertEqual(
                result.planning.input_envelope["project_context"],
                "SkillNudge repository",
            )
            self.assertEqual(result.planning.input_envelope["current_stage"], "debugging")
            input_artifact = json.loads(
                (run_dir / "00_input.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                input_artifact["input"]["project_context"],
                "SkillNudge repository",
            )
            self.assertEqual(input_artifact["input"]["current_stage"], "debugging")

    def test_clarification_stops_before_acquisition_and_judge(self):
        with tempfile.TemporaryDirectory() as directory:
            fake = DeterministicFakeModel(
                [_capability(missing=[], clarification_needed=True)]
            )
            run_dir = Path(directory) / "clarify"
            result = Phase1Runtime(
                fake,
                Path(directory) / "does-not-exist.sqlite3",
            ).run(InputEnvelope("I need security capability."), run_dir)

            self.assertEqual(result.final_advice["status"], "needs_clarification")
            self.assertEqual(result.final_advice["uncertainties"], ["Which security capability do you mean?"])
            self.assertEqual(len(fake.calls), 1)
            self.assertFalse((run_dir / "04_candidate_acquisition.json").exists())
            self.assertFalse((run_dir / "05_evidence_packs.json").exists())
            self.assertFalse((run_dir / "06_judgements.json").exists())

    def test_unsupported_only_family_returns_source_error_without_judge(self):
        with tempfile.TemporaryDirectory() as directory:
            fake = DeterministicFakeModel(
                [
                    _capability(missing=["external system automation"]),
                    {
                        "decision": "search",
                        "targets": [
                            {
                                "family": "integration",
                                "priority": "primary",
                                "rationale": "The task requires an external system surface.",
                            }
                        ],
                        "decision_reason": "Search the integration family.",
                    },
                    {
                        "status": "ready",
                        "queries": [
                            {
                                "family": "integration",
                                "angle": "operation",
                                "semantic_query": "external issue tracking task synchronization",
                                "purpose": "Find the required external system capability.",
                            }
                        ],
                    },
                ]
            )
            run_dir = Path(directory) / "integration-edge"
            result = Phase1Runtime(
                fake,
                self._database(directory),
            ).run(
                InputEnvelope("Keep an external task system synchronized."),
                run_dir,
            )

            self.assertEqual(result.final_advice["status"], "source_error")
            self.assertEqual(result.judge.judge_call_count, 0)
            self.assertEqual(result.candidate_runtime.acquisition["status"], "unsupported_family_surface")
            self.assertFalse((run_dir / "05_evidence_packs.json").exists())

    def test_resume_continues_from_partial_judgement_without_replanning(self):
        with tempfile.TemporaryDirectory() as directory:
            database = self._database(directory, record_count=2)

            class InterruptingModel:
                provider_name = "interrupting-fixture"
                model_name = "fixture-model"

                def __init__(self):
                    self.calls = []
                    self.judgement_calls = 0

                def generate_structured(self, *, stage, prompt, prompt_version):
                    self.calls.append(stage)
                    if stage == "Capability Framing":
                        return _capability(missing=["prototyping guidance"])
                    if stage == "Intervention Planning":
                        return _search_plan()
                    if stage == "Query Planning":
                        return _query_plan()
                    if stage == "Candidate Judgement":
                        if self.judgement_calls:
                            raise ModelProviderError("INTERRUPTED")
                        self.judgement_calls += 1
                        marker = '"candidate_id": "'
                        candidate_id = prompt.split(marker, 1)[1].split('"', 1)[0]
                        return _judgement(candidate_id)
                    raise ModelProviderError("INTERRUPTED_BEFORE_FINAL_ADVICE")

            first = InterruptingModel()
            run_dir = Path(directory) / "resume"
            with self.assertRaises(ModelProviderError):
                Phase1Runtime(first, database).run(
                    InputEnvelope("Help me make a better UI prototype."),
                    run_dir,
                )
            partial = json.loads((run_dir / "06_judgements.json").read_text(encoding="utf-8"))
            self.assertEqual(partial["stage_status"], "in_progress")
            self.assertEqual(partial["judged_candidate_count"], 1)

            evidence = json.loads((run_dir / "05_evidence_packs.json").read_text(encoding="utf-8"))
            completed_id = partial["judgements"][0]["candidate_id"]
            completed_name = next(
                pack["identity"]["name"]
                for pack in evidence["packs"]
                if pack["candidate_id"] == completed_id
            )

            class ResumeModel:
                provider_name = "resume-fixture"
                model_name = "fixture-model"

                def __init__(self):
                    self.calls = []

                def generate_structured(self, *, stage, prompt, prompt_version):
                    self.calls.append(stage)
                    if stage == "Candidate Judgement":
                        marker = '"candidate_id": "'
                        candidate_id = prompt.split(marker, 1)[1].split('"', 1)[0]
                        return _judgement(candidate_id)
                    if stage == "Final Advice":
                        return _advice(completed_id, completed_name)
                    raise AssertionError(stage)

            second = ResumeModel()
            result = Phase1Runtime(second, database).resume(run_dir)
            self.assertEqual(result.judge.resumed_judgement_count, 1)
            self.assertEqual(result.judge.judge_call_count, 1)
            self.assertEqual(result.judge.final_advice_call_count, 1)
            self.assertEqual(second.calls, ["Candidate Judgement", "Final Advice"])
            self.assertEqual(
                json.loads((run_dir / "06_judgements.json").read_text())["stage_status"],
                "complete",
            )

    def test_failed_run_records_failure_without_exposing_model_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            database = self._database(directory)
            fake = DeterministicFakeModel(
                [_capability(missing=["x"]), _search_plan(), _query_plan()]
            )
            run_dir = Path(directory) / "failed"
            with self.assertRaises(Exception):
                Phase1Runtime(fake, database).run(
                    InputEnvelope("Find a reusable capability."),
                    run_dir,
                )
            trace = (run_dir / "trace.jsonl").read_text(encoding="utf-8")
            self.assertIn('"event": "run_failed"', trace)
            self.assertNotIn("api_key", trace)

    def test_nonempty_run_directory_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory) / "existing"
            run_dir.mkdir()
            (run_dir / "trace.jsonl").write_text("preserve\n", encoding="utf-8")
            with self.assertRaises(Phase1RuntimeError):
                Phase1Runtime(
                    DeterministicFakeModel([]),
                    Path(directory) / "missing.sqlite3",
                ).run(InputEnvelope("request"), run_dir)
            self.assertEqual(
                (run_dir / "trace.jsonl").read_text(encoding="utf-8"),
                "preserve\n",
            )


class Phase1RenderingTests(unittest.TestCase):
    def test_rendering_stays_concise_and_keeps_uncertainty(self):
        rendered = render_advice(
            {
                "status": "recommendation",
                "primary": {
                    "name": "primary-skill",
                    "reason": "Main fit",
                },
                "supporting": None,
                "companion": None,
                "uncertainties": ["Integration was not evaluated."],
            }
        )
        self.assertIn("Primary: primary-skill — Main fit", rendered)
        self.assertIn("Important uncertainties:", rendered)
        self.assertIn("Integration was not evaluated.", rendered)
        self.assertNotIn("CandidateJudgement", rendered)

    def test_rendering_distinguishes_early_stop_statuses(self):
        self.assertIn("No additional capability", render_advice({"status": "no_intervention"}))
        self.assertIn("Needs clarification:", render_advice({
            "status": "needs_clarification",
            "uncertainties": ["Which capability?"],
        }))
        self.assertIn("enough evidence", render_advice({
            "status": "insufficient_evidence",
            "uncertainties": [],
        }))


if __name__ == "__main__":
    unittest.main()
