"""Small records for the first real Session -> Skill evolution path."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
from typing import Any, Mapping


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_DECISIONS = {"PENDING", "ACCEPTED", "REJECTED"}


class ModelError(ValueError):
    """Raised when a core evolution record cannot be trusted."""


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ModelError(f"{path} must be an object")
    return value


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ModelError(f"{path} must be a non-empty string")
    return value


def _keys(value: Mapping[str, Any], path: str, expected: set[str]) -> None:
    missing = sorted(expected - set(value))
    extra = sorted(set(value) - expected)
    if missing:
        raise ModelError(f"{path} missing required fields: {missing}")
    if extra:
        raise ModelError(f"{path} has unexpected fields: {extra}")


def content_sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def validate_skill(value: Any, *, path: str = "skill") -> dict[str, Any]:
    """Validate one immutable source or candidate Skill version."""

    skill = _mapping(value, path)
    fields = {"skill_id", "version", "content", "sha256", "source", "parent_version"}
    _keys(skill, path, fields)
    content = _string(skill["content"], f"{path}.content")
    sha256 = _string(skill["sha256"], f"{path}.sha256")
    if not _SHA256.fullmatch(sha256) or content_sha256(content) != sha256:
        raise ModelError(f"{path}.sha256 does not match {path}.content")
    source = _mapping(skill["source"], f"{path}.source")
    _keys(source, f"{path}.source", {"kind", "ref"})
    parent = skill["parent_version"]
    if parent is not None and _string(parent, f"{path}.parent_version") == skill["version"]:
        raise ModelError(f"{path}.parent_version must differ from version")
    return {
        "skill_id": _string(skill["skill_id"], f"{path}.skill_id"),
        "version": _string(skill["version"], f"{path}.version"),
        "content": content,
        "sha256": sha256,
        "source": {
            "kind": _string(source["kind"], f"{path}.source.kind"),
            "ref": _string(source["ref"], f"{path}.source.ref"),
        },
        "parent_version": parent,
    }

def validate_session_reference(value: Any, *, path: str = "evidence") -> dict[str, Any]:
    """Validate an observable Session/feedback reference, without judging it."""

    evidence = _mapping(value, path)
    fields = {"session_id", "trace_ref", "feedback_refs", "observed_summary"}
    _keys(evidence, path, fields)
    refs = evidence["feedback_refs"]
    if not isinstance(refs, list) or not refs or not all(isinstance(item, str) and item.strip() for item in refs):
        raise ModelError(f"{path}.feedback_refs must be a non-empty string list")
    for key in ("session_id", "trace_ref", "observed_summary"):
        _string(evidence[key], f"{path}.{key}")
    if any(key in evidence for key in ("chain_of_thought", "hidden_reasoning", "scratchpad")):
        raise ModelError(f"{path} must contain observable evidence only")
    return {
        "session_id": evidence["session_id"],
        "trace_ref": evidence["trace_ref"],
        "feedback_refs": list(refs),
        "observed_summary": evidence["observed_summary"],
    }


def validate_candidate(value: Any) -> dict[str, Any]:
    """Validate source -> candidate lineage and the Human accept/reject boundary."""

    candidate = _mapping(value, "candidate")
    fields = {"candidate_id", "source_skill", "candidate_skill", "operator_ref", "evidence", "human_decision"}
    _keys(candidate, "candidate", fields)
    source = validate_skill(candidate["source_skill"], path="candidate.source_skill")
    generated = validate_skill(candidate["candidate_skill"], path="candidate.candidate_skill")
    if source["skill_id"] != generated["skill_id"]:
        raise ModelError("source and candidate skill_id must match")
    if generated["parent_version"] != source["version"]:
        raise ModelError("candidate.parent_version must match source.version")
    evidence = validate_session_reference(candidate["evidence"], path="candidate.evidence")
    decision = _string(candidate["human_decision"], "candidate.human_decision").upper()
    if decision not in _DECISIONS:
        raise ModelError("candidate.human_decision must be PENDING, ACCEPTED, or REJECTED")
    return {
        "candidate_id": _string(candidate["candidate_id"], "candidate.candidate_id"),
        "source_skill": source,
        "candidate_skill": generated,
        "operator_ref": _string(candidate["operator_ref"], "candidate.operator_ref"),
        "evidence": evidence,
        "human_decision": decision,
    }


def build_skillopt_sleep_tasks(
    session: Any,
    source_skill: Any,
    *,
    project: str,
    target_skill_path: str,
    source_skill_path: str | None = None,
    intent: str,
    context_excerpt: str,
    attempted_solution: str,
    outcome: str = "fail",
    reference_kind: str = "none",
    reference: str = "",
    tags: list[str] | None = None,
    skill_hint: str = "",
    transcript_source: str = "codex",
) -> dict[str, Any]:
    """Build one reviewed-task handoff for SkillOpt-Sleep.

    SkillOpt-Sleep already owns harvesting, replay, gating, staging, and
    adoption. This function only translates one validated observable Session
    reference into its native task-file shape and keeps the source Skill and
    feedback lineage in a sidecar at the handoff boundary. SkillOpt-Sleep does
    not propagate arbitrary sidecar fields into its reports or staging
    manifest, so callers must retain the handoff payload for the later join.
    When ``source_skill_path`` is supplied, the exact file content is checked
    against the source Skill hash before a handoff is emitted. The handoff is
    deliberately unreviewed until a Human inspects and sets the task file's
    ``reviewed`` field before a real provider run.
    """

    evidence = validate_session_reference(session, path="session")
    skill = validate_skill(source_skill, path="source_skill")
    for value, path in (
        (project, "project"),
        (target_skill_path, "target_skill_path"),
        (intent, "intent"),
        (context_excerpt, "context_excerpt"),
        (attempted_solution, "attempted_solution"),
        (outcome, "outcome"),
        (reference_kind, "reference_kind"),
        (transcript_source, "transcript_source"),
    ):
        _string(value, path)
    if not isinstance(reference, str):
        raise ModelError("reference must be a string")
    if not isinstance(skill_hint, str):
        raise ModelError("skill_hint must be a string")
    if source_skill_path is not None:
        _string(source_skill_path, "source_skill_path")
        try:
            on_disk_content = Path(source_skill_path).read_text(encoding="utf-8")
        except OSError as exc:
            raise ModelError(f"source_skill_path cannot be read: {exc}") from exc
        if on_disk_content != skill["content"]:
            raise ModelError("source_skill_path content does not match source_skill.content")
    if tags is not None and (
        not isinstance(tags, list)
        or not all(isinstance(tag, str) and tag.strip() for tag in tags)
    ):
        raise ModelError("tags must be a list of non-empty strings")

    task = {
        "id": f"{evidence['session_id']}-skillnudge-handoff",
        "project": project,
        "intent": intent,
        "context_excerpt": context_excerpt,
        "attempted_solution": attempted_solution,
        "outcome": outcome,
        "reference_kind": reference_kind,
        "reference": reference,
        "tags": list(tags or []),
        "source_sessions": [evidence["session_id"]],
        "split": "train",
        "origin": "real",
        "skill_hint": skill_hint or skill["skill_id"],
    }
    return {
        "format": "skillopt_sleep.tasks.v1",
        "project": project,
        "transcript_source": transcript_source,
        "n_sessions": 1,
        "target_skill_path": target_skill_path,
        "reviewed": False,
        "tasks": [task],
        "skillnudge_provenance": {
            "session_id": evidence["session_id"],
            "trace_ref": evidence["trace_ref"],
            "feedback_refs": evidence["feedback_refs"],
            "source_skill": {
                "skill_id": skill["skill_id"],
                "version": skill["version"],
                "sha256": skill["sha256"],
            },
        },
    }
