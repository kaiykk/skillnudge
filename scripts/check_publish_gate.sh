#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

is_protected_path() {
    case "$1" in
        .env|.env.*|*/.env|*/.env.*|config/*.local.env|config/*secret*|config/*credential*)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

failed=0
while IFS= read -r path; do
    [[ -z "$path" ]] && continue
    if is_protected_path "$path"; then
        printf 'ERROR: protected configuration is tracked or staged: %s\n' "$path" >&2
        failed=1
    fi
done < <(git ls-files && git diff --cached --name-only)

for path in config/*.local.env; do
    [[ -e "$path" ]] || continue
    if ! git check-ignore --quiet "$path"; then
        printf 'ERROR: local provider configuration is not ignored: %s\n' "$path" >&2
        failed=1
    fi
done

if (( failed )); then
    printf '%s\n' 'Publish gate failed. Remove protected configuration from Git and fix ignore rules before pushing.' >&2
    exit 1
fi

printf '%s\n' 'Publish gate passed: protected provider and secret configuration is excluded from Git.'
