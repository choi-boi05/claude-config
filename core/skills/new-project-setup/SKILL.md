---
name: new-project-setup
description: Set up a new project for Claude Code with a lean CLAUDE.md, docs/status.md, .gitignore and .env.example. Use when Chase starts a new project or repo, asks for a CLAUDE.md, or wants an existing project's CLAUDE.md rebuilt.
---

# New project setup

Builds a lean project harness. Chase's preferences live in the global `~/.claude/CLAUDE.md`; the project file holds only project facts. Never repeat global rules (working style, secrets, writing) in it.

## 1. Look before asking
- New projects go in `~/Desktop/Claude/<project>`. If the folder is elsewhere, propose moving it there first.
- Check the folder: existing code, `README`, `package.json` / `pyproject.toml` / `requirements.txt`, `Makefile`, an existing `CLAUDE.md`, git status and remote.
- Derive what you can (language, commands, layout). Only ask for what you can't find.
- If a `CLAUDE.md` exists, this is a rebuild: keep its true project facts, cut the rest, and show a before/after line count.

## 2. Interview (one AskUserQuestion call, 4 questions max)
Ask only what's still unknown, with options where possible:
1. Purpose: what it is, who it's for, what "done" looks like.
2. Stack and commands: run, test, lint (offer detected ones as options).
3. Hard constraints: what must never happen (data rules, conflicts, deadlines, things not to touch).
4. Git: local only, or a **private** GitHub repo (never public without explicit say-so).

## 3. Show the plan, wait for go-ahead
List the files you'll create and the draft CLAUDE.md line count.

## 4. Create files
- `CLAUDE.md` from `template.md` (next to this skill). Fill every section from real facts only. Delete a section rather than leaving placeholders or generic advice. Target 15–40 lines.
- `docs/status.md`: Decisions (dated), Open (checkboxes), Next.
- `.gitignore` for the stack (secrets are already covered globally; don't repeat them).
- `.env.example` with variable names only, if the project uses keys.
- `IMPORTANT:` labels: max 3, only for rules meeting the budget test in the global CLAUDE.md. Often zero at the start.

## 5. Finish
- `git init` if needed, commit (the global gitleaks hook runs automatically). Create and push a private repo only if Chase chose it.
- Run the `project-journal` skill's first run: it creates `docs/journal.html`, publishes it, adds the `Journal:` line to `CLAUDE.md`, and commits.
- Report: files created, CLAUDE.md line count, and one line on how it grows: add a line when Claude makes a mistake a line would have prevented; move situational detail to `docs/` with a pointer.
