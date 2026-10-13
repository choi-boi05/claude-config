# claude-config

Chase's shared Claude Code setup, used on the personal Mac and a work laptop.

## What's here
- `core/`: linked into place by `install.sh`. Shared rules (`CLAUDE.core.md`), hooks, skills, `agents/` (pinned-model subagents: haiku-runner, sonnet-worker, sonnet-builder, opus-builder), git guards (gitleaks pre-commit, global gitignore), and a reference `settings.json`.
- `templates/`: work-safe starters for the machine-specific files (`~/.claude/CLAUDE.md`, `preferences/writing.md`). Copied only when missing.

Personal, machine-specific content is not in this repo and stays on the machine it belongs to.

## Use it yourself
This is a personal setup, shared as an example. The rules are written for me ("Chase"), so make a copy you can edit rather than installing it as is.

**Needs:** [Claude Code](https://docs.claude.com/en/docs/claude-code), `git`, `python3` (standard library only), and optionally `jq` and [`gitleaks`](https://github.com/gitleaks/gitleaks) (the secret-scanning commit hook skips itself without it). macOS or Linux; the desktop-alert hook (`notify.py`) is macOS-only.

1. **Fork** this repo (so your edits go to your own copy), then clone your fork anywhere:
   ```
   git clone https://github.com/<you>/claude-config.git && cd claude-config
   ```
2. **Preview, then install.** Nothing is deleted: anything the script replaces is moved to `~/.claude/backups/`.
   ```
   ./install.sh --dry-run
   ./install.sh
   ```
   What it does:
   - Links `core/CLAUDE.core.md`, `core/hooks/`, each skill in `core/skills/` and each agent in `core/agents/` into `~/.claude/`, so a `git pull` updates them.
   - Links the git guards into `~/.config/git/` and sets the **global** `core.hooksPath` and `core.excludesfile` (skipped with a warning if you already have them). A global hooks path stops repos' own git hooks from running, except `pre-commit`, which the shared hook chains to; skip this if you rely on other repo-local hooks.
   - Copies `templates/CLAUDE.md`, `templates/writing.md` and `core/settings.json` into `~/.claude/` **only if those files don't exist yet**.
3. **Make it yours:**
   - Rewrite `~/.claude/CLAUDE.md` (who you are, this machine) and `~/.claude/preferences/writing.md`. Keep the `@~/.claude/CLAUDE.core.md` line.
   - Edit `core/CLAUDE.core.md` in your fork for your own working style (it says "Chase" and "me" throughout).
   - If you already had a `~/.claude/settings.json`, the installer left it alone, so the hooks and status line aren't switched on yet. Copy the `hooks` and `statusLine` blocks from `core/settings.json` into it, and review its `permissions`, `model` and `env` values before adopting them.
4. **Check it:** start a new Claude Code session and look at `/hooks`, `/model` and `/context`. The agents need access to Haiku, Sonnet and Opus; if your plan or provider names them differently, change `model:` in `core/agents/*.md`.

**Uninstall** (run from your clone): remove the links and git settings, then restore anything you want from `~/.claude/backups/`.
```
find ~/.claude ~/.config/git -maxdepth 3 -type l -lname "$PWD/*" -print -delete
git config --global --unset core.hooksPath; git config --global --unset core.excludesfile
```
Copied files (`~/.claude/CLAUDE.md`, `writing.md`, `settings.json`) stay; edit or delete them yourself.

## Install (my machines)
```
./install.sh --dry-run   # see what would change
./install.sh             # link files; backs up anything it replaces to ~/.claude/backups/
```
Then reinstall plugins with `/plugin` (mattpocock-skills, product-management) and check `/model`, `/hooks`, `/context`.

## Rules
- Edit shared rules in `core/`; `~/.claude/CLAUDE.md` stays per machine and imports `@~/.claude/CLAUDE.core.md`.
- `settings.json` is copied, not linked (Claude Code rewrites it). After changing settings on the personal Mac, copy it into `core/settings.json` and commit.
- One way only: commit and push from the personal Mac. Never push from the work laptop.
- Tools the hooks expect: `git`, `python3`, `jq`, `gitleaks` (the script only checks; install may need IT).
- On a work machine that uses AWS Bedrock, check that `model` and `CLAUDE_CODE_SUBAGENT_MODEL` in settings resolve; adjust there if not. The pinned agents use the aliases `haiku`, `sonnet` and `opus`: if one fails, map it in that machine's `settings.json` `env` with `ANTHROPIC_DEFAULT_HAIKU_MODEL` / `ANTHROPIC_DEFAULT_SONNET_MODEL` / `ANTHROPIC_DEFAULT_OPUS_MODEL` set to the Bedrock model IDs your account has enabled, then run the `agent-test` skill on each agent.
- Skills that publish claude.ai artifacts (`refresh-artifact`, `project-journal`) need a claude.ai login and won't work on Bedrock; leaving them installed is harmless.
- Plugins are optional on the work laptop; install only what work needs.
- Before syncing, check that nothing personal is in `core/` or `templates/`: `grep -rniE 'job search|side business|artifact/[A-Za-z0-9]{10}' core templates` should print nothing, and employer or internal project names belong only in that machine's `~/.claude/CLAUDE.md`.
