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
test -s "$HOME/.agents/skills/skillnudge/SKILL.md"
test -x "$HOME/.local/bin/skillnudge"
test -s "$HOME/Library/Application Support/SkillNudge/skillnudge.sqlite3" \
    || test -s "$HOME/.local/share/skillnudge/skillnudge.sqlite3"
(
    cd "$target_repo"
    help_output="$(skillnudge --help)"
    case "$help_output" in
        *experiment*)
            printf 'ERROR: Phase 2 experiment entrypoint leaked into user-facing CLI\n' >&2
            exit 1
            ;;
    esac
    skillnudge bootstrap --json >/dev/null
)

printf 'Clean installation, CLI discovery, default index, and unrelated-repository checks passed.\n'
printf 'Smoke root: %s\n' "$temp_root"
