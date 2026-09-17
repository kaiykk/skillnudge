import json
import sys
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from skillnudge.d001 import run_d001
from skillnudge.retrieval import (
    BM25Retriever,
    build_index,
    check_d001_coverage,
    fuse_ranked_results,
    iter_json_array,
)


class Checkpoint1Tests(unittest.TestCase):
    def test_parser_import_build_and_duplicate_handling(self):
        records = [
            {"skill_id": "a", "name": "Alpha", "description": "alpha guidance", "content": "alpha body"},
            {"skill_id": "b", "name": "Beta", "description": "beta guidance", "content": "beta body"},
            {"skill_id": "a", "name": "Alpha replacement", "description": "replacement", "content": "replacement body"},
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            corpus = root / "corpus.json"
            corpus.write_text(json.dumps(records), encoding="utf-8")
            self.assertEqual([item["skill_id"] for item in iter_json_array(corpus, chunk_size=7)], ["a", "b", "a"])
            stats = build_index(corpus, root / "skills.sqlite3")
            self.assertEqual(stats.source_record_count, 3)
            self.assertEqual(stats.imported_record_count, 2)
            self.assertEqual(stats.skipped_record_count, 0)
            rebuilt = build_index(corpus, root / "skills.sqlite3")
            self.assertEqual(rebuilt.imported_record_count, 2)

            with BM25Retriever(root / "skills.sqlite3") as retriever:
                results = retriever.retrieve("replacement")
            self.assertEqual(results[0]["candidate_id"], "a")
            self.assertEqual([item["candidate_id"] for item in results].count("a"), 1)
            self.assertIsInstance(results[0]["raw_bm25_score"], float)
            self.assertIn("name", results[0])
            self.assertNotIn("score", results[0])

    def test_fts_query_and_deterministic_rrf(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            corpus = root / "corpus.json"
            corpus.write_text(
                json.dumps([
                    {"skill_id": "a", "name": "Alpha", "description": "alpha", "content": ""},
                    {"skill_id": "b", "name": "Beta", "description": "beta", "content": ""},
                ]),
                encoding="utf-8",
            )
            build_index(corpus, root / "skills.sqlite3")
            with BM25Retriever(root / "skills.sqlite3") as retriever:
                self.assertEqual(retriever.retrieve("does-not-exist"), [])
                self.assertTrue(retriever.retrieve("alpha"))

        lists = {
            "q1": [
                {"rank": 1, "candidate_id": "a", "name": "A", "raw_bm25_score": -2.0},
                {"rank": 2, "candidate_id": "a", "name": "A", "raw_bm25_score": -1.0},
                {"rank": 3, "candidate_id": "b", "name": "B", "raw_bm25_score": -0.5},
            ],
            "q2": [
                {"rank": 1, "candidate_id": "b", "name": "B", "raw_bm25_score": -3.0},
                {"rank": 2, "candidate_id": "a", "name": "A", "raw_bm25_score": -0.2},
            ],
        }
        first = fuse_ranked_results(lists, rrf_k=60)
        second = fuse_ranked_results(lists, rrf_k=60)
        self.assertEqual(first, second)
        self.assertEqual([item["candidate_id"] for item in first], ["a", "b"])
        self.assertEqual(first[0]["query_ranks"], {"q1": 1, "q2": 2})
        self.assertAlmostEqual(first[0]["rrf_score"], 1 / 61 + 1 / 62)

    def test_d001_coverage_and_trace_artifacts(self):
        body = "# Official D001 body\n\nprototype guidance\n"
        target = {
            "candidate_id": "owner/repo::d001",
            "repo": "owner/repo",
            "name": "d001",
            "official_body_sha256": sha256(body.rstrip("\n").encode()).hexdigest(),
        }
        query_plan = {
            "case_id": "D001",
            "queries": [
                {"family": "skill", "angle": "capability", "semantic_query": "prototype guidance", "purpose": "test"}
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            corpus = root / "corpus.json"
            corpus.write_text(
                json.dumps([
                    {"skill_id": "source-1", "name": "d001", "description": "prototype", "content": body},
                    {"skill_id": "other", "name": "other", "description": "other", "content": "other"},
                ]),
                encoding="utf-8",
            )
            target_path = root / "target.json"
            target_path.write_text(json.dumps(target), encoding="utf-8")
            plan_path = root / "query_plan.json"
            plan_path.write_text(json.dumps(query_plan), encoding="utf-8")
            coverage = check_d001_coverage(corpus, target)
            self.assertTrue(coverage["identity_verified"])
            run_dir = root / "run"
            summary = run_d001(
                corpus,
                run_dir,
                query_plan_path=plan_path,
                coverage_target_path=target_path,
                source_metadata={"repository_commit": "test"},
            )
            self.assertTrue(summary["d001_positive"]["present_in_corpus"])
            for filename in (
                "00_input.json",
                "01_capability_contract.json",
                "02_intervention_plan.json",
                "03_query_plan.json",
                "04_candidate_acquisition.json",
                "trace.jsonl",
            ):
                self.assertTrue((run_dir / filename).exists(), filename)
            self.assertFalse((run_dir / "05_evidence_packs.json").exists())
            acquisition = json.loads((run_dir / "04_candidate_acquisition.json").read_text())
            self.assertEqual(acquisition["d001_positive"]["fused_rank"], 1)


if __name__ == "__main__":
    unittest.main()
