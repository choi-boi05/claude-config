#!/usr/bin/env python3
"""UserPromptSubmit hook: when context passes the threshold, warn Chase and
tell Claude to recommend /compact or /clear. Hooks can't run those commands."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from context_usage import context_percent  # noqa: E402

THRESHOLD = float(os.environ.get("CLAUDE_CONTEXT_WARN_PCT", "30"))

try:
    payload = json.load(sys.stdin)
    pct = context_percent(payload)
except Exception:
    sys.exit(0)  # never block a prompt because of this hook

if pct is None or pct < THRESHOLD:
    sys.exit(0)

print(json.dumps({
    "systemMessage": "Context is %d%% full. Consider /compact (same task) or /clear (new task)." % pct,
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": (
            "Context window is about %d%% full. At the start of your reply, briefly "
            "recommend that Chase run /compact if continuing this task, or /clear if "
            "switching topics. Keep it to one line." % pct
        ),
    },
}))
