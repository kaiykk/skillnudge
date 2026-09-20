"""Install-time and first-run bootstrap for the Phase 1 local index."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any, Iterator

from .retrieval import BuildStats, build_index


BOOTSTRAP_SCHEMA_VERSION = "skillnudge.bootstrap.v1"
DEFAULT_CORPUS_VERSION = "default-seed-v1"
DEFAULT_DATABASE_NAME = "skillnudge.sqlite3"
DEFAULT_METADATA_NAME = "bootstrap.json"
DEFAULT_CORPUS_RESOURCE = "data/default_corpus.json"


class BootstrapError(RuntimeError):
    """Raised when the default local index cannot be built or verified."""


@dataclass(frozen=True)
class BootstrapResult:
    data_dir: str
    database_path: str
    metadata_path: str
    corpus_version: str
    corpus_sha256: str
    rebuilt: bool
    stats: BuildStats | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": BOOTSTRAP_SCHEMA_VERSION,
            "data_dir": self.data_dir,
            "database_path": self.database_path,
            "metadata_path": self.metadata_path,
            "corpus_version": self.corpus_version,
            "corpus_sha256": self.corpus_sha256,
            "rebuilt": self.rebuilt,
            "stats": self.stats.as_dict() if self.stats is not None else None,
        }


def default_data_dir() -> Path:
    """Return the per-user data directory without consulting the repository."""

    configured = os.environ.get("SKILLNUDGE_DATA_DIR")
    if configured:
        return Path(configured).expanduser()
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "SkillNudge"
    if os.name == "nt":
        root = os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local"
        return Path(root) / "SkillNudge"
    root = os.environ.get("XDG_DATA_HOME")
    return (
        Path(root).expanduser() / "skillnudge"
        if root
        else Path.home() / ".local" / "share" / "skillnudge"
    )


def default_index_path() -> Path:
    return default_data_dir() / DEFAULT_DATABASE_NAME


@contextmanager
def _bundled_corpus() -> Iterator[Path]:
    resource = resources.files("skillnudge").joinpath(DEFAULT_CORPUS_RESOURCE)
    with resources.as_file(resource) as path:
        yield Path(path)


def _read_metadata(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _database_is_readable(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        with sqlite3.connect(path) as connection:
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
                )
            }
            connection.execute("SELECT COUNT(*) FROM skills").fetchone()
            connection.execute("SELECT COUNT(*) FROM skills_fts").fetchone()
            return {"skills", "skills_fts", "build_metadata"} <= tables
    except sqlite3.Error:
        return False


def _write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    try:
        temporary.write_text(
            json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def _current_metadata(
    metadata: dict[str, Any] | None,
    *,
    corpus_sha256: str,
    database_path: Path,
) -> bool:
    return bool(
        metadata
        and metadata.get("schema_version") == BOOTSTRAP_SCHEMA_VERSION
        and metadata.get("corpus_version") == DEFAULT_CORPUS_VERSION
        and metadata.get("corpus_sha256") == corpus_sha256
        and metadata.get("database_name") == database_path.name
        and _database_is_readable(database_path)
    )


def bootstrap_default_index(
    data_dir: str | Path | None = None,
    *,
    force: bool = False,
) -> BootstrapResult:
    """Build or reuse the deterministic packaged corpus index."""

    target_dir = (
        Path(data_dir).expanduser() if data_dir is not None else default_data_dir()
    )
    database_path = target_dir / DEFAULT_DATABASE_NAME
    metadata_path = target_dir / DEFAULT_METADATA_NAME
    with _bundled_corpus() as corpus_path:
        try:
            corpus_bytes = corpus_path.read_bytes()
        except OSError as error:
            raise BootstrapError("DEFAULT_CORPUS_UNREADABLE") from error
        corpus_sha256 = hashlib.sha256(corpus_bytes).hexdigest()
        existing = _read_metadata(metadata_path)
        if not force and _current_metadata(
            existing,
            corpus_sha256=corpus_sha256,
            database_path=database_path,
        ):
            return BootstrapResult(
                data_dir=str(target_dir),
                database_path=str(database_path),
                metadata_path=str(metadata_path),
                corpus_version=DEFAULT_CORPUS_VERSION,
                corpus_sha256=corpus_sha256,
                rebuilt=False,
                stats=None,
            )

        target_dir.mkdir(parents=True, exist_ok=True)
        temporary_database = target_dir / f".{DEFAULT_DATABASE_NAME}.building"
        temporary_database.unlink(missing_ok=True)
        metadata = {
            "repository": "https://github.com/kaiykk/skillnudge",
            "corpus_version": DEFAULT_CORPUS_VERSION,
            "corpus_sha256": corpus_sha256,
            "license": "MIT",
            "source": "bundled deterministic SkillNudge seed corpus",
        }
        try:
            stats = build_index(
                corpus_path,
                temporary_database,
                metadata={"source": metadata},
            )
            os.replace(temporary_database, database_path)
            _write_json_atomic(
                metadata_path,
                {
                    "schema_version": BOOTSTRAP_SCHEMA_VERSION,
                    "database_name": database_path.name,
                    "corpus_version": DEFAULT_CORPUS_VERSION,
                    "corpus_sha256": corpus_sha256,
                    "record_count": stats.imported_record_count,
                    "source": metadata,
                },
            )
        except Exception as error:
            temporary_database.unlink(missing_ok=True)
            raise BootstrapError(
                f"DEFAULT_INDEX_BUILD_FAILED: {type(error).__name__}"
            ) from error

    return BootstrapResult(
        data_dir=str(target_dir),
        database_path=str(database_path),
        metadata_path=str(metadata_path),
        corpus_version=DEFAULT_CORPUS_VERSION,
        corpus_sha256=corpus_sha256,
        rebuilt=True,
        stats=BuildStats(
            source_record_count=stats.source_record_count,
            imported_record_count=stats.imported_record_count,
            skipped_record_count=stats.skipped_record_count,
            database_path=str(database_path),
        ),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="skillnudge bootstrap")
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = bootstrap_default_index(args.data_dir, force=args.force)
    except BootstrapError as error:
        print(str(error), file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
    else:
        action = "rebuilt" if result.rebuilt else "already current"
        print(f"Default SkillNudge index {action}: {result.database_path}")
    return 0
