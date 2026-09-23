#!/usr/bin/env bash
# Pull upstream changes into a vendored skill (added via git subtree, see
# vendor.json). Preserves upstream history in the merge commit.
#
# Usage: ./vendor-update.sh <name>          # e.g. frontend-design
#        ./vendor-update.sh --all
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$repo"

update_one() {
  local name="$1"
  local entry repo_url src_prefix target_prefix
  entry=$(jq -e ".\"$name\"" vendor.json) || {
    echo "unknown vendored skill: $name (see vendor.json)" >&2
    exit 1
  }
  repo_url=$(jq -r '.repo' <<<"$entry")
  src_prefix=$(jq -r '.source_prefix' <<<"$entry")
  target_prefix=$(jq -r '.target_prefix' <<<"$entry")

  echo "== $name: $repo_url ($src_prefix -> $target_prefix)"

  local tmp
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN

  git clone -q "$repo_url" "$tmp/src"
  (
    cd "$tmp/src"
    git subtree split -q --prefix="$src_prefix" -b split-branch
  )

  local remote="vendor-tmp-$name"
  git remote remove "$remote" 2>/dev/null || true
  git remote add "$remote" "$tmp/src"
  git fetch -q "$remote" split-branch
  git subtree pull -q --prefix="$target_prefix" "$remote" split-branch -m "vendor: update $name from upstream"
  git remote remove "$remote"

  echo "== $name updated. LICENSE/ATTRIBUTION.md in $target_prefix/ are hand-maintained — re-check them if upstream's own LICENSE changed."
}

if [[ "${1:-}" == "--all" ]]; then
  for name in $(jq -r 'keys[]' vendor.json); do
    update_one "$name"
  done
elif [[ -n "${1:-}" ]]; then
  update_one "$1"
else
  echo "usage: $0 <name>|--all   (names: $(jq -r 'keys | join(", ")' vendor.json))" >&2
  exit 1
fi
