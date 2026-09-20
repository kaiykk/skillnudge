import contextlib
import io
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from skillnudge.cli import main  # noqa: E402


class CliSurfaceTests(unittest.TestCase):
    def test_user_facing_help_excludes_phase2_experiment_entrypoint(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = main(["--help"])

        self.assertEqual(result, 0)
        self.assertIn("advise", output.getvalue())
        self.assertIn("bootstrap", output.getvalue())
        self.assertNotIn("experiment", output.getvalue())


if __name__ == "__main__":
    unittest.main()
