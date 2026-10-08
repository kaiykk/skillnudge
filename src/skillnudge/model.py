"""Small, provider-neutral records for Session -> Skill evolution."""

from __future__ import annotations

import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Mapping


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_DECISIONS = {"PENDING", "ACCEPTED", "REJECTED"}
_VALIDATION = {"UNVERIFIED", "VERIFIED", "UNAVAILABLE"}
_REFERENCE_KINDS = {"exact", "rubric", "rule", "none"}
_GATE_FIELDS = {"action", "validation_status", "validation_basis", "diff_sha256"}


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
    """Validate observable Session and feedback references without judging them."""

    evidence = _mapping(value, path)
    fields = {"session_id", "trace_ref", "feedback_refs", "observed_summary"}
    _keys(evidence, path, fields)
    refs = evidence["feedback_refs"]
    if not isinstance(refs, list) or not refs or not all(
        isinstance(item, str) and item.strip() for item in refs
    ):
        raise ModelError(f"{path}.feedback_refs must be a non-empty string list")
    for key in ("session_id", "trace_ref", "observed_summary"):
        _string(evidence[key], f"{path}.{key}")
    return {
        "session_id": evidence["session_id"],
        "trace_ref": evidence["trace_ref"],
        "feedback_refs": list(refs),
        "observed_summary": evidence["observed_summary"],
    }


def validate_candidate(value: Any) -> dict[str, Any]:
    """Validate source -> candidate lineage and the Human decision boundary."""

    candidate = _mapping(value, "candidate")
    fields = {
        "candidate_id", "source_skill", "candidate_skill", "operator_ref",
        "evidence", "human_decision",
    }
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
        "source_skill": source, "candidate_skill": generated,
        "operator_ref": _string(candidate["operator_ref"], "candidate.operator_ref"),
        "evidence": evidence, "human_decision": decision,
    }


def _validate_proposal(value: Any) -> dict[str, Any]:
    proposal = _mapping(value, "proposal")
    fields = {"diagnosis", "change_summary", "candidate_content", "validation_status", "validation_basis"}
    _keys(proposal, "proposal", fields)
    status = _string(proposal["validation_status"], "proposal.validation_status").upper()
    if status not in _VALIDATION:
        raise ModelError(f"proposal.validation_status must be one of {sorted(_VALIDATION)}")
    return {
        "diagnosis": _string(proposal["diagnosis"], "proposal.diagnosis"),
        "change_summary": _string(proposal["change_summary"], "proposal.change_summary"),
        "candidate_content": _string(proposal["candidate_content"], "proposal.candidate_content"),
        "validation_status": status,
        "validation_basis": _string(proposal["validation_basis"], "proposal.validation_basis"),
    }


def build_quick_improve_request(
    source_skill: Any,
    *,
    skill_path: str,
    failure: str,
    feedback: str,
    evidence: Any,
) -> dict[str, Any]:
    """Build the small request handed to a Host Agent improvement method."""

    skill = validate_skill(source_skill, path="source_skill")
    session = validate_session_reference(evidence, path="evidence")
    return {
        "schema": "skillnudge.quick-improve.request.v1",
        "skill_path": str(Path(_string(skill_path, "skill_path")).expanduser().resolve()),
        "source_skill": {
            "skill_id": skill["skill_id"], "version": skill["version"], "sha256": skill["sha256"],
        },
        "evidence": session,
        "failure": _string(failure, "failure"), "feedback": _string(feedback, "feedback"),
        "method": {
            "diagnose": "identify one observable failure mechanism",
            "edit": "propose one bounded targeted edit",
            "human_boundary": "return a candidate only; do not activate it",
        },
    }


def _unified_diff(source: str, candidate: str, path: str) -> str:
    return "".join(difflib.unified_diff(
        source.splitlines(keepends=True), candidate.splitlines(keepends=True),
        fromfile=f"a/{path}", tofile=f"b/{path}",
    ))


def quick_improve(
    source_skill: Any,
    *,
    skill_path: str,
    failure: str,
    feedback: str,
    evidence: Any,
    proposal: Any,
    candidate_id: str,
    candidate_version: str,
    operator_ref: str = "host-agent:quick-improve",
    staging_dir: str | None = None,
) -> dict[str, Any]:
    """Validate one Host Agent proposal and stage it without activation.

    The Host Agent owns semantic diagnosis and text generation. SkillNudge owns
    identity, evidence, diff, validation labels, and the pending Human boundary.
    No source file is modified by this function.
    """

    source = validate_skill(source_skill, path="source_skill")
    source_path = Path(_string(skill_path, "skill_path")).expanduser()
    if source_path.is_symlink() or not source_path.is_file():
        raise ModelError("skill_path must be a regular, non-symlink file")
    if source_path.read_text(encoding="utf-8") != source["content"]:
        raise ModelError("skill_path content does not match source Skill")
    request = build_quick_improve_request(
        source, skill_path=skill_path, failure=failure, feedback=feedback, evidence=evidence,
    )
    proposed = _validate_proposal(proposal)
    candidate_skill = validate_skill({
        "skill_id": source["skill_id"], "version": _string(candidate_version, "candidate_version"),
        "content": proposed["candidate_content"],
        "sha256": content_sha256(proposed["candidate_content"]),
        "source": {"kind": "quick-improve", "ref": request["evidence"]["session_id"]},
        "parent_version": source["version"],
    }, path="candidate_skill")
    if candidate_skill["content"] == source["content"]:
        raise ModelError("candidate_content must change the source Skill")
    candidate = validate_candidate({
        "candidate_id": _string(candidate_id, "candidate_id"), "source_skill": source,
        "candidate_skill": candidate_skill, "operator_ref": _string(operator_ref, "operator_ref"),
        "evidence": request["evidence"], "human_decision": "PENDING",
    })
    diff = _unified_diff(source["content"], candidate_skill["content"], source_path.name)
    gate = {
        "action": "STAGE_PENDING_REVIEW", "validation_status": proposed["validation_status"],
        "validation_basis": proposed["validation_basis"], "diff_sha256": content_sha256(diff),
    }
    manifest = None
    if staging_dir is not None:
        manifest = stage_candidate(
            candidate, task_id=request["evidence"]["session_id"], gate_result=gate,
            staging_dir=staging_dir, source_skill_path=skill_path, diff=diff,
            diagnosis=proposed["diagnosis"], change_summary=proposed["change_summary"],
        )
    return {
        "schema": "skillnudge.quick-improve.result.v1", "status": "CANDIDATE_PENDING",
        "request": request, "diagnosis": proposed["diagnosis"],
        "change_summary": proposed["change_summary"], "diff": diff,
        "validation": {"status": proposed["validation_status"], "basis": proposed["validation_basis"]},
        "candidate": candidate, "manifest": manifest, "source_modified": False,
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
    judge: Mapping[str, Any] | None = None,
    tags: list[str] | None = None,
    skill_hint: str = "",
    transcript_source: str = "codex",
) -> dict[str, Any]:
    """Keep the existing thin SkillOpt-Sleep handoff for compatibility."""

    evidence = validate_session_reference(session, path="session")
    skill = validate_skill(source_skill, path="source_skill")
    for value, path in (
        (project, "project"), (target_skill_path, "target_skill_path"), (intent, "intent"),
        (context_excerpt, "context_excerpt"), (attempted_solution, "attempted_solution"),
        (outcome, "outcome"), (reference_kind, "reference_kind"), (transcript_source, "transcript_source"),
    ):
        _string(value, path)
    if not isinstance(reference, str) or not isinstance(skill_hint, str):
        raise ModelError("reference and skill_hint must be strings")
    if reference_kind not in _REFERENCE_KINDS:
        raise ModelError("reference_kind must be exact, rubric, rule, or none")
    if reference_kind != "none" and not reference.strip():
        raise ModelError("reference is required when reference_kind is not none")
    if judge is not None:
        judge = dict(_mapping(judge, "judge"))
    if reference_kind == "rule" and not judge:
        raise ModelError("judge is required when reference_kind is rule")
    if source_skill_path is not None:
        on_disk = Path(_string(source_skill_path, "source_skill_path")).read_text(encoding="utf-8")
        if on_disk != skill["content"]:
            raise ModelError("source_skill_path content does not match source Skill")
    if tags is not None and (not isinstance(tags, list) or not all(isinstance(t, str) and t.strip() for t in tags)):
        raise ModelError("tags must be a list of non-empty strings")
    task = {
        "id": f"{evidence['session_id']}-skillnudge-handoff", "project": project,
        "intent": intent, "context_excerpt": context_excerpt, "attempted_solution": attempted_solution,
        "outcome": outcome, "reference_kind": reference_kind, "reference": reference,
        "judge": dict(judge or {}), "tags": list(tags or []),
        "source_sessions": [evidence["session_id"]], "split": "train", "origin": "real",
        "skill_hint": skill_hint or skill["skill_id"],
    }
    return {
        "format": "skillopt_sleep.tasks.v1", "project": project, "transcript_source": transcript_source,
        "n_sessions": 1, "target_skill_path": target_skill_path, "reviewed": False, "tasks": [task],
        "skillnudge_provenance": {
            "session_id": evidence["session_id"], "trace_ref": evidence["trace_ref"],
            "feedback_refs": evidence["feedback_refs"],
            "source_skill": {"skill_id": skill["skill_id"], "version": skill["version"], "sha256": skill["sha256"]},
        },
    }


def stage_candidate(
    candidate: Any,
    *,
    task_id: str,
    gate_result: Any,
    staging_dir: str,
    source_skill_path: str,
    diff: str = "",
    diagnosis: str = "",
    change_summary: str = "",
) -> dict[str, Any]:
    """Stage a non-active candidate and its review material atomically."""

    record = validate_candidate(candidate)
    _string(task_id, "task_id")
    gate = dict(_mapping(gate_result, "gate_result"))
    if set(gate) - _GATE_FIELDS:
        raise ModelError("gate_result has unexpected fields")
    status = _string(gate.get("validation_status"), "gate_result.validation_status").upper()
    if status not in _VALIDATION:
        raise ModelError(f"gate_result.validation_status must be one of {sorted(_VALIDATION)}")
    _string(gate.get("validation_basis"), "gate_result.validation_basis")
    if diff and gate.get("diff_sha256") != content_sha256(diff):
        raise ModelError("gate_result.diff_sha256 does not match diff")
    if record["human_decision"] != "PENDING":
        raise ModelError("candidate must remain PENDING while staged")
    source_path = Path(_string(source_skill_path, "source_skill_path")).expanduser()
    if source_path.is_symlink() or not source_path.is_file():
        raise ModelError("source_skill_path must be a regular, non-symlink file")
    if source_path.read_text(encoding="utf-8") != record["source_skill"]["content"]:
        raise ModelError("source_skill_path content does not match source Skill")
    directory = Path(_string(staging_dir, "staging_dir")).expanduser()
    if os.path.lexists(directory) and directory.is_symlink():
        raise ModelError("staging_dir must not be a symlink")
    directory.mkdir(parents=True, exist_ok=True)
    artifact_names = ("proposed_SKILL.md", "provenance.json", "manifest.json", "diff.patch")
    if any(os.path.lexists(directory / name) for name in artifact_names):
        raise ModelError("staging_dir already contains a candidate artifact")
    source_realpath = str(source_path.resolve())
    skill = record["candidate_skill"]
    provenance = {
        "schema": "skillnudge.provenance.v1", "candidate_id": record["candidate_id"], "task_id": task_id,
        "session": record["evidence"],
        "source_skill": {"skill_id": record["source_skill"]["skill_id"], "version": record["source_skill"]["version"], "sha256": record["source_skill"]["sha256"], "path": source_realpath},
        "candidate_skill": {"skill_id": skill["skill_id"], "version": skill["version"], "sha256": skill["sha256"]},
    }
    manifest = {
        "schema": "skillnudge.staging.v2", "candidate_id": record["candidate_id"], "task_id": task_id,
        "proposed_file": "proposed_SKILL.md", "proposed_sha256": skill["sha256"],
        "source_skill_sha256": record["source_skill"]["sha256"], "source_skill_path": source_realpath,
        "operator_ref": record["operator_ref"],
        "validation": {"status": status, "basis": gate["validation_basis"]},
        "diagnosis": diagnosis, "change_summary": change_summary, "diff_file": "diff.patch",
        "diff_sha256": gate.get("diff_sha256", content_sha256(diff)),
        "human_decision": "PENDING", "provenance_file": "provenance.json",
    }
    contents = {
        "proposed_SKILL.md": skill["content"], "provenance.json": _json_text(provenance),
        "manifest.json": _json_text(manifest), "diff.patch": diff,
    }
    created: list[Path] = []
    try:
        for name, content in contents.items():
            path = directory / name
            _atomic_write(path, content)
            created.append(path)
    except Exception:
        for path in created:
            try:
                path.unlink()
            except FileNotFoundError:
                pass
        raise
    return manifest


def _json_text(value: Mapping[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _atomic_write(path: Path, content: str) -> None:
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise
