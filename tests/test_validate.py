import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from skillnudge.cli import main  # noqa: E402
from skillnudge.validate import (  # noqa: E402
    VALIDATION_ENVELOPE_SCHEMA_VERSION,
    ValidationContractError,
    run_validation,
    validate_validation_envelope,
)


CONTENT = "Check the prerequisite before acting."
HASH = hashlib.sha256(CONTENT.encode()).hexdigest()
CONTEXT = {
    "task_id": "task-validate-001",
    "reference_host": "Codex",
    "model": "host-model",
    "harness_version": "host-v1",
    "tool_manifest": {"filesystem": "isolated"},
    "execution_budget": {"max_steps": 4, "max_tool_calls": 8},
    "environment_hash": "env-hash",
}


def envelope(control_success=True, treatment_success=True, valid=True):
    def arm(label, applied, success, started):
        return {
            "result": {"success": success},
            "observable_events": [{"event_id": f"{label}1", "kind": "completion", "summary": f"{label} completed bounded task.", "source_ref": f"fixture:{label}"}],
            "intervention_applied": applied,
            "intervention_identity": HASH if applied else None,
            "execution_context": dict(CONTEXT),
            "started_at": started,
            "execution_valid": valid,
            "execution_errors": [] if valid else [f"{label} host execution failed"],
        }
    return {
        "schema_version": VALIDATION_ENVELOPE_SCHEMA_VERSION,
        "review_result": {"schema_version": "native.review-result.v0", "experience_id": "exp-review-001", "disposition": "TEST", "problem": "Action preceded prerequisite check.", "assessment": {"impact": "medium", "attribution": {"primary": "capability_candidate", "alternatives": ["agent_lapse"]}, "addressability": "plausible", "testability": "testable", "uncertainty": ["Requires more than one task for reuse."]}, "evidence": {"referenced_event_ids": ["e1"]}, "intervention_candidate": {"title": "Precondition check", "target_behavior": "Check prerequisite before acting.", "intervention_hypothesis": "The instruction may improve this task.", "evidence_refs": ["e1"]}, "provider": None, "run_id": "review-run-001", "run_dir": "/user-data/review-runs/review-run-001"},
        "validation_spec": {"frozen_at": "2026-10-05T12:00:00+00:00", "task": {"task_id": CONTEXT["task_id"], "description": "Complete one bounded task.", "observable_success_condition": "Result success equals true."}, "intervention": {"type": "instruction", "exact_content": CONTENT, "sha256": HASH}, "oracle": {"type": "result_field_equals", "field": "success", "expected": True}, "execution": {"bounded": True, "mode": "host_observed_arms"}},
        "execution": {"control": arm("control", False, control_success, "2026-10-05T12:01:00+00:00"), "treatment": arm("treatment", True, treatment_success, "2026-10-05T12:02:00+00:00")},
    }


class ValidateTests(unittest.TestCase):
    def test_valid_pair_can_help(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_validation(envelope(False, True), run_dir=Path(directory) / "run")
        self.assertEqual(result["pair_status"], "VALID")
        self.assertEqual(result["validation_result"], "HELPS")
        self.assertEqual(result["scope"]["intervention_sha256"], HASH)

    def test_both_pass_is_neutral(self):
        result = run_validation(envelope(True, True), run_dir=Path(tempfile.mkdtemp()) / "run")
        self.assertEqual(result["validation_result"], "NEUTRAL")

    def test_invalid_execution_is_not_evaluated(self):
        result = run_validation(envelope(True, True, valid=False), run_dir=Path(tempfile.mkdtemp()) / "run")
        self.assertEqual(result["pair_status"], "INVALID")
        self.assertEqual(result["validation_result"], "NOT_EVALUATED")

    def test_hash_mismatch_rejected(self):
        value = envelope()
        value["validation_spec"]["intervention"]["sha256"] = "0" * 64
        with self.assertRaises(ValidationContractError):
            validate_validation_envelope(value)

    def test_context_mismatch_rejected(self):
        value = envelope()
        value["execution"]["treatment"]["execution_context"]["model"] = "other-model"
        with self.assertRaises(ValidationContractError):
            validate_validation_envelope(value)

    def test_started_before_freeze_rejected(self):
        value = envelope()
        value["execution"]["control"]["started_at"] = "2026-10-05T11:59:00+00:00"
        with self.assertRaises(ValidationContractError):
            validate_validation_envelope(value)

    def test_cli_help_and_stdin(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(["--help"]), 0)
        self.assertIn("validate", output.getvalue())
        value = json.dumps(envelope(False, True))
        with contextlib.redirect_stdout(io.StringIO()) as stdout, patch("sys.stdin", io.StringIO(value)):
            self.assertEqual(main(["validate", "--stdin", "--run-dir", str(Path(tempfile.mkdtemp()) / "cli-run")]), 0)
        self.assertEqual(json.loads(stdout.getvalue())["validation_result"], "HELPS")


if __name__ == "__main__":
    unittest.main()
