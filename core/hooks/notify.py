#!/usr/bin/env python3
"""Notification hook: macOS desktop alert when Claude needs input or is idle."""
import json
import subprocess
import sys

try:
    payload = json.load(sys.stdin)
except ValueError:
    payload = {}
msg = (payload.get("message") or "Claude needs your attention").replace("\\", "/").replace('"', "'")
subprocess.run(["osascript", "-e",
                'display notification "%s" with title "Claude Code"' % msg[:200]],
               check=False)
