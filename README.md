# claude-config

Chase's shared Claude Code setup, used on the personal Mac and a work laptop.

## What's here
- `core/`: linked into place by `install.sh`. Shared rules (`CLAUDE.core.md`), hooks, skills, `agents/` (pinned-model subagents: haiku-runner, sonnet-worker, sonnet-builder, opus-builder), git guards (gitleaks pre-commit, global gitignore), and a reference `settings.json`.
- `templates/`: work-safe starters for the machine-specific files (`~/.claude/CLAUDE.md`, `preferences/writing.md`). Copied only when missing.

Personal, machine-specific content is not in this repo and stays on the machine it belongs to.

## Install
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
