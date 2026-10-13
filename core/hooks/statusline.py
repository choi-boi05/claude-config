#!/usr/bin/env python3
"""Status line: model · folder · context used (yellow >=30%, red >=50%) ·
agent hand-off counts (H haiku-runner, W sonnet-worker, B sonnet-builder,
O opus-builder, G other) once the session has any tracked calls."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from context_usage import context_percent  # noqa: E402
from delegation import PINNED, read_counts  # noqa: E402

payload = json.load(sys.stdin)
model = (payload.get("model") or {}).get("display_name", "Claude")
folder = os.path.basename((payload.get("workspace") or {}).get("current_dir")
                          or payload.get("cwd") or "")
pct = context_percent(payload)

if pct is None:
    ctx = "ctx --"
else:
    color = "\033[31m" if pct >= 50 else "\033[33m" if pct >= 30 else "\033[32m"
    ctx = "%sctx %d%%\033[0m" % (color, round(pct))

line = "%s · %s · %s" % (model, folder, ctx)

try:
    state = read_counts(payload.get("session_id") or "")
except Exception:
    state = None
if state and (state["main"] > 0 or state["agents"]):
    counts = state["agents"]
    line += " · agents " + " ".join(
        "%s%d" % (letter, counts.get(name, 0)) for letter, name in zip("HWBO", PINNED))
    other = sum(n for name, n in counts.items() if name not in PINNED)
    if other:
        line += " G%d" % other

print(line)
