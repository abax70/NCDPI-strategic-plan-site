# WCAG 2.1 Level AA — Reviewer Cheat Sheet

Condensed reference for the 5 review agents. Not exhaustive — includes the criteria that automated + structural review can evaluate on a static HTML dashboard. Cognitive / plain-language criteria (3.1.x) are out of scope.

---

## 1. Perceivable

### 1.1 Text Alternatives

- **1.1.1 Non-text Content (A)** — Every `<img>`, `<svg>`, `<canvas>`, icon, or background image conveying information has a text alternative.
  - Meaningful image → `alt="descriptive text"` or `aria-label`
  - Decorative image → `alt=""` or `role="presentation"` or `aria-hidden="true"`
  - Icon font / inline SVG with meaning → `role="img"` + `aria-label`
  - Canvas charts → `role="img"` + `aria-label` summarizing the chart's message, AND a data-table alternative nearby (or visually hidden `<table>` following the canvas).

### 1.3 Adaptable

- **1.3.1 Info and Relationships (A)** — Structure is programmatically determinable.
  - Headings use `<h1>`–`<h6>`, not styled divs.
  - Heading order is continuous (don't skip H2 → H4).
  - Lists use `<ul>`/`<ol>`/`<dl>`, not styled divs.
  - Related form controls grouped with `<fieldset>` + `<legend>`.
  - Landmarks: `<header>`, `<nav>`, `<main>`, `<aside>`, `<footer>` OR equivalent `role="…"`. One `<main>` per page.
  - Tables: `<th scope="col">` / `<th scope="row">`; `<caption>` when table has a title.
- **1.3.2 Meaningful Sequence (A)** — DOM order matches visual reading order. CSS repositioning shouldn't reorder content semantically.
- **1.3.4 Orientation (AA)** — Content isn't locked to portrait or landscape.
- **1.3.5 Identify Input Purpose (AA)** — Form inputs for user info use the correct `autocomplete` attribute (e.g., `autocomplete="email"`).

### 1.4 Distinguishable

- **1.4.1 Use of Color (A)** — Color is never the only way to convey information. Status pills need icon + text + color (currently OK per exploration).
- **1.4.3 Contrast (Minimum) (AA)** — Text contrast ≥ **4.5:1** (normal) / **3:1** (large: ≥18.66px bold or ≥24px regular). Check all text colors against their backgrounds. **Pillar text colors** are approved per graphics team — flag but do not "fix."
- **1.4.4 Resize Text (AA)** — Text scales to 200% without loss of content or function. Test with browser zoom.
- **1.4.5 Images of Text (AA)** — Avoid images of text except for logos. Badge images are OK; prose-in-images is not.
- **1.4.10 Reflow (AA)** — Content reflows at **320 CSS pixels** wide without horizontal scrolling or content loss. (Known gap: current layout is desktop-only.)
- **1.4.11 Non-text Contrast (AA)** — UI components (buttons, form borders, focus indicators) and meaningful graphics have ≥ **3:1** contrast with adjacent colors.
- **1.4.12 Text Spacing (AA)** — No loss of content when: line-height 1.5×, paragraph spacing 2×, letter spacing 0.12×, word spacing 0.16×.
- **1.4.13 Content on Hover or Focus (AA)** — Tooltips/popovers that appear on hover/focus must be: dismissable (Esc), hoverable (can mouse onto the popover), persistent (not auto-closing on timeout).

---

## 2. Operable

### 2.1 Keyboard Accessible

- **2.1.1 Keyboard (A)** — All functionality available via keyboard. No mouse-only interactions. Measure carousel prev/next must be keyboard-reachable.
- **2.1.2 No Keyboard Trap (A)** — Focus can always leave a component via standard keys (Tab / Esc).
- **2.1.4 Character Key Shortcuts (A)** — Single-character shortcuts (if any) can be turned off or remapped.

### 2.4 Navigable

- **2.4.1 Bypass Blocks (A)** — Provide a way to skip repeated content. **Skip link** ("Skip to main content") is the standard fix. *(Known gap.)*
- **2.4.2 Page Titled (A)** — `<title>` describes the page purpose. Differentiate `index.html` vs. `pillar.html`.
- **2.4.3 Focus Order (A)** — Tab order follows reading/logical order.
- **2.4.4 Link Purpose (In Context) (A)** — Link text (+ surrounding context) makes purpose clear. Avoid "click here" / "read more" if unclear.
- **2.4.5 Multiple Ways (AA)** — Multiple ways to find a page (nav, search, sitemap). Sidebar nav satisfies for a single-page dashboard.
- **2.4.6 Headings and Labels (AA)** — Headings and labels describe topic/purpose.
- **2.4.7 Focus Visible (AA)** — Focused element has a **visible focus indicator**. *(Known gap: no `:focus-visible` CSS.)*

### 2.5 Input Modalities

- **2.5.1 Pointer Gestures (A)** — Multi-point/path gestures have single-pointer alternatives.
- **2.5.2 Pointer Cancellation (A)** — Down-event doesn't trigger function; up-event does (or has abort/undo).
- **2.5.3 Label in Name (A)** — Accessible name contains the visible label text.
- **2.5.4 Motion Actuation (A)** — No device-motion-triggered functionality without an alternative.

---

## 3. Understandable

### 3.1 Readable

- **3.1.1 Language of Page (A)** — `<html lang="en">` present.
- **3.1.2 Language of Parts (AA)** — Language changes within the page marked with `lang="…"`.

### 3.2 Predictable

- **3.2.1 On Focus (A)** — Focus doesn't cause unexpected context change (no auto-submit).
- **3.2.2 On Input (A)** — Changing a form value doesn't cause unexpected context change without warning.
- **3.2.3 Consistent Navigation (AA)** — Navigation appears in the same relative order across pages.
- **3.2.4 Consistent Identification (AA)** — Components with the same function are labeled consistently.

### 3.3 Input Assistance

- **3.3.1 Error Identification (A)** — Errors are identified in text (not color alone).
- **3.3.2 Labels or Instructions (A)** — Labels or instructions are provided for inputs. Placeholder is **not** a label.
- **3.3.3 Error Suggestion (AA)** — Where possible, suggest corrections.
- **3.3.4 Error Prevention (AA)** — For legal/financial/data-deletion actions: reversible, checked, or confirmed.

---

## 4. Robust

### 4.1 Compatible

- **4.1.1 Parsing (A)** — *Deprecated in WCAG 2.2; still listed in 2.1 AA.* Valid nesting, no duplicate IDs, tags properly closed.
- **4.1.2 Name, Role, Value (A)** — Every interactive element has an accessible name, role, and (where applicable) value. Custom widgets must expose state via ARIA.
- **4.1.3 Status Messages (AA)** — Dynamic status updates announced to AT via `role="status"`, `role="alert"`, or `aria-live`. Measure-change announcements should use `aria-live="polite"` (already present per exploration).

---

## Known dashboard-specific constraints (read before flagging)

- **Pillar colors** (`--pillar1` through `--pillar8` and their `-text` variants) are **graphics-team approved**. Flag contrast issues for reporting but do not change colors without Andy's approval.
- **Measure content copy** (names, goals, why-it-counts text) is Andy's domain. Don't rewrite — flag for his review.
- **Canvas charts** already have `role="img"` + `aria-label`. Evaluate whether the label is meaningful and whether a data-table fallback exists; this is a judgment call that may warrant a pause gate.
- **Pillar icon `alt=""`** is correct (decorative) because the pillar name appears as adjacent text. Don't "fix" to add redundant alt.
