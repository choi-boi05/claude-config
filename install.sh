#!/usr/bin/env bash
# Link the shared Claude Code setup into ~/.claude and ~/.config/git.
# Usage: ./install.sh [--dry-run]   (safe to re-run; existing files are backed up first)
set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1
BACKUP="$HOME/.claude/backups/claude-config-$(date +%Y%m%d-%H%M%S)"

run() { if [ "$DRY" = 1 ]; then echo "  would: $*"; else "$@"; fi; }

backup() {  # move an existing file/dir/link out of the way
  local target="$1" rel="${1#$HOME/}"
  run mkdir -p "$BACKUP/$(dirname "$rel")"
  run mv "$target" "$BACKUP/$rel"
  echo "  backed up $target"
}

link() {  # link <repo path> <target>
  local src="$REPO/$1" target="$2"
  if [ -L "$target" ] && [ "$(readlink "$target")" = "$src" ]; then echo "ok      $target"; return; fi
  if [ -e "$target" ] || [ -L "$target" ]; then backup "$target"; fi
  run mkdir -p "$(dirname "$target")"
  run ln -s "$src" "$target"
  echo "linked  $target -> $1"
}

seed() {  # copy a starter file only if the target doesn't exist yet
  local src="$REPO/$1" target="$2"
  if [ -e "$target" ]; then echo "kept    $target (machine-specific, not overwritten)"; return; fi
  run mkdir -p "$(dirname "$target")"
  run cp "$src" "$target"
  echo "seeded  $target from $1"
}

echo "== Shared files (linked to the repo)"
link core/CLAUDE.core.md "$HOME/.claude/CLAUDE.core.md"
link core/hooks "$HOME/.claude/hooks"
for s in "$REPO"/core/skills/*/; do
  name="$(basename "$s")"
  link "core/skills/$name" "$HOME/.claude/skills/$name"
done
for f in "$REPO"/core/agents/*.md; do
  name="$(basename "$f")"
  link "core/agents/$name" "$HOME/.claude/agents/$name"
done
link core/git/pre-commit "$HOME/.config/git/hooks/pre-commit"
link core/git/ignore "$HOME/.config/git/ignore"

echo "== Machine-specific files (copied once, then edited per machine)"
seed templates/CLAUDE.md "$HOME/.claude/CLAUDE.md"
seed templates/writing.md "$HOME/.claude/preferences/writing.md"
seed core/settings.json "$HOME/.claude/settings.json"
if [ -f "$HOME/.claude/settings.json" ] && ! cmp -s "$REPO/core/settings.json" "$HOME/.claude/settings.json"; then
  echo "  note: settings.json differs from the repo copy; review with: diff $REPO/core/settings.json ~/.claude/settings.json"
fi
if [ -f "$HOME/.claude/CLAUDE.md" ] && ! grep -q '@~/.claude/CLAUDE.core.md' "$HOME/.claude/CLAUDE.md"; then
  echo "  WARNING: ~/.claude/CLAUDE.md does not import the shared rules; add a line: @~/.claude/CLAUDE.core.md"
fi

echo "== Git settings"
gitset() {
  local key="$1" want="$2" have
  have="$(git config --global --get "$key" || true)"
  if [ "$have" = "$want" ]; then echo "ok      git $key"
  elif [ -z "$have" ]; then run git config --global "$key" "$want"; echo "set     git $key = $want"
  else echo "  WARNING: git $key is already '$have' (maybe set by IT); left unchanged"; fi
}
gitset core.hooksPath "$HOME/.config/git/hooks"
gitset core.excludesfile "$HOME/.config/git/ignore"

echo "== Tools (not installed by this script)"
for t in git python3 jq gitleaks; do
  if command -v "$t" >/dev/null 2>&1; then echo "ok      $t"; else echo "  MISSING $t (hooks warn or skip without it; may need IT to install)"; fi
done

if [ "$DRY" = 1 ]; then echo "Dry run: nothing changed."; else echo "Done. Backups (if any): $BACKUP"; fi
echo "Next: reinstall plugins with /plugin if this machine needs them (mattpocock-skills, product-management), then check /model, /hooks and /context. On Bedrock, see README (model aliases)."
