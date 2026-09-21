import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from skillnudge.native import main, run_native_retrieval  # noqa: E402
from skillnudge.planning_contracts import NATIVE_CONTRACT_ENUMS  # noqa: E402
from skillnudge.retrieval import build_index  # noqa: E402


def _envelope(*, decision: str = "search") -> dict:
    if decision == "no_intervention":
        return {
            "schema_version": "native.planning-envelope.v0",
            "input": {"raw_request": "Explain this local error."},
            "capability_framing": {
                "contract": {
                    "goal": "Understand the error",
                    "stage": None,
                    "blocker": "No external capability blocker is identified.",
                    "missing_capabilities": [],
                    "intended_effect": "Explain the local error.",
                    "constraints": [],
                    "not_needed": [],
                    "uncertainties": [],
                },
                "confidence": "high",
                "clarification_needed": False,
                "clarification_question": None,
            },
            "intervention_plan": {
                "decision": "no_intervention",
                "targets": [],
                "decision_reason": "The host can answer this directly.",
            },
            "query_plan": {"status": "skipped", "queries": []},
        }
    return {
        "schema_version": "native.planning-envelope.v0",
        "input": {"raw_request": "Find reusable interface guidance."},
        "capability_framing": {
            "contract": {
                "goal": "Improve the interface task",
                "stage": "exploration",
                "blocker": "The task needs reusable guidance.",
                "missing_capabilities": ["interface guidance"],
                "intended_effect": "Make the next step more concrete.",
                "constraints": [],
                "not_needed": [],
                "uncertainties": [],
            },
            "confidence": "medium",
            "clarification_needed": False,
            "clarification_question": None,
        },
        "intervention_plan": {
            "decision": "search",
            "targets": [{
                "family": "skill",
                "priority": "primary",
                "rationale": "A reusable skill may address the blocker.",
            }],
            "decision_reason": "Search the skill family.",
        },
        "query_plan": {
            "status": "ready",
            "queries": [{
                "family": "skill",
                "angle": "capability",
                "semantic_query": "interface guidance visual hierarchy",
                "purpose": "Find reusable interface guidance.",
            }],
        },
    }


def _database(root: Path) -> Path:
    corpus = root / "corpus.json"
    corpus.write_text(json.dumps([
        {
            "candidate_id": "candidate-1",
            "name": "interface-guidance",
            "description": "Reusable interface guidance",
            "body": "Use visual hierarchy and accessible interaction patterns.",
            "repo": "example/interface-guidance",
            "source_url": "https://example.test/interface-guidance",
            "license": "MIT",
            "updated_at": "2026-09-21",
            "source": "test-fixture",
        },
    ]), encoding="utf-8")
    database = root / "skills.sqlite3"
    build_index(corpus, database, metadata={"source": {"repository": "test-fixture"}})
    return database


class NativeRuntimeTests(unittest.TestCase):
    def test_documented_native_enums_match_validator_values(self):
        skill_dir = ROOT / ".agents" / "skills" / "skillnudge"
        skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        contract_text = (skill_dir / "native-contract.md").read_text(encoding="utf-8")
        self.assertIn("native-contract.md", skill_text)
        match = re.search(
            r"## Validator-Comparison Data.*?```json\n(\{.*?\})\n```",
            contract_text,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        documented = json.loads(match.group(1))
        self.assertEqual(
            documented,
            {key: sorted(values) for key, values in NATIVE_CONTRACT_ENUMS.items()},
        )

    def test_public_skill_does_not_delegate_to_standalone_command(self):
        skill_text = (ROOT / ".agents" / "skills" / "skillnudge" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("skillnudge advise", skill_text)
        self.assertIn("skillnudge retrieve --stdin", skill_text)

    def test_provider_free_native_retrieval_reuses_existing_acquisition(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = run_native_retrieval(
                _envelope(),
                database_path=_database(root),
                run_dir=root / "native",
            )

            self.assertEqual(result.acquisition["status"], "ready")
            self.assertEqual(result.evidence_packs["hydrated_candidate_count"], 1)
            self.assertEqual(result.evidence_packs["packs"][0]["candidate_id"], "candidate-1")
            trace = (root / "native" / "trace.jsonl").read_text(encoding="utf-8")
            self.assertIn("planning_handoff_validated", trace)
            self.assertIn("Evidence Hydration", trace)
            self.assertFalse((root / "native" / "07_final_advice.json").exists())

    def test_no_intervention_is_a_provider_free_early_stop(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = run_native_retrieval(
                _envelope(decision="no_intervention"),
                database_path=root / "does-not-exist.sqlite3",
                run_dir=root / "native-no-intervention",
            )

            self.assertIsNone(result.acquisition)
            self.assertIsNone(result.evidence_packs)

    def test_cli_returns_native_result_without_provider_import(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            database = _database(root)
            old_stdin = sys.stdin
            try:
                sys.stdin = io.StringIO(json.dumps(_envelope()))
                output = io.StringIO()
                with redirect_stdout(output):
                    result = main([
                        "--stdin",
                        "--database",
                        str(database),
                        "--run-dir",
                        str(root / "cli"),
                    ])
            finally:
                sys.stdin = old_stdin

            self.assertEqual(result, 0)
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["mode"], "native")
            self.assertIsNone(payload["provider"])
            self.assertIsNotNone(payload["evidence_packs"])

    def test_native_module_does_not_import_provider_boundary(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        env.pop("DEEPSEEK_API_KEY", None)
        for key in list(env):
            if key.startswith("SKILLNUDGE_MODEL_"):
                env.pop(key)
        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import sys; import skillnudge.native; "
                    "assert 'skillnudge.planning_model' not in sys.modules"
                ),
            ],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)


if __name__ == "__main__":
    unittest.main()
