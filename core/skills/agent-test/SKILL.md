---
name: agent-test
description: Check that a pinned agent in ~/.claude/agents/*.md (frontmatter `model`, `effort`) really runs on its model and follows its stop and escalation rules, cheaply, with headless runs. Use after creating or editing an agent definition.
---

# Agent test

Goal: prove the agent runs on the model it pins and stops when it should. Trust the JSON usage data, not what the model says about itself.

## 1. Write tiny briefs
One brief per behaviour:
- a happy path with an objective pass check;
- a case that must stop with the agent's signal word (`ESCALATE`, `NEEDS CHASE` or `NEEDS SONNET`, whichever its definition names).

Put fixture files in a scratch dir outside `~/.claude`, e.g. `mktemp -d`. Headless runs can't edit under `~/.claude` (sensitive path).

## 2. Run headless
From the scratch dir, one case at a time:
`claude -p --agent <name> --output-format json --permission-mode acceptEdits --allowedTools "Read,Edit,Bash(python3 *)" -- "<brief>" < /dev/null`
Before the first run, read `references/headless-flags.md`.

## 3. Parse the JSON
- `modelUsage` keys: the model(s) that actually ran.
- `total_cost_usd`: cost of the case.
- `result`: look for the expected signal word.
- `session_id`: keep it for a follow-up round (`--resume`).

## 4. Check side effects
In the scratch dir, confirm files changed or stayed untouched as the case expects (e.g. a refusal must leave the fixture alone).

## 5. Clean up and report
Delete the scratch dir. Report a table: `case | expected | got | model | cost`. Flag any case where the model differs from the agent's frontmatter.
