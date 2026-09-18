import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from skillnudge.candidate_runtime import CandidateAcquisitionRuntime
from skillnudge.planning import InputEnvelope, PlanningRuntime
from skillnudge.planning_model import DeterministicFakeModel
from skillnudge.retrieval import build_index


def _capability(*, missing: list[str], clarification_needed: bool = False) -> dict:
    return {
        "contract": {
            "goal": "Find the capability needed for the current task",
            "stage": "exploration",
            "blocker": "The user cannot turn the current blockage into a concrete next step.",
            "missing_capabilities": missing,
            "intended_effect": "Turn the blockage into an inspectable next step.",
            "constraints": [],
            "not_needed": [],
            "uncertainties": [],
        },
        "confidence": "medium",
        "clarification_needed": clarification_needed,
        "clarification_question": "What specific capability should change?" if clarification_needed else None,
    }


def _search_plan(primary: str, secondary: str | None = None, *, secondary_priority: str = "secondary") -> dict:
    targets = [
        {
            "family": primary,
            "priority": "primary",
            "rationale": "This family addresses the diagnosed blocker.",
        }
    ]
    if secondary:
        targets.append(
            {
                "family": secondary,
                "priority": secondary_priority,
                "rationale": "This family covers a complementary candidate surface.",
            }
        )
    return {
        "decision": "search",
        "targets": targets,
        "decision_reason": "A bounded search can address the capability gap.",
    }


def _query_plan(families: list[str]) -> dict:
    angles = ["capability", "problem", "professional_vocabulary", "outcome", "stage"]
    return {
        "status": "ready",
        "queries": [
            {
                "family": family,
                "angle": angles[index % len(angles)],
                "semantic_query": f"{family} {angles[index % len(angles)]} capability blocker",
                "purpose": f"Search the {angles[index % len(angles)]} angle.",
            }
            for index, family in enumerate(families)
        ],
    }


def _build_skill_index(root: Path, count: int = 40) -> Path:
    corpus = root / "corpus.json"
    records = [
        {
            "skill_id": f"skill-{index:03d}",
            "name": f"Local Skill {index:03d}",
            "description": "skill capability problem professional vocabulary outcome stage",
            "content": (
                "This skill provides capability guidance for the current "
                "problem blocker and desired outcome at the task stage."
            ),
        }
        for index in range(count)
    ]
    corpus.write_text(json.dumps(records), encoding="utf-8")
    database = root / "skills.sqlite3"
    build_index(
        corpus,
        database,
        metadata={
            "source": {
                "repository": "local-test-corpus",
                "repository_commit": "test-commit",
                "corpus_sha256": "test-sha",
            }
        },
    )
    return database


class Checkpoint3RuntimeTests(unittest.TestCase):
    def test_real_planning_result_feeds_skill_acquisition_and_top10_hydration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            database = _build_skill_index(root)
            run_dir = root / "D001"
            fake = DeterministicFakeModel(
                [
                    _capability(missing=["design framing"]),
                    _search_plan("skill", "resource", secondary_priority="companion"),
                    _query_plan(["skill", "skill", "skill", "resource"]),
                ]
            )
            planning = PlanningRuntime(fake).run(
                InputEnvelope("I need guidance for a vague design task."),
                run_dir,
            )
            result = CandidateAcquisitionRuntime(database).run(planning)

            self.assertEqual(len(fake.calls), 3)
            self.assertIsNotNone(result.acquisition)
            self.assertIsNotNone(result.evidence_packs)
            acquisition = result.acquisition
            assert acquisition is not None
            self.assertEqual(acquisition["status"], "partial_unsupported_family_surface")
            self.assertEqual(acquisition["planned_families"], ["skill", "resource"])
            self.assertEqual(acquisition["acquired_families"], ["skill"])
            self.assertEqual(len(acquisition["retrieval"]["fused_top_30"]), 30)

            skill_queries = [
                query
                for query in acquisition["retrieval"]["queries"]
                if query["family"] == "skill"
            ]
            self.assertEqual(len(skill_queries), 3)
            for query in skill_queries:
                self.assertTrue(query["semantic_query"])
                self.assertTrue(query["actual_fts_query"])
                self.assertLessEqual(len(query["results"]), 50)
                self.assertTrue(query["results"])
                self.assertIn("raw_bm25_score", query["results"][0])
                self.assertIn("rrf_contribution", query["results"][0])

            self.assertTrue(acquisition["warnings"])
            self.assertEqual(
                acquisition["warnings"][0]["code"],
                "unsupported_family_surface",
            )
            first_fused = acquisition["retrieval"]["fused_top_30"][0]
            self.assertIn("candidate_id", first_fused)
            self.assertIn("name", first_fused)
            self.assertIn("query_hits", first_fused)
            self.assertIn("rrf_score", first_fused)

            evidence = result.evidence_packs
            assert evidence is not None
            self.assertEqual(evidence["hydration_limit"], 10)
            self.assertEqual(evidence["hydrated_candidate_count"], 10)
            pack = evidence["packs"][0]
            self.assertEqual(pack["family"], "skill")
            self.assertEqual(pack["provenance_status"], "unknown")
            self.assertIsNone(pack["identity"]["repo"])
            self.assertIsNone(pack["identity"]["source_url"])
            self.assertIsNone(pack["identity"]["license"])
            self.assertIn("missing_repo", pack["evidence_gaps"])
            self.assertEqual(
                pack["content"]["body_sha256"],
                hashlib.sha256(pack["content"]["body"].encode("utf-8")).hexdigest(),
            )
            self.assertEqual(
                pack["content"]["body_length"],
                len(pack["content"]["body"].encode("utf-8")),
            )

            self.assertTrue((run_dir / "04_candidate_acquisition.json").exists())
            self.assertTrue((run_dir / "05_evidence_packs.json").exists())
            self.assertFalse((run_dir / "06_judgements.json").exists())
            self.assertFalse((run_dir / "07_final_advice.json").exists())
            trace = (run_dir / "trace.jsonl").read_text(encoding="utf-8")
            self.assertIn('"event": "query_execution"', trace)
            self.assertIn('"event": "fusion"', trace)
            self.assertIn('"stage": "Evidence Hydration"', trace)

    def test_d003_and_clarification_stop_before_acquisition(self):
        cases = [
            (
                "D003",
                [
                    _capability(missing=[]),
                    {
                        "decision": "no_intervention",
                        "targets": [],
                        "decision_reason": "The current agent can answer this local question.",
                    },
                ],
                "What does Python KeyError mean?",
            ),
            (
                "clarification-edge",
                [_capability(missing=[], clarification_needed=True)],
                "I want to add security capability to Codex.",
            ),
        ]
        with tempfile.TemporaryDirectory() as directory:
            database = _build_skill_index(Path(directory))
            for case_id, responses, request in cases:
                with self.subTest(case_id=case_id):
                    run_dir = Path(directory) / case_id
                    planning = PlanningRuntime(DeterministicFakeModel(responses)).run(
                        InputEnvelope(request),
                        run_dir,
                    )
                    result = CandidateAcquisitionRuntime(database).run(planning)
                    self.assertIsNone(result.acquisition)
                    self.assertIsNone(result.evidence_packs)
                    self.assertFalse((run_dir / "04_candidate_acquisition.json").exists())
                    self.assertFalse((run_dir / "05_evidence_packs.json").exists())
                    self.assertFalse((run_dir / "06_judgements.json").exists())
                    self.assertFalse((run_dir / "07_final_advice.json").exists())
                    trace = (run_dir / "trace.jsonl").read_text(encoding="utf-8")
                    self.assertIn('"event": "early_stop"', trace)
                    self.assertNotIn("query_execution", trace)

    def test_unsupported_integration_does_not_fall_back_to_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            database = _build_skill_index(root)
            run_dir = root / "integration-edge"
            planning = PlanningRuntime(
                DeterministicFakeModel(
                    [
                        _capability(missing=["external system task automation"]),
                        _search_plan("integration"),
                        _query_plan(["integration"]),
                    ]
                )
            ).run(
                InputEnvelope("Create and update Jira issues as tasks change."),
                run_dir,
            )
            result = CandidateAcquisitionRuntime(database).run(planning)

            self.assertIsNotNone(result.acquisition)
            self.assertIsNone(result.evidence_packs)
            acquisition = result.acquisition
            assert acquisition is not None
            self.assertEqual(acquisition["status"], "unsupported_family_surface")
            self.assertEqual(acquisition["acquired_families"], [])
            self.assertEqual(acquisition["retrieval"]["fused_top_30"], [])
            self.assertFalse((run_dir / "05_evidence_packs.json").exists())
            trace = (run_dir / "trace.jsonl").read_text(encoding="utf-8")
            self.assertIn('"event": "family_unsupported"', trace)
            self.assertIn("unsupported_family_surface", trace)


if __name__ == "__main__":
    unittest.main()

