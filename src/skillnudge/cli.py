"""Command line entry point for the small SkillNudge product path."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys
from typing import Any

from .model import ModelError, content_sha256, quick_improve


def _json_dump(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def _read_proposal(args: argparse.Namespace, request: dict[str, Any]) -> dict[str, Any] | None:
    if args.proposal_json and args.proposer_command:
        raise ModelError("use only one of --proposal-json and --proposer-command")
    if args.proposal_json:
        path = Path(args.proposal_json)
        if str(path) == "-":
            return json.load(sys.stdin)
        return json.loads(path.read_text(encoding="utf-8"))
    if args.proposer_command:
        command = shlex.split(args.proposer_command)
        if not command:
            raise ModelError("--proposer-command cannot be empty")
        try:
            completed = subprocess.run(
                command, input=json.dumps(request, ensure_ascii=False),
                capture_output=True, text=True, timeout=args.proposer_timeout, check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ModelError(f"proposer command unavailable: {exc}") from exc
        if completed.returncode != 0:
            raise ModelError(f"proposer command failed with exit code {completed.returncode}")
        try:
            return json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise ModelError(f"proposer command returned invalid JSON: {exc}") from exc
    return None


def _load_source(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    path = Path(args.skill).expanduser()
    if path.is_symlink() or not path.is_file():
        raise ModelError("--skill must point to a regular, non-symlink file")
    content = path.read_text(encoding="utf-8")
    skill_id = args.skill_id or path.stem
    version = args.version or "v1"
    source = {
        "skill_id": skill_id, "version": version, "content": content,
        "sha256": content_sha256(content), "source": {"kind": "file", "ref": str(path.resolve())},
        "parent_version": None,
    }
    evidence_hash = hashlib.sha256(f"{args.failure}\n{args.feedback}".encode("utf-8")).hexdigest()[:16]
    evidence = {
        "session_id": args.session_id or f"quick-improve:{evidence_hash}",
        "trace_ref": args.trace_ref or f"file://{path.resolve()}",
        "feedback_refs": args.feedback_ref or [f"quick-improve:feedback:{evidence_hash}"],
        "observed_summary": f"failure: {args.failure}; feedback: {args.feedback}",
    }
    return source, evidence


def _quick_improve(args: argparse.Namespace) -> int:
    source, evidence = _load_source(args)
    request = {
        "schema": "skillnudge.quick-improve.request.v1",
        "skill_path": str(Path(args.skill).expanduser().resolve()),
        "source_skill": {"skill_id": source["skill_id"], "version": source["version"], "sha256": source["sha256"]},
        "evidence": evidence, "failure": args.failure, "feedback": args.feedback,
        "method": {
            "diagnose": "identify one observable failure mechanism",
            "edit": "propose one bounded targeted edit",
            "human_boundary": "return a candidate only; do not activate it",
        },
    }
    proposal = _read_proposal(args, request)
    if proposal is None:
        _json_dump({
            "schema": "skillnudge.quick-improve.result.v1", "status": "NEEDS_HOST_PROPOSAL",
            "request": request, "source_modified": False,
            "message": "Host Agent must return one diagnosis and one bounded candidate edit; no Skill was changed.",
        })
        return 0
    if args.candidate_file:
        proposal = dict(proposal)
        proposal["candidate_content"] = Path(args.candidate_file).read_text(encoding="utf-8")
    candidate_content = proposal.get("candidate_content")
    if not isinstance(candidate_content, str):
        raise ModelError("proposal must contain candidate_content or use --candidate-file")
    candidate_hash = content_sha256(candidate_content)
    candidate_id = args.candidate_id or f"{source['skill_id']}-{candidate_hash[:12]}"
    candidate_version = args.candidate_version or f"{source['version']}-candidate-{candidate_hash[:8]}"
    staging_dir = None if args.no_stage else args.staging_dir
    if staging_dir is None and not args.no_stage:
        staging_dir = str(Path(args.skill).expanduser().parent / ".skillnudge" / "staging" / candidate_id)
    result = quick_improve(
        source, skill_path=args.skill, failure=args.failure, feedback=args.feedback,
        evidence=evidence, proposal=proposal, candidate_id=candidate_id,
        candidate_version=candidate_version, operator_ref=args.operator_ref, staging_dir=staging_dir,
    )
    _json_dump(result)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skillnudge")
    subparsers = parser.add_subparsers(dest="command", required=True)
    improve = subparsers.add_parser("quick-improve", help="propose one reviewable Skill edit")
    improve.add_argument("--skill", required=True, help="path to the source SKILL.md")
    improve.add_argument("--failure", required=True, help="observable failure")
    improve.add_argument("--feedback", required=True, help="user correction or feedback")
    improve.add_argument("--skill-id")
    improve.add_argument("--version")
    improve.add_argument("--session-id")
    improve.add_argument("--trace-ref")
    improve.add_argument("--feedback-ref", action="append")
    improve.add_argument("--proposal-json", help="Host Agent proposal JSON path, or - for stdin")
    improve.add_argument("--proposer-command", help="command that reads request JSON and returns proposal JSON")
    improve.add_argument("--proposer-timeout", type=float, default=120.0)
    improve.add_argument("--candidate-file", help="read candidate_content from this file")
    improve.add_argument("--candidate-id")
    improve.add_argument("--candidate-version")
    improve.add_argument("--operator-ref", default="host-agent:quick-improve")
    improve.add_argument("--staging-dir")
    improve.add_argument("--no-stage", action="store_true")
    improve.set_defaults(handler=_quick_improve)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except (ModelError, OSError, json.JSONDecodeError) as exc:
        _json_dump({"schema": "skillnudge.quick-improve.result.v1", "status": "ERROR", "error": str(exc)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
