"""Shared helper: estimate how full the main chat's context window is.

Reads the session transcript (JSONL) and uses the token usage of the most
recent main-thread assistant message: input + cache read + cache creation.
"""
import json
import os

DEFAULT_WINDOW = int(os.environ.get("CLAUDE_CONTEXT_WINDOW", "1000000"))


def tokens_from_transcript(path):
    """Return context tokens in use for the latest main-thread turn, or None (also after a compaction)."""
    if not path or not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        f.seek(0, 2)
        f.seek(max(0, f.tell() - 2_000_000))  # only scan the tail
        lines = f.read().decode("utf-8", "ignore").splitlines()
    for line in reversed(lines):
        if '"compact_boundary"' in line:  # cheap pre-check, then confirm
            try:
                entry = json.loads(line)
            except ValueError:
                entry = {}
            if entry.get("type") == "system" and entry.get("subtype") == "compact_boundary":
                return None
        if '"usage"' not in line:
            continue
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if entry.get("isSidechain"):  # subagent turns don't fill our context
            continue
        usage = (entry.get("message") or {}).get("usage")
        if usage:
            return (usage.get("input_tokens", 0)
                    + usage.get("cache_read_input_tokens", 0)
                    + usage.get("cache_creation_input_tokens", 0))
    return None


def context_percent(payload):
    """Percent of the context window in use, from a hook/statusline payload."""
    cw = payload.get("context_window") or {}
    if isinstance(cw.get("used_percentage"), (int, float)):
        return float(cw["used_percentage"])
    window = cw.get("context_window_size") or DEFAULT_WINDOW
    used = tokens_from_transcript(payload.get("transcript_path"))
    if used is None:
        return None
    return 100.0 * used / window
