#!/usr/bin/env bash
# Pull upstream changes into a vendored skill (added via git subtree, see
# vendor.json). Preserves upstream history in the merge commit.
#
# Usage: ./vendor-update.sh <name>          # e.g. frontend-design
#        ./vendor-update.sh --all
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$repo"

_vendor_tmp=""
_vendor_remote=""
_vendor_remote_added=0

vendor_cleanup() {
  if [[ "${_vendor_remote_added}" == 1 ]]; then
    git remote remove "$_vendor_remote" 2>/dev/null || true
    _vendor_remote_added=0
  fi
  case "${_vendor_tmp}" in
    /tmp/tmp.*|/var/tmp/tmp.*)
      rm -rf -- "$_vendor_tmp"
      ;;
  esac
  _vendor_tmp=""
}
trap vendor_cleanup EXIT

update_one() {
  local name="$1"
  local entry repo_url src_prefix target_prefix
  if ! [[ "$name" =~ ^[a-z0-9-]+$ ]]; then
    echo "vendor-update.sh: skill name must match [a-z0-9-]+" >&2
    exit 1
  fi
  entry=$(jq -e --arg name "$name" '.[$name]' vendor.json) || {
    echo "unknown vendored skill: $name (see vendor.json)" >&2
    exit 1
  }
  repo_url=$(jq -r '.repo' <<<"$entry")
  src_prefix=$(jq -r '.source_prefix' <<<"$entry")
  target_prefix=$(jq -r '.target_prefix' <<<"$entry")
  if ! [[ "$repo_url" =~ ^https://github.com/[^[:space:]]+$ ]]; then
    echo "vendor-update.sh: repo must be an https GitHub URL" >&2
    exit 1
  fi
  if ! [[ "$target_prefix" =~ ^skills/[a-z0-9-]+$ ]]; then
    echo "vendor-update.sh: target_prefix must be skills/<name>" >&2
    exit 1
  fi
  if [[ -n "$(git status --porcelain)" ]]; then
    echo "vendor-update.sh: working tree is not clean; commit or stash first" >&2
    exit 1
  fi

  echo "== $name: $repo_url ($src_prefix -> $target_prefix)"

  _vendor_tmp="$(mktemp -d)"
  case "${_vendor_tmp}" in
    /tmp/tmp.*|/var/tmp/tmp.*) ;;
    *)
      rm -rf -- "$_vendor_tmp"
      _vendor_tmp=""
      echo "vendor-update.sh: unexpected temp path" >&2
      exit 1
      ;;
  esac
  _vendor_remote="vendor-tmp-${name}-$$"
  if git remote get-url "$_vendor_remote" >/dev/null 2>&1; then
    echo "vendor-update.sh: remote ${_vendor_remote} already exists" >&2
    exit 1
  fi

  git clone -q -- "$repo_url" "$_vendor_tmp/src"
  (
    cd "$_vendor_tmp/src"
    git subtree split -q --prefix="$src_prefix" -b split-branch
  )

  git remote add "$_vendor_remote" "$_vendor_tmp/src"
  _vendor_remote_added=1
  git fetch -q "$_vendor_remote" split-branch
  if ! git subtree pull -q --prefix="$target_prefix" "$_vendor_remote" split-branch -m "vendor: update $name from upstream"; then
    git merge --abort >/dev/null 2>&1 || true
    exit 1
  fi

  vendor_cleanup
  echo "== $name updated. LICENSE/ATTRIBUTION.md in $target_prefix/ are hand-maintained — re-check them if upstream's own LICENSE changed."
}

if [[ "${1:-}" == "--all" ]]; then
  while IFS= read -r name; do
    [[ -n "$name" ]] || continue
    update_one "$name"
  done < <(jq -r 'keys[]' vendor.json)
elif [[ -n "${1:-}" ]]; then
  update_one "$1"
else
  echo "usage: $0 <name>|--all   (names: $(jq -r 'keys | join(", ")' vendor.json))" >&2
  exit 1
fi
