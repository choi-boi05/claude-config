#!/usr/bin/env python3
"""PreToolUse hook (Bash): force a confirmation prompt for hard-to-undo, public-facing
or secret-exposing commands, whatever the permission mode. Returns "ask", never a silent block.

The command is split into simple commands (on ; && || | & newlines and subshells) and each
is checked on its own words, so `uv run --env-file .env` or a `-f` in a later command
doesn't trigger a false prompt."""
import json
import os
import re
import shlex
import sys

READERS = {"cat", "less", "more", "head", "tail", "grep", "egrep", "fgrep", "rg", "sed", "awk",
           "source", ".", "bat", "strings", "xxd", "od", "hexdump", "base64", "nl", "tac"}
PREFIXES = {"sudo", "command", "nohup", "time", "exec"}
SHELLS = {"sh", "bash", "zsh"}
SEPARATORS = {";", "&&", "||", "|", "&", "\n", "(", ")", ";;", "|&"}
WRITE_REDIRECTS = {">", ">>", ">|", "&>", "&>>"}
HOME = os.path.expanduser("~")
HOME_TARGETS = {"/", "/*", "~", "~/", "~/*", "$HOME", "$HOME/", "$HOME/*",
                "${HOME}", "${HOME}/", "${HOME}/*", HOME, HOME + "/", HOME + "/*"}
HEREDOC = re.compile(r"(?<!<)<<(?!<)-?\s*(['\"]?)(\w+)\1")
CHECKED = READERS | SHELLS | {"git", "gh", "rm", "eval"}


def is_secret_path(word):
    word = word.strip("'\"`")
    base = os.path.basename(word.rstrip("/"))
    if re.match(r"^\.env(\.|$|\*)", base) and not re.search(r"\.(example|sample|template)$", base):
        return True
    if re.search(r"\.(pem|key|p12)$", base) or base in (".netrc", "credentials.json"):
        return True
    if base.startswith("service-account") and base.endswith(".json"):
        return True
    return bool(re.search(r"(^|/)\.ssh(/|$)|(^|/)\.aws/credentials$", word))


def split_heredocs(cmd):
    """Return (cmd without heredoc bodies, [bodies fed to a shell anywhere on that line]).
    An unclosed heredoc stays in the command, so it is checked as commands (fail closed)."""
    lines, out, bodies = cmd.split("\n"), [], []
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        i += 1
        for m in HEREDOC.finditer(line):
            end = i
            while end < len(lines) and lines[end].strip() != m.group(2):
                end += 1
            if end == len(lines):
                break
            if any(os.path.basename(w) in SHELLS | {"eval", "source", "."} for w in line.split()):
                bodies.append("\n".join(lines[i:end]))
            i = end + 1  # skip the body and its delimiter line
    return "\n".join(out), bodies


def tokenize(cmd):
    try:
        lex = shlex.shlex(cmd, posix=True, punctuation_chars="();<>|&\n")
        lex.whitespace = " \t\r"
        lex.whitespace_split = True
        lex.commenters = ""
        return list(lex)
    except ValueError:  # unbalanced quotes: fall back to a rough split
        rough = re.sub(r"(&&|\|\||[;|&\n()])", r" \1 ", cmd)
        return [w.strip("'\"") for w in rough.split()]


def segments(tokens):
    seg = []
    for tok in tokens:
        if tok in SEPARATORS:
            if seg:
                yield seg
            seg = []
        else:
            seg.append(tok.lstrip("`").rstrip("`") or tok)
    if seg:
        yield seg


def strip_prefix(seg):
    while seg and (re.match(r"^\w+=", seg[0]) or seg[0] in PREFIXES or seg[0] in ("env", "$")):
        seg = seg[1:]
    return seg


def git_sub(args):
    """Skip git's global options (-C dir, -c k=v, --git-dir=...) and return (subcommand, rest)."""
    i = 0
    while i < len(args) and args[i].startswith("-"):
        i += 2 if args[i] in ("-C", "-c", "--git-dir", "--work-tree", "--namespace") else 1
    return (args[i], args[i + 1:]) if i < len(args) else ("", [])


def check_segment(seg):
    """Check the segment from every word that names a checked command, so wrappers
    (timeout 5 cat, xargs cat, /usr/bin/env cat) can't hide it."""
    seg = strip_prefix(seg)
    for i, word in enumerate(seg):
        if os.path.basename(word) in CHECKED:
            label = check_command(os.path.basename(word), seg[i + 1:])
            if label:
                return label
    return None


def check_command(name, args):
    if name in SHELLS:
        for i, a in enumerate(args[:-1]):
            if re.match(r"^-[a-zA-Z]*c[a-zA-Z]*$", a):
                return check(args[i + 1])
    if name == "eval":
        return check(" ".join(args))

    if name == "git":
        sub, rest = git_sub(args)
        if sub == "push" and any(a in ("--force", "-f") or a.startswith("--force-with-lease")
                                 or re.match(r"^-[a-zA-Z]*f[a-zA-Z]*$", a) or a.startswith("+")
                                 for a in rest):
            return "force push"
        if sub == "reset" and "--hard" in rest:
            return "git reset --hard"
        if sub == "clean" and any(a == "--force" or re.match(r"^-[a-zA-Z]*f", a) for a in rest):
            return "git clean -f"

    if name == "gh" and len(args) >= 2:
        if args[:2] == ["repo", "create"] and any(a.startswith("--public") for a in args):
            return "creating a PUBLIC GitHub repo"
        if args[:2] == ["repo", "edit"] and ("--visibility=public" in args or any(
                a == "--visibility" and nxt == "public" for a, nxt in zip(args, args[1:]))):
            return "making a GitHub repo public"
        if args[:2] == ["gist", "create"] and ("--public" in args or "-p" in args):
            return "creating a public gist"

    if name == "rm":
        flags = [a for a in args if a.startswith("-")]
        recursive = any(a in ("--recursive",) or (not a.startswith("--") and re.search(r"[rR]", a))
                        for a in flags)
        if recursive and any(a in HOME_TARGETS for a in args if not a.startswith("-")):
            return "recursive delete of / or home"

    if name in READERS:
        read_args = [a for i, a in enumerate(args) if i == 0 or args[i - 1] not in WRITE_REDIRECTS]
        if any(is_secret_path(a) for a in read_args):
            return "reading a secrets file"
    return None


def check(cmd):
    body, bodies = split_heredocs(cmd)
    for seg in segments(tokenize(body)):
        label = check_segment(seg)
        if label:
            return label
    for b in bodies:
        label = check(b)
        if label:
            return label
    return None


if __name__ == "__main__":
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        sys.exit(0)
    label = check((payload.get("tool_input") or {}).get("command", ""))
    if label:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": "Guard hook: %s needs Chase's explicit OK." % label,
        }}))
