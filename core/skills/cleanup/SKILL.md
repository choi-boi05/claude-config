---
name: cleanup
description: "Find and fix dead code, duplicate logic, unused files or dependencies, and needless complexity added by recent work. Use when Chase types /cleanup, or before committing a finished feature. Args: `--full` (whole repo), `--base REF` (changes since a commit or branch)."
---

# Cleanup

Goal: leave the code smaller and simpler with the same behavior. Analyzers find candidates; you verify them; Chase approves; tests prove it.

## 1. Scan
Run `bash ~/.claude/skills/cleanup/scan.sh [args]` from the project root. Default scope is everything changed since the last push plus uncommitted files. Don't paste the raw output back; summarize it. Any section that printed "not installed", "skipped" or "no report" (tool missing or not applicable) is reported as "not checked", never as clean.

## 2. Review the changed code yourself
Read the diff in scope (`git diff <base>...HEAD` plus uncommitted). Look for what analyzers miss, using the "Writing code" rules in `~/.claude/CLAUDE.core.md`:
- new code that repeats an existing helper, script or pattern in the repo (grep for it);
- abstractions, options, wrappers, config or "for later" code with one use;
- leftover debug prints, commented-out code, stale TODOs, files nothing references.

## 3. Verify every candidate (false positives are the main risk)
A name is only dead if nothing uses it. Before listing it, grep the whole repo, including `.md`, `.json`, `.yml`, `.sh` and `.claude/` files: scripts run from skills or CLAUDE.md, hooks run from settings.json, CLI entry points (`if __name__ == "__main__"`, argparse subcommands), framework routes and tests are all used dynamically. If a symbol is used dynamically, add it to `.cleanup/vulture_whitelist.py` (one `name  # why` per line) so future scans skip it.

## 4. Report, then wait
Show one table: `# | kind (dead / duplicate / complexity / unused dep) | file:line | evidence | proposed fix | confidence (high/med)`. Drop anything low-confidence. Ask which to apply: all, by number, or none.

## 5. Apply
- **Pass check required:** the project's tests or documented self-checks (find them in its CLAUDE.md, e.g. `pytest -q` or a `--selftest` flag). If the project has none, apply only items Chase approved one by one, then say clearly that nothing automatic verified them, and suggest adding a test.
- One logical change per item; never change behavior, public interfaces or output formats.
- Re-run `scan.sh` and the pass check; report before/after counts and the line change from `git diff --stat`.
- Commit (`refactor: cleanup <scope>`) and push per the global git rule.
