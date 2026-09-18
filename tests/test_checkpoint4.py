import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from skillnudge.candidate_runtime import _provenance
from skillnudge.judge import (
    EVIDENCE_REFS,
    JudgeRuntime,
    JudgeStageError,
    JudgeValidationError,
    evidence_ref_resolves,
    validate_candidate_judgement,
    validate_final_advice_against_judgements,
)
from skillnudge.planning_model import DeterministicFakeModel, ModelProviderError


def _judgement(
    candidate_id: str,
    *,
    name: str = "Candidate",
    disposition: str = "viable",
    capability_fit: str = "strong",
    stage_fit: str = "now",
    compatibility: str = "unknown",
    constraint_fit: str = "unknown",
    friction: str = "unknown",
    trust: str = "unknown",
    evidence_status: str = "sufficient",
) -> dict:
    return {
        "candidate_id": candidate_id,
        "evidence_status": evidence_status,
        "assessment": {
            "capability_fit": capability_fit,
            "stage_fit": stage_fit,
            "mechanism_fit": "partial",
            "expected_gain": "medium",
            "practical_fit": {
                "compatibility": compatibility,
                "constraint_fit": constraint_fit,
                "friction": friction,
            },
            "trust": trust,
        },
        "matched_capabilities": ["address the current blocker"],
        "gaps_or_mismatches": [],
        "evidence": ["content.body", "provenance_status"],
        "disposition": disposition,
        "reason": f"{name} was assessed against the current capability gap.",
    }


def _pack(candidate_id: str, name: str, fused_rank: int = 1) -> dict:
    return {
        "candidate_id": candidate_id,
        "family": "skill",
        "identity": {
            "name": name,
            "repo": None,
            "source_url": None,
            "source": None,
            "license": None,
            "updated_at": None,
        },
        "content": {
            "description": f"{name} description",
            "body": f"# {name}\n\nA reusable method for the current task.",
            "body_sha256": "fixture",
            "body_length": 10,
        },
        "retrieval": {
            "fused_rank": fused_rank,
            "rrf_score": 1.0,
            "query_hits": [],
        },
        "provenance_status": "unknown",
        "evidence_gaps": ["missing_repo", "missing_source_url"],
        "corpus": {"identity": "fixture", "version": "fixture-commit"},
    }


def _write_run(
    root: Path,
    *,
    decision: str = "search",
    query_status: str = "ready",
    packs: list[dict] | None = None,
    warnings: list[dict] | None = None,
) -> Path:
    run_dir = root / "checkpoint4"
    run_dir.mkdir()
    (run_dir / "trace.jsonl").write_text("", encoding="utf-8")
    (run_dir / "01_capability_contract.json").write_text(
        json.dumps(
            {
                "contract": {
                    "goal": "Solve the current task",
                    "stage": "exploration",
                    "blocker": "The current agent lacks the requested behavior.",
                    "missing_capabilities": ["reusable behavior"],
                    "intended_effect": "Improve the next trajectory.",
                    "constraints": [],
                    "not_needed": [],
                    "uncertainties": [],
                },
                "confidence": "high",
                "clarification_needed": False,
                "clarification_question": None,
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "02_intervention_plan.json").write_text(
        json.dumps(
            {
                "decision": decision,
                "targets": (
                    [{"family": "skill", "priority": "primary", "rationale": "fixture"}]
                    if decision == "search"
                    else []
                ),
                "decision_reason": "fixture",
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "03_query_plan.json").write_text(
        json.dumps({"status": query_status, "queries": [] if query_status != "ready" else [{"family": "skill"}]}),
        encoding="utf-8",
    )
    if packs is not None:
        (run_dir / "04_candidate_acquisition.json").write_text(
            json.dumps(
                {
                    "schema_version": "checkpoint3.candidate_acquisition.v0",
                    "status": "partial_unsupported_family_surface" if warnings else "ready",
                    "planned_families": ["skill", "integration"] if warnings else ["skill"],
                    "acquired_families": ["skill"],
                    "warnings": warnings or [],
                    "retrieval": {"per_query_k": 50, "rrf": {"limit": 30}},
                }
            ),
            encoding="utf-8",
        )
        (run_dir / "05_evidence_packs.json").write_text(
            json.dumps({"packs": packs}),
            encoding="utf-8",
        )
    return run_dir


class Checkpoint4ContractTests(unittest.TestCase):
    def test_every_allowed_evidence_ref_resolves_against_evidence_pack(self):
        pack = _pack("candidate", "Canonical Skill")
        self.assertTrue(EVIDENCE_REFS)
        for reference in EVIDENCE_REFS:
            with self.subTest(reference=reference):
                self.assertTrue(evidence_ref_resolves(pack, reference))
        self.assertFalse(evidence_ref_resolves(pack, "candidate.body"))
        self.assertFalse(evidence_ref_resolves(pack, "identity.provenance_status"))

    def test_provenance_completeness_is_not_verification(self):
        self.assertEqual(_provenance({})[0], "unknown")
        self.assertEqual(
            _provenance({"repo": "r", "source_url": "u"})[0],
            "partial",
        )
        complete = {
            "repo": "r",
            "source_url": "u",
            "license": "MIT",
            "updated_at": "2026-01-01",
            "source": "catalog",
        }
        self.assertEqual(_provenance(complete)[0], "complete_unverified")
        self.assertEqual(
            _provenance(complete, verification_basis="pinned-body-hash")[0],
            "verified",
        )

    def test_judge_hard_gates(self):
        cases = [
            ("evidence insufficient", _judgement("c", evidence_status="insufficient", disposition="viable")),
            ("capability none", _judgement("c", capability_fit="none", disposition="viable")),
            ("incompatible", _judgement("c", compatibility="incompatible", disposition="viable")),
            ("constraint violation", _judgement("c", constraint_fit="violates", disposition="viable")),
            ("later stage", _judgement("c", stage_fit="later", disposition="viable")),
        ]
        for label, value in cases:
            with self.subTest(label=label):
                with self.assertRaises(JudgeValidationError):
                    validate_candidate_judgement(value)

    def test_unknown_provenance_can_have_strong_fit_without_strong_trust(self):
        judgement = _judgement(
            "c",
            capability_fit="strong",
            trust="unknown",
            disposition="viable",
        )
        self.assertEqual(validate_candidate_judgement(judgement)["assessment"]["trust"], "unknown")

    def test_final_advice_rejects_same_name_duplicates(self):
        judgements = [
            _judgement("c1", name="ask-questions-if-underspecified"),
            _judgement("c2", name="ask-questions-if-underspecified"),
        ]
        advice = {
            "status": "recommendation",
            "primary": {"candidate_id": "c1", "name": "ask-questions-if-underspecified", "reason": "one"},
            "supporting": {"candidate_id": "c2", "name": "ask-questions-if-underspecified", "reason": "two"},
            "companion": None,
            "deferred": [],
            "uncertainties": [],
        }
        with self.assertRaises(JudgeValidationError):
            validate_final_advice_against_judgements(advice, judgements)

    def test_final_advice_accepts_primary_supporting_and_companion(self):
        judgements = [
            _judgement("primary", name="Primary"),
            _judgement("supporting", name="Supporting"),
            _judgement("companion", name="Companion", disposition="companion"),
            _judgement("deferred", name="Deferred", disposition="defer", stage_fit="later"),
        ]
        advice = {
            "status": "recommendation",
            "primary": {"candidate_id": "primary", "name": "Primary", "reason": "main"},
            "supporting": {"candidate_id": "supporting", "name": "Supporting", "reason": "support"},
            "companion": {"candidate_id": "companion", "name": "Companion", "reason": "companion"},
            "deferred": [{"candidate_id": "deferred", "name": "Deferred", "reason": "later"}],
            "uncertainties": [],
        }
        result = validate_final_advice_against_judgements(advice, judgements)
        self.assertEqual(result["primary"]["candidate_id"], "primary")
        self.assertEqual(result["supporting"]["candidate_id"], "supporting")
        self.assertEqual(result["companion"]["candidate_id"], "companion")

    def test_final_advice_uses_canonical_evidence_pack_names(self):
        judgements = [
            _judgement("c1", name="Canonical"),
            _judgement("c2", name="Canonical"),
        ]
        advice = {
            "status": "recommendation",
            "primary": {"candidate_id": "c1", "name": "Model Alias", "reason": "one"},
            "supporting": {
                "candidate_id": "c2",
                "name": "Another Model Alias",
                "reason": "two",
            },
            "companion": None,
            "deferred": [],
            "uncertainties": [],
        }
        with self.assertRaises(JudgeValidationError):
            validate_final_advice_against_judgements(
                advice,
                judgements,
                {"c1": "Canonical", "c2": "Canonical"},
            )

    def test_final_advice_fills_missing_name_from_evidence_pack(self):
        judgements = [_judgement("c1", name="Canonical")]
        advice = {
            "status": "recommendation",
            "primary": {"candidate_id": "c1", "reason": "one"},
            "supporting": None,
            "companion": None,
            "deferred": [],
            "uncertainties": [],
        }
        result = validate_final_advice_against_judgements(
            advice,
            judgements,
            {"c1": "Canonical"},
        )
        self.assertEqual(result["primary"]["name"], "Canonical")


class Checkpoint4RuntimeTests(unittest.TestCase):
    def test_rank_one_rejected_candidate_does_not_force_recommendation(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = _write_run(Path(directory), packs=[_pack("rank-one", "Topical Candidate")])
            fake = DeterministicFakeModel(
                [
                    _judgement("rank-one", capability_fit="none", disposition="reject"),
                    {
                        "status": "no_intervention",
                        "primary": None,
                        "supporting": None,
                        "companion": None,
                        "deferred": [],
                        "uncertainties": ["The only judged candidate was rejected."],
                    },
                ]
            )
            result = JudgeRuntime(fake).run(run_dir)
            self.assertEqual(result.judgements[0]["disposition"], "reject")
            self.assertEqual(result.final_advice["status"], "no_intervention")
            self.assertEqual(result.judge_call_count, 1)
            self.assertTrue((run_dir / "06_judgements.json").exists())
            self.assertTrue((run_dir / "07_final_advice.json").exists())

    def test_final_advice_semantic_failure_gets_one_repair(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = _write_run(
                Path(directory),
                packs=[
                    _pack("same-1", "Repeated Skill", fused_rank=1),
                    _pack("same-2", "Repeated Skill", fused_rank=2),
                ],
            )
            invalid_advice = {
                "status": "recommendation",
                "primary": {"candidate_id": "same-1", "name": "Repeated Skill", "reason": "one"},
                "supporting": {"candidate_id": "same-2", "name": "Repeated Skill", "reason": "two"},
                "companion": None,
                "deferred": [],
                "uncertainties": [],
            }
            valid_advice = {
                "status": "recommendation",
                "primary": {"candidate_id": "same-1", "name": "Repeated Skill", "reason": "one"},
                "supporting": None,
                "companion": None,
                "deferred": [],
                "uncertainties": ["A redundant same-name candidate was not selected."],
            }
            fake = DeterministicFakeModel(
                [
                    _judgement("same-1", name="Repeated Skill"),
                    _judgement("same-2", name="Repeated Skill"),
                    invalid_advice,
                    valid_advice,
                ]
            )
            result = JudgeRuntime(fake).run(run_dir)
            self.assertEqual(result.final_advice["primary"]["candidate_id"], "same-1")
            self.assertEqual(len(fake.calls), 4)

    def test_d002_preserves_unsupported_integration_uncertainty(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = _write_run(
                Path(directory),
                packs=[_pack("skill-1", "Brainstorm Skill")],
                warnings=[
                    {
                        "code": "unsupported_family_surface",
                        "family": "integration",
                        "message": "No Week 1 acquisition surface exists for this family.",
                    }
                ],
            )
            fake = DeterministicFakeModel(
                [
                    _judgement("skill-1", name="Brainstorm Skill"),
                    {
                        "status": "recommendation",
                        "primary": {
                            "candidate_id": "skill-1",
                            "name": "Brainstorm Skill",
                            "reason": "Reusable deliberation behavior.",
                        },
                        "supporting": None,
                        "companion": None,
                        "deferred": [],
                        "uncertainties": [],
                    },
                ]
            )
            result = JudgeRuntime(fake).run(run_dir)
            self.assertIn(
                "planned Integration candidate surface was not evaluated",
                result.final_advice["uncertainties"][0],
            )

    def test_unrelated_acquisition_warning_does_not_create_integration_uncertainty(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = _write_run(
                Path(directory),
                packs=[_pack("skill-1", "Skill")],
                warnings=[
                    {
                        "code": "metadata_unavailable",
                        "family": "skill",
                        "message": "Metadata was unavailable.",
                    }
                ],
            )
            fake = DeterministicFakeModel(
                [
                    _judgement("skill-1", name="Skill"),
                    {
                        "status": "recommendation",
                        "primary": {"candidate_id": "skill-1", "reason": "one"},
                        "supporting": None,
                        "companion": None,
                        "deferred": [],
                        "uncertainties": [],
                    },
                ]
            )
            result = JudgeRuntime(fake).run(run_dir)
            self.assertNotIn(
                "planned Integration candidate surface was not evaluated",
                result.final_advice["uncertainties"],
            )

    def test_judgement_artifact_persists_after_each_successful_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = _write_run(
                Path(directory),
                packs=[
                    _pack("c1", "One", fused_rank=1),
                    _pack("c2", "Two", fused_rank=2),
                    _pack("c3", "Three", fused_rank=3),
                ],
            )
            fake = DeterministicFakeModel(
                [
                    _judgement("c1", name="One"),
                    _judgement("c2", name="Two"),
                ]
            )
            with self.assertRaises(ModelProviderError):
                JudgeRuntime(fake).run(run_dir)
            artifact = json.loads((run_dir / "06_judgements.json").read_text())
            self.assertEqual(artifact["stage_status"], "in_progress")
            self.assertEqual(artifact["expected_candidate_count"], 3)
            self.assertEqual(artifact["judged_candidate_count"], 2)
            self.assertEqual(
                [item["candidate_id"] for item in artifact["judgements"]],
                ["c1", "c2"],
            )
            self.assertEqual(set(artifact["input_fingerprints"]), {"c1", "c2"})

    def test_provider_failure_after_n_candidates_preserves_full_judgements(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = _write_run(
                Path(directory),
                packs=[_pack("c1", "One"), _pack("c2", "Two")],
            )
            fake = DeterministicFakeModel([_judgement("c1", name="One")])
            with self.assertRaises(ModelProviderError):
                JudgeRuntime(fake).run(run_dir)
            artifact = json.loads((run_dir / "06_judgements.json").read_text())
            self.assertEqual(artifact["judgements"][0]["assessment"]["capability_fit"], "strong")
            self.assertEqual(artifact["judgements"][0]["candidate_id"], "c1")

    def test_resume_skips_previously_completed_valid_candidates(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = _write_run(
                Path(directory),
                packs=[_pack("c1", "One"), _pack("c2", "Two"), _pack("c3", "Three")],
            )
            first = DeterministicFakeModel(
                [_judgement("c1", name="One"), _judgement("c2", name="Two")]
            )
            with self.assertRaises(ModelProviderError):
                JudgeRuntime(first).run(run_dir)

            second = DeterministicFakeModel(
                [
                    _judgement("c3", name="Three"),
                    {
                        "status": "recommendation",
                        "primary": {"candidate_id": "c3", "reason": "three"},
                        "supporting": None,
                        "companion": None,
                        "deferred": [],
                        "uncertainties": [],
                    },
                ]
            )
            result = JudgeRuntime(second).run(run_dir)
            self.assertEqual(result.judge_call_count, 3)
            self.assertEqual(
                [call["stage"] for call in second.calls],
                ["Candidate Judgement", "Final Advice"],
            )
            artifact = json.loads((run_dir / "06_judgements.json").read_text())
            self.assertEqual(artifact["stage_status"], "complete")
            self.assertEqual(artifact["judged_candidate_count"], 3)

    def test_resume_rejects_stale_judgement_when_body_hash_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = _write_run(
                Path(directory),
                packs=[_pack("c1", "One"), _pack("c2", "Two")],
            )
            first = DeterministicFakeModel([_judgement("c1", name="One")])
            with self.assertRaises(ModelProviderError):
                JudgeRuntime(first).run(run_dir)
            evidence_path = run_dir / "05_evidence_packs.json"
            evidence = json.loads(evidence_path.read_text())
            evidence["packs"][0]["content"]["body_sha256"] = "changed"
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")

            second = DeterministicFakeModel([])
            with self.assertRaisesRegex(JudgeStageError, "body_sha256 changed"):
                JudgeRuntime(second).run(run_dir)
            self.assertEqual(second.calls, [])

    def test_d003_writes_no_intervention_without_judge_calls(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = _write_run(Path(directory), decision="no_intervention", query_status="skipped")
            result = JudgeRuntime(DeterministicFakeModel([])).run(run_dir)
            self.assertEqual(result.final_advice["status"], "no_intervention")
            self.assertEqual(result.judge_call_count, 0)
            self.assertFalse((run_dir / "06_judgements.json").exists())
            self.assertTrue((run_dir / "07_final_advice.json").exists())

    def test_clarification_writes_needs_clarification_without_judge_calls(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = _write_run(Path(directory), decision="clarify", query_status="clarify")
            result = JudgeRuntime(DeterministicFakeModel([])).run(run_dir)
            self.assertEqual(result.final_advice["status"], "needs_clarification")
            self.assertEqual(result.judge_call_count, 0)
            self.assertFalse((run_dir / "06_judgements.json").exists())
            self.assertTrue((run_dir / "07_final_advice.json").exists())

    def test_unsupported_only_path_returns_source_error_without_judge(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = _write_run(Path(directory), packs=None)
            (run_dir / "04_candidate_acquisition.json").write_text(
                json.dumps(
                    {
                        "status": "unsupported_family_surface",
                        "warnings": [{"message": "Integration surface unavailable."}],
                    }
                ),
                encoding="utf-8",
            )
            result = JudgeRuntime(DeterministicFakeModel([])).run(run_dir)
            self.assertEqual(result.final_advice["status"], "source_error")
            self.assertEqual(result.judge_call_count, 0)
            self.assertFalse((run_dir / "06_judgements.json").exists())
            self.assertTrue((run_dir / "07_final_advice.json").exists())


if __name__ == "__main__":
    unittest.main()
