# Page pattern: the flowchart

Pattern: the `.fc` flowchart class. It uses tokens defined on `:root`: `--surface`, `--line`, `--muted`, `--accent`, `--warn`.

## CSS

```css
/* Flowchart: boxes and arrows across; stacks vertically on phones. */
.fc { list-style: none; margin: 0; padding: 0; display: flex; align-items: stretch; gap: 0; }
.fc li { display: flex; align-items: center; flex: 1 1 0; min-width: 0; }
.fc .node { flex: 1; min-width: 0; border: 1.5px solid var(--line); border-radius: 8px; background: var(--surface); padding: 10px 12px; display: grid; gap: 2px; height: 100%; }
.fc .node b { font-size: 14px; line-height: 1.3; }
.fc .node span { font-size: 12.5px; color: var(--muted); line-height: 1.35; }
.fc .node.you { border-color: var(--accent); }
.fc .node.gate { border-style: dashed; border-color: var(--warn); }
.fc li + li::before { content: "\2192"; flex: none; width: 26px; text-align: center; color: var(--muted); font-size: 18px; }
@media (max-width: 760px) {
  .fc { flex-direction: column; }
  .fc li { flex-direction: column; align-items: stretch; }
  .fc li + li::before { content: "\2193"; width: auto; padding: 4px 0; }
}
```

## Markup

```html
<section class="section" aria-labelledby="fc-h">
  <div class="section-head"><h2 id="fc-h">How it gets to paid work</h2><span class="label">flowchart</span></div>
  <ol class="fc">
    <li><div class="node you"><b>Discovery calls</b><span>3 to 4 managers, Mom Test guide</span></div></li>
    <li><div class="node"><b>Confirm the problem</b><span>synthesize notes, keep or swap the offer</span></div></li>
    <li><div class="node gate"><b>HR carve-out in writing?</b><span>no: calls only, no code</span></div></li>
    <li><div class="node"><b>Build demo</b><span>synthetic data, cost per run</span></div></li>
  </ol>
</section>
```

- `.you` (accent border): a step Chase does himself.
- `.gate` (dashed warn border): a decision or blocker.
- Plain `.node`: a normal step. Use 4 to 6 nodes.

## Checklist before publishing
- Mobile at 375px: no horizontal scroll, flowchart stacked with down arrows.
- Light and dark colour tokens defined on `:root` (dark via `prefers-color-scheme` and `data-theme`).
- Title is 2 to 4 words.
- Node labels short enough not to overlap or wrap badly in the row layout.
- Every fact comes from the repo; unknowns are marked, not guessed.
