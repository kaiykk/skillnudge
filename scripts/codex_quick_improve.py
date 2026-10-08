#!/usr/bin/env python3
"""Use the local Codex Host as the semantic Quick Improve proposer.

This is a deliberately thin adapter for ``skillnudge --proposer-command``.
SkillNudge still validates the returned proposal and owns staging; Codex only
reads the source Skill and proposes one bounded edit.
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "diagnosis",
        "change_summary",
        "candidate_content",
        "validation_status",
        "validation_basis",
    ],
    "properties": {
        "diagnosis": {"type": "string", "description": "Observable failure mechanism."},
        "change_summary": {"type": "string", "description": "One bounded edit in plain language."},
        "candidate_content": {
            "type": "string",
            "description": "The complete replacement contents of SKILL.md, including unchanged content and the one edit. Never return a patch or an instruction.",
        },
        "validation_status": {"type": "string", "enum": ["UNVERIFIED"]},
        "validation_basis": {"type": "string"},
    },
}


def main() -> int:
    request = json.load(sys.stdin)
    skill_path = Path(request["skill_path"]).expanduser().resolve()
    codex = shutil.which("codex") or "/Users/kai/.local/bin/codex"
    prompt = f"""
You are the semantic Host Agent for SkillNudge Quick Improve.

Read the source Skill at {skill_path}.
The observable failure is:
{request['failure']}

The user's correction or expected behavior is:
{request['feedback']}

Diagnose the concrete failure mechanism and propose exactly one bounded,
targeted edit to the Skill. Preserve its purpose and do not rewrite it
wholesale. The candidate_content field MUST contain the complete replacement
contents of the original SKILL.md: keep the YAML frontmatter and every
unchanged section, and apply only the one targeted edit. Do not put a patch,
an insertion instruction, or a summary in candidate_content. Return only the
JSON object required by the output schema. The candidate is not validated or
activated in this call, so validation_status must be UNVERIFIED and
validation_basis must say that independent validation was not run.
""".strip()
    with tempfile.TemporaryDirectory(prefix="skillnudge-codex-") as directory:
        root = Path(directory)
        schema_path = root / "proposal.schema.json"
        output_path = root / "proposal.json"
        schema_path.write_text(json.dumps(SCHEMA), encoding="utf-8")
        completed = subprocess.run(
            [
                codex,
                "exec",
                "--ephemeral",
                "--sandbox",
                "read-only",
                "--skip-git-repo-check",
                "--cd",
                str(skill_path.parent),
                "--output-schema",
                str(schema_path),
                "--output-last-message",
                str(output_path),
                "-",
            ],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=300,
            check=False,
        )
        if completed.returncode != 0:
            sys.stderr.write(completed.stderr)
            return completed.returncode or 1
        try:
            proposal = json.loads(output_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            sys.stderr.write(f"Codex did not return a valid proposal JSON: {exc}\n")
            return 1
        print(json.dumps(proposal, ensure_ascii=False))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
