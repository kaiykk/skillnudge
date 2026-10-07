import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _artifact(content, version, capability_id="record-identity"):
    return {
        "schema_version": "native.capability-artifact.v0",
        "capability_id": capability_id,
        "version": version,
        "type": "instruction",
        "exact_content": content,
        "sha256": hashlib.sha256(content.encode()).hexdigest(),
    }


def _subject(artifact):
    return {
        "capability_id": artifact["capability_id"],
        "candidate_version": artifact["version"],
        "candidate_sha256": artifact["sha256"],
    }


class GoldenPathTests(unittest.TestCase):
    def run_cli(self, args, value):
        completed = subprocess.run(
            [sys.executable, "-m", "skillnudge", *args],
            input=json.dumps(value),
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
            check=True,
        )
        return json.loads(completed.stdout)

    def test_review_evolve_suspend_wake_continue_and_post_wake_validate(self):
        with tempfile.TemporaryDirectory(prefix="skillnudge-golden-path-") as directory:
            root = Path(directory)
            data_dir = root / "data"
            runs = root / "runs"
            runs.mkdir()
            source = _artifact("Check the record identity before reporting.", "v1")
            candidate = _artifact(
                "Check the record identity and cite the exact source field before reporting.",
                "v2",
            )
            scope = {
                "model": "codex-reference-host",
                "harness": "native-v1",
                "task_family": "structured-record-transformation",
            }
            validation_context = {
                "task_id": "golden-task-001",
                "reference_host": "Codex Reference Host",
                "model": "codex-reference-model",
                "harness_version": "native-golden-v1",
                "tool_manifest": {"filesystem": "isolated"},
                "execution_budget": {"max_steps": 4, "max_tool_calls": 8},
                "environment_hash": "golden-env-v1",
            }
            review_envelope = {
                "schema_version": "native.review-envelope.v0",
                "experience": {
                    "experience_id": "golden-exp-source",
                    "source": {"type": "inline", "reference": "fixture://golden/source"},
                    "observable_events": [
                        {
                            "event_id": "source-failure",
                            "kind": "agent_action",
                            "summary": "Agent accepted a downstream record without checking identity.",
                            "source_ref": "fixture://golden/source-failure",
                        },
                        {
                            "event_id": "source-correction",
                            "kind": "user_correction",
                            "summary": "User required exact source identity verification before reporting.",
                            "source_ref": "fixture://golden/source-correction",
                        },
                    ],
                },
                "assessment": {
                    "problem": "The agent promoted a downstream finding before verifying source identity.",
                    "impact": "medium",
                    "attribution": {"primary": "capability_candidate", "alternatives": ["agent_lapse", "project_fact"]},
                    "addressability": "plausible",
                    "testability": "testable",
                    "evidence_refs": ["source-failure", "source-correction"],
                    "uncertainty": ["Whether candidate helps on future identity ambiguity."],
                },
                "intervention_candidate": {
                    "title": "Verify record identity before reporting",
                    "target_behavior": "Check source identity and cite exact field.",
                    "intervention_hypothesis": "The instruction may reduce premature conclusions.",
                    "evidence_refs": ["source-failure", "source-correction"],
                },
                "disposition": "TEST",
            }
            review = self.run_cli(["review", "--stdin", "--run-dir", str(runs / "review-source")], review_envelope)

            def arm(label, applied, result, event_id, started_at, *, mode, capability_identity=None, task_id="golden-task-001"):
                return {
                    "result": {"success": result},
                    "observable_events": [{"event_id": event_id, "kind": "completion", "summary": f"{label} completed.", "source_ref": f"fixture://golden/{event_id}"}],
                    "intervention_applied": applied,
                    "intervention_identity": candidate["sha256"] if mode == "INTERVENTION_ABLATION" and applied else None,
                    "capability_identity": capability_identity,
                    "execution_context": {**validation_context, "task_id": task_id},
                    "started_at": started_at,
                }

            initial_spec = {
                "frozen_at": "2026-10-07T10:00:00+00:00",
                "comparison_mode": "INTERVENTION_ABLATION",
                "task": {"task_id": "golden-task-001", "description": "Verify record identity before reporting.", "observable_success_condition": "result.success is true"},
                "intervention": {"type": "instruction", "exact_content": candidate["exact_content"], "sha256": candidate["sha256"]},
                "oracle": {"type": "result_field_equals", "field": "success", "expected": True},
                "execution": {"bounded": True, "mode": "host_observed_arms"},
            }
            initial_validation = self.run_cli(
                ["validate", "--stdin", "--run-dir", str(runs / "validate-initial")],
                {"schema_version": "native.validation-envelope.v0", "review_result": review, "validation_spec": initial_spec, "execution": {"control": arm("control", False, True, "initial-control", "2026-10-07T10:01:00+00:00", mode="INTERVENTION_ABLATION"), "treatment": arm("treatment", True, True, "initial-treatment", "2026-10-07T10:02:00+00:00", mode="INTERVENTION_ABLATION")}},
            )
            evolve = self.run_cli(
                ["evolve", "--stdin", "--run-dir", str(runs / "evolve")],
                {"schema_version": "native.evolve-envelope.v0", "source": source, "review_result": review, "validation_result": initial_validation, "candidate": {**candidate, "change_summary": "Add explicit identity check before reporting."}},
            )
            need = {
                "schema_version": "native.evidence-need.v0",
                "need_id": "golden-need-001",
                "subject": _subject(candidate),
                "unresolved_question": "Does candidate v2 reduce premature downstream conclusions on natural record-identity ambiguity?",
                "why_it_exists": "Initial comparison was valid but neutral; future natural evidence is needed before a Human lifecycle decision.",
                "evidence_role": "NATURAL_UTILITY_EVIDENCE",
                "interesting_future_event": "A later Native Host task contains a genuine record-identity ambiguity before reporting.",
                "scope": scope,
                "source_evidence_refs": [f"review:{review['run_id']}", f"validate:{initial_validation['run_id']}", f"evolve:{evolve['candidate']['sha256']}"],
                "status": "OPEN",
                "created_at": "2026-10-07T10:03:00+00:00",
            }
            self.run_cli(["need", "create", "--stdin", "--data-dir", str(data_dir)], need)

            def watch(experience_id, disposition, summary, event_id, run_name):
                return self.run_cli(
                    ["watch", "--stdin", "--data-dir", str(data_dir), "--run-dir", str(runs / run_name)],
                    {"schema_version": "native.watch-envelope.v1", "need_id": need["need_id"], "need_context": {"unresolved_question": need["unresolved_question"], "interesting_future_event": need["interesting_future_event"]}, "experience": {"experience_id": experience_id, "evidence_role": "NATIVE_HOST_EXPERIENCE", "subject": _subject(candidate), "execution_context": scope, "observable_events": [{"event_id": event_id, "kind": "agent_action", "summary": summary, "source_ref": f"fixture://golden/{event_id}"}]}, "assessment": {"disposition": disposition, "rationale": summary, "evidence_refs": [event_id]}},
                )

            ignored = watch("golden-exp-unrelated", "IGNORE", "Formatting only; no identity ambiguity.", "ignore-evt", "watch-ignore")
            wake = watch("golden-exp-future", "WAKE", "Genuine record identity ambiguity occurred before reporting.", "wake-evt", "watch-wake")
            continuation = {"schema_version": "native.watch-continuation.v0", "reactivation_context": wake["reactivation_context"], "continuation": {"continuation_id": "golden-continuation-001", "evidence_role": "NATIVE_HOST_CONTINUATION_EVIDENCE", "action": {"action_id": "golden-action-001", "kind": "bounded_identity_evidence_review", "summary": "Host compared new identity ambiguity against suspended question."}, "execution_context": scope, "observable_events": [{"event_id": "continuation-evt", "kind": "evidence_observation", "summary": "Host recorded identity ambiguity and exact source field for follow-up evaluation.", "source_ref": "fixture://golden/continuation"}]}}
            resumed = self.run_cli(["watch", "continue", "--stdin", "--data-dir", str(data_dir), "--reactivation-file", str(runs / "watch-wake" / "02_reactivation_context.json"), "--run-dir", str(runs / "continuation")], continuation)

            post_review = self.run_cli(
                ["review", "--stdin", "--run-dir", str(runs / "review-postwake")],
                {"schema_version": "native.review-envelope.v0", "experience": {"experience_id": "golden-exp-postwake", "source": {"type": "file", "reference": resumed["persisted_path"]}, "observable_events": continuation["continuation"]["observable_events"]}, "assessment": {"problem": "Resumed evidence provides bounded natural identity ambiguity for candidate comparison.", "impact": "medium", "attribution": {"primary": "capability_candidate", "alternatives": ["agent_lapse", "project_fact"]}, "addressability": "plausible", "testability": "testable", "evidence_refs": ["continuation-evt"], "uncertainty": ["One post-WAKE task only."]}, "intervention_candidate": {"title": "Verify record identity before reporting", "target_behavior": "Check source identity and cite exact field.", "intervention_hypothesis": "Candidate may reduce the observed ambiguity.", "evidence_refs": ["continuation-evt"]}, "disposition": "TEST"},
            )
            post_spec = {"frozen_at": "2026-10-07T10:10:00+00:00", "comparison_mode": "CAPABILITY_REVISION", "task": {"task_id": "golden-task-postwake", "description": "Evaluate candidate on resumed identity ambiguity.", "observable_success_condition": "result.success is true"}, "baseline_capability": source, "candidate_capability": candidate, "oracle": {"type": "result_field_equals", "field": "success", "expected": True}, "execution": {"bounded": True, "mode": "host_observed_arms"}}
            post_validation = self.run_cli(
                ["validate", "--stdin", "--run-dir", str(runs / "validate-postwake")],
                {"schema_version": "native.validation-envelope.v0", "review_result": post_review, "validation_spec": post_spec, "execution": {"control": arm("post-control", False, True, "post-control", "2026-10-07T10:11:00+00:00", mode="CAPABILITY_REVISION", capability_identity=source["sha256"], task_id="golden-task-postwake"), "treatment": arm("post-treatment", True, True, "post-treatment", "2026-10-07T10:12:00+00:00", mode="CAPABILITY_REVISION", capability_identity=candidate["sha256"], task_id="golden-task-postwake")}},
            )
            persisted = json.loads((data_dir / "evidence-needs" / need["need_id"] / "continuations" / "golden-continuation-001.json").read_text())
            self.assertEqual(ignored["disposition"], "IGNORE")
            self.assertIsNone(ignored["reactivation_context"])
            self.assertEqual(wake["disposition"], "WAKE")
            self.assertEqual(wake["reactivation_context"]["subject"], _subject(candidate))
            self.assertEqual(resumed["wake_experience_id"], wake["experience_id"])
            self.assertEqual(post_validation["decision_state"]["status"], "DECISION_READY")
            self.assertEqual(post_validation["decision_state"]["suggested_action"], "KEEP")
            self.assertEqual(persisted["wake_evidence_refs"], ["wake-evt"])
            self.assertEqual(persisted["source_evidence_refs"], need["source_evidence_refs"])


if __name__ == "__main__":
    unittest.main()
