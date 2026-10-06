import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from unittest import mock
from copy import deepcopy
from pathlib import Path

from skillnudge.cli import main
from skillnudge.evolve import EvolveContractError, run_evolve, validate_evolve_envelope


def artifact(content, version, capability_id="check-result"):
    return {
        "schema_version": "native.capability-artifact.v0",
        "capability_id": capability_id,
        "version": version,
        "type": "instruction",
        "exact_content": content,
        "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
    }


def envelope(*, disposition="TEST", validation_outcome="HELPS", validation_mode="INTERVENTION_ABLATION", include_validation=True, attribution="capability_candidate"):
    source = artifact("Check the result before reporting.", "v1")
    candidate = artifact("Check the result and cite the exact field before reporting.", "v2")
    review = {
        "schema_version": "native.review-result.v0",
        "experience_id": "exp-evolve-1",
        "disposition": disposition,
        "assessment": {"impact": "medium", "attribution": {"primary": attribution, "alternatives": ["agent_lapse", "project_fact"]}, "addressability": "plausible", "testability": "testable", "uncertainty": ["One bounded task."]},
        "evidence": {"referenced_event_ids": ["evt-1"]},
        "intervention_candidate": {"title": "Result check", "target_behavior": "verify output", "intervention_hypothesis": "A check instruction may prevent omission.", "evidence_refs": ["evt-1"]},
        "provider": None,
        "run_id": "review-evolve-1",
        "run_dir": "/tmp/review-evolve-1",
    }
    scope = {"task_id": "task-evolve-1", "comparison_mode": validation_mode}
    if validation_mode == "INTERVENTION_ABLATION":
        scope["intervention_sha256"] = candidate["sha256"]
    else:
        scope["baseline_capability"] = {"capability_id": source["capability_id"], "version": source["version"], "sha256": source["sha256"]}
        scope["candidate_capability"] = {"capability_id": candidate["capability_id"], "version": candidate["version"], "sha256": candidate["sha256"]}
    validation = {
        "schema_version": "native.validation-result.v0",
        "run_id": "validate-evolve-1",
        "review_run_id": "review-evolve-1",
        "experience_id": "exp-evolve-1",
        "task_id": "task-evolve-1",
        "pair_status": "VALID",
        "validation_result": validation_outcome,
        "scope": scope,
        "control": {"oracle": {"status": "failure"}, "observable_event_ids": ["evt-control"]},
        "treatment": {"oracle": {"status": "success"}, "observable_event_ids": ["evt-treatment"]},
        "limitations": ["One bounded task only."],
    }
    value = {"schema_version": "native.evolve-envelope.v0", "source": source, "review_result": review, "candidate": {**candidate, "change_summary": "Add an explicit field check."}}
    if include_validation:
        value["validation_result"] = validation
    return value


class EvolveTests(unittest.TestCase):
    def test_valid_evolve_emits_candidate_only(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_evolve(envelope(), run_dir=Path(directory) / "run")
        self.assertEqual(result["lifecycle_status"], "CANDIDATE")
        self.assertEqual(result["decision_state"], {"status": "PENDING_VALIDATION", "suggested_action": "VALIDATE", "authority": "HUMAN_REQUIRED"})
        self.assertEqual(result["candidate"]["parent_sha256"], result["source"]["sha256"])

    def test_direct_review_admission_emits_candidate_without_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_evolve(envelope(include_validation=False), run_dir=Path(directory) / "direct-run")
        self.assertEqual(result["admission_basis"], "REVIEW")
        self.assertIsNone(result["change"]["validation_run_id"])
        self.assertEqual(result["lifecycle_status"], "CANDIDATE")

    def test_direct_review_requires_capability_candidate_attribution(self):
        with self.assertRaisesRegex(EvolveContractError, "capability_candidate"):
            validate_evolve_envelope(envelope(include_validation=False, attribution="agent_lapse"))

    def test_review_must_be_test(self):
        value = envelope(disposition="WATCH")
        with self.assertRaises(EvolveContractError):
            validate_evolve_envelope(value)

    def test_optional_validation_must_be_valid_when_supplied(self):
        for kwargs in ({"validation_outcome": "NEUTRAL"},):
            validate_evolve_envelope(envelope(**kwargs))
        value = envelope()
        value["validation_result"]["pair_status"] = "INVALID"
        with self.assertRaises(EvolveContractError):
            validate_evolve_envelope(value)

    def test_unrelated_validation_rejected(self):
        value = envelope()
        value["validation_result"]["review_run_id"] = "other-review"
        with self.assertRaises(EvolveContractError):
            validate_evolve_envelope(value)

    def test_candidate_identity_collisions_rejected(self):
        value = envelope()
        value["candidate"]["version"] = "v1"
        with self.assertRaises(EvolveContractError):
            validate_evolve_envelope(value)
        value = envelope()
        value["candidate"]["exact_content"] = value["source"]["exact_content"]
        value["candidate"]["sha256"] = value["source"]["sha256"]
        with self.assertRaises(EvolveContractError):
            validate_evolve_envelope(value)

    def test_intervention_hash_linkage_is_required(self):
        value = envelope()
        value["validation_result"]["scope"]["intervention_sha256"] = "0" * 64
        with self.assertRaises(EvolveContractError):
            validate_evolve_envelope(value)

    def test_capability_revision_is_post_evolve_only(self):
        value = envelope(validation_mode="CAPABILITY_REVISION")
        with self.assertRaisesRegex(EvolveContractError, "CAPABILITY_REVISION runs after EVOLVE"):
            validate_evolve_envelope(value)

    def test_cli_help_and_stdin(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with self.assertRaises(SystemExit) as help_exit:
                main(["evolve", "--help"])
        self.assertEqual(help_exit.exception.code, 0)
        self.assertIn("--stdin", output.getvalue())
        with tempfile.TemporaryDirectory() as directory:
            with contextlib.redirect_stdout(io.StringIO()) as stdout, contextlib.redirect_stderr(io.StringIO()), mock.patch("sys.stdin", io.StringIO(json.dumps(envelope()))):
                self.assertEqual(main(["evolve", "--stdin", "--run-dir", str(Path(directory) / "cli-run")]), 0)
            self.assertEqual(json.loads(stdout.getvalue())["lifecycle_status"], "CANDIDATE")


if __name__ == "__main__":
    unittest.main()
