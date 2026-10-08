import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from skillnudge.cli import main


class CliTests(unittest.TestCase):
    def test_request_only_mode_is_honest_and_does_not_edit_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            skill = Path(directory) / "SKILL.md"
            skill.write_text("Answer the request.\n", encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                code = main(["quick-improve", "--skill", str(skill), "--failure", "omitted wrapper", "--feedback", "keep wrapper"])
            result = json.loads(output.getvalue())
            self.assertEqual(code, 0)
            self.assertEqual(result["status"], "NEEDS_HOST_PROPOSAL")
            self.assertEqual(skill.read_text(), "Answer the request.\n")

    def test_proposal_file_creates_reviewable_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "SKILL.md"
            skill.write_text("Answer the request.\n", encoding="utf-8")
            proposal = root / "proposal.json"
            proposal.write_text(json.dumps({
                "diagnosis": "The output boundary is missing.",
                "change_summary": "Add the requested wrapper rule.",
                "candidate_content": "Answer the request and preserve the wrapper.\n",
                "validation_status": "UNVERIFIED",
                "validation_basis": "No independent validation was supplied.",
            }), encoding="utf-8")
            stage = root / "stage"
            output = StringIO()
            with redirect_stdout(output):
                code = main(["quick-improve", "--skill", str(skill), "--failure", "omitted wrapper", "--feedback", "keep wrapper", "--proposal-json", str(proposal), "--staging-dir", str(stage)])
            result = json.loads(output.getvalue())
            self.assertEqual(code, 0)
            self.assertEqual(result["status"], "CANDIDATE_PENDING")
            self.assertTrue((stage / "proposed_SKILL.md").exists())
            self.assertEqual(result["candidate"]["human_decision"], "PENDING")
            self.assertEqual(skill.read_text(), "Answer the request.\n")


if __name__ == "__main__":
    unittest.main()
