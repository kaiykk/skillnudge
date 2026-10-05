import contextlib
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
from skillnudge.review import (  # noqa: E402
    REVIEW_ENVELOPE_SCHEMA_VERSION,
    ReviewValidationError,
    run_review,
    validate_review_envelope,
)


def envelope(*, disposition="TEST", candidate=True, addressability="plausible", testability="testable"):
    return {
        "schema_version": REVIEW_ENVELOPE_SCHEMA_VERSION,
        "experience": {
            "experience_id": "exp-fixture-001",
            "source": {"type": "inline", "reference": "fixture://review/001"},
            "observable_events": [
                {"event_id": "e1", "kind": "tool_error", "summary": "The prerequisite check returned an observable runtime error.", "source_ref": "fixture:1"},
                {"event_id": "e2", "kind": "agent_action", "summary": "The agent proceeded before resolving the prerequisite.", "source_ref": "fixture:2"},
            ],
        },
        "assessment": {
            "problem": "The agent acted before validating a prerequisite.",
            "impact": "medium",
            "attribution": {"primary": "capability_candidate", "alternatives": ["agent_lapse", "environment"]},
            "addressability": addressability,
            "testability": testability,
            "evidence_refs": ["e1", "e2"],
            "uncertainty": ["The pattern needs an independent task to confirm reuse."],
        },
        "intervention_candidate": {
            "title": "Prerequisite validation scaffold",
            "target_behavior": "Validate prerequisites before downstream action.",
            "intervention_hypothesis": "A small validation scaffold may reduce premature action.",
            "evidence_refs": ["e1", "e2"],
        } if candidate else None,
        "disposition": disposition,
    }


class ReviewContractTests(unittest.TestCase):
    def test_candidate_fixture_is_test(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_review(envelope(), run_dir=Path(directory) / "run")
            self.assertEqual(result["disposition"], "TEST")
            self.assertEqual(result["evidence"]["referenced_event_ids"], ["e1", "e2"])
            self.assertIsNotNone(result["intervention_candidate"])
            self.assertTrue((Path(result["run_dir"]) / "trace.jsonl").is_file())

    def test_environment_failure_is_no_intervention(self):
        value = envelope(disposition="NO_INTERVENTION", candidate=False, addressability="none", testability="not_testable")
        value["assessment"]["attribution"] = {"primary": "environment", "alternatives": ["agent_lapse"]}
        result = run_review(value, run_dir=Path(tempfile.mkdtemp()) / "run")
        self.assertEqual(result["disposition"], "NO_INTERVENTION")
        self.assertIsNone(result["intervention_candidate"])

    def test_insufficient_has_no_candidate(self):
        value = envelope(disposition="INSUFFICIENT", candidate=False, addressability="unknown", testability="unclear")
        value["assessment"]["attribution"] = {"primary": "unclear", "alternatives": ["project_fact"]}
        result = validate_review_envelope(value)
        self.assertEqual(result["disposition"], "INSUFFICIENT")

    def test_unknown_evidence_ref_rejected(self):
        value = envelope()
        value["assessment"]["evidence_refs"] = ["missing"]
        with self.assertRaises(ReviewValidationError):
            validate_review_envelope(value)

    def test_test_without_candidate_rejected(self):
        with self.assertRaises(ReviewValidationError):
            validate_review_envelope(envelope(candidate=False))

    def test_no_intervention_with_candidate_rejected(self):
        with self.assertRaises(ReviewValidationError):
            validate_review_envelope(envelope(disposition="NO_INTERVENTION"))

    def test_insufficient_with_candidate_rejected(self):
        with self.assertRaises(ReviewValidationError):
            validate_review_envelope(envelope(disposition="INSUFFICIENT"))

    def test_test_requires_testable_and_plausible(self):
        with self.assertRaises(ReviewValidationError):
            validate_review_envelope(envelope(testability="unclear"))
        with self.assertRaises(ReviewValidationError):
            validate_review_envelope(envelope(addressability="weak"))

    def test_private_reasoning_rejected(self):
        value = envelope()
        value["assessment"]["chain_of_thought"] = "private"
        with self.assertRaises(ReviewValidationError):
            validate_review_envelope(value)

    def test_duplicate_event_ids_and_unknown_fields_rejected(self):
        value = envelope()
        value["experience"]["observable_events"][1]["event_id"] = "e1"
        with self.assertRaises(ReviewValidationError):
            validate_review_envelope(value)
        value = envelope()
        value["extra"] = True
        with self.assertRaises(ReviewValidationError):
            validate_review_envelope(value)

    def test_cli_help_and_stdin(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(["--help"]), 0)
        self.assertIn("review", output.getvalue())
        stdin_value = json.dumps(envelope())
        with contextlib.redirect_stdout(io.StringIO()) as stdout, patch("sys.stdin", io.StringIO(stdin_value)):
            self.assertEqual(main(["review", "--stdin", "--run-dir", str(Path(tempfile.mkdtemp()) / "cli-run")]), 0)
        result = json.loads(stdout.getvalue())
        self.assertEqual(result["disposition"], "TEST")
        self.assertIsNone(result["provider"])


if __name__ == "__main__":
    unittest.main()
