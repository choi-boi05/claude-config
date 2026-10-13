# Headless test gotchas

- `< /dev/null`: otherwise a stdin warning line lands before the JSON and breaks parsing (or strip it with `tail -n +2`).
- `--allowedTools` takes several values, so space-separated tools swallow the prompt ("Input must be provided…"): pass one comma-separated string and put `--` before the brief.
- `--permission-mode acceptEdits`: so edits don't stall waiting for approval.
- `--allowedTools` patterns match whole commands: `Bash(python3 *)` does not match a compound `python3 x; echo y`. Keep test commands simple, or allow each one.
- Files under `~/.claude` are a sensitive path: headless edits there are blocked. Use a scratch dir elsewhere.
- `--resume <session_id>` continues the same agent session for a follow-up round.
- New agent files are visible to the Agent tool only in sessions started after they were created; headless `--agent` sees them immediately.
- Run tests sequentially, or with `&` plus `wait`; detached subshells lose their output.
- Subagent tool calls carry `agent_id` and `agent_type` in hook payloads (useful with `--settings <file>` to log hooks during a test).
- Cost reference: a refusal case on Opus is about $0.11, on Sonnet about $0.03 to $0.05.
