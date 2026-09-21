"""Run the first real Codex Control/Treatment pair for Phase 2."""

from __future__ import annotations

import argparse
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "eval" / "phase2_first_causal_task"))

from oracle import NativePlanningContractOracle  # noqa: E402
from skillnudge.experiment_runner import (  # noqa: E402
    AgentExecutionContext,
    AgentResult,
    Condition,
    ExecutionBudget,
    ExecutionPolicy,
    ExperimentRunError,
    ExperimentRunner,
    FROZEN_SKILL_ARTIFACT_ID,
    SkillExposureRenderer,
    TaskArtifact,
    TraceRecorder,
    UtilityConclusion,
    validate_pair_manifest,
    validate_real_paired_runs,
)
from skillnudge.real_experiment import (  # noqa: E402
    REAL_HARNESS_VERSION,
    environment_identity,
    fetch_frozen_skill_artifact,
)


EXPERIMENT_ID = "phase2-first-native-planning-contract-discoverability-v0.1"
BASE_COMMIT = "865bfdf191ce5d6be1aa3451e7767f063705c0ef"
TARGET_COMMIT = "869484cf19bd7589c7981e96f5417687166773bc"
TASK_FILE = ROOT / "eval" / "phase2_first_causal_task" / "task.json"
HARNESS_VERSION = "codex-external-reference-host-v0.1"
CODEX_TIMEOUT_SECONDS = 240


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if check and completed.returncode != 0:
        detail = completed.stderr.strip().splitlines()
        suffix = detail[-1] if detail else "unknown git failure"
        raise RuntimeError(f"git {' '.join(args)} failed: {suffix}")
    return completed


def _load_task_file() -> dict[str, Any]:
    return json.loads(TASK_FILE.read_text(encoding="utf-8"))


def _extract_base_tree(destination: Path) -> None:
    archive = subprocess.run(
        ["git", "-C", str(ROOT), "archive", "--format=tar", BASE_COMMIT],
        capture_output=True,
        check=False,
    )
    if archive.returncode != 0:
        raise RuntimeError("BASE_TREE_EXPORT_FAILED")
    destination.mkdir(parents=True, exist_ok=False)
    with tarfile.open(fileobj=io.BytesIO(archive.stdout), mode="r:") as bundle:
        members = bundle.getmembers()
        for member in members:
            member_path = Path(member.name)
            if member_path.is_absolute() or ".." in member_path.parts:
                raise RuntimeError("BASE_TREE_ARCHIVE_PATH_ESCAPE")
        bundle.extractall(destination)


def _prepare_sanitized_workspaces(run_root: Path) -> dict[str, Any]:
    source = run_root / "sanitized-source"
    _extract_base_tree(source)
    _git(source, "init", "-q", "-b", "main")
    _git(source, "config", "user.email", "phase2@skillnudge.local")
    _git(source, "config", "user.name", "SkillNudge Phase 2")
    _git(source, "add", ".")
    _git(source, "commit", "-q", "-m", "experiment base snapshot")
    sanitized_commit = _git(source, "rev-parse", "HEAD").stdout.strip()

    target_object = _git(source, "cat-file", "-e", f"{TARGET_COMMIT}^{{commit}}", check=False)
    target_grep = _git(source, "grep", "-n", TARGET_COMMIT, check=False)
    log_lines = _git(source, "log", "--oneline", "--decorate", "-5").stdout.splitlines()
    if target_object.returncode == 0:
        raise RuntimeError("SANITIZED_SNAPSHOT_LEAKS_TARGET_COMMIT_OBJECT")
    if target_grep.returncode == 0:
        raise RuntimeError("SANITIZED_SNAPSHOT_LEAKS_TARGET_COMMIT_TEXT")
    if len(log_lines) != 1:
        raise RuntimeError("SANITIZED_SNAPSHOT_HAS_EXTRA_HISTORY")

    control = run_root / "control-workspace"
    treatment = run_root / "treatment-workspace"
    _git(run_root, "clone", "-q", str(source), str(control))
    _git(run_root, "clone", "-q", str(source), str(treatment))
    for workspace in (control, treatment):
        _git(workspace, "remote", "remove", "origin")

    return {
        "source": source,
        "control": control,
        "treatment": treatment,
        "sanitized_commit": sanitized_commit,
        "history_lines": log_lines,
        "target_object_present": False,
        "target_text_present": False,
    }


def _candidate_skill_source() -> Path:
    candidates = (
        Path.home() / ".codex-oaiapi" / ".tmp" / "plugins" / "plugins" / "superpowers",
        Path.home() / ".codex" / ".tmp" / "plugins" / "plugins" / "superpowers",
    )
    for candidate in candidates:
        if (candidate / "skills" / "systematic-debugging" / "SKILL.md").is_file():
            return candidate
    raise RuntimeError("FROZEN_SKILL_SOURCE_NOT_AVAILABLE_LOCALLY")


def _install_native_treatment_skill(
    workspace: Path,
    source_root: Path | None,
) -> dict[str, Any]:
    artifact = (
        fetch_frozen_skill_artifact(source_root)
        if source_root is not None
        else fetch_frozen_skill_artifact()
    )
    if not artifact.verified:
        raise RuntimeError(artifact.verification_error or "FROZEN_SKILL_ARTIFACT_NOT_VERIFIED")
    skill_dir = workspace / ".agents" / "skills" / "systematic-debugging"
    skill_dir.mkdir(parents=True, exist_ok=True)
    for path, content in artifact.payload_files().items():
        (skill_dir / Path(path).name).write_bytes(content)
    return artifact.as_dict()


def _codex_version() -> str:
    completed = subprocess.run(
        ["codex", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.stdout.strip() or "unknown"


def _isolated_codex_environment() -> tuple[Path, dict[str, str]]:
    real_home = Path.home()
    temp_home = Path(tempfile.mkdtemp(prefix="skillnudge-phase2-codex-home-"))
    codex_home = temp_home / ".codex"
    codex_home.mkdir()
    for filename in ("auth.json", "config.toml"):
        source = real_home / ".codex" / filename
        if source.is_file():
            os.symlink(source, codex_home / filename)
    environment = os.environ.copy()
    environment.update(
        {
            "HOME": str(temp_home),
            "CODEX_HOME": str(codex_home),
            "XDG_CONFIG_HOME": str(temp_home / "config"),
        }
    )
    return temp_home, environment


class CodexReferenceAdapter:
    """Thin adapter around one external Codex CLI execution."""

    def __init__(
        self,
        *,
        workspace: Path,
        renderer: SkillExposureRenderer,
        codex_environment: Mapping[str, str],
        execution_budget: ExecutionBudget,
        environment_hash: str,
        tool_manifest: Mapping[str, Any],
        run_root: Path,
    ):
        self.workspace = workspace
        self.renderer = renderer
        self.codex_environment = dict(codex_environment)
        self.model = "codex-host"
        self.harness_version = HARNESS_VERSION
        self.tool_manifest = dict(tool_manifest)
        self.execution_budget = execution_budget
        self.environment_hash = environment_hash
        self.execution_policy = ExecutionPolicy(
            retry_policy={
                "transport_retry_limit": 0,
                "tool_failure_retry_limit": 0,
                "model_error_retry_limit": 0,
                "task_level_retry_limit": 0,
            },
            termination_policy={
                "stop_on_completion": True,
                "stop_on_failure": True,
                "budget_enforced": True,
            },
        )
        self.model_config = {
            "host": "Codex",
            "provider": "host-managed",
            "codex_version": _codex_version(),
            "credentials": "omitted",
        }
        self.run_root = run_root

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
    def _prompt(task: Any, condition: Condition) -> str:
        treatment_note = (
            "The workspace contains the frozen systematic-debugging Codex Skill. "
            "Use that native Skill for this task as the only external capability intervention.\n"
            if condition.skill is not None
            else "No external capability intervention is provided for this run.\n"
        )
        return (
            "Work as the reference Codex host for one bounded causal experiment.\n"
            "Use only the declared workspace. Do not inspect parent directories, "
            "other repositories, evaluator files, credentials, or later Git history.\n"
            f"{treatment_note}"
            "Solve the user task in the repository, make the smallest correct change, "
            "run the visible test command, and leave the workspace in the solved state. "
            "Do not create commits. Do not explain private reasoning.\n\n"
            f"Task:\n{task.description}\n\n"
            f"Visible test command: {task.visible_test_command}\n"
        )

    @staticmethod
    def _changed_files(workspace: Path) -> list[str]:
        tracked = _git(workspace, "diff", "--name-only").stdout.splitlines()
        untracked = _git(
            workspace,
            "ls-files",
            "--others",
            "--exclude-standard",
        ).stdout.splitlines()
        return sorted({line.strip() for line in tracked + untracked if line.strip()})

    def run(
        self,
        task: Any,
        condition: Condition,
        trace: TraceRecorder,
    ) -> AgentResult:
        started = time.perf_counter()
        output_path = self.run_root / "codex_last_message.txt"
        events_path = self.run_root / "codex_observable_events.jsonl"
        prompt = self._prompt(task, condition)
        command = [
            "codex",
            "exec",
            "--json",
            "--ephemeral",
            "--ignore-rules",
            "--cd",
            str(self.workspace),
            "--sandbox",
            "workspace-write",
            "--skip-git-repo-check",
            "-o",
            str(output_path),
            prompt,
        ]
        try:
            completed = subprocess.run(
                command,
                cwd=self.workspace,
                env=self.codex_environment,
                capture_output=True,
                text=True,
                timeout=CODEX_TIMEOUT_SECONDS,
                check=False,
            )
        except subprocess.TimeoutExpired:
            trace.emit("failure", {"category": "host", "reason": "codex_timeout"})
            return AgentResult(
                result={
                    "status": "agent_failure",
                    "termination_reason": "codex_timeout",
                    "summary": "Codex host timed out",
                    "workspace_reference": str(self.workspace),
                    "changed_files": self._changed_files(self.workspace),
                    "model_response_observations": [],
                },
                steps=0,
                tokens=None,
                latency_ms=(time.perf_counter() - started) * 1000,
            )

        observable_events: list[dict[str, Any]] = []
        response_observed = False
        turn_completed = False
        output_tokens = None
        command_index = 0
        for line in completed.stdout.splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            event_type = event.get("type")
            if event_type == "turn.completed":
                turn_completed = True
                response_observed = True
                usage = event.get("usage")
                if isinstance(usage, Mapping):
                    value = usage.get("output_tokens")
                    if isinstance(value, int) and value >= 0:
                        output_tokens = value
            elif event_type == "item.completed":
                item = event.get("item")
                if not isinstance(item, Mapping):
                    continue
                item_type = item.get("type")
                if item_type == "agent_message":
                    response_observed = True
                if item_type == "command_execution":
                    command_index += 1
                    command_text = item.get("command")
                    if not isinstance(command_text, str):
                        command_text = "codex_command"
                    command_event = {
                        "item_type": item_type,
                        "command_index": command_index,
                        "command": command_text[:500],
                        "exit_code": item.get("exit_code"),
                    }
                    observable_events.append(command_event)
                    trace.emit(
                        "tool_call",
                        {
                            "tool": "codex_command",
                            "command": command_text[:500],
                            "call_index": command_index,
                        },
                    )
                    trace.emit(
                        "tool_result",
                        {
                            "tool": "codex_command",
                            "ok": item.get("exit_code") in (0, None),
                            "exit_code": item.get("exit_code"),
                        },
                    )
            elif event_type in {"turn.failed", "error"}:
                observable_events.append({"item_type": event_type})

        events_path.write_text(
            "".join(json.dumps(item, sort_keys=True) + "\n" for item in observable_events),
            encoding="utf-8",
        )
        final_summary = ""
        if output_path.is_file():
            final_summary = output_path.read_text(encoding="utf-8", errors="replace").strip()
        status = "completed" if completed.returncode == 0 and turn_completed else "agent_failure"
        termination = "codex_completed" if status == "completed" else f"codex_exit_{completed.returncode}"
        changed_files = self._changed_files(self.workspace)
        if response_observed:
            trace.emit("completion", {"host": "Codex", "status": status})
        else:
            trace.emit("failure", {"category": "host", "reason": termination})
        return AgentResult(
            result={
                "status": status,
                "termination_reason": termination,
                "summary": final_summary[:12_000],
                "workspace_reference": str(self.workspace),
                "changed_files": changed_files,
                "model_response_observations": (
                    [{"response_index": 1, "observed_model_id": "codex-host"}]
                    if response_observed
                    else []
                ),
                "host_execution": {
                    "host": "Codex",
                    "return_code": completed.returncode,
                    "turn_completed": turn_completed,
                    "observable_command_count": command_index,
                    "stderr_present": bool(completed.stderr.strip()),
                },
            },
            steps=command_index,
            tokens=output_tokens,
            latency_ms=(time.perf_counter() - started) * 1000,
        )


def _blocked_pair(task_id: str, error: str) -> dict[str, Any]:
    return {
        "schema_version": "pair.manifest.experiment.v0",
        "experiment_id": EXPERIMENT_ID,
        "task_id": task_id,
        "control_run_id": "not-created",
        "treatment_run_id": "not-created",
        "shared_configuration_identity": "not-computed",
        "pair_status": "PROTOCOL_FAILURE",
        "errors": [error],
        "observed_model_identity": {"control": {}, "treatment": {}},
        "expected_intervention_difference": {
            "control": {"skill_payload": "absent", "condition": {"skill": None}},
            "treatment": {
                "skill_payload": "exact_declared_skill",
                "condition": {"skill": "systematic-debugging-v6.4.1"},
            },
        },
        "execution_evidence": {},
    }


def _default_run_root() -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return ROOT / "runs" / f"phase2-first-causal-pair-{stamp}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, default=_default_run_root())
    parser.add_argument("--skill-source-root", type=Path, default=None)
    args = parser.parse_args(argv)
    run_root = args.run_root.resolve()
    if run_root.exists() and any(run_root.iterdir()):
        print(f"Run root must be empty: {run_root}", file=sys.stderr)
        return 2
    run_root.mkdir(parents=True, exist_ok=True)

    task_file = _load_task_file()
    task_id = str(task_file["task_id"])
    environment_hash = environment_identity()
    _write_json(
        run_root / "task_artifact.json",
        task_file,
    )
    _write_json(
        run_root / "execution_manifest.json",
        {
            "schema_version": "execution.manifest.phase2.first-pair.v0",
            "experiment_id": EXPERIMENT_ID,
            "task_id": task_id,
            "reference_host": "Codex",
            "codex_version": _codex_version(),
            "model_identity": "host-managed; exact model recorded by host if available",
            "tool_surface": "Codex host tools in isolated workspace",
            "execution_budget": {
                "max_steps": 12,
                "max_tool_calls": 24,
                "max_latency_ms": 180_000,
            },
            "retry_policy": "zero task/model retries",
            "network_policy": "host-managed; no SkillNudge provider is called",
            "environment_hash": environment_hash,
            "trace_import_boundary": "observable Codex command events and final result only",
            "credentials": "omitted",
        },
    )

    try:
        snapshot = _prepare_sanitized_workspaces(run_root)
        _write_json(
            run_root / "snapshot_manifest.json",
            {
                "original_source_commit": BASE_COMMIT,
                "target_commit_forbidden": TARGET_COMMIT,
                "sanitized_commit": snapshot["sanitized_commit"],
                "history_lines": snapshot["history_lines"],
                "target_object_present": snapshot["target_object_present"],
                "target_text_present": snapshot["target_text_present"],
            },
        )
        skill_manifest = _install_native_treatment_skill(
            snapshot["treatment"], args.skill_source_root
        )
        _write_json(run_root / "skill_artifact_manifest.json", skill_manifest)
    except (OSError, RuntimeError, ValueError) as error:
        pair = _blocked_pair(task_id, str(error))
        validate_pair_manifest(pair)
        _write_json(run_root / "pair_manifest.json", pair)
        _write_json(
            run_root / "run_result.json",
            {
                "status": "BLOCKED_BY_CONCRETE_HOST_LIMITATION",
                "pair_status": "PROTOCOL_FAILURE",
                "blockers": [str(error)],
            },
        )
        print(json.dumps({"status": "BLOCKED_BY_CONCRETE_HOST_LIMITATION", "blockers": [str(error)]}))
        return 0

    task = TaskArtifact(
        task_id=task_id,
        repository=task_file["repository"],
        commit=snapshot["sanitized_commit"],
        test_command=task_file["agent_visible_task"]["visible_test_command"],
        description=task_file["agent_visible_task"]["description"],
        visible_test_command=task_file["agent_visible_task"]["visible_test_command"],
        environment_identity=environment_hash,
    )
    oracle = NativePlanningContractOracle()
    oracle_self_test = oracle.self_test(snapshot["source"])
    _write_json(run_root / "oracle_self_test.json", oracle_self_test)
    if oracle_self_test["regression_status"] != "PASS":
        blocker = "ORACLE_SELF_TEST_REGRESSION_FAILED"
        pair = _blocked_pair(task_id, blocker)
        validate_pair_manifest(pair)
        _write_json(run_root / "pair_manifest.json", pair)
        _write_json(run_root / "run_result.json", {"status": "BLOCKED_BY_CONCRETE_HOST_LIMITATION", "blockers": [blocker]})
        print(json.dumps({"status": "BLOCKED_BY_CONCRETE_HOST_LIMITATION", "blockers": [blocker]}))
        return 0

    codex_home, codex_environment = _isolated_codex_environment()
    try:
        renderer = SkillExposureRenderer(
            {
                path: (snapshot["treatment"] / ".agents" / "skills" / "systematic-debugging" / Path(path).name).read_bytes()
                for path in (
                    "skills/systematic-debugging/SKILL.md",
                    "skills/systematic-debugging/root-cause-tracing.md",
                    "skills/systematic-debugging/defense-in-depth.md",
                    "skills/systematic-debugging/condition-based-waiting.md",
                )
            },
            artifact_mode="frozen_verified_artifact",
            expected_manifest_sha256=skill_manifest["expected_manifest_sha256"],
            source_revision=skill_manifest["content_commit"],
        )
        common = {
            "renderer": renderer,
            "codex_environment": codex_environment,
            "execution_budget": ExecutionBudget(
                max_steps=12,
                max_tool_calls=24,
                max_tokens=None,
                max_latency_ms=180_000,
            ),
            "environment_hash": environment_hash,
            "tool_manifest": {
                "host": "Codex",
                "workspace": "isolated repository only",
                "oracle_files": "absent from agent workspace",
                "credentials": "not exposed",
                "skill_injection": "native workspace Skill only",
            },
        }
        control_adapter = CodexReferenceAdapter(
            workspace=snapshot["control"],
            run_root=run_root / "control",
            **common,
        )
        control_result = ExperimentRunner(control_adapter, oracle).run(
            task,
            experiment_id=EXPERIMENT_ID,
            condition=Condition.control(),
            run_dir=run_root / "control",
        )
        control_responses = control_result.agent_result.result.get(
            "model_response_observations", []
        )
        if not isinstance(control_responses, list) or not control_responses:
            blocker = "CONTROL_CODEX_HOST_PRODUCED_NO_OBSERVABLE_RESPONSE"
            pair = _blocked_pair(task_id, blocker)
            pair["execution_evidence"] = {
                "control": {"valid_for_pair": False, "errors": [blocker]}
            }
            validate_pair_manifest(pair)
            _write_json(run_root / "pair_manifest.json", pair)
            _write_json(
                run_root / "run_result.json",
                {
                    "status": "BLOCKED_BY_CONCRETE_HOST_LIMITATION",
                    "pair_status": "PROTOCOL_FAILURE",
                    "blockers": [blocker],
                    "control_run": control_result.run_dir,
                },
            )
            print(json.dumps({"status": "BLOCKED_BY_CONCRETE_HOST_LIMITATION", "blockers": [blocker]}))
            return 0

        treatment_adapter = CodexReferenceAdapter(
            workspace=snapshot["treatment"],
            run_root=run_root / "treatment",
            **common,
        )
        treatment_result = ExperimentRunner(treatment_adapter, oracle).run(
            task,
            experiment_id=EXPERIMENT_ID,
            condition=Condition.treatment(),
            run_dir=run_root / "treatment",
        )
        pair = validate_real_paired_runs(
            control_result.run,
            treatment_result.run,
            control_task=task,
            treatment_task=task,
            control_run_dir=control_result.run_dir,
            treatment_run_dir=treatment_result.run_dir,
        )
        validate_pair_manifest(pair.as_dict())
        _write_json(run_root / "pair_manifest.json", pair.as_dict())
        control_evidence = json.loads(
            (Path(control_result.run_dir) / "utility_evidence.json").read_text(encoding="utf-8")
        )
        treatment_evidence = json.loads(
            (Path(treatment_result.run_dir) / "utility_evidence.json").read_text(encoding="utf-8")
        )
        conclusion: UtilityConclusion = __import__(
            "skillnudge.experiment_runner", fromlist=["conclude_first_pair"]
        ).conclude_first_pair(
            pair,
            control_evidence,
            treatment_evidence,
            scope={
                "task_id": task_id,
                "capability": FROZEN_SKILL_ARTIFACT_ID,
                "host": "Codex",
                "environment_hash": environment_hash,
            },
            limitations=[
                "single task",
                "single Codex configuration",
                "internal SkillNudge maintenance task",
                "no generalization beyond this pair",
            ],
        )
        _write_json(run_root / "utility_conclusion.json", conclusion.as_dict())
        result = {
            "status": "FIRST_REAL_CAUSAL_PAIR_COMPLETE" if pair.pair_status == "VALID" else "FIRST_REAL_CAUSAL_PAIR_PROTOCOL_FAILURE",
            "pair_status": pair.pair_status,
            "utility_conclusion": conclusion.conclusion,
            "control_run": control_result.run_dir,
            "treatment_run": treatment_result.run_dir,
            "pair_errors": pair.errors,
        }
        _write_json(run_root / "run_result.json", result)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    finally:
        shutil.rmtree(codex_home.parent, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
