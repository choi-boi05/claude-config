#!/usr/bin/env python3
"""PreToolUse hook: count main-session edit/shell calls vs. agent hand-offs, and
nudge once when the main session does lots of work without using a pinned agent.
The status line reads the counts through read_counts()."""
import json
import os
import sys
import tempfile

PINNED = ("haiku-runner", "sonnet-worker", "sonnet-builder", "opus-builder")
NUDGE_AT = 8
STATE_DIR = os.path.join(tempfile.gettempdir(), "claude-delegation")


def state_path(session_id):
    return os.path.join(STATE_DIR, "%s.json" % session_id)


def read_counts(session_id):
    """Return {"main", "agents", "nudged"} for the session, or None."""
    try:
        with open(state_path(session_id)) as f:
            state = json.load(f)
        if isinstance(state, dict) and isinstance(state.get("agents"), dict):
            return state
    except Exception:
        pass
    return None


def main():
    payload = json.load(sys.stdin)
    if payload.get("agent_id"):
        return  # a subagent's own calls aren't counted
    session_id = str(payload["session_id"])
    tool = payload.get("tool_name")
    tool_input = payload.get("tool_input") or {}

    state = read_counts(session_id) or {"main": 0, "agents": {}, "nudged": False}
    state.setdefault("main", 0)
    state.setdefault("nudged", False)

    if tool in ("Agent", "Task"):
        kind = tool_input.get("subagent_type") or "general-purpose"
        state["agents"][kind] = state["agents"].get(kind, 0) + 1
    elif tool in ("Edit", "Write"):
        state["main"] += 1
    elif tool == "Bash":
        if not str(tool_input.get("command") or "").strip().startswith("git "):
            state["main"] += 1

    nudge = (state["main"] >= NUDGE_AT and not state["nudged"]
             and not any(state["agents"].get(p) for p in PINNED))
    if nudge:
        state["nudged"] = True

    os.makedirs(STATE_DIR, exist_ok=True)
    with open(state_path(session_id), "w") as f:
        json.dump(state, f)

    if nudge:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": (
                "Delegation check: %d main-session edit/shell calls and no pinned-agent "
                "hand-off this session. Per CLAUDE.core.md, route execution to "
                "haiku-runner / sonnet-worker / sonnet-builder unless this is a trivial "
                "edit, git, or a final check." % state["main"]
            ),
        }}))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # never break a session because of this hook
    sys.exit(0)
