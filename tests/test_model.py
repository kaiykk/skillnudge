import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from skillnudge.model import (
    ModelError,
    build_skillopt_sleep_tasks,
    content_sha256,
    quick_improve,
    stage_candidate,
    validate_candidate,
    validate_session_reference,
    validate_skill,
)


def make_skill(version: str, parent: str | None, text: str) -> dict:
    return {
        "skill_id": "format-skill",
        "version": version,
        "content": text,
        "sha256": hashlib.sha256(text.encode()).hexdigest(),
        "source": {"kind": "file", "ref": "SKILL.md"},
        "parent_version": parent,
    }


def make_evidence() -> dict:
    return {
        "session_id": "session-001",
        "trace_ref": "trace://session-001",
        "feedback_refs": ["user://feedback-001"],
        "observed_summary": "The agent omitted the requested wrapper; the user corrected it.",
    }


class ModelTests(unittest.TestCase):
    def test_quick_improve_stages_unverified_candidate_and_preserves_lineage(self):
        source = make_skill("v1", None, "Answer the request.")
        proposal = {
            "diagnosis": "The Skill does not encode the explicit output boundary.",
            "change_summary": "Add one instruction to preserve the requested wrapper.",
            "candidate_content": "Answer the request and preserve the exact output wrapper.",
            "validation_status": "UNVERIFIED",
            "validation_basis": "No independent replay was run for this proposal.",
        }
        with tempfile.TemporaryDirectory() as directory:
            skill_path = Path(directory) / "SKILL.md"
            skill_path.write_text(source["content"], encoding="utf-8")
            staging = Path(directory) / "candidate"
            result = quick_improve(
                source,
                skill_path=str(skill_path),
                failure="The output omitted the wrapper.",
                feedback="Keep the exact wrapper requested by the user.",
                evidence=make_evidence(), proposal=proposal,
                candidate_id="candidate-001", candidate_version="v1-candidate-1",
                staging_dir=str(staging),
            )
            self.assertEqual(result["status"], "CANDIDATE_PENDING")
            self.assertEqual(result["validation"]["status"], "UNVERIFIED")
            self.assertFalse(result["source_modified"])
            self.assertTrue(result["diff"])
            self.assertEqual(result["candidate"]["human_decision"], "PENDING")
            self.assertEqual(skill_path.read_text(encoding="utf-8"), source["content"])
            self.assertEqual(json.loads((staging / "provenance.json").read_text())["session"], make_evidence())
            manifest = json.loads((staging / "manifest.json").read_text())
            self.assertEqual(manifest["validation"]["status"], "UNVERIFIED")
            self.assertEqual((staging / "diff.patch").read_text(), result["diff"])

    def test_quick_improve_rejects_noop_and_invalid_status(self):
        source = make_skill("v1", None, "Answer the request.")
        base = {
            "diagnosis": "A diagnosis.", "change_summary": "A bounded edit.",
            "candidate_content": source["content"], "validation_status": "UNVERIFIED",
            "validation_basis": "Not run.",
        }
        with tempfile.TemporaryDirectory() as directory:
            skill_path = Path(directory) / "SKILL.md"
            skill_path.write_text(source["content"], encoding="utf-8")
            with self.assertRaises(ModelError):
                quick_improve(source, skill_path=str(skill_path), failure="bad", feedback="fix", evidence=make_evidence(), proposal=base, candidate_id="c", candidate_version="v2")
            with self.assertRaises(ModelError):
                quick_improve(source, skill_path=str(skill_path), failure="bad", feedback="fix", evidence=make_evidence(), proposal={**base, "candidate_content": "new", "validation_status": "MAYBE"}, candidate_id="c", candidate_version="v2")

    def test_stage_candidate_rejects_source_drift(self):
        source = make_skill("v1", None, "source")
        candidate = {
            "candidate_id": "candidate-001", "source_skill": source,
            "candidate_skill": make_skill("v2", "v1", "candidate"),
            "operator_ref": "host-agent:quick-improve", "evidence": make_evidence(),
            "human_decision": "PENDING",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "SKILL.md"
            path.write_text("drifted", encoding="utf-8")
            with self.assertRaises(ModelError):
                stage_candidate(candidate, task_id="session-001", gate_result={"action": "STAGE_PENDING_REVIEW", "validation_status": "UNVERIFIED", "validation_basis": "not run"}, staging_dir=str(Path(directory) / "stage"), source_skill_path=str(path))

    def test_skill_and_session_validators_remain_strict(self):
        source = make_skill("v1", None, "source")
        self.assertEqual(validate_skill(source)["sha256"], content_sha256("source"))
        self.assertEqual(validate_session_reference(make_evidence())["session_id"], "session-001")
        with self.assertRaises(ModelError):
            validate_candidate({"candidate_id": "c"})

    def test_skillopt_handoff_remains_a_thin_compatibility_boundary(self):
        source = make_skill("v1", None, "source")
        payload = build_skillopt_sleep_tasks(
            make_evidence(), source, project="/tmp/project", target_skill_path="/tmp/project/SKILL.md",
            intent="Return the requested value.", context_excerpt="The format was corrected.",
            attempted_solution="Returned an unformatted value.", reference_kind="exact", reference="42",
        )
        self.assertEqual(payload["format"], "skillopt_sleep.tasks.v1")
        self.assertEqual(payload["skillnudge_provenance"]["trace_ref"], "trace://session-001")
        self.assertFalse(payload["reviewed"])


if __name__ == "__main__":
    unittest.main()
