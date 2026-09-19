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
import json
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence


EXPERIMENT_RUN_SCHEMA = "experiment.run.v0"
TRACE_EVENT_SCHEMA = "trace.event.experiment.v0"
EVIDENCE_SCHEMA = "utility.evidence.experiment.v0"
SYSTEMATIC_DEBUGGING_SKILL = "systematic-debugging-v6.4.1"

SUPPORTED_SKILLS = frozenset({SYSTEMATIC_DEBUGGING_SKILL})
SUPPORTED_TRACE_EVENTS = frozenset(
    {
        "agent_start",
        "tool_call",
        "tool_result",
        "test_execution",
        "patch_generated",
        "verification",
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
    elif isinstance(value, list):
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
    """Minimal placeholder task input; no dataset implementation is assumed."""

    task_id: str
    repository: str
    commit: str
    test_command: str

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
        )

    def as_dict(self) -> dict[str, str]:
        return {
            "task_id": self.task_id,
            "repository": self.repository,
            "commit": self.commit,
            "test_command": self.test_command,
        }


def validate_task_artifact(value: Any) -> dict[str, Any]:
    if not _is_mapping(value):
        raise ExperimentSchemaError("TaskArtifact", ["task must be an object"])
    errors: list[str] = []
    allowed = {"task_id", "repository", "commit", "test_command"}
    _unexpected(value, allowed, errors)
    for key in allowed:
        _required_string(value, key, errors)
    if errors:
        raise ExperimentSchemaError("TaskArtifact", errors)
    return {key: value[key] for key in allowed}


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

    def __post_init__(self) -> None:
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
    skill_version = value.get("skill_version")
    if skill_version is not None and (
        not isinstance(skill_version, str) or skill_version not in SUPPORTED_SKILLS
    ):
        errors.append(f"skill_version must be null or one of {sorted(SUPPORTED_SKILLS)}")
    if _is_mapping(value.get("condition")):
        try:
            condition = Condition.from_value(value["condition"])
            if skill_version != condition.skill:
                errors.append("skill_version must match condition.skill")
        except ExperimentSchemaError as error:
            errors.extend(error.errors)
    if errors:
        raise ExperimentSchemaError("ExperimentRun", errors)
    _assert_observable_payload(value["tool_manifest"], "tool_manifest")
    _assert_json_serializable(value["tool_manifest"], "ExperimentRun")
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
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "regression": self.regression,
            "diagnostics": list(self.diagnostics),
            "tests_passed": self.tests_passed,
        }


def validate_oracle_result(value: Any) -> dict[str, Any]:
    if not _is_mapping(value):
        raise ExperimentSchemaError("OracleResult", ["oracle result must be an object"])
    errors: list[str] = []
    allowed = {"success", "regression", "diagnostics", "tests_passed"}
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
    if errors:
        raise ExperimentSchemaError("OracleResult", errors)
    return dict(value)


@dataclass(frozen=True)
class OutcomeEvidence:
    status: str
    success: bool | None
    regression: bool | None
    tests_passed: int | None
    diagnostics: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "success": self.success,
            "regression": self.regression,
            "tests_passed": self.tests_passed,
            "diagnostics": list(self.diagnostics),
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
    if errors:
        raise ExperimentSchemaError("UtilityEvidence", errors)
    return dict(value)


class Agent(Protocol):
    """Adapter boundary for a future model/harness implementation."""

    def run(
        self,
        task: TaskArtifact,
        condition: Condition,
        trace: TraceRecorder,
    ) -> AgentResult:
        """Execute one task and emit only observable events."""


class Oracle(Protocol):
    """Task oracle boundary; the final benchmark implementation is deferred."""

    def evaluate(self, task: TaskArtifact, result: Any) -> OracleResult:
        """Return success, regression, diagnostics, and optional test counts."""


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
        model: str,
        harness_version: str,
        skill_version: str | None = None,
        tool_manifest: Mapping[str, Any] | None = None,
        environment_hash: str,
        run_dir: str | Path,
        run_id: str | None = None,
    ) -> ExperimentResult:
        task_artifact = (
            task if isinstance(task, TaskArtifact) else TaskArtifact.from_dict(task)
        )
        condition_artifact = Condition.from_value(condition)
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
        )
        _write_json(output_dir / "experiment_run.json", run.as_dict())
        _write_json(output_dir / "task.json", task_artifact.as_dict())

        trace = TraceRecorder(output_dir / "trace.jsonl", run.run_id)
        started = time.perf_counter()
        try:
            trace.emit(
                "agent_start",
                {
                    "condition": condition_artifact.as_dict(),
                    "condition_name": condition_artifact.name,
                    "task_id": task_artifact.task_id,
                },
            )
            agent_result = self.agent.run(task_artifact, condition_artifact, trace)
            if not isinstance(agent_result, AgentResult):
                raise ExperimentRunError("agent must return AgentResult")
            oracle_result = OracleResult.from_value(
                self.oracle.evaluate(task_artifact, agent_result.result)
            )
            trace.emit(
                "verification",
                {
                    "source": "oracle",
                    "success": oracle_result.success,
                    "regression": oracle_result.regression,
                    "tests_passed": oracle_result.tests_passed,
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
        if oracle_result.success is True and oracle_result.regression is False:
            status = "success"
        elif oracle_result.success is False or oracle_result.regression is True:
            status = "failure"
        else:
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
        )


@dataclass
class FixtureAgent:
    """Small injected agent for tests and the non-benchmark CLI smoke path."""

    result: Any = field(default_factory=lambda: {"status": "fixture_only"})
    steps: int = 0
    tokens: int | None = 0
    latency_ms: float | None = 0.0
    events: Sequence[tuple[str, Mapping[str, Any]]] = field(default_factory=tuple)

    def run(
        self,
        task: TaskArtifact,
        condition: Condition,
        trace: TraceRecorder,
    ) -> AgentResult:
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

    def evaluate(self, task: TaskArtifact, result: Any) -> OracleResult:
        return OracleResult(
            success=None,
            regression=None,
            diagnostics=["ORACLE_NOT_IMPLEMENTED"],
            tests_passed=None,
        )


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
        result = ExperimentRunner(FixtureAgent(), DeferredOracle()).run(
            task,
            experiment_id=args.experiment_id,
            condition=condition,
            model=args.model,
            harness_version=args.harness_version,
            environment_hash=args.environment_hash,
            tool_manifest={"surface": "fixture_only", "benchmark": "not_run"},
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
