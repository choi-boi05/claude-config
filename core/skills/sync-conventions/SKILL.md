---
name: sync-conventions
description: "Check project CLAUDE.md files against Chase's global ~/.claude/CLAUDE.md conventions (size, duplicated or conflicting rules, IMPORTANT budget, .env.example, detail that belongs in docs/) and propose trims. Use when Chase types /sync-conventions, after the global CLAUDE.md changes, or when a project CLAUDE.md looks bloated."
---

# Sync conventions

The global `~/.claude/CLAUDE.md` loads in every project. Syncing a project means **removing** project lines that repeat or contradict it, never copying global rules in. Read the global file and `references/lean-rules.md` first; they are the source of truth for the rules below.

## Targets
- Args name the CLAUDE.md files or project folders to check. With no args, ask which projects (offer recent ones from `~/Desktop` with a `CLAUDE.md`).
- Check oversized files first.
- **Only projects Chase built.** Skip clones or forks of other people's repos (check `git remote -v` and authorship); never edit their CLAUDE.md, AGENTS.md or GEMINI.md. List them as "skipped: not Chase's" in the report.

## Exemptions
A line `Conventions: exempt from <rule>` in a project file skips that rule for that project. Rule names: `size`, `duplicates`, `conflicts`, `important-budget`, `env-example`, `progressive-disclosure`, `skills`, `skill-frontmatter`. Report skipped rules as "exempt".

## Checks (per file)
1. **size**: line count (`wc -l`). Target 60–100, hard cap 200. Under 60 is fine if nothing is missing.
2. **duplicates**: lines that restate a global rule (explore/spec/code or plan first, ask with options, subagents/models, git commit-and-push, secrets, writing style, learning, context hygiene, CLAUDE.md hygiene). Propose deletion. If the project *narrows* a global rule (e.g. "push to `dev`, not `main`"), keep only the project-specific part.
3. **conflicts**: lines that contradict a global rule. Project wins, so don't auto-delete: ask Chase whether it's intentional. If yes, keep it and suggest adding an exempt line; if no, delete it.
4. **important-budget**: count `IMPORTANT:` lines. Over 3 → propose which to demote, and flag any already enforced by a hook (`~/.claude/settings.json`, project `.claude/settings.json`).
5. **env-example**: if the project uses secrets (`.env` exists, or code reads env vars like `os.environ`/`getenv`/`process.env`/`dotenv`), check a committed `.env.example` exists with names only. Never read `.env` itself.
6. **progressive-disclosure**: situational detail (long procedures, schemas, reference tables, history, one workflow's steps) → propose moving to `docs/<topic>.md` or `.claude/rules/` with a plain-text pointer ("Before X, read `docs/x.md`"). Flag `@` imports that aren't needed every session. Also flag stale or vague lines ("write clean code").
7. **skills**: each project skill's `SKILL.md` over ~60 lines, or holding long templates/examples/tables inline → propose moving that material to `references/` with a pointer at the step that uses it.
8. **skill-frontmatter**: each project skill's `SKILL.md` frontmatter parses; `description` is double-quoted, has no unquoted ` #` and no `<angle>` placeholders, is at most 1024 chars, and has a "Use when/for" trigger.

## Report (show before editing anything)
For each project:
```
## <path>  —  <before> → <after est.> lines
Exempt: <rules or none>
| # | Check | Lines | Proposed edit |
|---|-------|-------|---------------|
Moves to docs/: <file> ← <section>, pointer text: "..."
Questions: <conflicts needing a decision>
```
End with a summary table of all projects (before/after line counts) and ask which edits to apply (all / per project / per item).

## Apply (only what Chase approves)
- Make the edits; create `docs/` files for moved content verbatim (don't lose information) and add the pointer line.
- Re-run `wc -l` and show the final count.
- Per repo: if it's a git repo, `git add` only the touched files, commit (`docs: sync CLAUDE.md with global conventions`), and push to the current branch. Never force-push. If not a git repo, say so and skip.
