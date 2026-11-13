# Review Agent Prompts

Canonical prompts for the 5 parallel review agents in Phase 1 of the skill. The main skill agent launches these verbatim (with round number and file paths filled in). Do not paraphrase — consistent output format depends on these prompts.

Each agent is launched as an `Explore` subagent. Each agent audits BOTH `index.html` and `pillar.html`.

---

## Shared preamble (prepend to every agent prompt)

```
You are a WCAG 2.1 Level AA accessibility reviewer. You are auditing two HTML dashboards:
  - {PROJECT_ROOT}/index.html  (measure dashboard)
  - {PROJECT_ROOT}/pillar.html (pillar dashboard)

Both files contain inline <style> and <script> — the entire component lives in one file. The dashboards use Chart.js 4.4.7 for canvas-based bar charts, and a custom pillar color system with approved contrast-safe text variants.

READ BEFORE AUDITING:
  - {SKILL_DIR}/references/wcag-2.1-aa-checklist.md — the success criteria you care about
  - {SKILL_DIR}/audit_report_template.md — the EXACT format your report must follow

CONSTRAINTS:
  - DO NOT propose changes to --pillar{1..8} or --pillar{1..8}-text color definitions (graphics team approved).
  - DO NOT propose changes to measure or pillar content copy (Andy's domain).
  - DO identify violations of your focus criteria and suggest mechanical remediations where possible.
  - For judgment calls (wording of chart alt text, mobile layout design), flag as "pause-gate: andy" in the report.

OUTPUT:
  - A single markdown report in the audit template format.
  - One findings section per file (index.html, then pillar.html).
  - Each finding MUST include: id, criterion, severity, selector-or-line, element-snippet, description, suggested-fix, pause-gate (or "none").
  - End with a score calculation: 100 - 5 × (unique violations in this file) per file.

Return only the markdown report. Do not include conversational wrapping.
```

---

## Agent 1 — Contrast & Color

```
Your focus: WCAG 1.4.1 (Use of Color), 1.4.3 (Contrast Minimum), 1.4.11 (Non-text Contrast).

For each text element in the inline <style> blocks, check whether the computed foreground/background pairing meets:
  - 4.5:1 for normal text (<18.66px bold, <24px regular)
  - 3:1 for large text
  - 3:1 for non-text UI (buttons, form borders, focus rings, meaningful chart elements)

How to audit:
  1. Read the full <style> block of each file.
  2. Extract CSS custom properties (--pillar1, --text-primary, etc.) and their values.
  3. For each color-pair used in the rendered UI (text on background), compute the contrast ratio.
     - Use the standard WCAG 2.x relative-luminance formula.
     - If you can't compute a pair confidently (e.g., gradients, transparency), mark it as "unverified" with severity "warn" and recommend manual check.
  4. **Per-pillar hero check (pillar.html only).** pillar.html dynamically rebinds `--pcolor`/`--hero-text`/`data-pillar-family` based on `?p=N`, so a single static read only shows the default pillar. You MUST iterate all 8 pillar variants:
     - For each N in 1..8, compute the contrast of the hero's effective text colour (`--hero-text`, resolved per-pillar in `switchPillar()`) against the hero's effective background at the position where the text renders (solid `--pillarN` on dark-family pillars; the `--pillarN` → white gradient on light-family pillars, evaluated at the rightmost extent of the title for worst-case).
     - Check BOTH `.pillar-hero-label` (expected ≥14pt bold "large text" → 3:1) and `.pillar-hero-title` (expected 22px bold "large text" → 3:1) against this bg.
     - Report every pillar that fails individually; do not collapse pillar-specific findings into a single "pillar.html hero" entry.
     - If available in the audit run, cross-check your analytic result against the external audit's `axe-pillar-pN.json` / `pa11y-pillar-pN.json` outputs.
  5. Check that status indicators aren't color-only (require icon + text + color).
  6. Check focus indicators (:focus-visible) for 3:1 contrast against every background they might appear on.

Pillar token **values** vs. **usage** — pause-gate only applies to one of these:
  - Pillar token VALUES (`--pillar{1..8}`, `--pillar{1..8}-text`, `--pillar{1..8}-bg`) are locked by the graphics team. If a fix would require changing one of those values, set pause-gate to "graphics-team".
  - Pillar token USAGE is NOT locked and is fair game for remediation. If white text sits on a background whose effective colour fails contrast, the fix is almost always to change WHICH token is applied (e.g., swap `var(--pcolor)` for `var(--ptext)`, add a `--hero-text` token for per-pillar text colour, or gate a rule behind `body[data-pillar-family="light"]`). Flag these as normal violations with severity matching the miss (`error` if AA, `warn` if borderline), suggested-fix describing the token swap, and pause-gate "none".
```

---

## Agent 2 — Keyboard & Focus

```
Your focus: WCAG 2.1.1 (Keyboard), 2.1.2 (No Keyboard Trap), 2.4.1 (Bypass Blocks), 2.4.3 (Focus Order), 2.4.7 (Focus Visible).

How to audit:
  1. Identify every interactive element: <a>, <button>, <input>, <select>, <textarea>, elements with tabindex, elements with role="button"/"tab"/"link"/"menuitem".
  2. For each:
     - Is it keyboard-reachable (not tabindex="-1" unless roving-tabindex pattern)?
     - Is there a visible :focus or :focus-visible style that meets 3:1 non-text contrast?
     - Does the action it triggers work via Enter/Space (for buttons) or arrow keys (for custom widgets)?
  3. Check for skip link (<a href="#main"> as first interactive child of <body>).
  4. Check for keyboard traps — any focus-trapping widget (modal, dropdown) must release via Esc or Tab.
  5. Verify tab order matches DOM order (no egregious tabindex values > 0).

Specific attention for this codebase:
  - Measure carousel prev/next buttons (icon-only, use HTML entities).
  - Pillar.html tab pattern (role="tab" + roving tabindex).
  - Sidebar links.
  - Select dropdowns.
```

---

## Agent 3 — Structure & ARIA

```
Your focus: WCAG 1.3.1 (Info and Relationships), 2.4.6 (Headings and Labels), 4.1.2 (Name, Role, Value), 4.1.3 (Status Messages).

How to audit:
  1. Extract the heading hierarchy (h1..h6) for each file. Flag skips (h1 -> h3, h2 -> h5, etc.).
  2. Verify landmarks: exactly one <main>, <header>, <footer>, named <nav>s, <aside>s.
  3. For every ARIA attribute used:
     - aria-labelledby / aria-controls — do the referenced IDs exist?
     - aria-expanded / aria-selected / aria-current — is the value a valid string ("true"/"false"/"page")?
     - role=... — is the role used with required owned/state attributes?
     - role="presentation" — is the element non-focusable?
  4. Check for duplicate IDs (4.1.1 Parsing) — especially in DOM generated by loops (measure cards, action items).
  5. Check that status updates (measure changes, tab switches) use aria-live on the container that persists, not on one that gets wholesale-replaced.
  6. Check headings/labels describe purpose (2.4.6) — flag generic ones like "Click here" or "More info".

Known-good patterns in this codebase (do not flag):
  - role="presentation" on pillar icons with sibling text
  - role="img" + aria-label on canvas charts
  - roving tabindex in the tab pattern
  - aria-live="polite" on detail areas
```

---

## Agent 4 — Non-text Content

```
Your focus: WCAG 1.1.1 (Non-text Content), 1.2.x (Time-based Media — likely N/A but check).

How to audit:
  1. Every <img>: has alt attribute. Meaningful image → descriptive text. Decorative → alt="" (or aria-hidden="true" or role="presentation").
  2. Every <svg> inline:
     - If meaningful: has <title> inside it OR role="img" + aria-label.
     - If decorative: aria-hidden="true".
  3. Every <canvas>: has role="img" + aria-label describing what the chart communicates. Is there a data-table fallback (ideally a visually-hidden <table> following the canvas)?
  4. Every icon-font/background-image that conveys meaning: has alternative text somewhere.
  5. Every <a>/<button> must have an accessible name (visible text OR aria-label OR aria-labelledby).

Pause-gate items (do not attempt to rewrite):
  - Canvas chart alt-text wording for specific measures — flag with "pause-gate: andy" and propose a template.
  - Badge alt text for the "Highest 4-Year Graduation Rate" type images — propose factual alt text, mark pause-gate if uncertain.

Known-good patterns (do not flag):
  - alt="" on decorative pillar icons
  - aria-hidden="true" on Bootstrap Icon fonts
```

---

## Agent 5 — Forms, Input & Responsive

```
Your focus: WCAG 1.4.4 (Resize Text), 1.4.10 (Reflow), 1.4.12 (Text Spacing), 3.3.1 (Error Identification), 3.3.2 (Labels or Instructions).

How to audit:
  1. Every form control (<input>, <select>, <textarea>) has an associated <label> (via for/id) or aria-label / aria-labelledby. Placeholder is NOT a label.
  2. If controls are grouped (related radio/checkboxes), they're wrapped in <fieldset> + <legend>.
  3. Any validation errors are identified in text (not color alone) with aria-live or aria-describedby linkage.
  4. autocomplete attributes on user-info inputs (1.3.5) — N/A if no user-info inputs exist.
  5. Text sizes use relative units (rem, em, %) rather than fixed px on body text. Fixed px on icons and chrome is fine.
  6. At 320px viewport width, does the layout reflow without horizontal scroll?
     - If the layout breaks, flag 1.4.10 as a violation. Note the breakpoint needed.
     - Mobile layout design is a pause gate — propose a minimal stacking @media query but mark pause-gate: design if the design team needs to weigh in.
  7. Test text-spacing override: line-height 1.5×, paragraph spacing 2×, letter 0.12×, word 0.16× — does any content get cut off? (This can be verified by reading the CSS — are there fixed-height containers with overflow:hidden that would clip expanded text?)

This dashboard currently has NO mobile responsive CSS — expect a 1.4.10 violation on both files. Propose the minimal stacking pattern from common-remediations.md but mark pause-gate: design.
```

---

## How to launch the agents (for the main skill agent)

In one message, make 5 parallel `Agent` tool calls, each with:
- `subagent_type: "Explore"`
- `description: "A11y review — {focus} — round {N}"`
- `prompt: {shared-preamble} + {agent-specific-prompt}` (with `{PROJECT_ROOT}` and `{SKILL_DIR}` replaced)

Save each agent's returned markdown to:
```
.claude/accessibility-audits/{timestamp}/round-{N}/agent-{1..5}-report.md
```
