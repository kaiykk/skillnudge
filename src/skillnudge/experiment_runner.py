"""Minimal Phase 2 experiment runner and evidence artifacts.

This module deliberately stops at the experiment boundary. It provides:

* versioned task, condition, run, trace, oracle, and evidence shapes;
* an injectable Agent and Oracle interface;
* a small runner that compares one condition at a time;
* a fixture CLI entry point that never claims to execute a benchmark.

The runner records observable events only. Agent adapters must not put private
reasoning or chain-of-thought into result payloads or trace details.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import uuid
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence, runtime_checkable


EXPERIMENT_RUN_SCHEMA = "experiment.run.v0"
TRACE_EVENT_SCHEMA = "trace.event.experiment.v0"
EVIDENCE_SCHEMA = "utility.evidence.experiment.v0"
PAIR_MANIFEST_SCHEMA = "pair.manifest.experiment.v0"
SYSTEMATIC_DEBUGGING_SKILL = "systematic-debugging-v6.4.1"
FROZEN_SKILL_ARTIFACT_ID = "systematic-debugging-superpowers-v6.4.1-source-unit"
FROZEN_SKILL_REPOSITORY = "https://github.com/obra/superpowers"
FROZEN_SKILL_VERSION = "v6.4.1"
FROZEN_SKILL_TAG_OBJECT = "b92c4fa87ea1252077a7f7d3bf420e52325dd25e"
FROZEN_SKILL_CONTENT_COMMIT = "5bf4e78011075bcfc0dc295f0724994cd123ee71"
FROZEN_SKILL_SOURCE_PATHS = (
    "skills/systematic-debugging/SKILL.md",
    "skills/systematic-debugging/root-cause-tracing.md",
    "skills/systematic-debugging/defense-in-depth.md",
    "skills/systematic-debugging/condition-based-waiting.md",
)
FROZEN_SKILL_FILE_SHA256 = {
    "skills/systematic-debugging/SKILL.md": (
        "808fc5717aa88ad65efff312b11c186294d3e6ee301afb584e2f86599b137787"
    ),
    "skills/systematic-debugging/root-cause-tracing.md": (
        "75b933b6a8c40bdb2031b10f21654395b56ec6ab6bc7b018c18d3fe57aeb7fb8"
    ),
    "skills/systematic-debugging/defense-in-depth.md": (
        "1e175fb86fc357e58c6aebf5441e481e1b7868b4380c0456b63a17eefbd18ba7"
    ),
    "skills/systematic-debugging/condition-based-waiting.md": (
        "e89fec8400d6cd50f43407cec9fab50976ba4d55d0ec2eb51c0bd68036b54c26"
    ),
}
FROZEN_SKILL_MANIFEST_SCHEME = "path-tab-sha256-prefix-v1"
FROZEN_SKILL_HISTORICAL_MANIFEST_SCHEME = "path-space-raw-digest-legacy"
FROZEN_SKILL_HISTORICAL_MANIFEST_SHA256 = (
    "92dc8f44a0a729f72e32e1c000f0e37ad8cfb9cbd6346ed4ddbe92694ebe86eb"
)
FROZEN_SKILL_MANIFEST_SHA256 = (
    "fdd07b9398e828b9ac6cd7194572cadd313e1478882f330f0f0d84fa1b60aea4"
)
SKILL_RENDERER_WRAPPER_REVISION = "skillnudge-fixed-context-v0"
FIXTURE_HARNESS_VERSION = "fixture-harness-v0"
FIXTURE_ORACLE_VERSION = "fixture-oracle-v0"
TRACE_INSTRUMENTATION_ID = TRACE_EVENT_SCHEMA
EVIDENCE_VALIDITIES = frozenset({"VALID", "INCONCLUSIVE", "PROTOCOL_FAILURE"})
PAIR_STATUSES = frozenset({"VALID", "PROTOCOL_FAILURE"})
UTILITY_CONCLUSIONS = frozenset(
    {"HELPS", "NEUTRAL", "HURTS", "INCONCLUSIVE", "PROTOCOL_FAILURE"}
)
ARTIFACT_VERIFICATION_MODES = frozenset(
    {"none", "synthetic_fixture", "frozen_verified_artifact"}
)

DEFAULT_RETRY_POLICY = {
    "transport_retry_limit": 0,
    "tool_failure_retry_limit": 0,
    "model_error_retry_limit": 0,
    "task_level_retry_limit": 0,
}
DEFAULT_TERMINATION_POLICY = {
    "stop_on_completion": True,
    "stop_on_failure": True,
    "budget_enforced": True,
}
DEFAULT_CONTROL_ARTIFACT_VERIFICATION = {
    "mode": "none",
    "verified": True,
    "expected_manifest_sha256": None,
    "actual_manifest_sha256": None,
}


def canonical_skill_manifest_sha256(file_hashes: Mapping[str, str]) -> str:
    """Hash the explicitly versioned ordered source-file manifest."""

    if set(file_hashes) != set(FROZEN_SKILL_SOURCE_PATHS):
        raise ValueError("file_hashes must contain exactly the frozen source paths")
    records = [
        f"{path}\tsha256:{file_hashes[path]}" for path in FROZEN_SKILL_SOURCE_PATHS
    ]
    canonical = "\n".join(records) + "\n"
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def unknown_observed_model_identity(requested_model: str) -> dict[str, Any]:
    return {
        "requested_model": requested_model,
        "observed_model_ids": [],
        "identity_consistent": None,
        "responses": [],
    }


def observed_model_identity_from_result(
    result: Any,
    requested_model: str,
) -> dict[str, Any]:
    """Summarize only provider-returned model identity observations."""

    observations = result.get("model_response_observations", []) if _is_mapping(result) else []
    if not isinstance(observations, list):
        observations = []
    clean_observations = [
        dict(item)
        for item in observations
        if isinstance(item, Mapping)
    ]
    observed_ids = sorted(
        {
            item["observed_model_id"]
            for item in clean_observations
            if isinstance(item.get("observed_model_id"), str)
            and item["observed_model_id"].strip()
        }
    )
    return {
        "requested_model": requested_model,
        "observed_model_ids": observed_ids,
        "identity_consistent": (
            len(observed_ids) <= 1 if clean_observations else None
        ),
        "responses": clean_observations,
    }

SUPPORTED_SKILLS = frozenset({SYSTEMATIC_DEBUGGING_SKILL})
SUPPORTED_TRACE_EVENTS = frozenset(
    {
        "agent_start",
        "tool_call",
        "tool_result",
        "test_execution",
        "patch_generated",
        "verification",
        "oracle_evaluation",
        "failure",
        "completion",
    }
)
_FORBIDDEN_PAYLOAD_KEYS = frozenset(
    {
        "chain_of_thought",
        "cot",
        "hidden_reasoning",
        "internal_reasoning",
        "private_reasoning",
        "thoughts",
    }
)


class ExperimentSchemaError(ValueError):
    """Raised when an experiment artifact violates its local schema."""

    def __init__(self, schema_name: str, errors: Sequence[str]):
        self.schema_name = schema_name
        self.errors = list(errors)
        super().__init__(f"{schema_name} validation failed: {'; '.join(self.errors)}")


class ExperimentRunError(RuntimeError):
    """Raised when an experiment run cannot complete safely."""


def _is_mapping(value: Any) -> bool:
    return isinstance(value, Mapping)


def _required_string(value: Mapping[str, Any], key: str, errors: list[str]) -> None:
    item = value.get(key)
    if not isinstance(item, str) or not item.strip():
        errors.append(f"{key} must be a non-empty string")


def _unexpected(
    value: Mapping[str, Any],
    allowed: set[str] | frozenset[str],
    errors: list[str],
) -> None:
    extra = sorted(set(value) - set(allowed))
    if extra:
        errors.append(f"unexpected fields: {extra}")


def _assert_observable_payload(value: Any, path: str = "payload") -> None:
    """Reject obvious private-reasoning fields from persisted payloads."""

    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).strip().lower().replace("-", "_")
            if normalized in _FORBIDDEN_PAYLOAD_KEYS:
                raise ExperimentSchemaError(
                    "ObservablePayload",
                    [f"{path}.{key} is not allowed in observable artifacts"],
                )
            _assert_observable_payload(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _assert_observable_payload(child, f"{path}[{index}]")


def _assert_json_serializable(value: Any, schema_name: str) -> None:
    try:
        json.dumps(value, ensure_ascii=False)
    except (TypeError, ValueError) as error:
        raise ExperimentSchemaError(schema_name, ["payload must be JSON serializable"]) from error


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_execution_budget_dict(
    value: "ExecutionBudget | Mapping[str, Any] | None",
) -> dict[str, Any]:
    if isinstance(value, ExecutionBudget):
        return value.as_dict()
    if value is None:
        return {}
    if not _is_mapping(value):
        raise ExperimentSchemaError("ExecutionBudget", ["budget must be an object"])
    return dict(value)


def _as_execution_policy_dict(
    value: "ExecutionPolicy | Mapping[str, Any] | None",
) -> dict[str, Any]:
    if isinstance(value, ExecutionPolicy):
        return value.as_dict()
    if value is None:
        return ExecutionPolicy().as_dict()
    if not _is_mapping(value):
        raise ExperimentSchemaError("ExecutionPolicy", ["policy must be an object"])
    return ExecutionPolicy.from_value(value).as_dict()


@dataclass(frozen=True)
class ExecutionPolicy:
    """Minimal identity for retry and termination behavior."""

    retry_policy: Mapping[str, Any] = field(
        default_factory=lambda: dict(DEFAULT_RETRY_POLICY)
    )
    termination_policy: Mapping[str, Any] = field(
        default_factory=lambda: dict(DEFAULT_TERMINATION_POLICY)
    )

    def __post_init__(self) -> None:
        for name in ("retry_policy", "termination_policy"):
            value = getattr(self, name)
            if not _is_mapping(value):
                raise ValueError(f"{name} must be an object")
            _assert_observable_payload(value, f"execution_policy.{name}")
            _assert_json_serializable(value, "ExecutionPolicy")

    @classmethod
    def from_value(cls, value: Any) -> "ExecutionPolicy":
        if isinstance(value, cls):
            return value
        if not _is_mapping(value):
            raise ExperimentSchemaError("ExecutionPolicy", ["policy must be an object"])
        errors: list[str] = []
        _unexpected(value, {"retry_policy", "termination_policy"}, errors)
        retry_policy = value.get("retry_policy", DEFAULT_RETRY_POLICY)
        termination_policy = value.get(
            "termination_policy", DEFAULT_TERMINATION_POLICY
        )
        if not _is_mapping(retry_policy):
            errors.append("retry_policy must be an object")
        if not _is_mapping(termination_policy):
            errors.append("termination_policy must be an object")
        if errors:
            raise ExperimentSchemaError("ExecutionPolicy", errors)
        return cls(dict(retry_policy), dict(termination_policy))

    def as_dict(self) -> dict[str, Any]:
        return {
            "retry_policy": dict(self.retry_policy),
            "termination_policy": dict(self.termination_policy),
        }


@dataclass(frozen=True)
class ExecutionBudget:
    """The bounded execution budget exposed by an Agent Adapter."""

    max_steps: int = 40
    max_tool_calls: int = 80
    max_tokens: int | None = 32_000
    max_latency_ms: int | None = 300_000

    def __post_init__(self) -> None:
        for name in ("max_steps", "max_tool_calls"):
            value = getattr(self, name)
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        for name in ("max_tokens", "max_latency_ms"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, int) or value < 0):
                raise ValueError(f"{name} must be null or a non-negative integer")

    def as_dict(self) -> dict[str, int | None]:
        return {
            "max_steps": self.max_steps,
            "max_tool_calls": self.max_tool_calls,
            "max_tokens": self.max_tokens,
            "max_latency_ms": self.max_latency_ms,
        }


@dataclass(frozen=True)
class SkillExposure:
    """The agent-visible result of one static Skill rendering."""

    skill_identity: str | None
    skill_version: str | None
    payload_hash: str | None
    manifest_hash: str | None
    visible_context: str
    file_paths: tuple[str, ...] = ()
    artifact_verification: Mapping[str, Any] = field(
        default_factory=lambda: dict(DEFAULT_CONTROL_ARTIFACT_VERIFICATION)
    )
    source_file_hashes: Mapping[str, str] = field(default_factory=dict)
    source_revision: str | None = None
    wrapper_revision: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "skill_identity": self.skill_identity,
            "skill_version": self.skill_version,
            "payload_hash": self.payload_hash,
            "manifest_hash": self.manifest_hash,
            "file_paths": list(self.file_paths),
            "artifact_verification": dict(self.artifact_verification),
            "source_file_hashes": dict(self.source_file_hashes),
            "source_revision": self.source_revision,
            "wrapper_revision": self.wrapper_revision,
        }


class SkillExposureRenderer:
    """Render only the frozen source unit; no external fetch or routing occurs."""

    def __init__(
        self,
        payload_files: Mapping[str, str | bytes] | None = None,
        *,
        wrapper_revision: str = SKILL_RENDERER_WRAPPER_REVISION,
        expected_manifest_sha256: str | None = None,
        artifact_mode: str = "synthetic_fixture",
        source_revision: str | None = None,
    ):
        self.payload_files = dict(payload_files or {})
        self.wrapper_revision = wrapper_revision
        self.expected_manifest_sha256 = expected_manifest_sha256
        self.artifact_mode = artifact_mode
        self.source_revision = source_revision
        if artifact_mode not in ARTIFACT_VERIFICATION_MODES - {"none"}:
            raise ValueError(
                "artifact_mode must be synthetic_fixture or "
                "frozen_verified_artifact"
            )
        if (
            artifact_mode == "frozen_verified_artifact"
            and expected_manifest_sha256 is None
        ):
            raise ValueError(
                "frozen_verified_artifact requires expected_manifest_sha256"
            )
        extra_paths = sorted(set(self.payload_files) - set(FROZEN_SKILL_SOURCE_PATHS))
        missing_paths = [
            path for path in FROZEN_SKILL_SOURCE_PATHS if path not in self.payload_files
        ]
        if extra_paths or (self.payload_files and missing_paths):
            raise ValueError(
                "payload_files must contain exactly the frozen four-file source unit; "
                f"missing={missing_paths}, extra={extra_paths}"
            )

    @staticmethod
    def _content_bytes(content: str | bytes) -> bytes:
        if isinstance(content, bytes):
            return content
        if isinstance(content, str):
            return content.encode("utf-8")
        raise TypeError("Skill payload content must be str or bytes")

    def _manifest_hash(self) -> str:
        manifest_hash = self.manifest_hash()
        if (
            self.expected_manifest_sha256 is not None
            and manifest_hash != self.expected_manifest_sha256
        ):
            raise ExperimentRunError(
                "FROZEN_SKILL_MANIFEST_MISMATCH: "
                f"expected={self.expected_manifest_sha256} actual={manifest_hash}"
            )
        return manifest_hash

    def manifest_hash(self) -> str:
        return canonical_skill_manifest_sha256(self.source_file_hashes())

    def source_file_hashes(self) -> dict[str, str]:
        return {
            path: hashlib.sha256(self._content_bytes(self.payload_files[path])).hexdigest()
            for path in FROZEN_SKILL_SOURCE_PATHS
        }

    def render(self, condition: "Condition") -> SkillExposure:
        condition = Condition.from_value(condition)
        if condition.skill is None:
            return SkillExposure(
                skill_identity=None,
                skill_version=None,
                payload_hash=None,
                manifest_hash=None,
                visible_context="",
                artifact_verification=dict(DEFAULT_CONTROL_ARTIFACT_VERIFICATION),
                wrapper_revision=self.wrapper_revision,
            )
        if condition.skill != SYSTEMATIC_DEBUGGING_SKILL:
            raise ExperimentRunError(
                f"unsupported Skill exposure condition: {condition.skill}"
            )
        if not self.payload_files:
            raise ExperimentRunError(
                "FROZEN_SKILL_PAYLOAD_REQUIRED: treatment needs all four source files"
            )

        manifest_hash = self._manifest_hash()
        file_hashes = self.source_file_hashes()
        sections = [
            f"wrapper_revision: {self.wrapper_revision}",
            f"artifact_id: {FROZEN_SKILL_ARTIFACT_ID}",
            f"source_repository: {FROZEN_SKILL_REPOSITORY}",
            f"source_version: {FROZEN_SKILL_VERSION}",
            f"source_manifest_sha256: {manifest_hash}",
            "",
        ]
        for path in FROZEN_SKILL_SOURCE_PATHS:
            content = self._content_bytes(self.payload_files[path]).decode("utf-8")
            sections.append(f"--- BEGIN {path} ---")
            sections.append(content.rstrip("\n"))
            sections.append(f"--- END {path} ---")
            sections.append("")
        visible_context = "\n".join(sections)
        payload_hash = hashlib.sha256(visible_context.encode("utf-8")).hexdigest()
        artifact_verification = {
            "mode": self.artifact_mode,
            "verified": self.artifact_mode == "frozen_verified_artifact",
            "expected_manifest_sha256": self.expected_manifest_sha256,
            "actual_manifest_sha256": manifest_hash,
            "source_repository": FROZEN_SKILL_REPOSITORY,
            "release": FROZEN_SKILL_VERSION,
            "tag_object": FROZEN_SKILL_TAG_OBJECT,
            "content_commit": self.source_revision,
            "source_file_hashes": file_hashes,
            "wrapper_revision": self.wrapper_revision,
        }
        return SkillExposure(
            skill_identity=FROZEN_SKILL_ARTIFACT_ID,
            skill_version=FROZEN_SKILL_VERSION,
            payload_hash=payload_hash,
            manifest_hash=manifest_hash,
            visible_context=visible_context,
            file_paths=FROZEN_SKILL_SOURCE_PATHS,
            artifact_verification=artifact_verification,
            source_file_hashes=file_hashes,
            source_revision=self.source_revision,
            wrapper_revision=self.wrapper_revision,
        )


@dataclass(frozen=True)
class AgentExecutionContext:
    """Only task-visible execution context passed from the adapter to an Agent."""

    condition: "Condition"
    visible_context: str
    skill_identity: str | None
    skill_version: str | None
    skill_manifest_hash: str | None
    skill_payload_hash: str | None
    model: str
    harness_version: str
    tool_manifest: Mapping[str, Any]
    execution_budget: Mapping[str, Any]
    environment_hash: str
    execution_policy: Mapping[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "condition": self.condition.as_dict(),
            "skill_identity": self.skill_identity,
            "skill_version": self.skill_version,
            "skill_manifest_hash": self.skill_manifest_hash,
            "skill_payload_hash": self.skill_payload_hash,
            "model": self.model,
            "harness_version": self.harness_version,
            "tool_manifest": dict(self.tool_manifest),
            "execution_budget": dict(self.execution_budget),
            "environment_hash": self.environment_hash,
            "execution_policy": dict(self.execution_policy),
        }


@dataclass(frozen=True)
class Condition:
    """The only two supported intervention conditions."""

    skill: str | None

    def __post_init__(self) -> None:
        if self.skill is not None and self.skill not in SUPPORTED_SKILLS:
            raise ValueError(f"unsupported skill condition: {self.skill}")

    @classmethod
    def control(cls) -> "Condition":
        return cls(skill=None)

    @classmethod
    def treatment(cls) -> "Condition":
        return cls(skill=SYSTEMATIC_DEBUGGING_SKILL)

    @classmethod
    def from_value(cls, value: Any) -> "Condition":
        if isinstance(value, cls):
            return value
        if not _is_mapping(value):
            raise ExperimentSchemaError("Condition", ["condition must be an object"])
        errors: list[str] = []
        _unexpected(value, {"skill"}, errors)
        skill = value.get("skill")
        if skill is not None and skill not in SUPPORTED_SKILLS:
            errors.append(
                f"skill must be null or one of {sorted(SUPPORTED_SKILLS)}"
            )
        if errors:
            raise ExperimentSchemaError("Condition", errors)
        return cls(skill=skill)

    @property
    def name(self) -> str:
        return "control" if self.skill is None else "treatment"

    def as_dict(self) -> dict[str, Any]:
        return {"skill": self.skill}


def validate_condition(value: Any) -> dict[str, Any]:
    return Condition.from_value(value).as_dict()


@dataclass(frozen=True)
class TaskArtifact:
    """Minimal task input with optional real-readiness visibility boundaries."""

    task_id: str
    repository: str
    commit: str
    test_command: str
    description: str = ""
    visible_test_command: str | None = None
    oracle_target_command: str | None = None
    oracle_regression_command: str | None = None
    environment_identity: str | None = None
    workspace_reference: str | None = None

    def __post_init__(self) -> None:
        validate_task_artifact(self.as_dict())

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "TaskArtifact":
        validate_task_artifact(value)
        return cls(
            task_id=value["task_id"],
            repository=value["repository"],
            commit=value["commit"],
            test_command=value["test_command"],
            description=value.get("description", ""),
            visible_test_command=value.get("visible_test_command"),
            oracle_target_command=value.get("oracle_target_command"),
            oracle_regression_command=value.get("oracle_regression_command"),
            environment_identity=value.get("environment_identity"),
            workspace_reference=value.get("workspace_reference"),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "repository": self.repository,
            "commit": self.commit,
            "test_command": self.test_command,
            "description": self.description,
            "visible_test_command": self.visible_test_command,
            "oracle_target_command": self.oracle_target_command,
            "oracle_regression_command": self.oracle_regression_command,
            "environment_identity": self.environment_identity,
            "workspace_reference": self.workspace_reference,
        }


def validate_task_artifact(value: Any) -> dict[str, Any]:
    if not _is_mapping(value):
        raise ExperimentSchemaError("TaskArtifact", ["task must be an object"])
    errors: list[str] = []
    allowed = {
        "task_id",
        "repository",
        "commit",
        "test_command",
        "description",
        "visible_test_command",
        "oracle_target_command",
        "oracle_regression_command",
        "environment_identity",
        "workspace_reference",
    }
    _unexpected(value, allowed, errors)
    for key in ("task_id", "repository", "commit", "test_command"):
        _required_string(value, key, errors)
    for key in (
        "description",
        "visible_test_command",
        "oracle_target_command",
        "oracle_regression_command",
        "environment_identity",
        "workspace_reference",
    ):
        item = value.get(key)
        if item is not None and not isinstance(item, str):
            errors.append(f"{key} must be null or a string")
    if errors:
        raise ExperimentSchemaError("TaskArtifact", errors)
    return {key: value.get(key) for key in allowed}


@dataclass(frozen=True)
class AgentVisibleTask:
    """Task data that may cross the Agent boundary."""

    task_id: str
    repository: str
    commit: str
    description: str
    visible_test_command: str
    environment_metadata: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_task(cls, task: TaskArtifact) -> "AgentVisibleTask":
        return cls(
            task_id=task.task_id,
            repository=task.repository,
            commit=task.commit,
            description=task.description,
            visible_test_command=task.visible_test_command or task.test_command,
            environment_metadata=(
                {"environment_identity": task.environment_identity}
                if task.environment_identity is not None
                else {}
            ),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "repository": self.repository,
            "commit": self.commit,
            "description": self.description,
            "visible_test_command": self.visible_test_command,
            "environment_metadata": dict(self.environment_metadata),
        }


@dataclass(frozen=True)
class OracleArtifact:
    """Evaluator-only data that must not cross the Agent boundary."""

    task_id: str
    target_command: str | None
    regression_command: str | None
    evaluator_config: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_task(cls, task: TaskArtifact) -> "OracleArtifact":
        return cls(
            task_id=task.task_id,
            target_command=task.oracle_target_command,
            regression_command=task.oracle_regression_command,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "target_command": self.target_command,
            "regression_command": self.regression_command,
            "evaluator_config": dict(self.evaluator_config),
        }


@dataclass(frozen=True)
class ExperimentRun:
    """Identity and frozen execution metadata for one condition run."""

    run_id: str
    experiment_id: str
    task_id: str
    condition: Condition
    model: str
    harness_version: str
    skill_version: str | None
    tool_manifest: Mapping[str, Any]
    environment_hash: str
    timestamp: str
    skill_identity: str | None = None
    skill_manifest_hash: str | None = None
    skill_payload_hash: str | None = None
    oracle_version: str = "unconfigured"
    execution_budget: Mapping[str, Any] = field(default_factory=dict)
    execution_policy: Mapping[str, Any] = field(
        default_factory=lambda: ExecutionPolicy().as_dict()
    )
    model_config: Mapping[str, Any] = field(default_factory=dict)
    evaluator_config: Mapping[str, Any] = field(default_factory=dict)
    trace_instrumentation: str = TRACE_INSTRUMENTATION_ID
    artifact_verification: Mapping[str, Any] = field(
        default_factory=lambda: dict(DEFAULT_CONTROL_ARTIFACT_VERIFICATION)
    )
    observed_model_identity: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        normalized_policy = ExecutionPolicy.from_value(self.execution_policy).as_dict()
        object.__setattr__(self, "execution_policy", normalized_policy)
        validate_experiment_run(self.as_dict())

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ExperimentRun":
        validate_experiment_run(value)
        condition = Condition.from_value(value["condition"])
        return cls(
            run_id=value["run_id"],
            experiment_id=value["experiment_id"],
            task_id=value["task_id"],
            condition=condition,
            model=value["model"],
            harness_version=value["harness_version"],
            skill_version=value["skill_version"],
            tool_manifest=dict(value["tool_manifest"]),
            environment_hash=value["environment_hash"],
            timestamp=value["timestamp"],
            skill_identity=value.get("skill_identity"),
            skill_manifest_hash=value.get("skill_manifest_hash"),
            skill_payload_hash=value.get("skill_payload_hash"),
            oracle_version=value.get("oracle_version", "unconfigured"),
            execution_budget=dict(value.get("execution_budget", {})),
            execution_policy=dict(
                value.get("execution_policy", ExecutionPolicy().as_dict())
            ),
            model_config=dict(value.get("model_config", {})),
            evaluator_config=dict(value.get("evaluator_config", {})),
            trace_instrumentation=value.get(
                "trace_instrumentation", TRACE_INSTRUMENTATION_ID
            ),
            artifact_verification=dict(
                value.get(
                    "artifact_verification",
                    DEFAULT_CONTROL_ARTIFACT_VERIFICATION,
                )
            ),
            observed_model_identity=dict(value.get("observed_model_identity", {})),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": EXPERIMENT_RUN_SCHEMA,
            "run_id": self.run_id,
            "experiment_id": self.experiment_id,
            "task_id": self.task_id,
            "condition": self.condition.as_dict(),
            "model": self.model,
            "harness_version": self.harness_version,
            "skill_version": self.skill_version,
            "tool_manifest": dict(self.tool_manifest),
            "environment_hash": self.environment_hash,
            "timestamp": self.timestamp,
            "skill_identity": self.skill_identity,
            "skill_manifest_hash": self.skill_manifest_hash,
            "skill_payload_hash": self.skill_payload_hash,
            "oracle_version": self.oracle_version,
            "execution_budget": dict(self.execution_budget),
            "execution_policy": dict(self.execution_policy),
            "model_config": dict(self.model_config),
            "evaluator_config": dict(self.evaluator_config),
            "trace_instrumentation": self.trace_instrumentation,
            "artifact_verification": dict(self.artifact_verification),
            "observed_model_identity": dict(self.observed_model_identity),
        }


def validate_experiment_run(value: Any) -> dict[str, Any]:
    if not _is_mapping(value):
        raise ExperimentSchemaError("ExperimentRun", ["run must be an object"])
    errors: list[str] = []
    allowed = {
        "schema_version",
        "run_id",
        "experiment_id",
        "task_id",
        "condition",
        "model",
        "harness_version",
        "skill_version",
        "tool_manifest",
        "environment_hash",
        "timestamp",
        "skill_identity",
        "skill_manifest_hash",
        "skill_payload_hash",
        "oracle_version",
        "execution_budget",
        "execution_policy",
        "model_config",
        "evaluator_config",
        "trace_instrumentation",
        "artifact_verification",
        "observed_model_identity",
    }
    _unexpected(value, allowed, errors)
    if value.get("schema_version") != EXPERIMENT_RUN_SCHEMA:
        errors.append(f"schema_version must be {EXPERIMENT_RUN_SCHEMA}")
    for key in (
        "run_id",
        "experiment_id",
        "task_id",
        "model",
        "harness_version",
        "environment_hash",
        "timestamp",
    ):
        _required_string(value, key, errors)
    if not _is_mapping(value.get("condition")):
        errors.append("condition must be an object")
    if not _is_mapping(value.get("tool_manifest")):
        errors.append("tool_manifest must be an object")
    if not _is_mapping(value.get("execution_budget", {})):
        errors.append("execution_budget must be an object")
    if not _is_mapping(value.get("execution_policy", {})):
        errors.append("execution_policy must be an object")
    if not _is_mapping(value.get("model_config", {})):
        errors.append("model_config must be an object")
    if not _is_mapping(value.get("evaluator_config", {})):
        errors.append("evaluator_config must be an object")
    if not isinstance(
        value.get("trace_instrumentation", TRACE_INSTRUMENTATION_ID), str
    ) or not value.get("trace_instrumentation", TRACE_INSTRUMENTATION_ID).strip():
        errors.append("trace_instrumentation must be a non-empty string")
    if not _is_mapping(
        value.get("artifact_verification", DEFAULT_CONTROL_ARTIFACT_VERIFICATION)
    ):
        errors.append("artifact_verification must be an object")
    if not _is_mapping(value.get("observed_model_identity", {})):
        errors.append("observed_model_identity must be an object")
    skill_version = value.get("skill_version")
    if skill_version is not None and (
        not isinstance(skill_version, str) or skill_version not in SUPPORTED_SKILLS
    ):
        errors.append(f"skill_version must be null or one of {sorted(SUPPORTED_SKILLS)}")
    skill_payload_hash = value.get("skill_payload_hash")
    if skill_payload_hash is not None and (
        not isinstance(skill_payload_hash, str) or not skill_payload_hash.strip()
    ):
        errors.append("skill_payload_hash must be null or a non-empty string")
    skill_identity = value.get("skill_identity")
    if skill_identity is not None and (
        not isinstance(skill_identity, str) or not skill_identity.strip()
    ):
        errors.append("skill_identity must be null or a non-empty string")
    skill_manifest_hash = value.get("skill_manifest_hash")
    if skill_manifest_hash is not None and (
        not isinstance(skill_manifest_hash, str) or not skill_manifest_hash.strip()
    ):
        errors.append("skill_manifest_hash must be null or a non-empty string")
    oracle_version = value.get("oracle_version", "unconfigured")
    if not isinstance(oracle_version, str) or not oracle_version.strip():
        errors.append("oracle_version must be a non-empty string")
    if _is_mapping(value.get("condition")):
        try:
            condition = Condition.from_value(value["condition"])
            if skill_version != condition.skill:
                errors.append("skill_version must match condition.skill")
        except ExperimentSchemaError as error:
            errors.extend(error.errors)
    if errors:
        raise ExperimentSchemaError("ExperimentRun", errors)
    try:
        ExecutionPolicy.from_value(value.get("execution_policy", {}))
    except (ExperimentSchemaError, ValueError) as error:
        errors.extend(
            getattr(error, "errors", [str(error)])
        )
    artifact_verification = value.get(
        "artifact_verification", DEFAULT_CONTROL_ARTIFACT_VERIFICATION
    )
    if _is_mapping(artifact_verification):
        mode = artifact_verification.get("mode")
        if mode not in ARTIFACT_VERIFICATION_MODES:
            errors.append("artifact_verification.mode is unsupported")
        if not isinstance(artifact_verification.get("verified"), bool):
            errors.append("artifact_verification.verified must be boolean")
        for key in ("expected_manifest_sha256", "actual_manifest_sha256"):
            hash_value = artifact_verification.get(key)
            if hash_value is not None and (
                not isinstance(hash_value, str) or not hash_value.strip()
            ):
                errors.append(
                    f"artifact_verification.{key} must be null or a non-empty string"
                )
    if errors:
        raise ExperimentSchemaError("ExperimentRun", errors)
    _assert_observable_payload(value["tool_manifest"], "tool_manifest")
    _assert_observable_payload(value.get("execution_budget", {}), "execution_budget")
    _assert_observable_payload(
        value.get("execution_policy", {}), "execution_policy"
    )
    _assert_observable_payload(value.get("model_config", {}), "model_config")
    _assert_observable_payload(
        value.get("evaluator_config", {}), "evaluator_config"
    )
    _assert_observable_payload(
        value.get("artifact_verification", DEFAULT_CONTROL_ARTIFACT_VERIFICATION),
        "artifact_verification",
    )
    _assert_observable_payload(
        value.get("observed_model_identity", {}),
        "observed_model_identity",
    )
    _assert_json_serializable(value["tool_manifest"], "ExperimentRun")
    _assert_json_serializable(value.get("execution_budget", {}), "ExperimentRun")
    _assert_json_serializable(value.get("execution_policy", {}), "ExperimentRun")
    _assert_json_serializable(value.get("model_config", {}), "ExperimentRun")
    _assert_json_serializable(value.get("evaluator_config", {}), "ExperimentRun")
    _assert_json_serializable(
        value.get("artifact_verification", DEFAULT_CONTROL_ARTIFACT_VERIFICATION),
        "ExperimentRun",
    )
    _assert_json_serializable(
        value.get("observed_model_identity", {}),
        "ExperimentRun",
    )
    return dict(value)


@dataclass(frozen=True)
class TraceEvent:
    """One observable event; private reasoning is outside this schema."""

    run_id: str
    event: str
    details: Mapping[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=_now)
    schema_version: str = TRACE_EVENT_SCHEMA

    def __post_init__(self) -> None:
        validate_trace_event(self.as_dict())

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "event": self.event,
            "details": dict(self.details),
        }


def validate_trace_event(value: Any) -> dict[str, Any]:
    if not _is_mapping(value):
        raise ExperimentSchemaError("TraceEvent", ["event must be an object"])
    errors: list[str] = []
    allowed = {"schema_version", "run_id", "timestamp", "event", "details"}
    _unexpected(value, allowed, errors)
    if value.get("schema_version") != TRACE_EVENT_SCHEMA:
        errors.append(f"schema_version must be {TRACE_EVENT_SCHEMA}")
    for key in ("run_id", "timestamp", "event"):
        _required_string(value, key, errors)
    if value.get("event") not in SUPPORTED_TRACE_EVENTS:
        errors.append(f"event must be one of {sorted(SUPPORTED_TRACE_EVENTS)}")
    if not _is_mapping(value.get("details")):
        errors.append("details must be an object")
    if errors:
        raise ExperimentSchemaError("TraceEvent", errors)
    _assert_observable_payload(value["details"], "details")
    _assert_json_serializable(value["details"], "TraceEvent")
    return dict(value)


class TraceRecorder:
    """Append-only JSONL writer for the observable experiment trace."""

    def __init__(self, path: str | Path, run_id: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id
        self._events: list[TraceEvent] = []

    @property
    def events(self) -> tuple[TraceEvent, ...]:
        return tuple(self._events)

    def emit(self, event: str, details: Mapping[str, Any] | None = None) -> TraceEvent:
        record = TraceEvent(
            run_id=self.run_id,
            event=event,
            details=dict(details or {}),
        )
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.as_dict(), ensure_ascii=False, sort_keys=True) + "\n")
        self._events.append(record)
        return record


@dataclass(frozen=True)
class AgentResult:
    """Visible agent result plus process counters supplied by the adapter."""

    result: Any
    steps: int
    tokens: int | None = None
    latency_ms: float | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.steps, int) or self.steps < 0:
            raise ValueError("steps must be a non-negative integer")
        if self.tokens is not None and (not isinstance(self.tokens, int) or self.tokens < 0):
            raise ValueError("tokens must be null or a non-negative integer")
        if self.latency_ms is not None and (
            not isinstance(self.latency_ms, (int, float)) or self.latency_ms < 0
        ):
            raise ValueError("latency_ms must be null or non-negative")
        _assert_observable_payload(self.result, "agent_result.result")
        _assert_json_serializable(self.result, "AgentResult")

    def as_dict(self) -> dict[str, Any]:
        return {
            "result": self.result,
            "steps": self.steps,
            "tokens": self.tokens,
            "latency_ms": self.latency_ms,
        }


@dataclass(frozen=True)
class OracleResult:
    """Result of the injected task oracle; no final benchmark is assumed."""

    success: bool | None
    regression: bool | None
    diagnostics: list[str]
    tests_passed: int | None = None
    target_status: str | None = None
    regression_status: str | None = None
    evaluator_valid: bool | None = None
    evaluation_environment: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.success is not None and not isinstance(self.success, bool):
            raise ValueError("success must be true, false, or null")
        if self.regression is not None and not isinstance(self.regression, bool):
            raise ValueError("regression must be true, false, or null")
        if not isinstance(self.diagnostics, list) or any(
            not isinstance(item, str) or not item.strip() for item in self.diagnostics
        ):
            raise ValueError("diagnostics must be a list of non-empty strings")
        if self.tests_passed is not None and (
            not isinstance(self.tests_passed, int) or self.tests_passed < 0
        ):
            raise ValueError("tests_passed must be null or a non-negative integer")
        target_status = self.target_status
        if target_status is None:
            target_status = (
                "pass" if self.success is True else
                "fail" if self.success is False else
                "unknown"
            )
            object.__setattr__(self, "target_status", target_status)
        if target_status not in {"pass", "fail", "unknown"}:
            raise ValueError("target_status must be pass, fail, or unknown")
        regression_status = self.regression_status
        if regression_status is None:
            regression_status = (
                "fail" if self.regression is True else
                "pass" if self.regression is False else
                "unknown"
            )
            object.__setattr__(self, "regression_status", regression_status)
        if regression_status not in {"pass", "fail", "unknown"}:
            raise ValueError("regression_status must be pass, fail, or unknown")
        if self.evaluator_valid is not None and not isinstance(
            self.evaluator_valid, bool
        ):
            raise ValueError("evaluator_valid must be true, false, or null")
        if not _is_mapping(self.evaluation_environment):
            raise ValueError("evaluation_environment must be an object")
        _assert_observable_payload(
            self.evaluation_environment, "evaluation_environment"
        )
        _assert_json_serializable(self.evaluation_environment, "OracleResult")

    @classmethod
    def from_value(cls, value: Any) -> "OracleResult":
        if isinstance(value, cls):
            return value
        if not _is_mapping(value):
            raise ExperimentSchemaError("OracleResult", ["oracle result must be an object"])
        validate_oracle_result(value)
        return cls(
            success=value["success"],
            regression=value["regression"],
            diagnostics=list(value["diagnostics"]),
            tests_passed=value.get("tests_passed"),
            target_status=value.get("target_status"),
            regression_status=value.get("regression_status"),
            evaluator_valid=value.get("evaluator_valid"),
            evaluation_environment=dict(value.get("evaluation_environment", {})),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "regression": self.regression,
            "diagnostics": list(self.diagnostics),
            "tests_passed": self.tests_passed,
            "target_status": self.target_status,
            "regression_status": self.regression_status,
            "evaluator_valid": self.evaluator_valid,
            "evaluation_environment": dict(self.evaluation_environment),
        }


def validate_oracle_result(value: Any) -> dict[str, Any]:
    if not _is_mapping(value):
        raise ExperimentSchemaError("OracleResult", ["oracle result must be an object"])
    errors: list[str] = []
    allowed = {
        "success",
        "regression",
        "diagnostics",
        "tests_passed",
        "target_status",
        "regression_status",
        "evaluator_valid",
        "evaluation_environment",
    }
    _unexpected(value, allowed, errors)
    if not isinstance(value.get("success"), (bool, type(None))):
        errors.append("success must be true, false, or null")
    if not isinstance(value.get("regression"), (bool, type(None))):
        errors.append("regression must be true, false, or null")
    diagnostics = value.get("diagnostics")
    if not isinstance(diagnostics, list) or any(
        not isinstance(item, str) or not item.strip() for item in diagnostics
    ):
        errors.append("diagnostics must be a list of non-empty strings")
    tests_passed = value.get("tests_passed")
    if tests_passed is not None and (
        not isinstance(tests_passed, int) or tests_passed < 0
    ):
        errors.append("tests_passed must be null or a non-negative integer")
    for key in ("target_status", "regression_status"):
        status = value.get(key)
        if status is not None and status not in {"pass", "fail", "unknown"}:
            errors.append(f"{key} must be pass, fail, or unknown")
    evaluator_valid = value.get("evaluator_valid")
    if evaluator_valid is not None and not isinstance(evaluator_valid, bool):
        errors.append("evaluator_valid must be true, false, or null")
    if not _is_mapping(value.get("evaluation_environment", {})):
        errors.append("evaluation_environment must be an object")
    if errors:
        raise ExperimentSchemaError("OracleResult", errors)
    _assert_observable_payload(
        value.get("evaluation_environment", {}), "evaluation_environment"
    )
    _assert_json_serializable(
        value.get("evaluation_environment", {}), "OracleResult"
    )
    return dict(value)


@dataclass(frozen=True)
class OutcomeEvidence:
    status: str
    success: bool | None
    regression: bool | None
    tests_passed: int | None
    diagnostics: list[str]
    target_status: str
    regression_status: str
    evaluator_valid: bool | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "success": self.success,
            "regression": self.regression,
            "tests_passed": self.tests_passed,
            "diagnostics": list(self.diagnostics),
            "target_status": self.target_status,
            "regression_status": self.regression_status,
            "evaluator_valid": self.evaluator_valid,
        }


@dataclass(frozen=True)
class TrajectoryEvidence:
    steps: int
    tool_calls: int
    verification_count: int
    failure_categories: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "steps": self.steps,
            "tool_calls": self.tool_calls,
            "verification_count": self.verification_count,
            "failure_categories": list(self.failure_categories),
        }


@dataclass(frozen=True)
class CostEvidence:
    tokens: int | None
    latency_ms: float | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "tokens": self.tokens,
            "latency_ms": self.latency_ms,
        }


@dataclass(frozen=True)
class UtilityEvidence:
    """Multidimensional evidence; intentionally contains no utility score."""

    run_id: str
    experiment_id: str
    task_id: str
    condition: Condition
    outcome: OutcomeEvidence
    trajectory: TrajectoryEvidence
    cost: CostEvidence
    evidence_validity: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": EVIDENCE_SCHEMA,
            "run_id": self.run_id,
            "experiment_id": self.experiment_id,
            "task_id": self.task_id,
            "condition": self.condition.as_dict(),
            "outcome": self.outcome.as_dict(),
            "trajectory": self.trajectory.as_dict(),
            "cost": self.cost.as_dict(),
            "evidence_validity": self.evidence_validity,
        }


def validate_utility_evidence(value: Any) -> dict[str, Any]:
    if not _is_mapping(value):
        raise ExperimentSchemaError("UtilityEvidence", ["evidence must be an object"])
    errors: list[str] = []
    allowed = {
        "schema_version",
        "run_id",
        "experiment_id",
        "task_id",
        "condition",
        "outcome",
        "trajectory",
        "cost",
        "evidence_validity",
    }
    _unexpected(value, allowed, errors)
    if value.get("schema_version") != EVIDENCE_SCHEMA:
        errors.append(f"schema_version must be {EVIDENCE_SCHEMA}")
    for key in ("run_id", "experiment_id", "task_id"):
        _required_string(value, key, errors)
    if not _is_mapping(value.get("condition")):
        errors.append("condition must be an object")
    else:
        try:
            Condition.from_value(value["condition"])
        except ExperimentSchemaError as error:
            errors.extend(error.errors)
    for section in ("outcome", "trajectory", "cost"):
        if not _is_mapping(value.get(section)):
            errors.append(f"{section} must be an object")
    if value.get("evidence_validity") not in EVIDENCE_VALIDITIES:
        errors.append(
            f"evidence_validity must be one of {sorted(EVIDENCE_VALIDITIES)}"
        )
    outcome = value.get("outcome")
    if _is_mapping(outcome):
        if outcome.get("status") not in {
            "success",
            "failure",
            "unknown",
            "protocol_failure",
        }:
            errors.append("outcome.status is unsupported")
        for key in ("target_status", "regression_status"):
            if outcome.get(key) not in {"pass", "fail", "unknown"}:
                errors.append(f"outcome.{key} must be pass, fail, or unknown")
        if not isinstance(outcome.get("evaluator_valid"), (bool, type(None))):
            errors.append("outcome.evaluator_valid must be true, false, or null")
    if value.get("evidence_validity") == "VALID" and (
        not _is_mapping(outcome) or outcome.get("evaluator_valid") is not True
    ):
        errors.append("VALID evidence requires evaluator_valid=true")
    if value.get("evidence_validity") == "PROTOCOL_FAILURE" and (
        not _is_mapping(outcome)
        or outcome.get("evaluator_valid") is not False
        or outcome.get("status") != "protocol_failure"
    ):
        errors.append(
            "PROTOCOL_FAILURE evidence requires evaluator_valid=false and "
            "protocol_failure outcome"
        )
    if value.get("evidence_validity") == "INCONCLUSIVE" and (
        not _is_mapping(outcome) or outcome.get("status") != "unknown"
    ):
        errors.append("INCONCLUSIVE evidence requires unknown outcome")
    if errors:
        raise ExperimentSchemaError("UtilityEvidence", errors)
    return dict(value)


class Agent(Protocol):
    """Legacy runner seam; use AgentAdapter for real execution metadata."""

    def run(
        self,
        task: AgentVisibleTask,
        condition: Condition,
        trace: TraceRecorder,
    ) -> AgentResult:
        """Execute one task and emit only observable events."""


class ExecutionAgent(Protocol):
    """Underlying agent callback that receives only visible execution context."""

    def run(
        self,
        task: AgentVisibleTask,
        context: AgentExecutionContext,
        trace: TraceRecorder,
    ) -> AgentResult:
        """Execute one task without access to Oracle-only information."""


@runtime_checkable
class AgentAdapter(Protocol):
    """Minimal SkillNudge-to-Agent execution boundary."""

    model: str
    harness_version: str
    tool_manifest: Mapping[str, Any]
    execution_budget: ExecutionBudget
    environment_hash: str
    execution_policy: ExecutionPolicy
    model_config: Mapping[str, Any]

    def exposure_for(self, condition: Condition) -> SkillExposure:
        """Return the deterministic Skill exposure for a condition."""

    def run(
        self,
        task: AgentVisibleTask,
        condition: Condition,
        trace: TraceRecorder,
    ) -> AgentResult:
        """Construct visible context and execute the underlying Agent."""


@dataclass
class FixtureAgentAdapter:
    """Concrete adapter used by tests and the local fixture experiment."""

    execution_agent: ExecutionAgent
    renderer: SkillExposureRenderer
    model: str
    harness_version: str
    tool_manifest: Mapping[str, Any]
    execution_budget: ExecutionBudget
    environment_hash: str
    execution_policy: ExecutionPolicy = field(default_factory=ExecutionPolicy)
    model_config: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.model.strip():
            raise ValueError("model must be a non-empty string")
        if not self.harness_version.strip():
            raise ValueError("harness_version must be a non-empty string")
        if not self.environment_hash.strip():
            raise ValueError("environment_hash must be a non-empty string")
        if not isinstance(self.execution_budget, ExecutionBudget):
            self.execution_budget = ExecutionBudget(**dict(self.execution_budget))
        if not isinstance(self.execution_policy, ExecutionPolicy):
            self.execution_policy = ExecutionPolicy.from_value(self.execution_policy)
        _assert_observable_payload(self.tool_manifest, "tool_manifest")
        _assert_json_serializable(self.tool_manifest, "AgentAdapter")
        _assert_observable_payload(self.model_config, "model_config")
        _assert_json_serializable(self.model_config, "AgentAdapter")

    def exposure_for(self, condition: Condition) -> SkillExposure:
        return self.renderer.render(condition)

    def context_for(self, condition: Condition) -> AgentExecutionContext:
        exposure = self.exposure_for(condition)
        return AgentExecutionContext(
            condition=Condition.from_value(condition),
            visible_context=exposure.visible_context,
            skill_identity=exposure.skill_identity,
            skill_version=exposure.skill_version,
            skill_manifest_hash=exposure.manifest_hash,
            skill_payload_hash=exposure.payload_hash,
            model=self.model,
            harness_version=self.harness_version,
            tool_manifest=dict(self.tool_manifest),
            execution_budget=self.execution_budget.as_dict(),
            environment_hash=self.environment_hash,
            execution_policy=self.execution_policy.as_dict(),
        )

    def run(
        self,
        task: TaskArtifact,
        condition: Condition,
        trace: TraceRecorder,
    ) -> AgentResult:
        context = self.context_for(condition)
        return self.execution_agent.run(task, context, trace)


class Oracle(Protocol):
    """Task oracle boundary; the final benchmark implementation is deferred."""

    oracle_version: str

    def evaluate(self, task: OracleArtifact, result: Any) -> OracleResult:
        """Return success, regression, diagnostics, and optional test counts."""


OracleAdapter = Oracle


@dataclass(frozen=True)
class ExperimentResult:
    run: ExperimentRun
    agent_result: AgentResult
    oracle_result: OracleResult
    evidence: UtilityEvidence
    run_dir: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "run": self.run.as_dict(),
            "agent_result": self.agent_result.as_dict(),
            "oracle_result": self.oracle_result.as_dict(),
            "evidence": self.evidence.as_dict(),
            "run_dir": self.run_dir,
        }


class ExperimentRunner:
    """Run one condition and persist its observable artifacts."""

    def __init__(self, agent: Agent, oracle: Oracle, *, clock: Callable[[], str] = _now):
        self.agent = agent
        self.oracle = oracle
        self.clock = clock

    def run(
        self,
        task: TaskArtifact | Mapping[str, Any],
        *,
        experiment_id: str,
        condition: Condition | Mapping[str, Any],
        model: str | None = None,
        harness_version: str | None = None,
        skill_version: str | None = None,
        skill_payload_hash: str | None = None,
        tool_manifest: Mapping[str, Any] | None = None,
        execution_budget: ExecutionBudget | Mapping[str, Any] | None = None,
        environment_hash: str | None = None,
        execution_policy: ExecutionPolicy | Mapping[str, Any] | None = None,
        model_config: Mapping[str, Any] | None = None,
        oracle_version: str | None = None,
        evaluator_config: Mapping[str, Any] | None = None,
        run_dir: str | Path,
        run_id: str | None = None,
    ) -> ExperimentResult:
        task_artifact = (
            task if isinstance(task, TaskArtifact) else TaskArtifact.from_dict(task)
        )
        visible_task = AgentVisibleTask.from_task(task_artifact)
        oracle_artifact = OracleArtifact.from_task(task_artifact)
        condition_artifact = Condition.from_value(condition)
        adapter_metadata: AgentAdapter | None = None
        exposure: SkillExposure | None = None
        if isinstance(self.agent, AgentAdapter):
            adapter_metadata = self.agent
            exposure = adapter_metadata.exposure_for(condition_artifact)
            effective_budget = adapter_metadata.execution_budget.as_dict()
            effective_policy = _as_execution_policy_dict(
                adapter_metadata.execution_policy
            )
            effective_model_config = dict(
                getattr(adapter_metadata, "model_config", {}) or {}
            )
            if model is not None and model != adapter_metadata.model:
                raise ExperimentRunError(
                    "model must match AgentAdapter effective configuration"
                )
            if (
                harness_version is not None
                and harness_version != adapter_metadata.harness_version
            ):
                raise ExperimentRunError(
                    "harness_version must match AgentAdapter effective configuration"
                )
            if (
                tool_manifest is not None
                and dict(tool_manifest) != dict(adapter_metadata.tool_manifest)
            ):
                raise ExperimentRunError(
                    "tool_manifest must match AgentAdapter effective configuration"
                )
            if (
                environment_hash is not None
                and environment_hash != adapter_metadata.environment_hash
            ):
                raise ExperimentRunError(
                    "environment_hash must match AgentAdapter effective configuration"
                )
            if (
                execution_budget is not None
                and _as_execution_budget_dict(execution_budget) != effective_budget
            ):
                raise ExperimentRunError(
                    "execution_budget must match AgentAdapter effective configuration"
                )
            if (
                execution_policy is not None
                and _as_execution_policy_dict(execution_policy) != effective_policy
            ):
                raise ExperimentRunError(
                    "execution_policy must match AgentAdapter effective configuration"
                )
            if (
                model_config is not None
                and dict(model_config) != effective_model_config
            ):
                raise ExperimentRunError(
                    "model_config must match AgentAdapter effective configuration"
                )
            model = adapter_metadata.model
            harness_version = adapter_metadata.harness_version
            tool_manifest = dict(adapter_metadata.tool_manifest)
            environment_hash = adapter_metadata.environment_hash
            execution_budget = effective_budget
            execution_policy = effective_policy
            model_config = effective_model_config
            if skill_payload_hash is None:
                skill_payload_hash = exposure.payload_hash
        if condition_artifact.skill is not None and exposure is None:
            raise ExperimentRunError(
                "FROZEN_SKILL_PAYLOAD_REQUIRED: treatment requires an AgentAdapter "
                "with a static Skill exposure"
            )
        if exposure is not None:
            if (
                skill_payload_hash is not None
                and skill_payload_hash != exposure.payload_hash
            ):
                raise ExperimentRunError(
                    "skill_payload_hash must match the rendered Skill exposure"
                )
            skill_payload_hash = exposure.payload_hash
        model = model or "unconfigured"
        harness_version = harness_version or "unconfigured"
        environment_hash = environment_hash or "unconfigured"
        if tool_manifest is None:
            tool_manifest = {}
        execution_budget = _as_execution_budget_dict(execution_budget)
        execution_policy = _as_execution_policy_dict(execution_policy)
        model_config = dict(model_config or {})
        effective_oracle_version = getattr(
            self.oracle, "oracle_version", "unconfigured"
        )
        if oracle_version is not None and oracle_version != effective_oracle_version:
            raise ExperimentRunError(
                "oracle_version must match Oracle effective configuration"
            )
        oracle_version = effective_oracle_version
        effective_evaluator_config = dict(
            getattr(self.oracle, "evaluator_config", {}) or {}
        )
        if evaluator_config is not None and dict(evaluator_config) != effective_evaluator_config:
            raise ExperimentRunError(
                "evaluator_config must match Oracle effective configuration"
            )
        evaluator_config = effective_evaluator_config
        if skill_version is not None and skill_version != condition_artifact.skill:
            raise ExperimentRunError("skill_version must match condition.skill")
        if skill_version is None:
            skill_version = condition_artifact.skill

        output_dir = Path(run_dir)
        if output_dir.exists() and any(output_dir.iterdir()):
            raise ExperimentRunError(
                "EXPERIMENT_RUN_DIR_EXISTS: choose an empty run directory"
            )
        output_dir.mkdir(parents=True, exist_ok=True)
        resolved_run_id = run_id or output_dir.name or uuid.uuid4().hex
        run = ExperimentRun(
            run_id=resolved_run_id,
            experiment_id=experiment_id,
            task_id=task_artifact.task_id,
            condition=condition_artifact,
            model=model,
            harness_version=harness_version,
            skill_version=skill_version,
            tool_manifest=dict(tool_manifest or {}),
            environment_hash=environment_hash,
            timestamp=self.clock(),
            skill_identity=exposure.skill_identity if exposure is not None else None,
            skill_manifest_hash=exposure.manifest_hash if exposure is not None else None,
            skill_payload_hash=skill_payload_hash,
            oracle_version=oracle_version,
            execution_budget=dict(execution_budget),
            execution_policy=dict(execution_policy),
            model_config=dict(model_config),
            evaluator_config=dict(evaluator_config),
            trace_instrumentation=TRACE_INSTRUMENTATION_ID,
            artifact_verification=(
                dict(exposure.artifact_verification)
                if exposure is not None
                else dict(DEFAULT_CONTROL_ARTIFACT_VERIFICATION)
            ),
            observed_model_identity=unknown_observed_model_identity(model),
        )
        _write_json(output_dir / "experiment_run.json", run.as_dict())
        _write_json(output_dir / "run_manifest.json", run.as_dict())
        _write_json(output_dir / "task.json", visible_task.as_dict())

        trace = TraceRecorder(output_dir / "trace.jsonl", run.run_id)
        started = time.perf_counter()
        try:
            trace.emit(
                "agent_start",
                {
                    "condition": condition_artifact.as_dict(),
                    "condition_name": condition_artifact.name,
                    "task_id": task_artifact.task_id,
                    "model": run.model,
                    "harness_version": run.harness_version,
                    "skill_identity": run.skill_identity,
                    "skill_manifest_hash": run.skill_manifest_hash,
                    "skill_payload_hash": run.skill_payload_hash,
                    "execution_budget": dict(run.execution_budget),
                    "execution_policy": dict(run.execution_policy),
                    "model_config": dict(run.model_config),
                    "artifact_verification": dict(run.artifact_verification),
                    "trace_instrumentation": run.trace_instrumentation,
                },
            )
            agent_result = self.agent.run(visible_task, condition_artifact, trace)
            if not isinstance(agent_result, AgentResult):
                raise ExperimentRunError("agent must return AgentResult")
            run = replace(
                run,
                observed_model_identity=observed_model_identity_from_result(
                    agent_result.result,
                    run.model,
                ),
            )
            _write_json(output_dir / "experiment_run.json", run.as_dict())
            _write_json(output_dir / "run_manifest.json", run.as_dict())
            oracle_result = OracleResult.from_value(
                self.oracle.evaluate(oracle_artifact, agent_result.result)
            )
            trace.emit(
                "oracle_evaluation",
                {
                    "source": "oracle",
                    "success": oracle_result.success,
                    "regression": oracle_result.regression,
                    "target_status": oracle_result.target_status,
                    "regression_status": oracle_result.regression_status,
                    "evaluator_valid": oracle_result.evaluator_valid,
                    "tests_passed": oracle_result.tests_passed,
                    "evaluation_environment": dict(
                        oracle_result.evaluation_environment
                    ),
                },
            )
            evidence = self._build_evidence(
                run,
                agent_result,
                oracle_result,
                trace.events,
                measured_latency_ms=(time.perf_counter() - started) * 1000,
            )
            trace.emit("completion", {"outcome_status": evidence.outcome.status})
            _write_json(output_dir / "agent_result.json", agent_result.as_dict())
            _write_json(output_dir / "oracle_result.json", oracle_result.as_dict())
            _write_json(output_dir / "utility_evidence.json", evidence.as_dict())
            return ExperimentResult(
                run=run,
                agent_result=agent_result,
                oracle_result=oracle_result,
                evidence=evidence,
                run_dir=str(output_dir),
            )
        except Exception as error:
            try:
                trace.emit(
                    "failure",
                    {
                        "category": "runner",
                        "error_type": type(error).__name__,
                    },
                )
            except Exception:
                pass
            raise

    @staticmethod
    def _build_evidence(
        run: ExperimentRun,
        agent_result: AgentResult,
        oracle_result: OracleResult,
        events: Sequence[TraceEvent],
        *,
        measured_latency_ms: float,
    ) -> UtilityEvidence:
        if oracle_result.evaluator_valid is False:
            evidence_validity = "PROTOCOL_FAILURE"
            status = "protocol_failure"
        elif oracle_result.evaluator_valid is None:
            evidence_validity = "INCONCLUSIVE"
            status = "unknown"
        elif oracle_result.success is True and oracle_result.regression is False:
            evidence_validity = "VALID"
            status = "success"
        elif oracle_result.success is False or oracle_result.regression is True:
            evidence_validity = "VALID"
            status = "failure"
        else:
            evidence_validity = "INCONCLUSIVE"
            status = "unknown"
        failure_categories: list[str] = []
        for event in events:
            if event.event != "failure":
                continue
            category = event.details.get("category", "unspecified")
            if isinstance(category, str) and category not in failure_categories:
                failure_categories.append(category)
        latency_ms = (
            agent_result.latency_ms
            if agent_result.latency_ms is not None
            else measured_latency_ms
        )
        return UtilityEvidence(
            run_id=run.run_id,
            experiment_id=run.experiment_id,
            task_id=run.task_id,
            condition=run.condition,
            outcome=OutcomeEvidence(
                status=status,
                success=oracle_result.success,
                regression=oracle_result.regression,
                tests_passed=oracle_result.tests_passed,
                diagnostics=list(oracle_result.diagnostics),
                target_status=oracle_result.target_status or "unknown",
                regression_status=oracle_result.regression_status or "unknown",
                evaluator_valid=oracle_result.evaluator_valid,
            ),
            trajectory=TrajectoryEvidence(
                steps=agent_result.steps,
                tool_calls=sum(event.event == "tool_call" for event in events),
                verification_count=sum(
                    event.event == "verification" for event in events
                ),
                failure_categories=failure_categories,
            ),
            cost=CostEvidence(
                tokens=agent_result.tokens,
                latency_ms=latency_ms,
            ),
            evidence_validity=evidence_validity,
        )


@dataclass(frozen=True)
class PairValidationResult:
    """Causal comparability result for exactly one Control/Treatment pair."""

    experiment_id: str
    task_id: str
    control_run_id: str
    treatment_run_id: str
    shared_configuration_identity: str
    pair_status: str
    errors: list[str] = field(default_factory=list)
    control_observed_model_identity: Mapping[str, Any] = field(default_factory=dict)
    treatment_observed_model_identity: Mapping[str, Any] = field(default_factory=dict)
    execution_evidence: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.pair_status not in PAIR_STATUSES:
            raise ValueError(f"unsupported pair status: {self.pair_status}")

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": PAIR_MANIFEST_SCHEMA,
            "experiment_id": self.experiment_id,
            "task_id": self.task_id,
            "control_run_id": self.control_run_id,
            "treatment_run_id": self.treatment_run_id,
            "shared_configuration_identity": self.shared_configuration_identity,
            "pair_status": self.pair_status,
            "errors": list(self.errors),
            "observed_model_identity": {
                "control": dict(self.control_observed_model_identity),
                "treatment": dict(self.treatment_observed_model_identity),
            },
            "execution_evidence": dict(self.execution_evidence),
            "expected_intervention_difference": {
                "control": {
                    "skill_payload": "absent",
                    "condition": {"skill": None},
                },
                "treatment": {
                    "skill_payload": "exact_declared_skill",
                    "condition": {"skill": SYSTEMATIC_DEBUGGING_SKILL},
                },
            },
        }


def validate_pair_manifest(value: Any) -> dict[str, Any]:
    """Validate the bounded pair artifact without interpreting utility."""

    if not _is_mapping(value):
        raise ExperimentSchemaError("PairManifest", ["pair manifest must be an object"])
    errors: list[str] = []
    allowed = {
        "schema_version",
        "experiment_id",
        "task_id",
        "control_run_id",
        "treatment_run_id",
        "shared_configuration_identity",
        "pair_status",
        "errors",
        "observed_model_identity",
        "expected_intervention_difference",
        "execution_evidence",
    }
    _unexpected(value, allowed, errors)
    if value.get("schema_version") != PAIR_MANIFEST_SCHEMA:
        errors.append(f"schema_version must be {PAIR_MANIFEST_SCHEMA}")
    for key in (
        "experiment_id",
        "task_id",
        "control_run_id",
        "treatment_run_id",
        "shared_configuration_identity",
    ):
        _required_string(value, key, errors)
    if value.get("pair_status") not in PAIR_STATUSES:
        errors.append(f"pair_status must be one of {sorted(PAIR_STATUSES)}")
    if not isinstance(value.get("errors"), list) or any(
        not isinstance(item, str) or not item.strip()
        for item in value.get("errors", [])
    ):
        errors.append("errors must be a list of non-empty strings")
    observed_identity = value.get("observed_model_identity")
    if not _is_mapping(observed_identity):
        errors.append("observed_model_identity must be an object")
    elif not all(
        _is_mapping(observed_identity.get(key))
        for key in ("control", "treatment")
    ):
        errors.append("observed_model_identity must contain control and treatment objects")
    if not _is_mapping(value.get("expected_intervention_difference")):
        errors.append("expected_intervention_difference must be an object")
    if not _is_mapping(value.get("execution_evidence", {})):
        errors.append("execution_evidence must be an object")
    if errors:
        raise ExperimentSchemaError("PairManifest", errors)
    _assert_observable_payload(value, "PairManifest")
    _assert_json_serializable(value, "PairManifest")
    return dict(value)


def _pair_task(value: TaskArtifact | Mapping[str, Any] | None) -> TaskArtifact | None:
    if value is None:
        return None
    if isinstance(value, TaskArtifact):
        return value
    return TaskArtifact.from_dict(value)


def _configuration_identity(
    run: ExperimentRun,
    task: TaskArtifact | None,
) -> str:
    common = {
        "experiment_id": run.experiment_id,
        "task_id": run.task_id,
        "task": task.as_dict() if task is not None else None,
        "model": run.model,
        "harness_version": run.harness_version,
        "tool_manifest": dict(run.tool_manifest),
        "environment_hash": run.environment_hash,
        "execution_budget": dict(run.execution_budget),
        "execution_policy": dict(run.execution_policy),
        "model_config": dict(run.model_config),
        "oracle_version": run.oracle_version,
        "evaluator_config": dict(run.evaluator_config),
        "trace_instrumentation": run.trace_instrumentation,
    }
    canonical = json.dumps(common, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_paired_runs(
    control: ExperimentRun | Mapping[str, Any],
    treatment: ExperimentRun | Mapping[str, Any],
    *,
    control_task: TaskArtifact | Mapping[str, Any] | None = None,
    treatment_task: TaskArtifact | Mapping[str, Any] | None = None,
    execution_evidence: Mapping[str, Any] | None = None,
) -> PairValidationResult:
    """Validate causal parity without interpreting utility."""

    control_run = (
        control if isinstance(control, ExperimentRun) else ExperimentRun.from_dict(control)
    )
    treatment_run = (
        treatment
        if isinstance(treatment, ExperimentRun)
        else ExperimentRun.from_dict(treatment)
    )
    control_task_artifact = _pair_task(control_task)
    treatment_task_artifact = _pair_task(treatment_task)
    errors: list[str] = []

    common_fields = (
        "experiment_id",
        "task_id",
        "model",
        "harness_version",
        "tool_manifest",
        "environment_hash",
        "execution_budget",
        "execution_policy",
        "model_config",
        "oracle_version",
        "evaluator_config",
        "trace_instrumentation",
    )
    for field_name in common_fields:
        control_value = getattr(control_run, field_name)
        treatment_value = getattr(treatment_run, field_name)
        if isinstance(control_value, Mapping):
            control_value = dict(control_value)
        if isinstance(treatment_value, Mapping):
            treatment_value = dict(treatment_value)
        if control_value != treatment_value:
            errors.append(f"{field_name} mismatch")

    control_observed = dict(control_run.observed_model_identity)
    treatment_observed = dict(treatment_run.observed_model_identity)
    if control_observed.get("identity_consistent") is False:
        errors.append("control observed model identity changed within run")
    if treatment_observed.get("identity_consistent") is False:
        errors.append("treatment observed model identity changed within run")
    control_ids = {
        value
        for value in control_observed.get("observed_model_ids", [])
        if isinstance(value, str) and value.strip()
    }
    treatment_ids = {
        value
        for value in treatment_observed.get("observed_model_ids", [])
        if isinstance(value, str) and value.strip()
    }
    if control_ids and treatment_ids and control_ids != treatment_ids:
        errors.append("observed model identity mismatch")

    if control_task_artifact is None or treatment_task_artifact is None:
        errors.append(
            "task artifact identity is required for paired validation"
        )
    elif control_task_artifact.as_dict() != treatment_task_artifact.as_dict():
        errors.append("task artifact identity mismatch")

    if control_run.condition.skill is not None:
        errors.append("control condition must have no Skill")
    if any(
        value is not None
        for value in (
            control_run.skill_version,
            control_run.skill_identity,
            control_run.skill_manifest_hash,
            control_run.skill_payload_hash,
        )
    ):
        errors.append("control Skill payload metadata must be absent")
    if dict(control_run.artifact_verification) != DEFAULT_CONTROL_ARTIFACT_VERIFICATION:
        errors.append("control artifact verification must be mode none")

    if treatment_run.condition.skill != SYSTEMATIC_DEBUGGING_SKILL:
        errors.append("treatment condition must use the declared systematic debugging Skill")
    if treatment_run.skill_version != SYSTEMATIC_DEBUGGING_SKILL:
        errors.append("treatment skill_version must identify the declared Skill")
    if treatment_run.skill_identity != FROZEN_SKILL_ARTIFACT_ID:
        errors.append("treatment skill_identity must identify the frozen artifact")
    for field_name in ("skill_manifest_hash", "skill_payload_hash"):
        if not isinstance(getattr(treatment_run, field_name), str) or not getattr(
            treatment_run, field_name
        ):
            errors.append(f"treatment {field_name} must be present")

    artifact_verification = dict(treatment_run.artifact_verification)
    artifact_mode = artifact_verification.get("mode")
    if artifact_mode not in ARTIFACT_VERIFICATION_MODES - {"none"}:
        errors.append("treatment artifact verification mode is not explicit")
    elif artifact_mode == "synthetic_fixture":
        if artifact_verification.get("verified") is not False:
            errors.append("synthetic treatment must be marked verified=false")
        if not artifact_verification.get("actual_manifest_sha256"):
            errors.append("synthetic treatment must record actual manifest hash")
    elif artifact_mode == "frozen_verified_artifact":
        if artifact_verification.get("verified") is not True:
            errors.append("frozen treatment must be marked verified=true")
        if (
            artifact_verification.get("expected_manifest_sha256")
            != FROZEN_SKILL_MANIFEST_SHA256
            or artifact_verification.get("actual_manifest_sha256")
            != FROZEN_SKILL_MANIFEST_SHA256
        ):
            errors.append("frozen treatment manifest hash is not verified")
    if (
        treatment_run.skill_manifest_hash
        != artifact_verification.get("actual_manifest_sha256")
    ):
        errors.append("treatment skill_manifest_hash must match actual manifest hash")

    if execution_evidence is not None:
        if not _is_mapping(execution_evidence):
            errors.append("execution_evidence must be an object")
        else:
            for arm in ("control", "treatment"):
                arm_evidence = execution_evidence.get(arm)
                if not _is_mapping(arm_evidence):
                    errors.append(f"{arm} execution evidence is required")
                elif arm_evidence.get("valid_for_pair") is not True:
                    arm_errors = arm_evidence.get("errors", [])
                    if isinstance(arm_errors, list) and arm_errors:
                        errors.extend(
                            f"{arm} execution evidence: {item}"
                            for item in arm_errors
                            if isinstance(item, str) and item.strip()
                        )
                    else:
                        errors.append(f"{arm} execution evidence is not valid")

    task_id = control_run.task_id
    shared_identity = _configuration_identity(control_run, control_task_artifact)
    status = "VALID" if not errors else "PROTOCOL_FAILURE"
    return PairValidationResult(
        experiment_id=control_run.experiment_id,
        task_id=task_id,
        control_run_id=control_run.run_id,
        treatment_run_id=treatment_run.run_id,
        shared_configuration_identity=shared_identity,
        pair_status=status,
        errors=errors,
        control_observed_model_identity=control_observed,
        treatment_observed_model_identity=treatment_observed,
        execution_evidence=dict(execution_evidence or {}),
    )


def inspect_real_execution_artifacts(run_dir: str | Path) -> dict[str, Any]:
    """Check that one arm contains real observable execution evidence."""

    root = Path(run_dir).resolve()
    errors: list[str] = []
    required = (
        "experiment_run.json",
        "agent_result.json",
        "oracle_result.json",
        "utility_evidence.json",
        "trace.jsonl",
    )
    loaded: dict[str, Any] = {}
    for name in required:
        path = root / name
        if not path.is_file():
            errors.append(f"missing {name}")
            continue
        try:
            if name.endswith(".jsonl"):
                loaded[name] = [
                    json.loads(line)
                    for line in path.read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ]
            else:
                loaded[name] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"invalid {name}: {type(error).__name__}")

    agent_result = loaded.get("agent_result.json")
    result = agent_result.get("result") if _is_mapping(agent_result) else None
    response_observations = (
        result.get("model_response_observations")
        if _is_mapping(result)
        else None
    )
    observable_response = isinstance(response_observations, list) and bool(
        response_observations
    )
    if not observable_response:
        errors.append("no observable host model response")
    outcome_observable = _is_mapping(result) and isinstance(
        result.get("workspace_reference"), str
    )
    if not outcome_observable:
        errors.append("repository/task outcome is not observable")

    events = loaded.get("trace.jsonl", [])
    event_names = {
        item.get("event")
        for item in events
        if _is_mapping(item)
    }
    if "agent_start" not in event_names:
        errors.append("trace is missing agent_start")
    if not event_names.intersection({"completion", "failure"}):
        errors.append("trace is missing terminal execution event")

    oracle = loaded.get("oracle_result.json")
    oracle_executed = (
        _is_mapping(oracle) and oracle.get("evaluator_valid") is True
    )
    if not oracle_executed:
        errors.append("oracle did not execute successfully")

    evidence = loaded.get("utility_evidence.json")
    if (
        _is_mapping(evidence)
        and evidence.get("evidence_validity") == "PROTOCOL_FAILURE"
    ):
        errors.append("utility evidence is protocol_failure")

    return {
        "run_dir": str(root),
        "actual_host_execution": observable_response,
        "observable_response": observable_response,
        "outcome_observable": outcome_observable,
        "oracle_executed": oracle_executed,
        "valid_for_pair": not errors,
        "errors": errors,
    }


def validate_real_paired_runs(
    control: ExperimentRun | Mapping[str, Any],
    treatment: ExperimentRun | Mapping[str, Any],
    *,
    control_task: TaskArtifact | Mapping[str, Any],
    treatment_task: TaskArtifact | Mapping[str, Any],
    control_run_dir: str | Path,
    treatment_run_dir: str | Path,
) -> PairValidationResult:
    """Validate parity and require real observable evidence for both arms."""

    execution_evidence = {
        "control": inspect_real_execution_artifacts(control_run_dir),
        "treatment": inspect_real_execution_artifacts(treatment_run_dir),
    }
    return validate_paired_runs(
        control,
        treatment,
        control_task=control_task,
        treatment_task=treatment_task,
        execution_evidence=execution_evidence,
    )


@dataclass(frozen=True)
class UtilityConclusion:
    """Conservative first-pair conclusion; no universal utility scalar."""

    conclusion: str
    scope: Mapping[str, Any]
    control_outcome: Mapping[str, Any]
    treatment_outcome: Mapping[str, Any]
    trajectory_difference: Mapping[str, Any]
    cost_difference: Mapping[str, Any]
    limitations: list[str]

    def __post_init__(self) -> None:
        if self.conclusion not in UTILITY_CONCLUSIONS:
            raise ValueError(f"unsupported utility conclusion: {self.conclusion}")

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "utility.conclusion.first-pair.v0",
            "conclusion": self.conclusion,
            "scope": dict(self.scope),
            "control_outcome": dict(self.control_outcome),
            "treatment_outcome": dict(self.treatment_outcome),
            "trajectory_difference": dict(self.trajectory_difference),
            "cost_difference": dict(self.cost_difference),
            "limitations": list(self.limitations),
        }


def conclude_first_pair(
    pair: PairValidationResult | Mapping[str, Any],
    control_evidence: UtilityEvidence | Mapping[str, Any],
    treatment_evidence: UtilityEvidence | Mapping[str, Any],
    *,
    scope: Mapping[str, Any],
    limitations: Sequence[str] = (),
) -> UtilityConclusion:
    """Apply the frozen outcome-first rules for exactly one causal pair."""

    pair_status = (
        pair.pair_status
        if isinstance(pair, PairValidationResult)
        else pair.get("pair_status")
    )
    control = (
        control_evidence.as_dict()
        if isinstance(control_evidence, UtilityEvidence)
        else dict(control_evidence)
    )
    treatment = (
        treatment_evidence.as_dict()
        if isinstance(treatment_evidence, UtilityEvidence)
        else dict(treatment_evidence)
    )
    control_outcome = dict(control.get("outcome", {}))
    treatment_outcome = dict(treatment.get("outcome", {}))
    valid_evidence = (
        pair_status == "VALID"
        and control.get("evidence_validity") == "VALID"
        and treatment.get("evidence_validity") == "VALID"
    )
    control_pass = (
        control_outcome.get("success") is True
        and control_outcome.get("regression") is False
        and control_outcome.get("evaluator_valid") is True
    )
    treatment_pass = (
        treatment_outcome.get("success") is True
        and treatment_outcome.get("regression") is False
        and treatment_outcome.get("evaluator_valid") is True
    )
    control_fail = (
        control_outcome.get("evaluator_valid") is True
        and (
            control_outcome.get("success") is False
            or control_outcome.get("regression") is True
        )
    )
    treatment_fail = (
        treatment_outcome.get("evaluator_valid") is True
        and (
            treatment_outcome.get("success") is False
            or treatment_outcome.get("regression") is True
        )
    )
    if not valid_evidence:
        conclusion = "PROTOCOL_FAILURE"
    elif treatment_pass and control_fail:
        conclusion = "HELPS"
    elif control_pass and treatment_fail:
        conclusion = "HURTS"
    elif control_pass and treatment_pass:
        conclusion = "NEUTRAL"
    else:
        conclusion = "INCONCLUSIVE"

    control_trajectory = dict(control.get("trajectory", {}))
    treatment_trajectory = dict(treatment.get("trajectory", {}))
    control_cost = dict(control.get("cost", {}))
    treatment_cost = dict(treatment.get("cost", {}))
    trajectory_difference = {
        key: treatment_trajectory.get(key) - control_trajectory.get(key)
        for key in ("steps", "tool_calls", "verification_count")
        if isinstance(treatment_trajectory.get(key), (int, float))
        and isinstance(control_trajectory.get(key), (int, float))
    }
    cost_difference = {
        key: treatment_cost.get(key) - control_cost.get(key)
        for key in ("tokens", "latency_ms")
        if isinstance(treatment_cost.get(key), (int, float))
        and isinstance(control_cost.get(key), (int, float))
    }
    return UtilityConclusion(
        conclusion=conclusion,
        scope=dict(scope),
        control_outcome=control_outcome,
        treatment_outcome=treatment_outcome,
        trajectory_difference=trajectory_difference,
        cost_difference=cost_difference,
        limitations=list(limitations),
    )


def write_pair_manifest(
    path: str | Path,
    control: ExperimentRun | Mapping[str, Any],
    treatment: ExperimentRun | Mapping[str, Any],
    *,
    control_task: TaskArtifact | Mapping[str, Any] | None = None,
    treatment_task: TaskArtifact | Mapping[str, Any] | None = None,
) -> PairValidationResult:
    result = validate_paired_runs(
        control,
        treatment,
        control_task=control_task,
        treatment_task=treatment_task,
    )
    artifact = result.as_dict()
    validate_pair_manifest(artifact)
    _write_json(Path(path), artifact)
    return result


@dataclass
class FixtureAgent:
    """Small injected agent for tests and the non-benchmark CLI smoke path."""

    result: Any = field(default_factory=lambda: {"status": "fixture_only"})
    steps: int = 0
    tokens: int | None = 0
    latency_ms: float | None = 0.0
    events: Sequence[tuple[str, Mapping[str, Any]]] = field(default_factory=tuple)
    last_context: AgentExecutionContext | None = field(
        default=None, init=False, repr=False
    )

    def run(
        self,
        task: TaskArtifact,
        context: Any,
        trace: TraceRecorder,
    ) -> AgentResult:
        if isinstance(context, AgentExecutionContext):
            self.last_context = context
        for event, details in self.events:
            trace.emit(event, details)
        return AgentResult(
            result=self.result,
            steps=self.steps,
            tokens=self.tokens,
            latency_ms=self.latency_ms,
        )


class DeferredOracle:
    """Explicit placeholder oracle for the CLI; it never claims task success."""

    oracle_version = "deferred-oracle-v0"

    def evaluate(self, task: TaskArtifact, result: Any) -> OracleResult:
        return OracleResult(
            success=None,
            regression=None,
            diagnostics=["ORACLE_NOT_IMPLEMENTED"],
            tests_passed=None,
            evaluator_valid=None,
        )


@dataclass(frozen=True)
class FixtureOracle:
    """Deterministic Oracle boundary for the local paired fixture."""

    result: OracleResult = field(
        default_factory=lambda: OracleResult(
            success=True,
            regression=False,
            diagnostics=["fixture target and regression checks passed"],
            tests_passed=1,
            evaluator_valid=True,
        )
    )
    oracle_version: str = FIXTURE_ORACLE_VERSION

    def evaluate(self, task: TaskArtifact, result: Any) -> OracleResult:
        return self.result


def fixture_skill_payload() -> dict[str, str]:
    """Return a clearly synthetic four-file payload for local plumbing only."""

    return {
        path: (
            f"# Fixture surrogate for {path}\n"
            "This is test data only. It is not the upstream Skill source.\n"
        )
        for path in FROZEN_SKILL_SOURCE_PATHS
    }


def _load_task(path: Path) -> TaskArtifact:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ExperimentRunError(f"TASK_ARTIFACT_READ_FAILED: {path}") from error
    return TaskArtifact.from_dict(value)


def main(argv: list[str] | None = None) -> int:
    """Run an explicit fixture-only experiment plumbing smoke."""

    parser = argparse.ArgumentParser(prog="skillnudge experiment")
    parser.add_argument("--task", type=Path, required=True, help="task artifact JSON")
    parser.add_argument(
        "--condition",
        choices=("control", "treatment"),
        required=True,
        help="control or systematic-debugging treatment",
    )
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--experiment-id", default="skill-utility-v0.1")
    parser.add_argument("--model", default="unconfigured")
    parser.add_argument("--harness-version", default="fixture-harness-v0")
    parser.add_argument("--environment-hash", default="unconfigured")
    args = parser.parse_args(argv)

    try:
        task = _load_task(args.task)
        condition = (
            Condition.control()
            if args.condition == "control"
            else Condition.treatment()
        )
        agent = FixtureAgentAdapter(
            execution_agent=FixtureAgent(),
            renderer=SkillExposureRenderer(fixture_skill_payload()),
            model=args.model,
            harness_version=args.harness_version,
            environment_hash=args.environment_hash,
            tool_manifest={"surface": "fixture_only", "benchmark": "not_run"},
            execution_budget=ExecutionBudget(),
        )
        result = ExperimentRunner(agent, DeferredOracle()).run(
            task,
            experiment_id=args.experiment_id,
            condition=condition,
            run_dir=args.run_dir,
        )
    except (ExperimentRunError, ExperimentSchemaError, OSError, ValueError) as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "run_id": result.run.run_id,
                "run_dir": result.run_dir,
                "condition": result.run.condition.name,
                "outcome_status": result.evidence.outcome.status,
                "benchmark_executed": False,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
