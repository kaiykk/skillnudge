"""Evaluator-only Oracle for the first real SkillNudge causal task."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]

ORACLE_VERSION = "native-planning-contract-discoverability-oracle-v0.1"
EXPECTED_ENUMS = {
    "capability_framing.confidence": ["high", "low", "medium"],
    "intervention_plan.decision": ["clarify", "no_intervention", "search"],
    "intervention_plan.targets[].family": ["integration", "resource", "skill"],
    "intervention_plan.targets[].priority": ["companion", "primary", "secondary"],
    "query_plan.status": ["clarify", "ready", "skipped"],
    "query_plan.queries[].family": ["integration", "resource", "skill"],
    "query_plan.queries[].angle": [
        "capability",
        "operation",
        "outcome",
        "problem",
        "professional_vocabulary",
        "stage",
    ],
}


def _load_contracts(workspace: Path) -> Any:
    module_path = workspace / "src" / "skillnudge" / "planning_contracts.py"
    spec = importlib.util.spec_from_file_location("phase2_oracle_contracts", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("PLANNING_CONTRACTS_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _base_framing(confidence: str) -> dict[str, Any]:
    return {
        "contract": {
            "goal": "Make the native planning contract discoverable",
            "stage": None,
            "blocker": "The host lacks documented enum values.",
            "missing_capabilities": ["contract discoverability"],
            "intended_effect": "Allow valid host-produced planning envelopes.",
            "constraints": [],
            "not_needed": [],
            "uncertainties": [],
        },
        "confidence": confidence,
        "clarification_needed": False,
        "clarification_question": None,
    }


def _intervention(decision: str, family: str = "skill") -> dict[str, Any]:
    if decision in {"no_intervention", "clarify"}:
        return {
            "decision": decision,
            "targets": [],
            "decision_reason": "The host can stop before retrieval.",
        }
    return {
        "decision": decision,
        "targets": [
            {
                "family": family,
                "priority": "primary",
                "rationale": "A direct capability gap is present.",
            }
        ],
        "decision_reason": "Search the planned family.",
    }


def _query(status: str, family: str = "skill", angle: str = "capability") -> dict[str, Any]:
    if status in {"skipped", "clarify"}:
        return {"status": status, "queries": []}
    return {
        "status": "ready",
        "queries": [
            {
                "family": family,
                "angle": angle,
                "semantic_query": "native planning contract discoverability",
                "purpose": "Find the documented capability boundary.",
            }
        ],
    }


def _must_reject(callable_obj: Any, value: Any, label: str, errors: list[str]) -> None:
    try:
        callable_obj(value)
    except Exception:
        return
    errors.append(f"validator accepted invalid {label}")


def _check_contract_docs(workspace: Path) -> list[str]:
    errors: list[str] = []
    skill_path = workspace / ".agents" / "skills" / "skillnudge" / "SKILL.md"
    contract_path = skill_path.parent / "native-contract.md"
    if not skill_path.is_file():
        return ["native Skill contract is missing"]
    if not contract_path.is_file():
        return ["native-contract.md is missing"]
    skill_text = skill_path.read_text(encoding="utf-8")
    contract_text = contract_path.read_text(encoding="utf-8")
    if "native-contract.md" not in skill_text:
        errors.append("SKILL.md does not reference native-contract.md")
    if "skillnudge advise" in skill_text:
        errors.append("public native Skill delegates to standalone advise")
    match = re.search(
        r"## Validator-Comparison Data.*?```json\n(\{.*?\})\n```",
        contract_text,
        re.DOTALL,
    )
    if match is None:
        errors.append("native contract lacks machine-readable enum mapping")
    else:
        try:
            documented = json.loads(match.group(1))
        except json.JSONDecodeError:
            documented = None
        if documented != EXPECTED_ENUMS:
            errors.append("documented enum mapping does not match frozen ground truth")
    for marker in (
        "Required",
        "Optional",
        "`search` requires exactly one `primary` target",
        "Every query family must exist in `intervention_plan.targets`",
        "## Compact Valid Example",
    ):
        if marker not in contract_text:
            errors.append(f"native contract is missing required marker: {marker}")
    return errors


def _check_validator_behavior(workspace: Path) -> list[str]:
    errors: list[str] = []
    try:
        contracts = _load_contracts(workspace)
    except Exception as error:
        return [f"validator import failed: {type(error).__name__}"]

    exported = getattr(contracts, "NATIVE_CONTRACT_ENUMS", None)
    if exported is None:
        errors.append("validator enum exports are missing")
    else:
        normalized = {key: sorted(value) for key, value in exported.items()}
        if normalized != EXPECTED_ENUMS:
            errors.append("validator enum exports drift from frozen ground truth")

    for confidence in EXPECTED_ENUMS["capability_framing.confidence"]:
        try:
            contracts.validate_capability_framing(_base_framing(confidence))
        except Exception as error:
            errors.append(f"valid confidence rejected: {confidence}: {error}")

    for decision in EXPECTED_ENUMS["intervention_plan.decision"]:
        try:
            contracts.validate_intervention_plan(_intervention(decision))
        except Exception as error:
            errors.append(f"valid decision rejected: {decision}: {error}")

    for family in EXPECTED_ENUMS["intervention_plan.targets[].family"]:
        try:
            contracts.validate_intervention_plan(_intervention("search", family))
        except Exception as error:
            errors.append(f"valid target family rejected: {family}: {error}")

    for priority in EXPECTED_ENUMS["intervention_plan.targets[].priority"]:
        plan = _intervention("search")
        if priority == "primary":
            plan["targets"][0]["priority"] = priority
        else:
            plan["targets"].append(
                {
                    "family": "integration",
                    "priority": priority,
                    "rationale": "A distinct optional family.",
                }
            )
        try:
            contracts.validate_intervention_plan(plan)
        except Exception as error:
            errors.append(f"valid target priority rejected: {priority}: {error}")

    for status in EXPECTED_ENUMS["query_plan.status"]:
        try:
            contracts.validate_query_plan(_query(status))
        except Exception as error:
            errors.append(f"valid query status rejected: {status}: {error}")

    for family in EXPECTED_ENUMS["query_plan.queries[].family"]:
        plan = _query("ready", family=family)
        intervention = _intervention("search", family)
        try:
            contracts.validate_query_plan(plan)
            contracts.validate_planning_consistency(intervention, plan)
        except Exception as error:
            errors.append(f"valid query family rejected: {family}: {error}")

    for angle in EXPECTED_ENUMS["query_plan.queries[].angle"]:
        try:
            contracts.validate_query_plan(_query("ready", angle=angle))
        except Exception as error:
            errors.append(f"valid query angle rejected: {angle}: {error}")

    _must_reject(
        contracts.validate_capability_framing,
        _base_framing("invalid"),
        "confidence",
        errors,
    )
    invalid_decision = _intervention("search")
    invalid_decision["decision"] = "invalid"
    _must_reject(
        contracts.validate_intervention_plan,
        invalid_decision,
        "decision",
        errors,
    )
    invalid_family = _intervention("search")
    invalid_family["targets"][0]["family"] = "invalid"
    _must_reject(
        contracts.validate_intervention_plan,
        invalid_family,
        "target family",
        errors,
    )
    invalid_priority = _intervention("search")
    invalid_priority["targets"][0]["priority"] = "invalid"
    _must_reject(
        contracts.validate_intervention_plan,
        invalid_priority,
        "target priority",
        errors,
    )
    invalid_status = _query("ready")
    invalid_status["status"] = "invalid"
    _must_reject(
        contracts.validate_query_plan,
        invalid_status,
        "query status",
        errors,
    )
    invalid_angle = _query("ready")
    invalid_angle["queries"][0]["angle"] = "invalid"
    _must_reject(
        contracts.validate_query_plan,
        invalid_angle,
        "query angle",
        errors,
    )

    two_primary = _intervention("search")
    two_primary["targets"].append(
        {
            "family": "integration",
            "priority": "primary",
            "rationale": "Invalid second primary.",
        }
    )
    _must_reject(
        contracts.validate_intervention_plan,
        two_primary,
        "two primary targets",
        errors,
    )
    duplicate_family = _intervention("search")
    duplicate_family["targets"].append(
        {
            "family": "skill",
            "priority": "secondary",
            "rationale": "Invalid duplicate family.",
        }
    )
    _must_reject(
        contracts.validate_intervention_plan,
        duplicate_family,
        "duplicate target family",
        errors,
    )

    inconsistent_query = _query("ready", family="integration")
    _must_reject(
        lambda value: contracts.validate_planning_consistency(
            _intervention("search", "skill"), value
        ),
        inconsistent_query,
        "cross-stage family mismatch",
        errors,
    )
    _must_reject(
        lambda value: contracts.validate_planning_consistency(
            _intervention("no_intervention"), value
        ),
        _query("ready"),
        "no_intervention ready query plan",
        errors,
    )
    return errors


def _run_regression_suite(workspace: Path) -> tuple[bool, str]:
    command = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        "test_*.py",
        "-v",
    ]
    completed = subprocess.run(
        command,
        cwd=workspace,
        env={
            "PATH": ":".join(filter(None, [str(Path(sys.executable).parent), "/usr/bin", "/bin"])),
            "PYTHONPATH": str(workspace / "src"),
            "LANG": "C.UTF-8",
        },
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    return completed.returncode == 0, f"exit_code={completed.returncode}"


def _run_target_checks(workspace: Path) -> tuple[bool, list[str]]:
    checks: list[str] = []
    checks.extend(_check_contract_docs(workspace))
    checks.extend(_check_validator_behavior(workspace))
    native_path = workspace / "src" / "skillnudge" / "native.py"
    if not native_path.is_file():
        checks.append("native retrieval module is missing")
    return not checks, checks


class NativePlanningContractOracle:
    oracle_version = ORACLE_VERSION

    def __init__(self, *, timeout_seconds: float = 180.0):
        self.timeout_seconds = timeout_seconds
        self.evaluator_config = {
            "oracle_version": ORACLE_VERSION,
            "agent_visibility": "forbidden",
            "historical_target_patch": "forbidden",
            "expected_ground_truth": "frozen-in-evaluator",
            "regression_command": "python3 -m unittest discover -s tests -p test_*.py -v",
        }

    def self_test(self, workspace: str | Path) -> dict[str, Any]:
        path = Path(workspace).resolve()
        target_ok, target_errors = _run_target_checks(path)
        regression_ok, regression_diag = _run_regression_suite(path)
        return {
            "status": "PASS" if regression_diag.startswith("exit_code=0") else "FAIL",
            "target_checks_executed": True,
            "target_baseline_status": "PASS" if target_ok else "EXPECTED_BASELINE_MISS",
            "target_diagnostics": target_errors,
            "regression_status": "PASS" if regression_ok else "FAIL",
            "regression_diagnostics": [regression_diag],
            "oracle_version": ORACLE_VERSION,
        }

    def evaluate(self, task: Any, result: Any) -> Any:
        from skillnudge.experiment_runner import OracleResult

        if not isinstance(result, Mapping):
            return OracleResult(
                success=None,
                regression=None,
                diagnostics=["ORACLE_WORKSPACE_REFERENCE_MISSING"],
                evaluator_valid=False,
                evaluation_environment={"oracle_version": ORACLE_VERSION},
            )
        reference = result.get("workspace_reference")
        if not isinstance(reference, str):
            return OracleResult(
                success=None,
                regression=None,
                diagnostics=["ORACLE_WORKSPACE_REFERENCE_MISSING"],
                evaluator_valid=False,
                evaluation_environment={"oracle_version": ORACLE_VERSION},
            )
        workspace = Path(reference).resolve()
        target_ok, target_errors = _run_target_checks(workspace)
        regression_ok, regression_diag = _run_regression_suite(workspace)
        diagnostics = [
            "target_checks:PASS" if target_ok else "target_checks:FAIL",
            *target_errors,
            f"regression_suite:{regression_diag}",
        ]
        return OracleResult(
            success=target_ok,
            regression=not regression_ok,
            diagnostics=diagnostics,
            tests_passed=2 if target_ok and regression_ok else None,
            target_status="pass" if target_ok else "fail",
            regression_status="pass" if regression_ok else "fail",
            evaluator_valid=True,
            evaluation_environment={
                "oracle_version": ORACLE_VERSION,
                "workspace_reference": str(workspace),
                "agent_visibility": "forbidden",
                "historical_target_patch": "forbidden",
                "hidden_checks": "contract_behavior_and_regression",
            },
        )
