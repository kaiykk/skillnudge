#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_bin="${PYTHON:-python3}"
install_root="${SKILLNUDGE_INSTALL_DIR:-$HOME/.local/share/skillnudge}"
venv_dir="$install_root/venv"
package_dir="$install_root/package"
bin_dir="$HOME/.local/bin"
launcher="$bin_dir/skillnudge"
skill_source="$repo_root/.agents/skills/skillnudge"
skill_target="$HOME/.agents/skills/skillnudge"

command -v "$python_bin" >/dev/null 2>&1 || {
    printf 'ERROR: Python is required: %s\n' "$python_bin" >&2
    exit 1
}
test -f "$repo_root/pyproject.toml" || {
    printf 'ERROR: installer must run from a SkillNudge source copy\n' >&2
    exit 1
}
test -f "$skill_source/SKILL.md" || {
    printf 'ERROR: source Codex Skill is missing\n' >&2
    exit 1
}

mkdir -p "$install_root" "$bin_dir" "$HOME/.agents/skills"
"$python_bin" -m venv "$venv_dir"
venv_python="$venv_dir/bin/python"
test -x "$venv_python" || {
    printf 'ERROR: isolated Python was not created\n' >&2
    exit 1
}

# The dogfood installer must work in a fresh Python venv even when the
# interpreter does not bundle setuptools. Copying the dependency-free package
# keeps the install offline-safe while leaving pyproject.toml available for
# standard package installers.
rm -rf "$package_dir"
mkdir -p "$package_dir"
cp -R "$repo_root/src/skillnudge" "$package_dir/"
test -f "$package_dir/skillnudge/__init__.py" || {
    printf 'ERROR: installed SkillNudge package is incomplete\n' >&2
    exit 1
}

cli_launcher="$venv_dir/bin/skillnudge"
printf '%s\n' \
    '#!/usr/bin/env bash' \
    'set -euo pipefail' \
    "export PYTHONPATH=$(printf '%q' "$package_dir")" \
    "exec $(printf '%q' "$venv_python") -m skillnudge \"\$@\"" \
    >"$cli_launcher"
chmod 755 "$cli_launcher"

"$cli_launcher" bootstrap
ln -sfn "$cli_launcher" "$launcher"
rm -rf "$skill_target"
mkdir -p "$skill_target"
cp -R "$skill_source/." "$skill_target/"

"$launcher" --help >/dev/null
"$launcher" bootstrap --json >/dev/null
"$launcher" advise --help >/dev/null
test -s "$skill_target/SKILL.md"
test -x "$launcher"

printf 'SkillNudge installed.\n'
printf 'CLI: %s\n' "$launcher"
printf 'Codex Skill: %s\n' "$skill_target"
printf 'Data directory: %s\n' "$("$launcher" bootstrap --json | "$venv_python" -c 'import json,sys; print(json.load(sys.stdin)["data_dir"])')"
printf 'Ensure %s is on PATH before using the bare skillnudge command.\n' "$bin_dir"
