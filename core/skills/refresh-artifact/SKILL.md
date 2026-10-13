---
name: refresh-artifact
description: Update a project's published overview page (a private claude.ai Artifact) so it matches the repo, then republish to the same URL. Use when Chase says "refresh the artifact", "refresh the overview" or "refresh the map", or after a project's status changes.
---

# Refresh artifact

Goal: the published page matches the repo today, at the same link. The live page is the base; the repo supplies the facts.

## 1. Find the page
The project `CLAUDE.md` names the page URL and its local copy (e.g. `project-overview.html` published at a `https://claude.ai/artifact/...` link). If it names none, ask Chase.

## 2. Read the live version
Use the Artifact tool with `action: "read"` and the `url`. It saves the full page to a local file. Build on that file, never on the local copy in the repo: the page may have been edited elsewhere.

## 3. Gather current facts
Read the project `CLAUDE.md`, `docs/status.md`, config files and scripts. Never invent; mark unknowns as "unknown" or "to confirm" on the page.

## 4. Edit only what changed
- Keep exactly one simple flowchart of the main process near the top (global rule: every artifact has one). CSS flex boxes and arrows: a row on wide screens, stacked with down arrows on phones.
- Before touching layout or the flowchart, read `references/page-pattern.md`.
- Update the "Updated" date and any status fields; leave unchanged sections alone.

## 5. Strip the wrapper
If the read returned a full document, remove the outer document wrapper the publisher adds. Keep the head/style/body content as the original file had it.

## 6. Publish and save
- Publish with the Artifact tool to the same `url`. No new URL; omit `icon` on a redeploy.
- Copy the final HTML over the project's local copy (e.g. `project-overview.html`).
- Commit and push per the project's git rules. A project whose cloud routines push to main uses a PR instead.

## 7. Report
The URL, the version, and what changed, one line each.
