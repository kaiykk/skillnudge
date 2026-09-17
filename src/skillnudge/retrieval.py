"""Local Skill corpus normalization, SQLite FTS5, BM25, and RRF.

This module intentionally stops at candidate acquisition. It does not infer a
capability contract, judge candidates, or produce advice.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import tempfile
from dataclasses import asdict, dataclass, replace
from json import JSONDecodeError, JSONDecoder
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence


SKILL_FIELDS = (
    "candidate_id",
    "name",
    "description",
    "body",
    "repo",
    "source_url",
    "license",
    "updated_at",
    "source",
)

_TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)


@dataclass(frozen=True)
class SkillRecord:
    candidate_id: str
    name: str
    description: str | None = None
    body: str | None = None
    repo: str | None = None
    source_url: str | None = None
    license: str | None = None
    updated_at: str | None = None
    source: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BuildStats:
    source_record_count: int
    imported_record_count: int
    skipped_record_count: int
    database_path: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class CorpusCoverageError(RuntimeError):
    """Raised when the required D001 positive is not verifiably covered."""

    def __init__(self, coverage: Mapping[str, Any]):
        self.coverage = dict(coverage)
        super().__init__("CORPUS_COVERAGE_FAILURE")


def iter_json_array(path: str | Path, chunk_size: int = 1024 * 1024) -> Iterator[dict[str, Any]]:
    """Stream dictionaries from a JSON array without loading the corpus at once."""

    decoder = JSONDecoder()
    with Path(path).open("r", encoding="utf-8") as handle:
        buffer = ""
        position = 0
        eof = False

        def fill() -> None:
            nonlocal buffer, eof
            chunk = handle.read(chunk_size)
            if chunk:
                buffer += chunk
            else:
                eof = True

        fill()
        if buffer.startswith("\ufeff"):
            buffer = buffer[1:]

        while True:
            while position >= len(buffer) and not eof:
                fill()
            while position < len(buffer) and buffer[position].isspace():
                position += 1
            if position >= len(buffer):
                raise ValueError("Corpus is empty or missing the opening JSON array")
            if buffer[position] != "[":
                raise ValueError("Corpus must be a JSON array")
            position += 1
            break

        while True:
            while True:
                while position < len(buffer) and buffer[position].isspace():
                    position += 1
                if position < len(buffer):
                    break
                if eof:
                    raise ValueError("Corpus ended before the closing JSON array")
                buffer = buffer[position:]
                position = 0
                fill()

            if buffer[position] == "]":
                return

            while True:
                try:
                    value, end = decoder.raw_decode(buffer, position)
                    break
                except JSONDecodeError:
                    if eof:
                        raise
                    buffer = buffer[position:]
                    position = 0
                    fill()

            if not isinstance(value, dict):
                raise ValueError("Every corpus item must be a JSON object")
            yield value
            position = end

            while True:
                while position < len(buffer) and buffer[position].isspace():
                    position += 1
                if position < len(buffer):
                    break
                if eof:
                    raise ValueError("Corpus ended before the closing JSON array")
                buffer = buffer[position:]
                position = 0
                fill()

            delimiter = buffer[position]
            if delimiter == ",":
                position += 1
                if position > chunk_size:
                    buffer = buffer[position:]
                    position = 0
                continue
            if delimiter == "]":
                return
            raise ValueError(f"Unexpected JSON array delimiter: {delimiter!r}")


def _text(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def normalize_skill(
    raw: Mapping[str, Any],
    override: Mapping[str, Any] | None = None,
) -> SkillRecord:
    """Normalize only the fields needed by Checkpoint 1."""

    candidate_id = raw.get("candidate_id") or raw.get("skill_id") or raw.get("id")
    if candidate_id is None or not str(candidate_id).strip():
        raise ValueError("Skill record is missing candidate_id/skill_id/id")

    record = SkillRecord(
        candidate_id=str(candidate_id),
        name=str(raw.get("name") or ""),
        description=_text(raw.get("description")),
        body=_text(raw.get("body") if raw.get("body") is not None else raw.get("content")),
        repo=_text(raw.get("repo")),
        source_url=_text(raw.get("source_url") if raw.get("source_url") is not None else raw.get("url")),
        license=_text(raw.get("license")),
        updated_at=_text(raw.get("updated_at")),
        source=_text(raw.get("source")),
    )
    if override:
        allowed = {key: value for key, value in override.items() if key in SKILL_FIELDS}
        record = replace(record, **allowed)
    return record


def _body_sha256(body: str | None) -> str:
    return hashlib.sha256((body or "").rstrip("\n").encode("utf-8")).hexdigest()


def check_d001_coverage(
    corpus_path: str | Path,
    target: Mapping[str, Any],
) -> dict[str, Any]:
    """Verify D001 by name plus a pinned official body hash."""

    target_name = str(target["name"])
    expected_hash = str(target["official_body_sha256"])
    name_matches: list[str] = []
    body_matches: list[str] = []
    for raw in iter_json_array(corpus_path):
        record = normalize_skill(raw)
        if record.name != target_name:
            continue
        name_matches.append(record.candidate_id)
        if _body_sha256(record.body) == expected_hash:
            body_matches.append(record.candidate_id)

    result = {
        "status": "verified" if body_matches else "failure",
        "target": dict(target),
        "name_match_count": len(name_matches),
        "name_match_ids": name_matches,
        "verified_record_ids": body_matches,
        "identity_verified": bool(body_matches),
        "verification_rule": "name plus normalized body SHA-256 match to the pinned official file",
    }
    if not body_matches:
        raise CorpusCoverageError(result)
    return result


def _create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE skills (
            candidate_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            body TEXT,
            repo TEXT,
            source_url TEXT,
            license TEXT,
            updated_at TEXT,
            source TEXT
        );

        CREATE VIRTUAL TABLE skills_fts USING fts5(
            candidate_id UNINDEXED,
            name,
            description,
            body,
            tokenize = 'unicode61'
        );

        CREATE TABLE build_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """
    )


def build_index(
    corpus_path: str | Path,
    database_path: str | Path,
    *,
    metadata: Mapping[str, Any] | None = None,
    identity_overrides: Mapping[str, Mapping[str, Any]] | None = None,
) -> BuildStats:
    """Build a fresh SQLite/FTS5 index and atomically replace the target file."""

    target = Path(database_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
    )
    os.close(fd)
    temporary = Path(temporary_name)
    source_count = 0
    skipped_count = 0
    overrides = identity_overrides or {}
    seen_candidate_ids: set[str] = set()

    try:
        connection = sqlite3.connect(temporary)
        try:
            _create_schema(connection)
            for raw in iter_json_array(corpus_path):
                source_count += 1
                try:
                    source_id = str(raw.get("candidate_id") or raw.get("skill_id") or raw.get("id") or "")
                    record = normalize_skill(raw, overrides.get(source_id))
                except (TypeError, ValueError):
                    skipped_count += 1
                    continue
                values = record.as_dict()
                if record.candidate_id in seen_candidate_ids:
                    connection.execute(
                        "DELETE FROM skills_fts WHERE candidate_id = ?",
                        (record.candidate_id,),
                    )
                seen_candidate_ids.add(record.candidate_id)
                connection.execute(
                    """
                    INSERT OR REPLACE INTO skills
                    (candidate_id, name, description, body, repo, source_url,
                     license, updated_at, source)
                    VALUES (:candidate_id, :name, :description, :body, :repo,
                            :source_url, :license, :updated_at, :source)
                    """,
                    values,
                )
                connection.execute(
                    """
                    INSERT OR REPLACE INTO skills_fts
                    (candidate_id, name, description, body)
                    VALUES (:candidate_id, :name, :description, :body)
                    """,
                    {
                        "candidate_id": record.candidate_id,
                        "name": record.name,
                        "description": record.description or "",
                        "body": record.body or "",
                    },
                )

            for key, value in (metadata or {}).items():
                encoded = json.dumps(value, ensure_ascii=False, sort_keys=True)
                connection.execute(
                    "INSERT OR REPLACE INTO build_metadata (key, value) VALUES (?, ?)",
                    (str(key), encoded),
                )
            connection.commit()
            imported_count = int(connection.execute("SELECT COUNT(*) FROM skills").fetchone()[0])
        finally:
            connection.close()

        os.replace(temporary, target)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise

    return BuildStats(
        source_record_count=source_count,
        imported_record_count=imported_count,
        skipped_record_count=skipped_count,
        database_path=str(target),
    )


def to_fts_query(query: str) -> str:
    """Turn plain-language query text into a safe OR query for SQLite FTS5."""

    tokens = _TOKEN_RE.findall(query)
    return " OR ".join(f'"{token.replace(chr(34), chr(34) * 2)}"' for token in tokens)


class BM25Retriever:
    """Small SQLite-backed retriever that preserves raw ``bm25()`` scores."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "BM25Retriever":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def retrieve(self, query: str, k: int = 50) -> list[dict[str, Any]]:
        if k < 1:
            return []
        fts_query = to_fts_query(query)
        if not fts_query:
            return []
        rows = self.connection.execute(
            """
            SELECT skills.candidate_id, skills.name, skills.repo,
                   skills.source_url, skills.source,
                   bm25(skills_fts) AS raw_bm25_score
            FROM skills_fts
            JOIN skills ON skills.candidate_id = skills_fts.candidate_id
            WHERE skills_fts MATCH ?
            ORDER BY raw_bm25_score ASC, skills.candidate_id ASC
            LIMIT ?
            """,
            (fts_query, k),
        ).fetchall()
        return [
            {
                "rank": rank,
                "candidate_id": row["candidate_id"],
                "name": row["name"],
                "repo": row["repo"],
                "source_url": row["source_url"],
                "source": row["source"],
                "raw_bm25_score": float(row["raw_bm25_score"]),
            }
            for rank, row in enumerate(rows, start=1)
        ]


def fuse_ranked_results(
    results_by_query: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    limit: int = 30,
    rrf_k: int = 60,
) -> list[dict[str, Any]]:
    """Fuse independent ranked lists with deterministic Reciprocal Rank Fusion."""

    if rrf_k < 1:
        raise ValueError("rrf_k must be positive")
    fused: dict[str, dict[str, Any]] = {}
    for query, results in results_by_query.items():
        seen_in_query: set[str] = set()
        for fallback_rank, result in enumerate(results, start=1):
            candidate_id = str(result["candidate_id"])
            if candidate_id in seen_in_query:
                continue
            seen_in_query.add(candidate_id)
            rank = int(result.get("rank", fallback_rank))
            entry = fused.setdefault(
                candidate_id,
                {
                    "candidate_id": candidate_id,
                    "name": result.get("name"),
                    "repo": result.get("repo"),
                    "source_url": result.get("source_url"),
                    "source": result.get("source"),
                    "query_ranks": {},
                    "raw_bm25_scores": {},
                    "rrf_contributions": {},
                    "rrf_score": 0.0,
                },
            )
            contribution = 1.0 / (rrf_k + rank)
            entry["query_ranks"][query] = rank
            if "raw_bm25_score" in result:
                entry["raw_bm25_scores"][query] = result["raw_bm25_score"]
            entry["rrf_contributions"][query] = contribution
            entry["rrf_score"] += contribution

    ordered = sorted(fused.values(), key=lambda item: (-item["rrf_score"], item["candidate_id"]))
    for rank, item in enumerate(ordered[: max(0, limit)], start=1):
        item["fused_rank"] = rank
    return ordered[: max(0, limit)]
