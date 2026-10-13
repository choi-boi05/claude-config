#!/usr/bin/env bash
# Run dead-code, duplicate and complexity analyzers; print findings for the scope.
# Usage: scan.sh [--full] [--base <git ref>]
#   default scope: files changed since upstream (@{u}) plus uncommitted/untracked files
set -uo pipefail
FULL=0; BASE=""
while [ $# -gt 0 ]; do case "$1" in
  --full) FULL=1 ;; --base) BASE="$2"; shift ;; *) echo "unknown arg $1" >&2; exit 2 ;; esac; shift; done
ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "not a git repo" >&2; exit 2; }
cd "$ROOT"
CAP=80   # max lines per section, to keep output small
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

if [ "$FULL" = 1 ]; then git ls-files > "$TMP/scope"; SCOPE_DESC="whole repo"
else
  [ -z "$BASE" ] && BASE="$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || echo HEAD)"
  { git diff --name-only "$BASE"...HEAD 2>/dev/null; git diff --name-only HEAD; git ls-files --others --exclude-standard; } | sort -u > "$TMP/scope"
  SCOPE_DESC="changed since $BASE + uncommitted"
fi
# drop deleted files
while read -r f; do [ -f "$f" ] && echo "$f"; done < "$TMP/scope" > "$TMP/files"
grep -E '\.py$' "$TMP/files" > "$TMP/py" || true
echo "== Scope: $SCOPE_DESC ($(wc -l < "$TMP/files" | tr -d ' ') files, $(wc -l < "$TMP/py" | tr -d ' ') Python)"
[ -s "$TMP/files" ] || { echo "Nothing in scope. Pass --full or --base <ref>."; exit 0; }

KEEP=".cleanup/vulture_whitelist.py"   # per-project names that are used dynamically
if [ -s "$TMP/py" ]; then
  echo "== Unused imports / variables / redefinitions (ruff F401 F811 F841 F541)"
  if command -v ruff >/dev/null; then
    xargs ruff check --no-cache --isolated --select F401,F811,F841,F541 --output-format concise < "$TMP/py" 2>&1 | grep -v '^Found\|^\[\*\]\|^All checks' | head -$CAP
  else echo "ruff not installed"; fi

  echo "== Complexity (ruff C901 >12, SIM simplifications)"
  if command -v ruff >/dev/null; then
    xargs ruff check --no-cache --isolated --select C901,SIM --config 'lint.mccabe.max-complexity=12' --output-format concise < "$TMP/py" 2>&1 | grep -v '^Found\|^\[\*\]\|^All checks' | head -$CAP
  fi

  echo "== Dead functions / classes / variables (vulture, whole repo, filtered to scope)"
  if command -v vulture >/dev/null; then
    ALLPY="$(git ls-files '*.py')"
    # shellcheck disable=SC2086
    vulture $ALLPY $( [ -f "$KEEP" ] && echo "$KEEP" ) --min-confidence 60 2>/dev/null | grep -F -f "$TMP/py" | head -$CAP
  else echo "vulture not installed"; fi
fi

echo "== Duplicate blocks (jscpd, whole repo, pairs touching scope)"
if command -v npx >/dev/null; then
  npx --yes jscpd@4.0.5 --silent --min-tokens 60 --reporters json --output "$TMP/jscpd" \
    --ignore "**/node_modules/**,**/.git/**,**/data/**,**/drive/**,**/applications/**,**/reports/**" . >/dev/null 2>&1
  python3 - "$TMP/jscpd/jscpd-report.json" "$TMP/files" "$FULL" "$CAP" <<'PY'
import json, sys
rep, scope, full, cap = sys.argv[1], set(open(sys.argv[2]).read().split()), sys.argv[3] == "1", int(sys.argv[4])
try: dups = json.load(open(rep)).get("duplicates", [])
except Exception: print("jscpd produced no report"); sys.exit()
n = 0
for d in dups:
    a, b = d["firstFile"], d["secondFile"]
    if full or a["name"] in scope or b["name"] in scope:
        print(f'{a["name"]}:{a["start"]}-{a["end"]}  ==  {b["name"]}:{b["start"]}-{b["end"]}  ({d["lines"]} lines)')
        n += 1
        if n >= cap: break
print(f"{n} duplicate block(s)" if n else "none")
PY
else echo "npx not installed; skipped"; fi

if [ -f package.json ]; then
  echo "== Unused files / exports / dependencies (knip)"
  if out="$(npx --yes knip@5.27.0 --no-progress 2>&1)"; then echo "${out:-none}" | grep -v "npm warn" | head -$CAP
  else echo "knip failed to run (often a Node/TypeScript version mismatch); skipped. Last line: $(echo "$out" | grep -v '^\s*at ' | tail -1)"; fi
fi
