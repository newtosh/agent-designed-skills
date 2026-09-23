#!/usr/bin/env bash
# Symlinks every skills/<name> into ~/.claude/skills/<name>, and every
# hooks/<file> into ~/.claude/hooks/<file>. Re-run after `git pull` to pick
# up new/renamed skills or hooks; safe to re-run.
#
# Hook *wiring* (which tool calls trigger which hook) still lives in
# ~/.claude/settings.json — see README.md for the PreToolUse block to add.
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

link_all() {
  local src_root="$1" target_root="$2"
  mkdir -p "$target_root"
  for src in "$src_root"/*; do
    [[ -e "$src" ]] || continue
    name="$(basename "$src")"
    target="$target_root/$name"
    if [[ -L "$target" || ! -e "$target" ]]; then
      ln -sfn "$src" "$target"
      echo "linked $name -> $target"
    else
      echo "skip $name: $target exists and is not a symlink" >&2
    fi
  done
}

link_all "$repo/skills" "${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
link_all "$repo/hooks" "${CLAUDE_HOOKS_DIR:-$HOME/.claude/hooks}"
