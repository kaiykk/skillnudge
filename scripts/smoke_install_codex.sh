#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
temp_root="$(mktemp -d "${TMPDIR:-/tmp}/skillnudge-install-smoke.XXXXXX")"
trap 'rm -rf "$temp_root"' EXIT

source_copy="$temp_root/source"
target_repo="$temp_root/unrelated-repository"
isolated_home="$temp_root/home"
mkdir -p "$source_copy" "$target_repo" "$isolated_home"

tar -C "$repo_root" \
    --exclude='.git' \
    --exclude='runs' \
    --exclude='config/*.local.env' \
    --exclude='config/*secret*' \
    --exclude='config/*credential*' \
    -cf - . | tar -C "$source_copy" -xf -
git -C "$target_repo" init -q -b main
git -C "$target_repo" config user.email smoke@skillnudge.local
git -C "$target_repo" config user.name "SkillNudge Smoke"

HOME="$isolated_home" \
SKILLNUDGE_INSTALL_DIR="$isolated_home/.local/share/skillnudge" \
"$source_copy/scripts/install_codex.sh" >/dev/null

export HOME="$isolated_home"
export PATH="$HOME/.local/bin:$PATH"
installed_python="$isolated_home/.local/share/skillnudge/venv/bin/python"
test -s "$HOME/.agents/skills/skillnudge/SKILL.md"
test -x "$HOME/.local/bin/skillnudge"
test -x "$installed_python"
if grep -Fq 'skillnudge advise' "$HOME/.agents/skills/skillnudge/SKILL.md"; then
    printf '%s\n' 'ERROR: public Skill still delegates Native Mode to advise' >&2
    exit 1
fi
(
    cd "$target_repo"
    help_output="$(skillnudge --help)"
    case "$help_output" in
        *experiment*)
            printf 'ERROR: Phase 2 experiment entrypoint leaked into user-facing CLI\n' >&2
            exit 1
            ;;
    esac
    skillnudge retrieve --help >/dev/null
    bootstrap_json="$(skillnudge bootstrap --json)"
    database_path="$(printf '%s' "$bootstrap_json" | "$installed_python" -c '
import json
import sys

result = json.load(sys.stdin)
if result.get("corpus_version") != "public-corpus-v2-2026-09-20":
    raise SystemExit("ERROR: installed corpus version is not the pinned public corpus")
print(result["database_path"])
')"
    "$installed_python" - "$database_path" <<'PY' || {
import sqlite3
import sys

with sqlite3.connect(sys.argv[1]) as connection:
    count = connection.execute("SELECT COUNT(*) FROM skills").fetchone()[0]
if count < 50:
    raise SystemExit("ERROR: installed corpus contains fewer than 50 records")
PY
        printf '%s\n' 'ERROR: unable to validate installed bootstrap metadata' >&2
        exit 1
    }
    data_dir="$(printf '%s' "$bootstrap_json" | "$installed_python" -c '
import json
import sys
print(json.load(sys.stdin)["data_dir"])
')"
    test -s "$data_dir/skillnudge.sqlite3"
    test -s "$data_dir/bootstrap.json"
    (
    unset DEEPSEEK_API_KEY
    unset SKILLNUDGE_MODEL
    unset SKILLNUDGE_MODEL_API_KEY
    unset SKILLNUDGE_MODEL_BASE_URL
    unset SKILLNUDGE_MODEL_TIMEOUT_SECONDS
    unset SKILLNUDGE_MODEL_TEMPERATURE
    unset SKILLNUDGE_MODEL_TOP_P
    unset SKILLNUDGE_MODEL_SEED
    unset SKILLNUDGE_MODEL_MAX_OUTPUT_TOKENS
    unset SKILLNUDGE_MODEL_REASONING_EFFORT
    "$installed_python" - <<'PY' | "$HOME/.local/bin/skillnudge" retrieve --stdin >/dev/null
import json
import sys

print(json.dumps({
    "schema_version": "native.planning-envelope.v0",
    "input": {
        "raw_request": "Find guidance for a vague interface task.",
        "project_context": None,
        "current_stage": None,
    },
    "capability_framing": {
        "contract": {
            "goal": "Improve the interface task",
            "stage": "exploration",
            "blocker": "The task needs reusable guidance.",
            "missing_capabilities": ["interface guidance"],
            "intended_effect": "Make the next step more concrete.",
            "constraints": [],
            "not_needed": [],
            "uncertainties": [],
        },
        "confidence": "medium",
        "clarification_needed": False,
        "clarification_question": None,
    },
    "intervention_plan": {
        "decision": "search",
        "targets": [{
            "family": "skill",
            "priority": "primary",
            "rationale": "A reusable skill may address the blocker.",
        }],
        "decision_reason": "Search the skill family.",
    },
    "query_plan": {
        "status": "ready",
        "queries": [{
            "family": "skill",
            "angle": "capability",
            "semantic_query": "interface guidance visual hierarchy",
            "purpose": "Find reusable interface guidance.",
        }],
    },
}))
PY
    )
)

"$installed_python" - "$source_copy/src/skillnudge/data/default_corpus.json" <<'PY'
import hashlib
import json
import sys

corpus_path = sys.argv[1]
records = json.loads(open(corpus_path, encoding="utf-8").read())
target = next(
    record
    for record in records
    if record.get("candidate_id") == "nextlevelbuilder/ui-ux-pro-max-skill::ui-ux-pro-max"
)
if target.get("source_revision") != "5fe9624cb844266aeae50d8a3f24c403bd456c16":
    raise SystemExit("ERROR: D001 source revision is not pinned")
body_hash = hashlib.sha256(target["body"].rstrip("\n").encode("utf-8")).hexdigest()
if body_hash != "b6627ae64792f475731d3fb0643d4521370c26dbc447fd91675e4f446aa0f3c3":
    raise SystemExit("ERROR: D001 body hash does not match the frozen artifact")
if target.get("content_sha256") != body_hash:
    raise SystemExit("ERROR: D001 content_sha256 is inconsistent")
PY

printf 'Clean installation, CLI discovery, default index, and unrelated-repository checks passed.\n'
printf 'Smoke root: %s\n' "$temp_root"
