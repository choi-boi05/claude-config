#!/usr/bin/env python3
"""Session handoff across /clear and /compact. Hooks can't start a turn, so
this only adds context Claude reads on Chase's next prompt.

SessionEnd (reason=clear): save cwd, last few requests and transcript path.
SessionStart (source=clear): one-line pointer to the previous task.
SessionStart (source=compact): re-add the compaction checklist."""
import json
import os
import sys
import time

HANDOFF = os.path.expanduser("~/.claude/handoff.json")
MAX_AGE = 6 * 3600  # ignore stale handoffs


def last_requests(transcript_path, n=3):
    """Last n prompts Chase typed (skips tool results and command wrappers)."""
    found = []
    try:
        with open(transcript_path) as f:
            for line in f:
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if e.get("type") != "user" or e.get("isMeta"):
                    continue
                c = (e.get("message") or {}).get("content")
                if isinstance(c, list):
                    c = " ".join(b.get("text", "") for b in c
                                 if isinstance(b, dict) and b.get("type") == "text")
                if isinstance(c, str) and c.strip() and not c.lstrip().startswith("<"):
                    found.append(" ".join(c.split())[:200])
    except OSError:
        pass
    return found[-n:]


def context(text):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart", "additionalContext": text}}))


try:
    p = json.load(sys.stdin)
except Exception:
    sys.exit(0)

event = p.get("hook_event_name")

if event == "SessionEnd" and p.get("reason") == "clear":
    reqs = last_requests(p.get("transcript_path") or "")
    if reqs:
        with open(HANDOFF, "w") as f:
            json.dump({"time": time.time(), "cwd": p.get("cwd"),
                       "transcript": p.get("transcript_path"), "requests": reqs}, f)

elif event == "SessionStart" and p.get("source") == "clear":
    try:
        with open(HANDOFF) as f:
            h = json.load(f)
        os.remove(HANDOFF)
    except (OSError, ValueError):
        sys.exit(0)
    if time.time() - h.get("time", 0) > MAX_AGE:
        sys.exit(0)
    context(
        "Chase just ran /clear. Previous task (in %s), last request: \"%s\". "
        "Full transcript: %s. Treat this as a fresh start: don't resume it unless "
        "Chase asks (e.g. 'continue'); then read the transcript tail for context."
        % (h.get("cwd"), h["requests"][-1], h.get("transcript")))

elif event == "SessionStart" and p.get("source") == "compact":
    context(
        "Context was just compacted. Continue the task that was in progress. Make sure "
        "you still have: the current task and its approval status, files changed, "
        "commands to verify the work, and open decisions. If any is missing from the "
        "summary, recover it from the transcript at %s before acting."
        % p.get("transcript_path"))
