"""Immutable, instruction-only capability artifact contract."""

from __future__ import annotations

import hashlib
import re
from typing import Any, Mapping


CAPABILITY_ARTIFACT_SCHEMA_VERSION = "native.capability-artifact.v0"
SUPPORTED_CAPABILITY_TYPES = {"instruction"}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class CapabilityArtifactError(ValueError):
    """Raised when a capability artifact violates its identity contract."""


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise CapabilityArtifactError(f"{path} must be an object")
    return value


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CapabilityArtifactError(f"{path} must be a non-empty string")
    return value


def _keys(value: Mapping[str, Any], path: str, required: set[str], allowed: set[str]) -> None:
    missing = sorted(required - set(value))
    extra = sorted(set(value) - allowed)
    if missing:
        raise CapabilityArtifactError(f"{path} missing required fields: {missing}")
    if extra:
        raise CapabilityArtifactError(f"{path} has unexpected fields: {extra}")


def validate_capability_artifact(value: Any, *, path: str = "artifact") -> dict[str, str]:
    """Validate exact UTF-8 identity and return a normalized immutable record."""

    artifact = _mapping(value, path)
    fields = {"schema_version", "capability_id", "version", "type", "exact_content", "sha256"}
    _keys(artifact, path, fields, fields)
    if artifact["schema_version"] != CAPABILITY_ARTIFACT_SCHEMA_VERSION:
        raise CapabilityArtifactError(f"{path}.schema_version must be {CAPABILITY_ARTIFACT_SCHEMA_VERSION}")
    capability_id = _string(artifact["capability_id"], f"{path}.capability_id")
    version = _string(artifact["version"], f"{path}.version")
    artifact_type = _string(artifact["type"], f"{path}.type")
    if artifact_type not in SUPPORTED_CAPABILITY_TYPES:
        raise CapabilityArtifactError(f"{path}.type must be instruction")
    exact_content = _string(artifact["exact_content"], f"{path}.exact_content")
    expected_hash = _string(artifact["sha256"], f"{path}.sha256")
    if not _SHA256.fullmatch(expected_hash):
        raise CapabilityArtifactError(f"{path}.sha256 must be a lowercase SHA-256 hex digest")
    actual_hash = hashlib.sha256(exact_content.encode("utf-8")).hexdigest()
    if expected_hash != actual_hash:
        raise CapabilityArtifactError(f"{path}.sha256 does not match exact_content")
    return {
        "schema_version": CAPABILITY_ARTIFACT_SCHEMA_VERSION,
        "capability_id": capability_id,
        "version": version,
        "type": "instruction",
        "exact_content": exact_content,
        "sha256": expected_hash,
    }


def artifact_identity(value: Mapping[str, Any]) -> tuple[str, str, str]:
    """Return the stable identity tuple after the caller has validated it."""

    return (str(value["capability_id"]), str(value["version"]), str(value["sha256"]))
