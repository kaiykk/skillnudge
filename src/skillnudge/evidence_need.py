"""Bounded persistence for one suspended Evidence Need.

An Evidence Need records an unresolved question that may be revisited by a
later host-observed experience.  It is deliberately not a capability registry
or a lifecycle state.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .bootstrap import default_data_dir


EVIDENCE_NEED_SCHEMA_VERSION = "native.evidence-need.v0"
EVIDENCE_NEED_DIRNAME = "evidence-needs"
_NEED_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_EVIDENCE_ROLES = {"NATURAL_UTILITY_EVIDENCE"}
_STATUSES = {"OPEN", "CLOSED"}


class EvidenceNeedError(ValueError):
    """Raised when an Evidence Need violates its public contract."""


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise EvidenceNeedError(f"{path} must be an object")
    return value


def _keys(value: Mapping[str, Any], path: str, required: set[str], allowed: set[str]) -> None:
    missing = sorted(required - set(value))
    extra = sorted(set(value) - allowed)
    if missing:
        raise EvidenceNeedError(f"{path} missing required fields: {missing}")
    if extra:
        raise EvidenceNeedError(f"{path} has unexpected fields: {extra}")


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EvidenceNeedError(f"{path} must be a non-empty string")
    return value


def _string_list(value: Any, path: str, *, non_empty: bool = True) -> list[str]:
    if not isinstance(value, list):
        raise EvidenceNeedError(f"{path} must be a list")
    if non_empty and not value:
        raise EvidenceNeedError(f"{path} must be non-empty")
    return [_string(item, f"{path}[{index}]") for index, item in enumerate(value)]


def _timestamp(value: Any, path: str) -> str:
    raw = _string(value, path)
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as error:
        raise EvidenceNeedError(f"{path} must be an ISO-8601 timestamp") from error
    if parsed.tzinfo is None:
        raise EvidenceNeedError(f"{path} must include a timezone")
    return parsed.isoformat()


def _validate_need_id(value: Any, path: str = "need_id") -> str:
    result = _string(value, path)
    if not _NEED_ID.fullmatch(result):
        raise EvidenceNeedError(
            f"{path} must contain only letters, digits, '.', '_' or '-' and be at most 128 characters"
        )
    return result


def validate_evidence_need(value: Any, *, require_open: bool = False) -> dict[str, Any]:
    """Validate and normalize one persisted Evidence Need."""

    envelope = _mapping(value, "evidence_need")
    _keys(
        envelope,
        "evidence_need",
        {"schema_version", "need_id", "subject", "unresolved_question", "why_it_exists", "evidence_role", "interesting_future_event", "scope", "source_evidence_refs", "status", "created_at"},
        {"schema_version", "need_id", "subject", "unresolved_question", "why_it_exists", "evidence_role", "interesting_future_event", "scope", "source_evidence_refs", "status", "created_at"},
    )
    if envelope["schema_version"] != EVIDENCE_NEED_SCHEMA_VERSION:
        raise EvidenceNeedError(f"schema_version must be {EVIDENCE_NEED_SCHEMA_VERSION!r}")
    need_id = _validate_need_id(envelope["need_id"])
    subject = _mapping(envelope["subject"], "subject")
    _keys(subject, "subject", {"capability_id", "candidate_version", "candidate_sha256"}, {"capability_id", "candidate_version", "candidate_sha256"})
    subject_normalized = {key: _string(subject[key], f"subject.{key}") for key in ("capability_id", "candidate_version", "candidate_sha256")}
    if not re.fullmatch(r"[0-9a-fA-F]{64}", subject_normalized["candidate_sha256"]):
        raise EvidenceNeedError("subject.candidate_sha256 must be a 64-character hex digest")
    role = _string(envelope["evidence_role"], "evidence_role")
    if role not in _EVIDENCE_ROLES:
        raise EvidenceNeedError(f"evidence_role must be one of {sorted(_EVIDENCE_ROLES)}")
    scope = _mapping(envelope["scope"], "scope")
    _keys(scope, "scope", {"model", "harness", "task_family"}, {"model", "harness", "task_family"})
    scope_normalized = {key: _string(scope[key], f"scope.{key}") for key in ("model", "harness", "task_family")}
    status = _string(envelope["status"], "status")
    if status not in _STATUSES:
        raise EvidenceNeedError(f"status must be one of {sorted(_STATUSES)}")
    if require_open and status != "OPEN":
        raise EvidenceNeedError("Evidence Need is not OPEN")
    return {
        "schema_version": EVIDENCE_NEED_SCHEMA_VERSION,
        "need_id": need_id,
        "subject": subject_normalized,
        "unresolved_question": _string(envelope["unresolved_question"], "unresolved_question"),
        "why_it_exists": _string(envelope["why_it_exists"], "why_it_exists"),
        "evidence_role": role,
        "interesting_future_event": _string(envelope["interesting_future_event"], "interesting_future_event"),
        "scope": scope_normalized,
        "source_evidence_refs": _string_list(envelope["source_evidence_refs"], "source_evidence_refs"),
        "status": status,
        "created_at": _timestamp(envelope["created_at"], "created_at"),
    }


def evidence_need_dir(data_dir: str | Path | None = None) -> Path:
    root = Path(data_dir).expanduser() if data_dir is not None else default_data_dir()
    return root / EVIDENCE_NEED_DIRNAME


def evidence_need_path(need_id: str, *, data_dir: str | Path | None = None) -> Path:
    return evidence_need_dir(data_dir) / f"{_validate_need_id(need_id)}.json"


def _write_atomic(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def create_evidence_need(value: Any, *, data_dir: str | Path | None = None) -> dict[str, Any]:
    """Validate and persist a new OPEN Evidence Need without overwriting one."""

    normalized = validate_evidence_need(value)
    if normalized["status"] != "OPEN":
        raise EvidenceNeedError("new Evidence Need must have status=OPEN")
    path = evidence_need_path(normalized["need_id"], data_dir=data_dir)
    if path.exists():
        raise EvidenceNeedError(f"Evidence Need already exists: {normalized['need_id']}")
    _write_atomic(path, normalized)
    return normalized


def load_evidence_need(need_id: str, *, data_dir: str | Path | None = None, require_open: bool = False) -> dict[str, Any]:
    path = evidence_need_path(need_id, data_dir=data_dir)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise EvidenceNeedError(f"unknown Evidence Need: {need_id}") from error
    except (OSError, json.JSONDecodeError) as error:
        raise EvidenceNeedError(f"Evidence Need cannot be read: {need_id}") from error
    normalized = validate_evidence_need(raw, require_open=require_open)
    if normalized["need_id"] != need_id:
        raise EvidenceNeedError("persisted Evidence Need identity does not match requested need_id")
    return normalized


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="skillnudge need")
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create", help="persist one OPEN Evidence Need")
    create.add_argument("--stdin", action="store_true", help="read the Evidence Need JSON from standard input")
    create.add_argument("--data-dir", type=Path, help="override the per-user SkillNudge data directory")
    args = parser.parse_args(argv)
    if args.command == "create" and not args.stdin:
        parser.error("need create requires --stdin")
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            raise EvidenceNeedError("the Evidence Need must not be empty")
        value = json.loads(raw)
        result = create_evidence_need(value, data_dir=args.data_dir)
    except (json.JSONDecodeError, EvidenceNeedError, OSError) as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
