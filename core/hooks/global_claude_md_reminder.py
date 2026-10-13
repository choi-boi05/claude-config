#!/usr/bin/env python3
"""PostToolUse hook (Edit|Write): after the global CLAUDE.md or its shared core is edited, remind
Chase to run /sync-conventions. Reminder only; never edits anything."""
import json
import os
import sys

TARGETS = {os.path.realpath(os.path.expanduser(p)) for p in ("~/.claude/CLAUDE.md", "~/.claude/CLAUDE.core.md")}

try:
    payload = json.load(sys.stdin)
    path = (payload.get("tool_input") or {}).get("file_path") or ""
except Exception:
    sys.exit(0)

if path and os.path.realpath(os.path.expanduser(path)) in TARGETS:
    print(json.dumps({
        "systemMessage": "Global CLAUDE.md changed. Run /sync-conventions to check project CLAUDE.md files."
    }))
