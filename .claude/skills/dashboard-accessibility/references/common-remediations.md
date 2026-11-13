# Common Remediations — Dashboard-Specific Patterns

Mapping of frequent WCAG 2.1 AA violations to concrete fix patterns, tuned for this codebase (inline `<style>` and `<script>`, Chart.js canvases, pillar color system). Remediation agents should use these patterns rather than inventing fixes.

Each pattern shows **before** and **after** and notes the scope (which file/section to edit).

---

## Contrast & color

### Low text contrast on pillar backgrounds
**Don't** change `--pillar{N}` or `--pillar{N}-text` definitions — graphics team approved. Pause gate.
**Do** check that pillar text is only used on its approved background. If flagged on the wrong background, change the *background* or switch to `--text-primary` / `--text-secondary`.

### Focus indicator contrast (1.4.11)
Browsers' default focus ring may not hit 3:1 against all backgrounds. Add an explicit rule in the embedded `<style>` block:

```css
:focus-visible {
  outline: 3px solid #005fcc;
  outline-offset: 2px;
  border-radius: 2px;
}

/* For elements on dark backgrounds (hero, pillar headers) */
.hero :focus-visible,
[class*="pillar"][data-dark] :focus-visible {
  outline: 3px solid #ffe066;
  outline-offset: 2px;
}
```

Apply to both `index.html` and `pillar.html` — they each carry their own `<style>`.

### Status pill color-only
Already has icon + text per exploration — no change needed. If flagged, verify the icon is an actual SVG/character, not a background image (which screen readers miss).

---

## Keyboard & focus

### Missing skip link (2.4.1)
Add as the **first** element inside `<body>`:

```html
<a href="#main-content" class="skip-link">Skip to main content</a>
```

CSS in the embedded `<style>` block:

```css
.skip-link {
  position: absolute;
  left: -9999px;
  top: 0;
  background: #003A70;
  color: #fff;
  padding: 0.75rem 1rem;
  z-index: 9999;
  text-decoration: none;
  font-weight: 600;
}
.skip-link:focus {
  left: 1rem;
  top: 1rem;
}
```

Add `id="main-content"` to the existing `<main>` element (or create `<main>` wrapping the primary content column if it's currently a `<div>`).

### Icon-only buttons (2.5.3, 4.1.2)
Prev/Next carousel buttons use `&#8249;` / `&#8250;` with `aria-label` — that's fine per 4.1.2. For 2.5.3 (label in name), if a visible label is ever added, the accessible name must contain it verbatim.

### Hover-only link underlines (2.4.7)
Add `:focus-visible` mirror of the `:hover` underline:

```css
.sidebar-link:hover,
.sidebar-link:focus-visible {
  text-decoration: underline;
}
```

---

## Structure & ARIA

### Heading-level skip (1.3.1, 2.4.6)
Exploration found H1 → H2 → H5 (missing H3, H4). Don't style-shift — insert semantically meaningful H3s for section groupings, then demote former H5s to H3 or H4 as appropriate. Example before/after in `index.html`:

```html
<!-- Before -->
<h2>Measure name</h2>
…
<h5>What's In Motion</h5>

<!-- After -->
<h2>Measure name</h2>
…
<h3>What's In Motion</h3>
```

Update CSS selectors (`h5.motion-header` → `h3.motion-header`) to preserve styling. Do not just add visual H3s that are invisible — screen readers need the structure regardless of whether they're sighted-styled.

### Missing `<main>` landmark
If primary content isn't wrapped in `<main>`, wrap it. One `<main>` per page.

### Canvas chart alternative (1.1.1)
Canvas elements already have `role="img"` + `aria-label`. To add a data-table fallback, place a visually-hidden `<table>` immediately after the canvas:

```html
<canvas id="measure-chart" role="img" aria-label="Bar chart: 2019 baseline 86%, 2024 actual 87%, 2030 target 95%">
</canvas>
<table class="visually-hidden" aria-label="Measure data table">
  <caption>Measure progress by year</caption>
  <thead><tr><th scope="col">Year</th><th scope="col">Value</th><th scope="col">Type</th></tr></thead>
  <tbody>
    <tr><td>2019</td><td>86%</td><td>Baseline</td></tr>
    <tr><td>2024</td><td>87%</td><td>Actual</td></tr>
    <tr><td>2030</td><td>95%</td><td>Target</td></tr>
  </tbody>
</table>
```

Rendering the table from `measures.json` at the same time the chart renders keeps them in sync. The *wording* of specific aria-labels is a **pause gate** — Andy approves per measure.

Add `.visually-hidden` utility class (if not already present):

```css
.visually-hidden {
  position: absolute !important;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

### Duplicate IDs (4.1.1)
IDs generated in loops (measure cards, action items) must be unique. If duplicates found, append the record ID: `id="action-" + action.actionId`.

### ARIA attribute validity (4.1.2)
- `aria-labelledby` / `aria-controls` must reference existing IDs.
- Boolean attributes (`aria-expanded`, `aria-selected`, `aria-hidden`) take `"true"` / `"false"` as strings, not JS booleans (in HTML attributes).
- `role="presentation"` on a focusable element is invalid — either un-focus it or remove the role.

---

## Non-text content

### Missing / poor alt text (1.1.1)
Per the `pdf-accessibility` guidance:
- Describe the communicative purpose, not appearance.
- Charts: describe the trend or key takeaway.
- Logos: simple identification ("NCDPI logo").
- Icons: describe the function ("Search icon").
- Never start with "Image of" or "Picture of".
- Keep under 150 characters for simple images.

### Pillar icons — already correct
`alt=""` + `role="presentation"` is right when the pillar name appears as sibling text. Don't "fix" these.

### Badge images
SVG achievement badges (e.g., "Highest 4-Year Graduation Rate in NC History") need `alt` or `aria-label` describing the achievement — they convey meaning.

---

## Forms, input & responsive

### Placeholder-as-label (3.3.2)
Replace `<input placeholder="Search">` with either:
- `<label for="search">Search</label><input id="search">`
- `<input aria-label="Search" placeholder="Type a measure name">` (placeholder = example, not label)

### Select without label (1.3.1, 3.3.2)
Measure carousel `<select>` must have an associated `<label>` or `aria-label`. Per exploration, `aria-label` is present — verify it's meaningful ("Jump to measure") not generic ("Select").

### Reflow at 320px (1.4.10)
The hard case. Current layout is desktop-fixed (280 + main + 360). Options:
1. **Add a mobile breakpoint** with `@media (max-width: 768px)` that stacks sidebars above/below main content.
2. **Pause gate** if the design team wants a different mobile design — don't ship mobile CSS that conflicts with design intent.

Minimal mobile-safe pattern:
```css
@media (max-width: 900px) {
  .layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto 1fr auto;
  }
  .sidebar-left,
  .sidebar-right {
    width: 100%;
  }
}
```

### Text resize to 200% (1.4.4)
Avoid fixed `px` on body font size; use relative units (`rem`, `em`). If fixed sizes found, convert to `rem` relative to a 16px root.

---

## Status messages (4.1.3)

Measure / tab changes should announce to AT. Exploration confirmed `aria-live="polite"` already present on detail areas — verify it's on the outermost container that updates, not a child that gets replaced wholesale (replacing a live region's parent loses the live behavior).

---

## Remediator discipline

- **Edit only the flagged elements.** No drive-by refactors, no "while I'm here" cleanups.
- **Don't rename classes.** CSS selectors scattered across inline styles break easily.
- **Don't re-order the DOM** unless the fix explicitly requires it (e.g., skip link must be first child of body).
- **Don't change Chart.js config** unless the fix is chart-related (aria-label, data-table alternative).
- **Cite the finding ID** in your edit summary so the main skill agent can verify each finding was addressed.
