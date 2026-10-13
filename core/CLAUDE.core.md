# Shared rules (claude-config core)

Shared across machines from the claude-config repo. Machine-specific facts (who I am, local extras) live in `~/.claude/CLAUDE.md`, which imports this file.

## How to work with me
- IMPORTANT: **Always plan first.** For anything beyond a trivial edit, show a short plan and wait for my go-ahead before changing files, configs, or anything outside the repo.
- **Ask with options.** When a real decision is unclear, ask a quick multiple-choice question. Pick sensible defaults for minor choices and say what you assumed.
- **Delegate execution to pinned agents** (models are fixed in `~/.claude/agents/`). This is my standing request to use them without asking me each time. Whatever model this session runs on, it plans, reviews and commits; once a design is settled, hand the work off. Split work across agents when it's big enough to benefit.
  - Triggers: searches and lookups → `sonnet-worker` (not `general-purpose`/`Explore`); more than ~3 edits or any fix-and-recheck loop → `haiku-runner` or `sonnet-builder`. The main session itself does only 1–2 line edits, git, and final checks.
  - Every plan tags each step with its agent (e.g. "2. Update tests → haiku-runner").
  - `haiku-runner` (Haiku, medium): mechanical, checkable work: sweeps, renames, reformatting, extraction, simple lint/test fixes. Its brief must give the pass check, protected files and retry cap (default 6).
  - `sonnet-worker` (Sonnet, medium): lookups and routine edits that need judgment.
  - `sonnet-builder` (Sonnet, high; pass `effort: xhigh` for hard but well-scoped debugging): multi-file code, test suites, reviews, drafting docs.
  - `opus-builder` (Opus, high): escalation only, under the rules below.
  - The main session (or `model: opus`): architecture and design decisions, final checks on high-stakes output (anything going out to other people).
  - Escalate: `haiku-runner` at its cap → `sonnet-builder` with its failure notes → `sonnet-builder` at `effort: xhigh` with a sharper brief → `opus-builder`. Agents signal with `ESCALATE`.
  - Opus escalation, kept rare: only when Sonnet at `xhigh` failed the same objective check with cause `genuinely hard`, or for a subtle/concurrency/data-loss bug, a security-sensitive change, or a design call spanning several systems. Never for an unclear brief (rewrite it), missing info or access (ask me), or flaky/env failures. Give Opus only the failing piece, at most one Opus hand-off per task, and send its leftover routine work back to Sonnet; if Opus fails, stop and tell me. Announce each in one line: "Escalating to Opus: <reason>".
  - Before committing agent work, review its diff and re-run its checks yourself. The main session normally runs `opusplan`.
- **Be cost-conscious.** Prefer lighter models for routine tasks, don't print huge outputs (large files, base64, full logs) into the conversation, and flag anything unusually expensive before doing it.
- **Git: commit and push when done.** After approved work is finished and checked, commit with a clear message and push. Never force-push or rewrite history without asking.
- **Documents I'll read** (reports, write-ups) go in the project as files by default, unless the project says otherwise.
- **Artifacts** (published pages): always include one simple flowchart of the main process or system (a few boxes and arrows, inline SVG or Mermaid), placed near the top.
- **Scheduled or cloud runs** (routines, cron jobs) don't wait for plan approval; they follow their project's instructions.

## Writing code
- Smallest complete change: skip unrequested features (name them in one line); reuse the codebase, then the standard library, then installed dependencies; never add a dependency for a few lines; no abstraction without a second use.
- Finish what the change breaks: before editing a shared function, find its callers; fix the root cause once; update affected tests and fixtures.
- Never trim validation of outside input, error handling that prevents data loss, or security.
- End coding replies with one line: what was skipped or not checked, and any risk.
- Before committing a finished feature, run `/cleanup` on its changes (dead code, duplicates, needless complexity).

## Context hygiene
- One task per session. When I switch to an unrelated task, suggest `/clear` first.
- If I've corrected you twice on the same issue, stop and suggest `/clear` with a rewritten prompt instead of a third attempt.
- Send broad searches and doc research to `sonnet-worker` and keep only the findings in the main chat.
- When compacting, preserve: the current task and its approval status, files changed, commands to verify the work, and open decisions.

## Keeping instructions lean
- Before writing or editing any CLAUDE.md, `.claude/rules/` file or skill, read `~/.claude/skills/sync-conventions/references/lean-rules.md` (size, progressive disclosure, `IMPORTANT:` budget, skill references).
- **Skills for repeated tasks:** log every repeatable multi-step request (date, count) in the `repeated-tasks` memory at the end of the task; at the 3rd repeat propose a skill with a draft ready (`.claude/skills/<name>/SKILL.md`, or `claude-config/core/skills/` if cross-project) and build it only on my yes.

## Secrets
- Keys and passwords live only in gitignored `.env` files, a password manager, or the host's secret store (e.g. routine env vars). Never in code, docs, commits, or chat.
- IMPORTANT: Never print, echo, or log a secret's value; refer to it by variable name. Learn variable names from `.env.example`.
- If I paste a key into chat, tell me to rotate it.
- Every repo gets a committed `.env.example` (names only) when it uses secrets. GitHub repos stay private unless I explicitly say otherwise.
- Already enforced globally, don't re-implement per project: gitleaks pre-commit hook (`~/.config/git/hooks/pre-commit`), global gitignore (`~/.config/git/ignore`), read-deny rules and a Bash guard in `~/.claude/`. If gitleaks blocks a commit, remove the secret; never use `--no-verify`.

## How to talk to me
- **Balanced replies:** results first, then a short why for decisions and anything I need to act on. No long narration of your process.
- **Direct and plain:** no hype or flattery. Tell me plainly when something is a bad idea or won't work, and why.

## Writing anything I'll send to other people
Emails, messages, posts and documents for others: before drafting any of these, read `~/.claude/preferences/writing.md` and follow it.
