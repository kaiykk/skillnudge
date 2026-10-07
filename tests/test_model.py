import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from skillnudge.model import (
    ModelError,
    build_skillopt_sleep_tasks,
    content_sha256,
    stage_candidate,
    validate_candidate,
    validate_session_reference,
    validate_skill,
)


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
    def test_stage_candidate_closes_provenance_without_adoption(self):
        session = {
            "session_id": "session-001",
            "trace_ref": "trace://session-001",
            "feedback_refs": ["user://feedback-001"],
            "observed_summary": "User corrected the requested output format.",
        }
        source = make_skill("v1", None, "Follow the user's requested output format.")
        candidate_skill = make_skill("v2", "v1", "Always wrap the final answer.")
        candidate = {
            "candidate_id": "candidate-001",
            "source_skill": source,
            "candidate_skill": candidate_skill,
            "operator_ref": "skillopt-sleep:night-7",
            "evidence": session,
            "human_decision": "PENDING",
        }
        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / "source-SKILL.md"
            source_path.write_text(source["content"], encoding="utf-8")
            staging_path = Path(directory) / "staging"
            manifest = stage_candidate(
                candidate,
                task_id="session-001-skillnudge-handoff",
                gate_result={"accepted": True, "baseline_score": 0.0, "candidate_score": 1.0},
                staging_dir=str(staging_path),
                source_skill_path=str(source_path),
            )
            provenance = json.loads(
                (staging_path / "provenance.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["human_decision"], "PENDING")
            self.assertEqual(provenance["session"]["session_id"], "session-001")
            self.assertEqual(provenance["session"]["trace_ref"], "trace://session-001")
            self.assertEqual(provenance["session"]["feedback_refs"], ["user://feedback-001"])
            self.assertEqual(provenance["candidate_skill"]["sha256"], content_sha256(candidate_skill["content"]))
            self.assertEqual(
                (staging_path / "proposed_SKILL.md").read_text(encoding="utf-8"),
                candidate_skill["content"],
            )
            with self.assertRaises(ModelError):
                stage_candidate(
                    candidate,
                    task_id="session-001-skillnudge-handoff",
                    gate_result={"accepted": True},
                    staging_dir=str(staging_path),
                    source_skill_path=str(source_path),
                )

    def test_stage_candidate_rejects_unaccepted_gate(self):
        source = make_skill("v1", None, "source")
        candidate = {
            "candidate_id": "candidate-001",
            "source_skill": source,
            "candidate_skill": make_skill("v2", "v1", "candidate"),
            "operator_ref": "external",
            "evidence": {
                "session_id": "session-001",
                "trace_ref": "trace://session-001",
                "feedback_refs": ["user://feedback-001"],
                "observed_summary": "correction",
            },
            "human_decision": "PENDING",
        }
        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / "source-SKILL.md"
            source_path.write_text(source["content"], encoding="utf-8")
            with self.assertRaises(ModelError):
                stage_candidate(
                    candidate,
                    task_id="task-001",
                    gate_result={"accepted": False},
                    staging_dir=directory,
                    source_skill_path=str(source_path),
                )

    def test_stage_candidate_rejects_source_baseline_drift(self):
        source = make_skill("v1", None, "source")
        candidate = {
            "candidate_id": "candidate-001",
            "source_skill": source,
            "candidate_skill": make_skill("v2", "v1", "candidate"),
            "operator_ref": "external",
            "evidence": {
                "session_id": "session-001",
                "trace_ref": "trace://session-001",
                "feedback_refs": ["user://feedback-001"],
                "observed_summary": "correction",
            },
            "human_decision": "PENDING",
        }
        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / "source-SKILL.md"
            source_path.write_text("drifted", encoding="utf-8")
            with self.assertRaises(ModelError):
                stage_candidate(
                    candidate,
                    task_id="task-001",
                    gate_result={"accepted": True},
                    staging_dir=str(Path(directory) / "staging"),
                    source_skill_path=str(source_path),
                )

    @unittest.skipUnless(
        os.environ.get("SKILLOPT_SOURCE"),
        "set SKILLOPT_SOURCE to run the optional upstream loader compatibility check",
    )
    def test_handoff_round_trips_through_upstream_loader(self):
        root = os.environ["SKILLOPT_SOURCE"]
        sys.path.insert(0, root)
        try:
            from skillopt_sleep.tasks_file import load_tasks_file

            session = {
                "session_id": "session-001",
                "trace_ref": "trace://session-001",
                "feedback_refs": ["user://feedback-001"],
                "observed_summary": "correction",
            }
            source = make_skill("v1", None, "source")
            payload = build_skillopt_sleep_tasks(
                session,
                source,
                project="/tmp/project",
                target_skill_path="/tmp/project/SKILL.md",
                intent="Return the requested value.",
                context_excerpt="The format was corrected.",
                attempted_solution="Returned an unformatted value.",
                reference_kind="exact",
                reference="42",
            )
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "tasks.json"
                path.write_text(json.dumps(payload), encoding="utf-8")
                tasks, meta = load_tasks_file(str(path))
            self.assertEqual(tasks[0].id, "session-001-skillnudge-handoff")
            self.assertEqual(tasks[0].source_sessions, ["session-001"])
            self.assertEqual(meta["skillnudge_provenance"]["trace_ref"], "trace://session-001")
        finally:
            sys.path.remove(root)

    def test_skillopt_sleep_handoff_preserves_session_and_skill_provenance(self):
        session = {
            "session_id": "session-001",
            "trace_ref": "trace://session-001",
            "feedback_refs": ["user://feedback-001"],
            "observed_summary": "User corrected the requested output format.",
        }
        source = make_skill("v1", None, "Follow the user's requested output format.")
        payload = build_skillopt_sleep_tasks(
            session,
            source,
            project="/tmp/project",
            target_skill_path="/tmp/project/SKILL.md",
            intent="Return the requested value in the exact format.",
            context_excerpt="The observed answer omitted the requested wrapper.",
            attempted_solution="Returned a plain answer.",
            reference_kind="exact",
            reference="42",
            tags=["reviewed:format-correction"],
        )
        self.assertFalse(payload["reviewed"])
        self.assertEqual(payload["tasks"][0]["source_sessions"], ["session-001"])
        self.assertEqual(payload["tasks"][0]["tags"], ["reviewed:format-correction"])
        self.assertEqual(payload["skillnudge_provenance"]["trace_ref"], "trace://session-001")
        self.assertEqual(payload["skillnudge_provenance"]["feedback_refs"], ["user://feedback-001"])
        self.assertEqual(
            payload["skillnudge_provenance"]["source_skill"]["sha256"],
            source["sha256"],
        )

    def test_skillopt_sleep_handoff_rejects_source_skill_file_drift(self):
        session = {
            "session_id": "session-001",
            "trace_ref": "trace://session-001",
            "feedback_refs": ["user://feedback-001"],
            "observed_summary": "User corrected the requested output format.",
        }
        source = make_skill("v1", None, "Follow the user's requested output format.")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "SKILL.md"
            path.write_text("drifted", encoding="utf-8")
            with self.assertRaises(ModelError):
                build_skillopt_sleep_tasks(
                    session,
                    source,
                    project=directory,
                    target_skill_path=str(path),
                    source_skill_path=str(path),
                    intent="Return the requested value in the exact format.",
                    context_excerpt="The observed answer omitted the requested wrapper.",
                    attempted_solution="Returned a plain answer.",
                )

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
