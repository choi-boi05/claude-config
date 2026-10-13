#!/usr/bin/env python3
"""PreToolUse hook (Bash): force a confirmation prompt for hard-to-undo
or secret-exposing commands, whatever the permission mode. Returns "ask", never a silent block."""
import json
import re
import sys

RISKY = [
    (r"\bgit\s+push\b.*(\s--force\b|\s-f\b|\s--force-with-lease\b|\s\+\S)", "force push"),
    (r"\bgit\s+reset\s+--hard\b", "git reset --hard"),
    (r"\bgit\s+clean\s+-\w*f", "git clean -f"),
    (r"\bgit\s+branch\s+-D\b", "force-delete a branch"),
    (r"\bgh\s+repo\s+create\b.*--public\b", "creating a PUBLIC GitHub repo"),
    (r"\bgh\s+repo\s+edit\b.*--visibility[\s=]+public\b", "making a GitHub repo public"),
    (r"\bgh\s+gist\s+create\b.*(--public|\s-p\b)", "creating a public gist"),
    (r"(\bcat|\bless|\bmore|\bhead|\btail|\bgrep|\bsed|\bawk|\bsource|\bprintenv|\benv)\b[^|;&]*"
     r"(\.env(?!\.example|\.sample)\b|\.pem\b|\.ssh/|\.aws/credentials)", "reading a secrets file"),
    (r"\brm\s+-\w*r\w*\s+(-\w+\s+)*(/|~|\$HOME)(/?\*?)?(\s|$)", "recursive delete of / or home"),
]

try:
    payload = json.load(sys.stdin)
except ValueError:
    sys.exit(0)
cmd = (payload.get("tool_input") or {}).get("command", "")
for pattern, label in RISKY:
    if re.search(pattern, cmd):
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": "Guard hook: %s needs Chase's explicit OK." % label,
        }}))
        break
