# Keeping instructions lean

Read before writing or editing any CLAUDE.md, `.claude/rules/` file or skill (moved out of `CLAUDE.core.md` so it doesn't load every session). Applies to the global files and every project CLAUDE.md.

- **Size:** aim for 60–100 lines; never past 200. Keep only lines that would cause mistakes if removed.
- **Progressive disclosure:** detail lives in `docs/` or `.claude/rules/`; the main file points to it in plain text ("before X, read `path`"). `@` imports load every launch, so use them only for what every session needs.
- **Specific, not vague:** exact commands and constraints ("run `pytest -q` after changes"), never "write clean code" or "test everything".
- **Only what Claude can't guess:** build/test/run commands, env var names, branch and commit conventions, architecture quirks, gotchas. Skip language defaults and anything readable from the code.
- **References in skills:** keep `SKILL.md` to steps and pointers (~60 lines); long templates, examples, flag lists and schemas go in `references/` beside it, read at the step that needs them ("At step 3, read `references/x.md`").
- **`IMPORTANT:` budget, max 3 per file:** use it only for a rule that (a) would cause real harm or rework if missed, (b) isn't already enforced by a hook, and (c) applies in most sessions. When adding or editing these files, flag any rule that meets all three, and if a file would go over 3, propose which one to demote. Once a hook enforces a rule, drop its label.
- **Hooks for must-happen rules:** if a rule must never be skipped, propose a hook instead of more text.
- **Editing:** `/init` output is only a draft; prune it. When editing, remove stale or duplicate lines (including ones repeating this global file) instead of only adding.
