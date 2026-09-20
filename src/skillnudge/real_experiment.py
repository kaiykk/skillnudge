"""Bounded real-execution infrastructure for the Phase 2B.0 readiness smoke.

This module is intentionally narrower than a general agent framework.  It
provides one OpenAI-compatible model boundary, an argv-allowlisted workspace
tool surface, isolated local task checkouts, a post-execution Oracle, and the
frozen Skill artifact preflight.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shlex
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from .experiment_runner import (
    AgentExecutionContext,
    AgentResult,
    Condition,
    ExecutionBudget,
    ExecutionPolicy,
    ExperimentRunError,
    FROZEN_SKILL_ARTIFACT_ID,
    FROZEN_SKILL_CONTENT_COMMIT,
    FROZEN_SKILL_MANIFEST_SHA256,
    FROZEN_SKILL_REPOSITORY,
    FROZEN_SKILL_SOURCE_PATHS,
    FROZEN_SKILL_TAG_OBJECT,
    OracleResult,
    SkillExposureRenderer,
    SYSTEMATIC_DEBUGGING_SKILL,
    TaskArtifact,
    TraceRecorder,
)
from .planning_model import LiveModelProviderUnavailable, _read_local_provider_env


REAL_HARNESS_VERSION = "transparent-single-agent-coding-loop-v0.1"
REAL_ORACLE_VERSION = "readiness-workspace-oracle-v0.1"
READINESS_EXPERIMENT_ID = "phase2b0-real-paired-execution-readiness-v0.1"
MAX_TOOL_OUTPUT_CHARS = 12_000
MAX_FILE_WRITE_CHARS = 40_000
DEFAULT_MODEL_OUTPUT_TOKENS = 1_200
DEFAULT_PROVIDER_TIMEOUT_SECONDS = 60.0


class RealExecutionError(RuntimeError):
    """Raised for a bounded real-execution setup or protocol failure."""


@dataclass(frozen=True)
class CodingModelConfig:
    """Effective provider controls with credentials intentionally omitted."""

    provider_name: str
    endpoint_identity: str
    model_name: str
    model_revision: str | None
    temperature: float
    top_p: float
    seed: int | None
    seed_support: str
    reasoning_configuration: str | None
    max_output_tokens: int
    timeout_seconds: float
    retry_policy: Mapping[str, Any]
    api_key: str = field(repr=False, default="")

    @classmethod
    def from_environment(cls) -> "CodingModelConfig":
        local = _read_local_provider_env()
        model = os.environ.get("SKILLNUDGE_MODEL") or local.get("SKILLNUDGE_MODEL", "")
        api_key = os.environ.get("SKILLNUDGE_MODEL_API_KEY") or local.get(
            "SKILLNUDGE_MODEL_API_KEY", ""
        )
        base_url = os.environ.get("SKILLNUDGE_MODEL_BASE_URL") or local.get(
            "SKILLNUDGE_MODEL_BASE_URL", "https://api.openai.com/v1"
        )
        timeout = os.environ.get("SKILLNUDGE_MODEL_TIMEOUT_SECONDS") or local.get(
            "SKILLNUDGE_MODEL_TIMEOUT_SECONDS", str(DEFAULT_PROVIDER_TIMEOUT_SECONDS)
        )
        if not model or not api_key:
            raise LiveModelProviderUnavailable()
        try:
            timeout_seconds = float(timeout)
            temperature = float(
                os.environ.get(
                    "SKILLNUDGE_MODEL_TEMPERATURE",
                    local.get("SKILLNUDGE_MODEL_TEMPERATURE", "0"),
                )
            )
            top_p = float(
                os.environ.get(
                    "SKILLNUDGE_MODEL_TOP_P",
                    local.get("SKILLNUDGE_MODEL_TOP_P", "1"),
                )
            )
            max_output_tokens = int(
                os.environ.get(
                    "SKILLNUDGE_MODEL_MAX_OUTPUT_TOKENS",
                    local.get(
                        "SKILLNUDGE_MODEL_MAX_OUTPUT_TOKENS",
                        str(DEFAULT_MODEL_OUTPUT_TOKENS),
                    ),
                )
            )
        except ValueError as error:
            raise RealExecutionError("MODEL_CONFIGURATION_INVALID") from error
        seed_text = os.environ.get(
            "SKILLNUDGE_MODEL_SEED", local.get("SKILLNUDGE_MODEL_SEED", "")
        )
        seed = int(seed_text) if seed_text else None
        reasoning = os.environ.get(
            "SKILLNUDGE_MODEL_REASONING_EFFORT",
            local.get("SKILLNUDGE_MODEL_REASONING_EFFORT", ""),
        ) or None
        parsed = urllib.parse.urlsplit(base_url)
        endpoint_identity = urllib.parse.urlunsplit(
            (parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", "")
        )
        return cls(
            provider_name="openai-compatible",
            endpoint_identity=endpoint_identity,
            model_name=model,
            model_revision=None,
            temperature=temperature,
            top_p=top_p,
            seed=seed,
            seed_support="unknown" if seed is None else "requested",
            reasoning_configuration=reasoning,
            max_output_tokens=max_output_tokens,
            timeout_seconds=timeout_seconds,
            retry_policy={
                "transport_retry_limit": 0,
                "model_error_retry_limit": 0,
            },
            api_key=api_key,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "provider_identity": self.provider_name,
            "endpoint_identity": self.endpoint_identity,
            "model_identifier": self.model_name,
            "model_revision": self.model_revision,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "seed": self.seed,
            "seed_support": self.seed_support,
            "reasoning_configuration": self.reasoning_configuration,
            "max_output_tokens": self.max_output_tokens,
            "timeout_seconds": self.timeout_seconds,
            "retry_policy": dict(self.retry_policy),
            "credentials": "omitted",
        }


@dataclass(frozen=True)
class ModelResponse:
    action: Mapping[str, Any]
    output_tokens: int | None
    model_revision: str | None


class CodingModelError(RealExecutionError):
    """A redacted provider or response-protocol failure."""


class OpenAICompatibleCodingModel:
    """Minimal Chat Completions client for the real coding loop."""

    def __init__(self, config: CodingModelConfig):
        if not config.api_key or not config.model_name:
            raise LiveModelProviderUnavailable()
        self.config = config

    @classmethod
    def from_environment(cls) -> "OpenAICompatibleCodingModel":
        return cls(CodingModelConfig.from_environment())

    def complete(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        max_output_tokens: int,
        timeout_seconds: float,
    ) -> ModelResponse:
        body: dict[str, Any] = {
            "model": self.config.model_name,
            "messages": list(messages),
            "response_format": {"type": "json_object"},
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "max_tokens": max_output_tokens,
        }
        if self.config.seed is not None:
            body["seed"] = self.config.seed
        if self.config.reasoning_configuration is not None:
            body["reasoning_effort"] = self.config.reasoning_configuration
        request = urllib.request.Request(
            url=self.config.endpoint_identity.rstrip("/") + "/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(
                request, timeout=max(0.1, timeout_seconds)
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            raise CodingModelError(f"MODEL_PROVIDER_HTTP_{error.code}") from error
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, UnicodeDecodeError) as error:
            raise CodingModelError("MODEL_PROVIDER_REQUEST_FAILED") from error
        try:
            content = payload["choices"][0]["message"]["content"]
            if isinstance(content, list):
                content = "".join(
                    item.get("text", "") for item in content if isinstance(item, Mapping)
                )
            action = json.loads(content) if isinstance(content, str) else content
            if not isinstance(action, Mapping):
                raise TypeError
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
            raise CodingModelError("MODEL_PROVIDER_INVALID_ACTION") from error
        usage = payload.get("usage", {})
        output_tokens = usage.get("completion_tokens") if isinstance(usage, Mapping) else None
        if output_tokens is not None and (
            not isinstance(output_tokens, int) or output_tokens < 0
        ):
            output_tokens = None
        return ModelResponse(
            action=dict(action),
            output_tokens=output_tokens,
            model_revision=payload.get("model")
            if isinstance(payload.get("model"), str)
            else None,
        )


@dataclass(frozen=True)
class FrozenSkillArtifact:
    """External four-file snapshot and its preflight evidence."""

    source_dir: Path
    file_hashes: Mapping[str, str]
    actual_manifest_sha256: str
    expected_manifest_sha256: str
    verified: bool
    verification_error: str | None

    def payload_files(self) -> dict[str, bytes]:
        return {
            path: (self.source_dir / path).read_bytes()
            for path in FROZEN_SKILL_SOURCE_PATHS
        }

    def renderer(self) -> SkillExposureRenderer:
        if not self.verified:
            raise RealExecutionError(
                "FROZEN_SKILL_MANIFEST_MISMATCH: "
                f"expected={self.expected_manifest_sha256} "
                f"actual={self.actual_manifest_sha256}"
            )
        return SkillExposureRenderer(
            self.payload_files(),
            artifact_mode="frozen_verified_artifact",
            expected_manifest_sha256=self.expected_manifest_sha256,
            source_revision=FROZEN_SKILL_CONTENT_COMMIT,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "artifact_id": FROZEN_SKILL_ARTIFACT_ID,
            "source_repository": FROZEN_SKILL_REPOSITORY,
            "release": "v6.4.1",
            "tag_object": FROZEN_SKILL_TAG_OBJECT,
            "content_commit": FROZEN_SKILL_CONTENT_COMMIT,
            "file_paths": list(FROZEN_SKILL_SOURCE_PATHS),
            "file_hashes": dict(self.file_hashes),
            "expected_manifest_sha256": self.expected_manifest_sha256,
            "actual_manifest_sha256": self.actual_manifest_sha256,
            "verified": self.verified,
            "verification_error": self.verification_error,
        }


def fetch_frozen_skill_artifact(
    source_dir: str | Path | None = None,
) -> FrozenSkillArtifact:
    """Load only the frozen four files from an external snapshot or raw URLs."""

    if source_dir is None:
        target = Path(
            tempfile.mkdtemp(prefix="skillnudge-superpowers-v6.4.1-")
        )
        for path in FROZEN_SKILL_SOURCE_PATHS:
            destination = target / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            url = f"https://raw.githubusercontent.com/obra/superpowers/v6.4.1/{path}"
            try:
                with urllib.request.urlopen(url, timeout=30) as response:
                    destination.write_bytes(response.read())
            except (urllib.error.URLError, TimeoutError, OSError) as error:
                raise RealExecutionError("FROZEN_SKILL_SOURCE_FETCH_FAILED") from error
    else:
        target = Path(source_dir)
    payload_files: dict[str, bytes] = {}
    for path in FROZEN_SKILL_SOURCE_PATHS:
        source = target / path
        if not source.is_file():
            raise RealExecutionError(f"FROZEN_SKILL_FILE_MISSING:{path}")
        payload_files[path] = source.read_bytes()
    file_hashes = {
        path: hashlib.sha256(content).hexdigest()
        for path, content in payload_files.items()
    }
    records = [
        f"{path}\tsha256:{file_hashes[path]}" for path in FROZEN_SKILL_SOURCE_PATHS
    ]
    actual = hashlib.sha256(("\n".join(records) + "\n").encode("utf-8")).hexdigest()
    error = None
    if actual != FROZEN_SKILL_MANIFEST_SHA256:
        error = (
            "FROZEN_SKILL_MANIFEST_MISMATCH: "
            f"expected={FROZEN_SKILL_MANIFEST_SHA256} actual={actual}"
        )
    return FrozenSkillArtifact(
        source_dir=target,
        file_hashes=file_hashes,
        actual_manifest_sha256=actual,
        expected_manifest_sha256=FROZEN_SKILL_MANIFEST_SHA256,
        verified=error is None,
        verification_error=error,
    )


class WorkspaceToolError(RealExecutionError):
    """A rejected or failed workspace operation."""


class WorkspaceToolExecutor:
    """Filesystem and argv-only shell tools confined to one checkout."""

    allowed_tools = frozenset({"read_file", "write_file", "shell", "test"})
    allowed_commands = frozenset(
        {"cat", "find", "git", "grep", "ls", "pwd", "python", "python3", "pytest", "rg", "sed"}
    )
    allowed_git_subcommands = frozenset({"diff", "grep", "log", "ls-files", "show", "status"})

    def __init__(self, workspace: str | Path, visible_test_command: str):
        self.workspace = Path(workspace).resolve()
        self.visible_test_command = visible_test_command

    def _path(self, value: Any, *, write: bool = False) -> Path:
        if not isinstance(value, str) or not value or Path(value).is_absolute():
            raise WorkspaceToolError("WORKSPACE_PATH_INVALID")
        candidate = (self.workspace / value).resolve()
        try:
            candidate.relative_to(self.workspace)
        except ValueError as error:
            raise WorkspaceToolError("WORKSPACE_PATH_ESCAPE") from error
        if ".git" in candidate.relative_to(self.workspace).parts:
            raise WorkspaceToolError("WORKSPACE_GIT_METADATA_DENIED")
        if write and len(value) > 256:
            raise WorkspaceToolError("WORKSPACE_PATH_TOO_LONG")
        return candidate

    @staticmethod
    def _truncate(value: str) -> str:
        if len(value) <= MAX_TOOL_OUTPUT_CHARS:
            return value
        return value[:MAX_TOOL_OUTPUT_CHARS] + "\n[output truncated]"

    def _command(self, command: str) -> list[str]:
        if not isinstance(command, str) or not command.strip():
            raise WorkspaceToolError("SHELL_COMMAND_EMPTY")
        if any(char in command for char in "\n;|&><`$()"):
            raise WorkspaceToolError("SHELL_SYNTAX_DENIED")
        tokens = shlex.split(command)
        if not tokens or any(
            token.startswith(("/", "~")) or ".." in Path(token).parts
            for token in tokens
        ):
            raise WorkspaceToolError("SHELL_PATH_ESCAPE")
        executable = tokens[0]
        if executable not in self.allowed_commands:
            raise WorkspaceToolError(f"SHELL_COMMAND_DENIED:{executable}")
        if executable == "git":
            if len(tokens) < 2 or tokens[1] not in self.allowed_git_subcommands:
                raise WorkspaceToolError("GIT_SUBCOMMAND_DENIED")
        if executable in {"python", "python3"}:
            if "-c" in tokens or "-u" in tokens:
                raise WorkspaceToolError("PYTHON_EXECUTION_MODE_DENIED")
            if "-m" not in tokens:
                raise WorkspaceToolError("PYTHON_MODULE_DENIED")
            module_index = tokens.index("-m")
            if module_index + 1 >= len(tokens) or tokens[module_index + 1] not in {
                "pytest",
                "unittest",
            }:
                raise WorkspaceToolError("PYTHON_MODULE_DENIED")
        return tokens

    def _run(self, command: str, timeout_seconds: float) -> dict[str, Any]:
        tokens = self._command(command)
        environment = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "PYTHONPATH": str(self.workspace),
            "LANG": "C.UTF-8",
        }
        try:
            result = subprocess.run(
                tokens,
                cwd=self.workspace,
                env=environment,
                capture_output=True,
                text=True,
                timeout=max(0.1, timeout_seconds),
                check=False,
            )
        except subprocess.TimeoutExpired:
            return {
                "ok": False,
                "exit_code": None,
                "stdout": "",
                "stderr": "TOOL_TIMEOUT",
            }
        return {
            "ok": result.returncode == 0,
            "exit_code": result.returncode,
            "stdout": self._truncate(result.stdout),
            "stderr": self._truncate(result.stderr),
        }

    def execute(
        self,
        tool: str,
        arguments: Mapping[str, Any],
        *,
        timeout_seconds: float,
    ) -> dict[str, Any]:
        if tool not in self.allowed_tools:
            raise WorkspaceToolError(f"TOOL_DENIED:{tool}")
        if tool == "read_file":
            path = self._path(arguments.get("path"))
            try:
                content = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as error:
                raise WorkspaceToolError("READ_FILE_FAILED") from error
            return {"ok": True, "path": str(path.relative_to(self.workspace)), "content": self._truncate(content)}
        if tool == "write_file":
            content = arguments.get("content")
            if not isinstance(content, str) or len(content) > MAX_FILE_WRITE_CHARS:
                raise WorkspaceToolError("WRITE_FILE_CONTENT_INVALID")
            path = self._path(arguments.get("path"), write=True)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return {"ok": True, "path": str(path.relative_to(self.workspace))}
        if tool == "test":
            return self._run(self.visible_test_command, timeout_seconds)
        return self._run(str(arguments.get("command", "")), timeout_seconds)


class RealCodingAgentAdapter:
    """Transparent single-agent loop with no hidden planner or subagents."""

    def __init__(
        self,
        *,
        model_client: OpenAICompatibleCodingModel,
        renderer: SkillExposureRenderer,
        workspace: str | Path,
        model_config: Mapping[str, Any],
        tool_manifest: Mapping[str, Any],
        execution_budget: ExecutionBudget,
        environment_hash: str,
        execution_policy: ExecutionPolicy | None = None,
    ):
        self.model_client = model_client
        self.renderer = renderer
        self.workspace = Path(workspace).resolve()
        self.model = model_client.config.model_name
        self.model_config = dict(model_config)
        self.harness_version = REAL_HARNESS_VERSION
        self.tool_manifest = dict(tool_manifest)
        self.execution_budget = execution_budget
        self.environment_hash = environment_hash
        self.execution_policy = execution_policy or ExecutionPolicy()
        self.tool_executor: WorkspaceToolExecutor | None = None

    def exposure_for(self, condition: Condition):
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

    @staticmethod
    def _system_prompt(skill_context: str) -> str:
        skill_block = (
            "\n\nThe following is the fixed treatment capability payload. Use only "
            "the procedures in this payload; it does not add tools or hidden data.\n"
            + skill_context
            if skill_context
            else ""
        )
        return (
            "You are a transparent single-agent coding task solver. "
            "Return exactly one JSON object and never include private reasoning. "
            "Use visible tools only. Valid actions are: "
            '{"type":"tool_call","tool":"read_file","arguments":{"path":"..."}}, '
            '{"type":"tool_call","tool":"write_file","arguments":{"path":"...","content":"..."}}, '
            '{"type":"tool_call","tool":"shell","arguments":{"command":"..."}}, '
            '{"type":"tool_call","tool":"test","arguments":{}}, or '
            '{"type":"final","summary":"..."} . '
            "Paths are relative to the declared workspace. Do not access parent "
            "directories, hidden evaluator files, credentials, the network, or "
            "another run. Make the smallest correct patch and run the visible tests."
            + skill_block
        )

    @staticmethod
    def _failure_result(
        *,
        workspace: Path,
        termination_reason: str,
        steps: int,
        tokens: int,
        started: float,
        summary: str,
    ) -> AgentResult:
        return AgentResult(
            result={
                "status": "agent_failure",
                "termination_reason": termination_reason,
                "summary": summary,
                "workspace_reference": str(workspace),
                "changed_files": [],
            },
            steps=steps,
            tokens=tokens,
            latency_ms=(time.perf_counter() - started) * 1000,
        )

    def _changed_files(self) -> list[str]:
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            cwd=self.workspace,
            env={"PATH": os.environ.get("PATH", "/usr/bin:/bin")},
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return [
            line.strip()
            for line in result.stdout.splitlines()
            if line.strip() and not line.startswith(".git/")
        ]

    def run(self, task: TaskArtifact, condition: Condition, trace: TraceRecorder) -> AgentResult:
        context = self.context_for(condition)
        self.tool_executor = WorkspaceToolExecutor(
            self.workspace, task.visible_test_command or task.test_command
        )
        started = time.perf_counter()
        deadline = (
            float("inf")
            if self.execution_budget.max_latency_ms is None
            else started + self.execution_budget.max_latency_ms / 1000
        )
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": self._system_prompt(context.visible_context)},
            {
                "role": "user",
                "content": (
                    f"Task: {task.description}\n"
                    f"Repository base commit: {task.commit}\n"
                    f"Visible test command: {task.visible_test_command or task.test_command}\n"
                    "Begin by inspecting the repository in the declared workspace."
                ),
            },
        ]
        steps = 0
        tool_calls = 0
        output_tokens = 0
        retries = 0
        while True:
            if steps >= self.execution_budget.max_steps:
                trace.emit("failure", {"category": "budget", "reason": "max_steps"})
                return self._failure_result(
                    workspace=self.workspace,
                    termination_reason="max_steps",
                    steps=steps,
                    tokens=output_tokens,
                    started=started,
                    summary="agent step budget exhausted",
                )
            remaining = deadline - time.perf_counter()
            if remaining <= 0:
                trace.emit("failure", {"category": "budget", "reason": "wall_clock"})
                return self._failure_result(
                    workspace=self.workspace,
                    termination_reason="wall_clock_timeout",
                    steps=steps,
                    tokens=output_tokens,
                    started=started,
                    summary="agent wall-clock budget exhausted",
                )
            steps += 1
            max_output = self.model_client.config.max_output_tokens
            if self.execution_budget.max_tokens is not None:
                max_output = min(
                    max_output,
                    max(1, self.execution_budget.max_tokens - output_tokens),
                )
            try:
                response = self.model_client.complete(
                    messages,
                    max_output_tokens=max_output,
                    timeout_seconds=min(
                        self.model_client.config.timeout_seconds, remaining
                    ),
                )
                retries = 0
            except CodingModelError as error:
                if retries < int(
                    self.execution_policy.retry_policy.get("model_error_retry_limit", 0)
                ):
                    retries += 1
                    steps -= 1
                    continue
                trace.emit(
                    "failure",
                    {"category": "model", "reason": str(error)},
                )
                return self._failure_result(
                    workspace=self.workspace,
                    termination_reason=str(error),
                    steps=steps,
                    tokens=output_tokens,
                    started=started,
                    summary="model request or action protocol failed",
                )
            if response.output_tokens is not None:
                output_tokens += response.output_tokens
            action = dict(response.action)
            action_type = action.get("type")
            if action_type == "final":
                summary = action.get("summary")
                if not isinstance(summary, str):
                    summary = "agent returned final action without a summary"
                return AgentResult(
                    result={
                        "status": "completed",
                        "termination_reason": "model_final",
                        "summary": summary,
                        "workspace_reference": str(self.workspace),
                        "changed_files": self._changed_files(),
                    },
                    steps=steps,
                    tokens=output_tokens,
                    latency_ms=(time.perf_counter() - started) * 1000,
                )
            if action_type != "tool_call":
                trace.emit(
                    "failure",
                    {"category": "model_protocol", "reason": "unsupported_action"},
                )
                return self._failure_result(
                    workspace=self.workspace,
                    termination_reason="unsupported_action",
                    steps=steps,
                    tokens=output_tokens,
                    started=started,
                    summary="model returned an unsupported action",
                )
            tool = action.get("tool")
            arguments = action.get("arguments", {})
            if not isinstance(tool, str) or not isinstance(arguments, Mapping):
                trace.emit(
                    "failure",
                    {"category": "model_protocol", "reason": "invalid_tool_call"},
                )
                return self._failure_result(
                    workspace=self.workspace,
                    termination_reason="invalid_tool_call",
                    steps=steps,
                    tokens=output_tokens,
                    started=started,
                    summary="model returned an invalid tool call",
                )
            if tool_calls >= self.execution_budget.max_tool_calls:
                trace.emit("failure", {"category": "budget", "reason": "max_tool_calls"})
                return self._failure_result(
                    workspace=self.workspace,
                    termination_reason="max_tool_calls",
                    steps=steps,
                    tokens=output_tokens,
                    started=started,
                    summary="agent tool-call budget exhausted",
                )
            tool_calls += 1
            trace.emit(
                "tool_call",
                {"tool": tool, "arguments": dict(arguments), "call_index": tool_calls},
            )
            try:
                result = self.tool_executor.execute(
                    tool,
                    arguments,
                    timeout_seconds=max(0.1, deadline - time.perf_counter()),
                )
            except WorkspaceToolError as error:
                result = {"ok": False, "error": str(error)}
            trace.emit(
                "tool_result",
                {
                    "tool": tool,
                    "ok": bool(result.get("ok")),
                    "exit_code": result.get("exit_code"),
                    "stdout": result.get("stdout", result.get("content", "")),
                    "stderr": result.get("stderr", result.get("error", "")),
                },
            )
            if tool == "test":
                trace.emit(
                    "test_execution",
                    {
                        "command": task.visible_test_command or task.test_command,
                        "exit_code": result.get("exit_code"),
                        "passed": result.get("ok") is True,
                    },
                )
                if result.get("ok") is True:
                    trace.emit(
                        "verification",
                        {"kind": "visible_tests", "passed": True},
                    )
            if tool == "write_file" and result.get("ok") is True:
                trace.emit(
                    "patch_generated",
                    {"files": [result.get("path")]},
                )
            messages.append({"role": "assistant", "content": json.dumps(action)})
            messages.append(
                {
                    "role": "tool",
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )


class ReadinessWorkspaceOracle:
    """Runs hidden target and regression checks only after Agent execution."""

    oracle_version = REAL_ORACLE_VERSION

    def __init__(self, *, timeout_seconds: float = 30.0):
        self.timeout_seconds = timeout_seconds
        self.evaluator_config = {
            "target_check": "external_hidden_command",
            "regression_check": "external_hidden_command",
            "agent_visibility": "forbidden",
            "timeout_seconds": timeout_seconds,
        }

    def _run_check(self, command: str, workspace: Path) -> tuple[bool | None, str]:
        try:
            tokens = shlex.split(command)
            if (
                not tokens
                or tokens[0] not in {"python", "python3"}
                or "-m" not in tokens
                or "unittest" not in tokens
            ):
                return None, "ORACLE_COMMAND_INVALID"
            result = subprocess.run(
                tokens,
                cwd=workspace,
                env={
                    "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                    "PYTHONPATH": str(workspace),
                    "LANG": "C.UTF-8",
                    "SKILLNUDGE_EVAL_WORKSPACE": str(workspace),
                },
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return None, "ORACLE_TIMEOUT"
        except (OSError, ValueError):
            return None, "ORACLE_EXECUTION_FAILED"
        status = result.returncode == 0
        return status, f"exit_code={result.returncode}"

    def evaluate(self, task: TaskArtifact, result: Any) -> OracleResult:
        if not isinstance(result, Mapping):
            return OracleResult(
                success=None,
                regression=None,
                diagnostics=["ORACLE_WORKSPACE_REFERENCE_MISSING"],
                evaluator_valid=False,
                evaluation_environment={"oracle_version": self.oracle_version},
            )
        reference = result.get("workspace_reference")
        if not isinstance(reference, str):
            return OracleResult(
                success=None,
                regression=None,
                diagnostics=["ORACLE_WORKSPACE_REFERENCE_MISSING"],
                evaluator_valid=False,
                evaluation_environment={"oracle_version": self.oracle_version},
            )
        workspace = Path(reference).resolve()
        target_status, target_diag = self._run_check(
            task.oracle_target_command or "", workspace
        )
        regression_status, regression_diag = self._run_check(
            task.oracle_regression_command or "", workspace
        )
        evaluator_valid = target_status is not None and regression_status is not None
        success = target_status if evaluator_valid else None
        regression = (
            not regression_status if evaluator_valid else None
        )
        diagnostics = [
            f"target_check:{target_diag}",
            f"regression_check:{regression_diag}",
        ]
        return OracleResult(
            success=success,
            regression=regression,
            diagnostics=diagnostics,
            tests_passed=(2 if evaluator_valid and success and not regression else None),
            target_status=(
                "pass" if target_status is True else
                "fail" if target_status is False else
                "unknown"
            ),
            regression_status=(
                "pass" if regression_status is True else
                "fail" if regression_status is False else
                "unknown"
            ),
            evaluator_valid=evaluator_valid,
            evaluation_environment={
                "oracle_version": self.oracle_version,
                "workspace_reference": str(workspace),
                "hidden_checks_external": True,
                "agent_visibility": "forbidden",
            },
        )


def environment_identity() -> str:
    """Hash only the stable execution facts needed for paired comparison."""

    values = [
        platform.platform(),
        sys.executable,
        sys.version,
        subprocess.run(
            ["git", "--version"], capture_output=True, text=True, check=False
        ).stdout.strip(),
    ]
    return hashlib.sha256("\n".join(values).encode("utf-8")).hexdigest()


def default_tool_manifest() -> dict[str, Any]:
    return {
        "filesystem": {
            "mode": "declared_workspace_only",
            "other_arm": "blocked",
            "oracle_files": "blocked",
            "credentials": "blocked",
        },
        "shell": {
            "mode": "argv_allowlist",
            "network": "disabled",
            "subagents": "disabled",
            "mcp": "disabled",
        },
        "git": "local_repository_only",
        "test_runner": "task_visible_command_only",
    }


@dataclass(frozen=True)
class ReadinessTaskBundle:
    task: TaskArtifact
    source_repository: Path
    hidden_oracle_directory: Path
    control_workspace: Path
    treatment_workspace: Path


def _run_host(command: Sequence[str], cwd: Path) -> str:
    cwd = cwd.resolve()
    result = subprocess.run(
        list(command),
        cwd=cwd,
        env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "C.UTF-8"},
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip().splitlines()
        suffix = detail[-1] if detail else "unknown"
        raise RealExecutionError(f"HOST_COMMAND_FAILED:{command[0]}:{suffix}")
    return result.stdout.strip()


def create_readiness_task_bundle(run_root: str | Path) -> ReadinessTaskBundle:
    """Create one tiny pinned debugging repository and two isolated clones."""

    root = Path(run_root).resolve()
    source = root / "readiness-source-repository"
    source.mkdir(parents=True, exist_ok=False)
    (source / "src").mkdir()
    (source / "tests").mkdir()
    (source / "src" / "price.py").write_text(
        "def apply_discount(amount, percent):\n"
        "    return round(amount - amount * percent, 2)\n",
        encoding="utf-8",
    )
    (source / "tests" / "test_public.py").write_text(
        "import unittest\n\n"
        "from src.price import apply_discount\n\n"
        "class PublicDiscountTests(unittest.TestCase):\n"
        "    def test_whole_percentage_is_applied(self):\n"
        "        self.assertEqual(apply_discount(100, 20), 80)\n\n"
        "    def test_zero_discount_is_unchanged(self):\n"
        "        self.assertEqual(apply_discount(50, 0), 50)\n",
        encoding="utf-8",
    )
    _run_host(["git", "init", "-q", "-b", "main"], source)
    _run_host(["git", "config", "user.email", "readiness@skillnudge.local"], source)
    _run_host(["git", "config", "user.name", "SkillNudge Readiness"], source)
    _run_host(["git", "add", "src", "tests"], source)
    _run_host(["git", "commit", "-q", "-m", "readiness task base"], source)
    base_commit = _run_host(["git", "rev-parse", "HEAD"], source)

    hidden = root / "oracle-hidden-checks"
    (hidden / "target").mkdir(parents=True)
    (hidden / "regression").mkdir(parents=True)
    (hidden / "target" / "test_target.py").write_text(
        "import os\nimport sys\nimport unittest\n\n"
        "sys.path.insert(0, os.environ['SKILLNUDGE_EVAL_WORKSPACE'])\n"
        "from src.price import apply_discount\n\n"
        "class TargetTests(unittest.TestCase):\n"
        "    def test_decimal_discount(self):\n"
        "        self.assertEqual(apply_discount(19.99, 15), 16.99)\n",
        encoding="utf-8",
    )
    (hidden / "regression" / "test_regression.py").write_text(
        "import os\nimport sys\nimport unittest\n\n"
        "sys.path.insert(0, os.environ['SKILLNUDGE_EVAL_WORKSPACE'])\n"
        "from src.price import apply_discount\n\n"
        "class RegressionTests(unittest.TestCase):\n"
        "    def test_boundary_values(self):\n"
        "        self.assertEqual(apply_discount(50, 0), 50)\n"
        "        self.assertEqual(apply_discount(50, 100), 0)\n",
        encoding="utf-8",
    )
    control = root / "workspaces" / "control"
    treatment = root / "workspaces" / "treatment"
    control.parent.mkdir(parents=True)
    treatment.parent.mkdir(parents=True, exist_ok=True)
    _run_host(["git", "clone", "-q", str(source), str(control)], root)
    _run_host(["git", "clone", "-q", str(source), str(treatment)], root)
    _run_host(["git", "remote", "remove", "origin"], control)
    _run_host(["git", "remote", "remove", "origin"], treatment)
    task = TaskArtifact(
        task_id="phase2b0-readiness-discount-001",
        repository="skillnudge/local-readiness-discount",
        commit=base_commit,
        test_command="python3 -m unittest discover -s tests -v",
        description=(
            "Fix the discount bug in src/price.py. The public API receives a "
            "whole-number percentage, so percent=20 means a 20% discount. "
            "Preserve two-decimal currency rounding and boundary behavior. "
            "Do not change the public tests."
        ),
        visible_test_command="python3 -m unittest discover -s tests -v",
        oracle_target_command=(
            f"python3 -m unittest discover -s {hidden / 'target'} -p 'test_*.py' -v"
        ),
        oracle_regression_command=(
            f"python3 -m unittest discover -s {hidden / 'regression'} -p 'test_*.py' -v"
        ),
        environment_identity=environment_identity(),
    )
    return ReadinessTaskBundle(
        task=task,
        source_repository=source,
        hidden_oracle_directory=hidden,
        control_workspace=control,
        treatment_workspace=treatment,
    )
