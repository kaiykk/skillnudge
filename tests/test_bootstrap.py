import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from skillnudge.bootstrap import (  # noqa: E402
    BOOTSTRAP_SCHEMA_VERSION,
    bootstrap_default_index,
    default_data_dir,
)
from skillnudge.retrieval import BM25Retriever  # noqa: E402


class BootstrapTests(unittest.TestCase):
    def test_default_data_dir_honors_explicit_override(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {"SKILLNUDGE_DATA_DIR": directory}):
                self.assertEqual(default_data_dir(), Path(directory))

    def test_bootstrap_builds_readable_index_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            first = bootstrap_default_index(directory)
            second = bootstrap_default_index(directory)

            self.assertTrue(first.rebuilt)
            self.assertFalse(second.rebuilt)
            self.assertEqual(first.database_path, second.database_path)
            metadata = json.loads(Path(first.metadata_path).read_text())
            self.assertEqual(metadata["schema_version"], BOOTSTRAP_SCHEMA_VERSION)
            self.assertGreater(metadata["record_count"], 0)
            with BM25Retriever(first.database_path) as retriever:
                results = retriever.retrieve("vague UI prototype visual hierarchy", 5)
            self.assertTrue(results)
            self.assertEqual(
                results[0]["candidate_id"],
                "skillnudge.seed.ui-ux-prototyping",
            )


if __name__ == "__main__":
    unittest.main()
