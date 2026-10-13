---
name: project-journal
description: Create or update a project's living journal (docs/journal.html, published as a private artifact) covering goal, design, decision log, timeline, open questions and lessons. Use when Chase types /project-journal, or as the last step of new-project-setup. In a project that has docs/journal.html, suggest running it (one line, don't run it) when a milestone ships, a real decision is made, or the design changes; never suggest it after routine edits.
---

# Project journal

One private artifact per project that records how it was designed and built. `docs/journal.html` in the repo is the source of truth; the artifact is the published view. The decision log matters most: it's what Chase reuses in FDE interviews and write-ups.

Typing `/project-journal` is the go-ahead; don't ask for plan approval. When you only *suggest* it, wait for a yes.

## 1. Locate
- Repo root, `docs/journal.html`, and the `Journal:` line in the project `CLAUDE.md` (holds the artifact URL).
- No journal yet: first run (step 2). Journal exists: update (step 3).

## 2. First run
- Copy `template.html` (next to this skill) to `docs/journal.html`.
- Fill the JSON block in `<script id="journal-data">` from real facts only: project `CLAUDE.md`, `docs/status.md`, README, and this conversation. Leave a field empty rather than invent it; the page shows a clean empty state.
- Design section: replace the `<pre class="mermaid">` diagram with the real components and data flow. If nothing is built yet, keep a one-node diagram of the intended system.
- First decision entries: stack and architecture choices made during setup, each with why and alternatives.
- Set `lastCommit` to `git rev-parse --short HEAD` (empty if no commits yet) and `updated` to today.

## 3. Update run
- Gather, cheaply: `git log --oneline --no-merges <lastCommit>..HEAD` (if that hash is gone from history, use `--since=<updated>`), `docs/status.md`, and decisions or design changes from this conversation. Don't read full diffs.
- Append only to `decisions`, `timeline` and `lessons`; never edit or delete past entries. A reversed decision gets a new entry that names the old one.
- Group commits into timeline entries by milestone, not one per commit; keep the short hashes in `commits`.
- Update in place: overview fields, `status`/`statusLevel`, `open`, `next`, `components`, and the mermaid diagram (only when the design actually changed).
- Set `lastCommit` and `updated`.
- Inside the JSON, never write `</` (write `<\/`) so the script tag can't close early. Validate it parses (`python3 -c` with `json.loads` on the extracted block).

## 4. Publish
- The Artifact tool requires loading `artifact-design` first; do so, but keep the template's design and only change content.
- First run: publish `docs/journal.html` with `icon: "notebook"` and a one-sentence description. Then add to the project `CLAUDE.md` under "Where to look": `- Journal: docs/journal.html, published at <url> (update with /project-journal)`.
- Later runs: publish with `url` from that line, so the link never changes.

## 5. Finish
- Commit `docs/journal.html` (and `CLAUDE.md` if changed) as `docs: update project journal`; push if the repo has a remote.
- Report: the link, and what was added (e.g. "2 decisions, 1 timeline entry, status now at-risk").
