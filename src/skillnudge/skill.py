"""Immutable Skill identity and version records."""

from __future__ import annotations

import hashlib
import re
from typing import Any, Mapping


SKILL_VERSION_SCHEMA = "skillnudge.skill-version.v0"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_STATUSES = {"ACTIVE", "CANDIDATE"}


class SkillValidationError(ValueError):
    """Raised when a Skill version record is invalid."""


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SkillValidationError(f"{path} must be an object")
    return value


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SkillValidationError(f"{path} must be a non-empty string")
    return value


def _keys(value: Mapping[str, Any], path: str, required: set[str], allowed: set[str]) -> None:
    missing = sorted(required - set(value))
    extra = sorted(set(value) - allowed)
    if missing:
        raise SkillValidationError(f"{path} missing required fields: {missing}")
    if extra:
        raise SkillValidationError(f"{path} has unexpected fields: {extra}")


def validate_skill_version(value: Any, *, path: str = "skill") -> dict[str, Any]:
    """Validate and normalize one immutable Skill version."""

    skill = _mapping(value, path)
    fields = {
        "schema_version", "skill_id", "version", "content", "sha256", "source",
        "parent_version", "lifecycle_status",
    }
    _keys(skill, path, fields, fields)
    if skill["schema_version"] != SKILL_VERSION_SCHEMA:
        raise SkillValidationError(f"{path}.schema_version must be {SKILL_VERSION_SCHEMA}")
    skill_id = _string(skill["skill_id"], f"{path}.skill_id")
    version = _string(skill["version"], f"{path}.version")
    content = _string(skill["content"], f"{path}.content")
    sha256 = _string(skill["sha256"], f"{path}.sha256")
    if not _SHA256.fullmatch(sha256):
        raise SkillValidationError(f"{path}.sha256 must be a lowercase SHA-256 digest")
    actual = hashlib.sha256(content.encode("utf-8")).hexdigest()
    if actual != sha256:
        raise SkillValidationError(f"{path}.sha256 does not match {path}.content")
    source = _mapping(skill["source"], f"{path}.source")
    _keys(source, f"{path}.source", {"kind", "ref"}, {"kind", "ref"})
    source_normalized = {
        "kind": _string(source["kind"], f"{path}.source.kind"),
        "ref": _string(source["ref"], f"{path}.source.ref"),
    }
    parent = skill["parent_version"]
    if parent is not None:
        parent = _string(parent, f"{path}.parent_version")
        if parent == version:
            raise SkillValidationError(f"{path}.parent_version must differ from version")
    lifecycle_status = _string(skill["lifecycle_status"], f"{path}.lifecycle_status")
    if lifecycle_status not in _STATUSES:
        raise SkillValidationError(f"{path}.lifecycle_status must be one of {sorted(_STATUSES)}")
    return {
        "schema_version": SKILL_VERSION_SCHEMA,
        "skill_id": skill_id,
        "version": version,
        "content": content,
        "sha256": sha256,
        "source": source_normalized,
        "parent_version": parent,
        "lifecycle_status": lifecycle_status,
    }


def content_sha256(content: str) -> str:
    """Return the canonical hash for Skill content."""

    return hashlib.sha256(content.encode("utf-8")).hexdigest()
