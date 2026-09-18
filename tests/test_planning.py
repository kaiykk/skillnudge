import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from skillnudge.planning import InputEnvelope, PlanningRunResult, PlanningRuntime, PlanningStageError
from skillnudge.planning_contracts import (
    ContractValidationError,
    validate_capability_framing,
    validate_intervention_plan,
    validate_query_plan,
)
from skillnudge.planning_model import DeterministicFakeModel, LiveModelProviderUnavailable, OpenAICompatibleModel


def _capability(*, missing: list[str], clarification_needed: bool = False) -> dict:
    return {
        "contract": {
            "goal": "Make progress on the user's current task",
            "stage": "exploration",
            "blocker": "The user cannot yet turn the current problem into a concrete next step.",
            "missing_capabilities": missing,
            "intended_effect": "Turn the current blockage into a clear next step.",
            "constraints": [],
            "not_needed": [],
            "uncertainties": [],
        },
        "confidence": "medium",
        "clarification_needed": clarification_needed,
        "clarification_question": "Which kind of security capability do you mean?" if clarification_needed else None,
    }


def _search_plan(primary: str, secondary: str | None = None) -> dict:
    targets = [{"family": primary, "priority": "primary", "rationale": "The main blocker is best addressed through this intervention family."}]
    if secondary:
        targets.append({"family": secondary, "priority": "secondary", "rationale": "A smaller complementary search surface may cover a distinct mechanism."})
    return {"decision": "search", "targets": targets, "decision_reason": "A bounded search can address the diagnosed capability gap."}


def _query_plan(families: list[str]) -> dict:
    angles = ["capability", "problem", "outcome", "operation", "professional_vocabulary"]
    return {
        "status": "ready",
        "queries": [
            {
                "family": family,
                "angle": angles[index % len(angles)],
                "semantic_query": f"{family} response to the current capability blocker",
                "purpose": "Explore a complementary semantic angle for the diagnosed capability.",
            }
            for index, family in enumerate(families)
        ],
    }


def _responses_for(case_id: str) -> list[dict]:
    if case_id == "D001":
        return [
            _capability(missing=["design framing", "prototyping guidance", "professional vocabulary"]),
            _search_plan("skill", "resource"),
            _query_plan(["skill", "skill", "skill", "resource"]),
        ]
    if case_id == "D002":
        return [
            _capability(missing=["deliberative collaboration", "problem reframing", "gradual convergence"]),
            _search_plan("integration", "skill"),
            _query_plan(["integration", "integration", "skill"]),
        ]
    if case_id == "D003":
        return [
            {
                **_capability(missing=[]),
                "contract": {
                    **_capability(missing=[])["contract"],
                    "goal": "Understand the concrete error",
                    "stage": None,
                    "blocker": "No external capability blocker is identified.",
                    "intended_effect": "Understand the error and next step without an additional intervention.",
                },
            },
            {"decision": "no_intervention", "targets": [], "decision_reason": "The current agent can explain this local error directly."},
        ]
    raise AssertionError(case_id)


class PlanningContractTests(unittest.TestCase):
    def test_capability_contract_maximum_and_clarification_consistency(self):
        valid = _capability(missing=["a", "b", "c"])
        self.assertEqual(validate_capability_framing(valid)["contract"]["missing_capabilities"], ["a", "b", "c"])
        too_many = _capability(missing=["a", "b", "c", "d"])
        with self.assertRaises(ContractValidationError):
            validate_capability_framing(too_many)
        invalid_clarification = _capability(missing=[], clarification_needed=False)
        invalid_clarification["clarification_question"] = "not null"
        with self.assertRaises(ContractValidationError):
            validate_capability_framing(invalid_clarification)
        empty_clarification = _capability(missing=[], clarification_needed=True)
        empty_clarification["clarification_question"] = ""
        with self.assertRaises(ContractValidationError):
            validate_capability_framing(empty_clarification)

    def test_intervention_plan_limits_and_early_stop_invariants(self):
        valid = _search_plan("skill", "resource")
        self.assertEqual(validate_intervention_plan(valid), valid)
        too_many = _search_plan("skill", "resource")
        too_many["targets"].append({"family": "integration", "priority": "companion", "rationale": "extra"})
        with self.assertRaises(ContractValidationError):
            validate_intervention_plan(too_many)
        invalid_stop = {"decision": "no_intervention", "targets": [{"family": "skill", "priority": "primary", "rationale": "x"}], "decision_reason": "x"}
        with self.assertRaises(ContractValidationError):
            validate_intervention_plan(invalid_stop)

    def test_query_plan_limits_and_early_stop_invariants(self):
        valid = _query_plan(["skill", "skill", "resource", "skill", "resource"])
        self.assertEqual(len(validate_query_plan(valid)["queries"]), 5)
        too_many = _query_plan(["skill"] * 6)
        with self.assertRaises(ContractValidationError):
            validate_query_plan(too_many)
        with self.assertRaises(ContractValidationError):
            validate_query_plan({"status": "skipped", "queries": [{"family": "skill", "angle": "problem", "semantic_query": "x", "purpose": "x"}]})


class PlanningRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads((ROOT / "eval/cases/planning_runtime.json").read_text(encoding="utf-8"))["cases"]
        cls.case_by_id = {case["case_id"]: case for case in cls.cases}

    def test_fake_runtime_runs_d001_d002_d003_without_candidate_acquisition(self):
        for case_id in ("D001", "D002", "D003"):
            case = self.case_by_id[case_id]
            with self.subTest(case_id=case_id), tempfile.TemporaryDirectory() as directory:
                fake = DeterministicFakeModel(_responses_for(case_id))
                result = PlanningRuntime(fake).run(InputEnvelope(case["raw_request"]), Path(directory) / case_id)
                self.assertIsInstance(result, PlanningRunResult)
                self.assertEqual(result.input_envelope["raw_request"], case["raw_request"])
                self.assertEqual(result.intervention_plan["decision"], case["expected"]["intervention_decision"])
                self.assertEqual(result.query_plan["status"], case["expected"]["query_status"])
                if case_id == "D003":
                    self.assertEqual(result.capability_framing["contract"]["missing_capabilities"], [])
                    self.assertEqual(len(fake.calls), 2)
                else:
                    self.assertEqual(result.intervention_plan["targets"][0]["family"], case["expected"]["primary_family"])
                    self.assertEqual(len(fake.calls), 3)
                output_dir = Path(directory) / case_id
                self.assertTrue((output_dir / "00_input.json").exists())
                self.assertTrue((output_dir / "01_capability_contract.json").exists())
                self.assertTrue((output_dir / "02_intervention_plan.json").exists())
                self.assertTrue((output_dir / "03_query_plan.json").exists())
                self.assertFalse((output_dir / "04_candidate_acquisition.json").exists())
                trace = (output_dir / "trace.jsonl").read_text(encoding="utf-8")
                self.assertNotIn("Candidate Acquisition", trace)
                self.assertIn('"event": "run_completed"', trace)
                if case_id == "D003":
                    self.assertIn('"event": "early_stop"', trace)

    def test_clarification_early_stop_does_not_call_later_stages(self):
        case = self.case_by_id["clarification-edge"]
        fake = DeterministicFakeModel([_capability(missing=[], clarification_needed=True)])
        with tempfile.TemporaryDirectory() as directory:
            result = PlanningRuntime(fake).run(InputEnvelope(case["raw_request"]), directory)
            self.assertEqual(result.intervention_plan, {"decision": "clarify", "targets": [], "decision_reason": "Clarification is required before choosing an intervention family."})
            self.assertEqual(result.query_plan, {"status": "clarify", "queries": []})
            self.assertEqual(len(fake.calls), 1)

    def test_invalid_model_json_gets_one_repair_attempt(self):
        responses = ["not json", _capability(missing=[]), {"decision": "no_intervention", "targets": [], "decision_reason": "direct answer"}]
        fake = DeterministicFakeModel(responses)
        with tempfile.TemporaryDirectory() as directory:
            PlanningRuntime(fake).run(InputEnvelope("a request"), directory)
            self.assertEqual(len(fake.calls), 3)
            trace = (Path(directory) / "trace.jsonl").read_text(encoding="utf-8")
            self.assertIn('"repair_attempt": 1', trace)

    def test_second_invalid_model_response_fails_explicitly(self):
        fake = DeterministicFakeModel(["not json", "still not json"])
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(PlanningStageError):
                PlanningRuntime(fake).run(InputEnvelope("a request"), directory)
            trace = (Path(directory) / "trace.jsonl").read_text(encoding="utf-8")
            self.assertIn('"event": "error"', trace)
            self.assertFalse((Path(directory) / "02_intervention_plan.json").exists())

    def test_live_provider_without_credentials_reports_unavailable(self):
        model = OpenAICompatibleModel(api_key=None)
        with self.assertRaises(LiveModelProviderUnavailable):
            model.generate_structured(stage="Capability Framing", prompt="{}", prompt_version="test")

    def test_production_planning_has_no_golden_case_routing(self):
        production = "\n".join(
            (ROOT / "src/skillnudge" / name).read_text(encoding="utf-8")
            for name in ("planning.py", "planning_contracts.py", "prompts.py")
        )
        for forbidden in ("ui-ux-pro-max", "Superpowers", "if \"ui\"", "if \"brainstorm\""):
            self.assertNotIn(forbidden, production)


if __name__ == "__main__":
    unittest.main()
