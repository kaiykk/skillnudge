import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from skillnudge.cli import main
from skillnudge.evidence_need import (
    EVIDENCE_NEED_SCHEMA_VERSION,
    EvidenceNeedError,
    create_evidence_need,
    evidence_need_continuation_path,
    evidence_need_path,
    load_evidence_need,
)
from skillnudge.watch import (
    WATCH_CONTINUATION_SCHEMA_VERSION,
    WATCH_ENVELOPE_SCHEMA_VERSION,
    WATCH_REACTIVATION_SCHEMA_VERSION,
    WatchValidationError,
    run_watch,
    run_watch_continuation,
)


ROOT = Path(__file__).resolve().parents[1]


def need_value(status="OPEN"):
    return {
        "schema_version": EVIDENCE_NEED_SCHEMA_VERSION,
        "need_id": "need-episode-1",
        "subject": {
            "capability_id": "structured-record-transformation",
            "candidate_version": "v2",
            "candidate_sha256": "9db1c7f97c9a06885881e53014e47784de1b95d0302481dddbe3a62c3a805532",
        },
        "unresolved_question": "Does frozen candidate v2 help on a naturally occurring record-identity ambiguity?",
        "why_it_exists": "Episode 1 stopped after designed probes failed to establish natural utility and explicitly requested future natural evidence.",
        "evidence_role": "NATURAL_UTILITY_EVIDENCE",
        "interesting_future_event": "A new Native Host task contains genuine record-admission or record-identity ambiguity.",
        "scope": {"model": "codex-reference-host", "harness": "native-v1", "task_family": "structured-record-transformation"},
        "source_evidence_refs": ["episode-1:WAIT_FOR_NATURAL_EVIDENCE"],
        "status": status,
        "created_at": "2026-10-06T10:00:00+00:00",
    }


def watch_value(disposition="WAKE", *, role="WATCH_ROUTING_TEST_EVIDENCE", summary="The host recorded an observable record identity decision."):
    events = [{"event_id": "evt-1", "kind": "agent_action", "summary": summary, "source_ref": "fixture://watch/evt-1"}]
    return {
        "schema_version": WATCH_ENVELOPE_SCHEMA_VERSION,
        "need_id": "need-episode-1",
        "need_context": {
            "unresolved_question": need_value()["unresolved_question"],
            "interesting_future_event": need_value()["interesting_future_event"],
        },
        "experience": {
            "experience_id": "experience-later-1",
            "evidence_role": role,
            "subject": need_value()["subject"],
            "execution_context": {"model": "codex-reference-host", "harness": "native-v1", "task_family": "structured-record-transformation"},
            "observable_events": events,
        },
        "assessment": {
            "disposition": disposition,
            "rationale": "The host supplied a bounded routing assessment.",
            "evidence_refs": ["evt-1"] if disposition != "INSUFFICIENT" else [],
        },
    }


def continuation_value(context, *, continuation_id="continuation-1"):
    return {
        "schema_version": WATCH_CONTINUATION_SCHEMA_VERSION,
        "reactivation_context": context,
        "continuation": {
            "continuation_id": continuation_id,
            "evidence_role": "NATIVE_HOST_CONTINUATION_EVIDENCE",
            "action": {
                "action_id": "action-1",
                "kind": "bounded_evidence_review",
                "summary": "The host compared the newly observed identity evidence against the suspended question.",
            },
            "execution_context": need_value()["scope"],
            "observable_events": [
                {
                    "event_id": "continuation-evt-1",
                    "kind": "evidence_observation",
                    "summary": "The host recorded a bounded comparison result.",
                    "source_ref": "fixture://watch/continuation-evt-1",
                }
            ],
        },
    }


class WatchTests(unittest.TestCase):
    def test_need_persists_and_reloads_in_later_process(self):
        with tempfile.TemporaryDirectory() as directory:
            create_evidence_need(need_value(), data_dir=directory)
            path = evidence_need_path("need-episode-1", data_dir=directory)
            self.assertTrue(path.is_file())
            script = "from skillnudge.evidence_need import load_evidence_need; print(load_evidence_need('need-episode-1')['status'])"
            env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
            completed = subprocess.run([sys.executable, "-c", script], env={**env, "SKILLNUDGE_DATA_DIR": directory}, capture_output=True, text=True, check=True)
            self.assertEqual(completed.stdout.strip(), "OPEN")

    def test_ignore_wake_and_insufficient(self):
        with tempfile.TemporaryDirectory() as directory:
            create_evidence_need(need_value(), data_dir=directory)
            for disposition in ("IGNORE", "WAKE", "INSUFFICIENT"):
                result = run_watch(watch_value(disposition), data_dir=directory, run_dir=Path(directory) / f"run-{disposition.lower()}")
                self.assertEqual(result["disposition"], disposition)
                self.assertFalse(result["utility_claim"])
                self.assertIsNone(result["lifecycle_transition"])
            self.assertEqual(load_evidence_need("need-episode-1", data_dir=directory)["status"], "OPEN")

    def test_default_watch_receipt_uses_same_data_dir(self):
        with tempfile.TemporaryDirectory() as directory:
            create_evidence_need(need_value(), data_dir=directory)
            result = run_watch(watch_value("IGNORE"), data_dir=directory)
            self.assertTrue(result["run_dir"].startswith(directory))

    def test_unknown_refs_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            create_evidence_need(need_value(), data_dir=directory)
            value = watch_value()
            value["assessment"]["evidence_refs"] = ["missing"]
            with self.assertRaises(WatchValidationError):
                run_watch(value, data_dir=directory, run_dir=Path(directory) / "bad")

    def test_interesting_future_event_is_loaded_from_persisted_need(self):
        with tempfile.TemporaryDirectory() as directory:
            create_evidence_need(need_value(), data_dir=directory)
            result = run_watch(watch_value("WAKE"), data_dir=directory, run_dir=Path(directory) / "wake")
            self.assertEqual(result["need_context"]["interesting_future_event"], need_value()["interesting_future_event"])
            trace = (Path(directory) / "wake" / "trace.jsonl").read_text(encoding="utf-8")
            self.assertIn('"event": "interesting_future_event_loaded"', trace)

    def test_wake_creates_bounded_reactivation_context(self):
        with tempfile.TemporaryDirectory() as directory:
            create_evidence_need(need_value(), data_dir=directory)
            run_dir = Path(directory) / "wake"
            result = run_watch(watch_value("WAKE"), data_dir=directory, run_dir=run_dir)
            context = result["reactivation_context"]
            self.assertEqual(context["schema_version"], WATCH_REACTIVATION_SCHEMA_VERSION)
            self.assertEqual(context["need_id"], "need-episode-1")
            self.assertEqual(context["subject"], need_value()["subject"])
            self.assertEqual(context["unresolved_question"], need_value()["unresolved_question"])
            self.assertEqual(context["interesting_future_event"], need_value()["interesting_future_event"])
            self.assertEqual(context["source_evidence_refs"], need_value()["source_evidence_refs"])
            self.assertEqual(context["wake_evidence_refs"], ["evt-1"])
            self.assertEqual(context["execution_context"], need_value()["scope"])
            persisted = json.loads((run_dir / "02_reactivation_context.json").read_text(encoding="utf-8"))
            self.assertEqual(persisted, context)
            trace = (run_dir / "trace.jsonl").read_text(encoding="utf-8")
            self.assertIn('"event": "reactivation_context_created"', trace)

    def test_non_wake_does_not_create_reactivation_context(self):
        with tempfile.TemporaryDirectory() as directory:
            create_evidence_need(need_value(), data_dir=directory)
            for disposition in ("IGNORE", "INSUFFICIENT"):
                run_dir = Path(directory) / disposition.lower()
                result = run_watch(watch_value(disposition), data_dir=directory, run_dir=run_dir)
                self.assertIsNone(result["reactivation_context"])
                self.assertFalse((run_dir / "02_reactivation_context.json").exists())

    def test_wake_continuation_persists_new_evidence_with_lineage(self):
        with tempfile.TemporaryDirectory() as directory:
            create_evidence_need(need_value(), data_dir=directory)
            wake_dir = Path(directory) / "wake"
            wake = run_watch(watch_value("WAKE"), data_dir=directory, run_dir=wake_dir)
            continuation_dir = Path(directory) / "continuation"
            result = run_watch_continuation(
                continuation_value(wake["reactivation_context"]),
                reactivation_file=wake_dir / "02_reactivation_context.json",
                data_dir=directory,
                run_dir=continuation_dir,
            )
            self.assertEqual(result["schema_version"], "native.watch-continuation-result.v0")
            self.assertEqual(result["need_id"], "need-episode-1")
            self.assertEqual(result["reactivation_run_id"], wake["run_id"])
            self.assertEqual(result["wake_experience_id"], wake["experience_id"])
            self.assertEqual(result["source_evidence_refs"], need_value()["source_evidence_refs"])
            self.assertEqual(result["wake_evidence_refs"], ["evt-1"])
            self.assertEqual(result["need_status"], "OPEN")
            self.assertFalse(result["utility_claim"])
            self.assertIsNone(result["lifecycle_transition"])
            persisted_path = evidence_need_continuation_path("need-episode-1", "continuation-1", data_dir=directory)
            self.assertTrue(persisted_path.is_file())
            self.assertEqual(json.loads(persisted_path.read_text(encoding="utf-8"))["continuation_id"], "continuation-1")
            self.assertEqual(load_evidence_need("need-episode-1", data_dir=directory)["status"], "OPEN")
            trace = (continuation_dir / "trace.jsonl").read_text(encoding="utf-8")
            self.assertIn('"event": "continuation_evidence_persisted"', trace)

    def test_continuation_requires_exact_persisted_context(self):
        with tempfile.TemporaryDirectory() as directory:
            create_evidence_need(need_value(), data_dir=directory)
            wake_dir = Path(directory) / "wake"
            wake = run_watch(watch_value("WAKE"), data_dir=directory, run_dir=wake_dir)
            value = continuation_value(wake["reactivation_context"])
            value["reactivation_context"]["unresolved_question"] = "tampered"
            with self.assertRaisesRegex(WatchValidationError, "does not match"):
                run_watch_continuation(
                    value,
                    reactivation_file=wake_dir / "02_reactivation_context.json",
                    data_dir=directory,
                    run_dir=Path(directory) / "bad",
                )

    def test_cli_watch_continue_is_cross_process_ready(self):
        with tempfile.TemporaryDirectory() as directory:
            create_evidence_need(need_value(), data_dir=directory)
            wake_dir = Path(directory) / "wake"
            wake = run_watch(watch_value("WAKE"), data_dir=directory, run_dir=wake_dir)
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "skillnudge",
                    "watch",
                    "continue",
                    "--stdin",
                    "--data-dir",
                    directory,
                    "--reactivation-file",
                    str(wake_dir / "02_reactivation_context.json"),
                    "--run-dir",
                    str(Path(directory) / "continuation"),
                ],
                input=json.dumps(continuation_value(wake["reactivation_context"])),
                capture_output=True,
                text=True,
                env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
                check=True,
            )
            self.assertEqual(json.loads(completed.stdout)["continuation_id"], "continuation-1")

    def test_cross_process_host_can_consume_wake_context(self):
        with tempfile.TemporaryDirectory() as directory:
            create_evidence_need(need_value(), data_dir=directory)
            run_dir = Path(directory) / "wake"
            run_watch(watch_value("WAKE"), data_dir=directory, run_dir=run_dir)
            script = (
                "import json, sys; "
                "context=json.load(open(sys.argv[1])); "
                "assert context['unresolved_question']; "
                "assert context['wake_evidence_refs'] == ['evt-1']; "
                "print('HOST_CONTINUATION_STEP_READY')"
            )
            completed = subprocess.run(
                [sys.executable, "-c", script, str(run_dir / "02_reactivation_context.json")],
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertEqual(completed.stdout.strip(), "HOST_CONTINUATION_STEP_READY")

    def test_host_condition_sequence_with_one_persisted_need(self):
        cases = [
            ("condition not yet instantiated", "IGNORE"),
            ("topically related only", "IGNORE"),
            ("observable evidence is insufficient", "INSUFFICIENT"),
            ("record identity ambiguity occurred", "WAKE"),
            ("equivalent record identity ambiguity occurred", "WAKE"),
        ]
        with tempfile.TemporaryDirectory() as directory:
            create_evidence_need(need_value(), data_dir=directory)
            for index, (summary, expected) in enumerate(cases):
                result = run_watch(
                    watch_value(expected, summary=summary),
                    data_dir=directory,
                    run_dir=Path(directory) / f"sequence-{index}",
                )
                self.assertEqual(result["disposition"], expected)
                self.assertEqual(result["need_context"]["interesting_future_event"], need_value()["interesting_future_event"])
                self.assertFalse(result["utility_claim"])
                self.assertIsNone(result["lifecycle_transition"])
            self.assertEqual(load_evidence_need("need-episode-1", data_dir=directory)["status"], "OPEN")

    def test_need_context_must_match_persisted_need(self):
        with tempfile.TemporaryDirectory() as directory:
            create_evidence_need(need_value(), data_dir=directory)
            value = watch_value("WAKE")
            value["need_context"]["interesting_future_event"] = "a different condition"
            with self.assertRaisesRegex(WatchValidationError, "need_context does not match"):
                run_watch(value, data_dir=directory, run_dir=Path(directory) / "mismatch")

    def test_closed_need_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            create_evidence_need(need_value(), data_dir=directory)
            path = evidence_need_path("need-episode-1", data_dir=directory)
            stored = json.loads(path.read_text(encoding="utf-8"))
            stored["status"] = "CLOSED"
            path.write_text(json.dumps(stored), encoding="utf-8")
            with self.assertRaisesRegex(WatchValidationError, "not OPEN"):
                run_watch(watch_value(), data_dir=directory, run_dir=Path(directory) / "closed")

    def test_candidate_identity_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            create_evidence_need(need_value(), data_dir=directory)
            value = watch_value()
            value["experience"]["subject"]["candidate_sha256"] = hashlib.sha256(b"other").hexdigest()
            with self.assertRaisesRegex(WatchValidationError, "does not match"):
                run_watch(value, data_dir=directory, run_dir=Path(directory) / "mismatch")

    def test_private_reasoning_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            create_evidence_need(need_value(), data_dir=directory)
            value = watch_value()
            value["assessment"]["private_reasoning"] = "hidden"
            with self.assertRaises(WatchValidationError):
                run_watch(value, data_dir=directory, run_dir=Path(directory) / "private")

    def test_cli_need_create_and_watch(self):
        with tempfile.TemporaryDirectory() as directory:
            with contextlib.redirect_stdout(io.StringIO()) as stdout, contextlib.redirect_stderr(io.StringIO()), mock.patch("sys.stdin", io.StringIO(json.dumps(need_value()))):
                self.assertEqual(main(["need", "create", "--stdin", "--data-dir", directory]), 0)
            self.assertIn("need-episode-1", stdout.getvalue())
            with contextlib.redirect_stdout(io.StringIO()) as stdout, mock.patch("sys.stdin", io.StringIO(json.dumps(watch_value("WAKE")))):
                self.assertEqual(main(["watch", "--stdin", "--data-dir", directory, "--run-dir", str(Path(directory) / "cli-watch")]), 0)
            self.assertEqual(json.loads(stdout.getvalue())["disposition"], "WAKE")


if __name__ == "__main__":
    unittest.main()
