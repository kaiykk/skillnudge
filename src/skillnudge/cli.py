"""Minimal CLI for validating control-plane records."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Callable

from .evidence import validate_session_evidence
from .lineage import apply_human_decision, validate_candidate
from .operator import validate_evolution_request, validate_operator_result
from .skill import validate_skill_version


def _read_stdin() -> Any:
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError as error:
        raise ValueError(f"stdin must contain one JSON object: {error.msg}") from error


def _emit(value: Any) -> int:
    json.dump(value, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


def _validator(kind: str) -> Callable[[Any], dict[str, Any]]:
    validators = {
        "skill": validate_skill_version,
        "evidence": validate_session_evidence,
        "request": validate_evolution_request,
        "operator-result": validate_operator_result,
        "candidate": validate_candidate,
    }
    try:
        return validators[kind]
    except KeyError as error:
        raise ValueError(f"unknown record kind: {kind}") from error


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="skillnudge",
        description="Validate and carry traceable Skill evolution records.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate", help="validate one JSON record")
    validate.add_argument("kind", choices=["skill", "evidence", "request", "operator-result", "candidate"])
    validate.add_argument("--stdin", action="store_true", required=True)
    decide = subparsers.add_parser("candidate-decide", help="record one Human candidate decision")
    decide.add_argument("decision", choices=["ACCEPTED", "REJECTED", "ROLLED_BACK", "RETIRED"])
    decide.add_argument("--stdin", action="store_true", required=True)
    args = parser.parse_args(argv)
    try:
        value = _read_stdin()
        if args.command == "validate":
            return _emit(_validator(args.kind)(value))
        return _emit(apply_human_decision(value, args.decision))
    except (ValueError, KeyError, TypeError) as error:
        print(f"skillnudge: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
