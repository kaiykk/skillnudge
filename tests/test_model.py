import hashlib
import unittest

from skillnudge.model import ModelError, validate_candidate, validate_session_reference, validate_skill


def make_skill(version: str, parent: str | None, text: str) -> dict:
    return {
        "skill_id": "identity-check",
        "version": version,
        "content": text,
        "sha256": hashlib.sha256(text.encode()).hexdigest(),
        "source": {"kind": "session", "ref": "session://001"},
        "parent_version": parent,
    }


class ModelTests(unittest.TestCase):
    def test_skill_content_identity_is_immutable(self):
        source = make_skill("v1", None, "Check source identity before reporting.")
        self.assertEqual(validate_skill(source)["version"], "v1")
        source["content"] = "changed"
        with self.assertRaises(ModelError):
            validate_skill(source)

    def test_session_reference_is_observable(self):
        evidence = {
            "session_id": "session-001",
            "trace_ref": "trace://session-001",
            "feedback_refs": ["user://feedback-001"],
            "observed_summary": "User corrected the source identity.",
        }
        self.assertEqual(validate_session_reference(evidence)["session_id"], "session-001")
        evidence["hidden_reasoning"] = "forbidden"
        with self.assertRaises(ModelError):
            validate_session_reference(evidence)

    def test_candidate_keeps_source_evidence_and_human_decision(self):
        source = make_skill("v1", None, "Check source identity before reporting.")
        candidate_skill = make_skill("v2", "v1", "Check source identity and cite the exact field.")
        candidate = {
            "candidate_id": "candidate-001",
            "source_skill": source,
            "candidate_skill": candidate_skill,
            "operator_ref": "external://pending-run",
            "evidence": {
                "session_id": "session-001",
                "trace_ref": "trace://session-001",
                "feedback_refs": ["user://feedback-001"],
                "observed_summary": "User corrected the source identity.",
            },
            "human_decision": "PENDING",
        }
        normalized = validate_candidate(candidate)
        self.assertEqual(normalized["human_decision"], "PENDING")
        candidate["human_decision"] = "ACCEPTED"
        self.assertEqual(validate_candidate(candidate)["human_decision"], "ACCEPTED")
        candidate["human_decision"] = "ROLLED_BACK"
        with self.assertRaises(ModelError):
            validate_candidate(candidate)


if __name__ == "__main__":
    unittest.main()
