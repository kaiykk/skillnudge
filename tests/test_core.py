import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from skillnudge.cli import main
from skillnudge.evidence import EvidenceValidationError, validate_session_evidence
from skillnudge.lineage import apply_human_decision, validate_candidate
from skillnudge.operator import validate_evolution_request, validate_operator_result
from skillnudge.skill import SkillValidationError, validate_skill_version
from skillnudge.storage import read_json, write_json_atomic


def skill(*, version="v2", status="CANDIDATE"):
    content = f"Check the source before reporting ({version})."
    return {
        "schema_version": "skillnudge.skill-version.v0",
        "skill_id": "record-identity",
        "version": version,
        "content": content,
        "sha256": hashlib.sha256(content.encode()).hexdigest(),
        "source": {"kind": "operator", "ref": "operator://run-001"},
        "parent_version": "v1" if version != "v1" else None,
        "lifecycle_status": status,
    }


class CoreRecordTests(unittest.TestCase):
    def test_skill_identity_and_hash_are_validated(self):
        normalized = validate_skill_version(skill())
        self.assertEqual(normalized["skill_id"], "record-identity")
        broken = skill()
        broken["content"] = "tampered"
        with self.assertRaises(SkillValidationError):
            validate_skill_version(broken)

    def test_session_evidence_is_observable_only(self):
        value = {
            "schema_version": "skillnudge.session-evidence.v0",
            "evidence_id": "evidence-001",
            "session_id": "session-001",
            "trace_ref": "trace://session-001",
            "feedback_refs": ["feedback://user-001"],
            "observed_summary": "User corrected the source identity after the report.",
        }
        self.assertEqual(validate_session_evidence(value)["session_id"], "session-001")
        value["hidden_reasoning"] = "must not enter evidence"
        with self.assertRaises(EvidenceValidationError):
            validate_session_evidence(value)

    def test_operator_request_and_result_preserve_boundary(self):
        request = validate_evolution_request({
            "schema_version": "skillnudge.evolution-request.v0",
            "request_id": "request-001",
            "skill_id": "record-identity",
            "source_version": "v1",
            "objective": "Reduce source identity mistakes.",
            "operator": "external",
            "evidence_refs": ["evidence-001"],
        })
        result = validate_operator_result({
            "schema_version": "skillnudge.operator-result.v0",
            "result_id": "operator-result-001",
            "request_id": request["request_id"],
            "operator": "external",
            "operator_version": "adapter-prototype",
            "status": "CANDIDATE",
            "candidate": skill(),
            "native_ref": "operator://run-001/result.json",
            "provenance_refs": ["evidence-001"],
        })
        self.assertEqual(result["candidate"]["parent_version"], "v1")

    def test_candidate_lineage_requires_parent_and_keeps_pending(self):
        value = {
            "schema_version": "skillnudge.candidate.v0",
            "candidate_id": "candidate-001",
            "source_skill_id": "record-identity",
            "source_version": "v1",
            "candidate_skill": skill(),
            "operator_result_id": "operator-result-001",
            "evidence_refs": ["evidence-001"],
            "human_decision": "PENDING",
        }
        self.assertEqual(validate_candidate(value)["human_decision"], "PENDING")
        accepted = apply_human_decision(value, "ACCEPTED")
        self.assertEqual(accepted["human_decision"], "ACCEPTED")
        self.assertEqual(accepted["candidate_skill"]["lifecycle_status"], "CANDIDATE")
        broken = dict(value)
        broken["source_version"] = "v3"
        with self.assertRaises(ValueError):
            validate_candidate(broken)

    def test_atomic_json_persistence_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = write_json_atomic(Path(directory) / "records" / "candidate.json", {"id": "candidate-001"})
            self.assertEqual(read_json(path), {"id": "candidate-001"})

    def test_cli_validates_and_records_human_decision(self):
        value = json.dumps({
            "schema_version": "skillnudge.session-evidence.v0",
            "evidence_id": "evidence-001",
            "session_id": "session-001",
            "trace_ref": "trace://session-001",
            "feedback_refs": ["feedback://user-001"],
            "observed_summary": "A correction was recorded.",
        })
        # Call with an isolated stdin so the test covers the public parser.
        import sys
        original_stdin = sys.stdin
        try:
            sys.stdin = io.StringIO(value)
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["validate", "evidence", "--stdin"]), 0)
        finally:
            sys.stdin = original_stdin
        self.assertEqual(json.loads(output.getvalue())["evidence_id"], "evidence-001")


if __name__ == "__main__":
    unittest.main()
