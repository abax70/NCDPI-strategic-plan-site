---
title: How we built the Strategic Plan Dashboard with Claude
audience: Colleague asking about our process, tools, and workflow
author: Andy Baxter (NCDPI), written with Claude Code
updated: 2026-09-10
---

# How we built the Strategic Plan Dashboard with Claude

A colleague asked how this dashboard came together working with Claude — the basic
flow, the major steps, how Claude actually produced the website, and what tools were
involved. This is that write-up.

The dashboard monitors NCDPI's "Achieving Educational Excellence" strategic plan:
a public landing page ("Best in the Nation"), eight pillar pages, ~14 headline
measures, ~109 implementation actions, and "stories from the field." It's a static
website (HTML/CSS/JS) served on GitHub Pages, backed by a small Python pipeline that
turns our existing spreadsheets into the JSON the pages read.

---

## The short version of the flow

```
Source spreadsheets (Excel/CSV) + Smartsheet + blog list
        │
        ▼   Python build scripts (CSV/XLSX → JSON)
   data/*.json  ── pillar-data.json, measures.json
        │
        ▼   read at page load by vanilla JS
  index.html · pillar.html · best-in-nation.html
        │
        ▼   verify scripts + headless browser + accessibility checks
        │
        ▼   git commit → push → GitHub Pages (live)
```

The pages are hand-authored HTML/CSS/JS. **No data is hard-coded into the HTML** —
every number, status, and story comes from JSON files that a Python step generates
from our source spreadsheets. That separation is the single most important design
choice: routine updates never touch the website code, only the data.

---

## What Claude is, in this context

"Claude" here is **Claude Code** — Anthropic's coding assistant running in the terminal
(and VS Code). It reads and writes files in the project, runs commands and scripts,
uses git, drives a headless browser to check pages, and calls out to connectors like
Smartsheet. I work with it conversationally: I describe what I want, it proposes a plan,
I approve, it makes the change, verifies it, and commits. Every session's work is logged
in `CHANGELOG.md`, and the running to-do state lives in `HANDOFF.md`.

The whole thing runs inside a **dev container** (Podman) so the environment — Python,
the browser, the fonts, the linters — is identical on my work laptop and home desktop.

---

## The major steps, in order

### 1. Decide the platform (the Tableau → website pivot)

The dashboard started as a Tableau Public prototype. The content is overwhelmingly
**text and navigation** — pillar theming, story publishing, hierarchical drill-down —
which is exactly what Tableau fights against and what a website does natively. We
wrote this reasoning down in `PROJECT-PLAN.md`, using the
[myFutureNC dashboard](https://dashboard.myfuturenc.org) as a reference model. Tableau
stays where it's genuinely good (charts), embeddable where needed.

### 2. Prototype the design

Claude built throwaway mockups so we could react to something concrete instead of
arguing in the abstract — you can still see them in the repo (`mockup-a-redesign.html`,
`mockup-b-three-column.html`, `preview-axis-options.html`). We picked a direction from
those, then Claude built the real pages.

### 3. Build the data pipeline

Our source of truth is the same set of dimension tables we already maintained for
Tableau — `DIM_Pillars`, `DIM_FocusAreas`, `DIM_Measures`, `DIM_Actions`, the
`LandingPage_*` tables — plus a Smartsheet Actions Tracker and a list of blog posts.
Claude wrote small, single-purpose Python scripts that read those and emit the JSON
the site consumes:

- `data/build-pillar-data.py` → `data/pillar-data.json` (pillars, focus areas, actions, stories)
- `data/build-measures.py` / `build-pillar-measures.py` → `data/measures.json` (headline measures, values, targets, status)

These are **scripts, not notebooks** — they run end-to-end from the command line, diff
cleanly in git, and can carry their own checks.

### 4. Build the pages

Claude hand-authored the three main pages in plain HTML/CSS/vanilla JavaScript (no
framework, no build step for the front end):

- `index.html` — the landing page
- `best-in-nation.html` — the 14 headline measures with trajectory cards
- `pillar.html` — one template that renders any of the eight pillars from `?p=N`

The JS fetches the JSON at load time and builds the cards, tabs, charts, and the
"What's in Motion" ticker. Brand assets (logos, pillar gradients, measure icons) came
from our graphics team and live under `images/`.

### 5. Make it accessible and responsive

Claude ran a WCAG 2.1 AA remediation pass over both pages (contrast, alt text, reading
order, keyboard nav) and added the responsive mobile/tablet layouts. Accessibility is
re-checked with automated tooling on an ongoing basis (see tools below).

### 6. Refine content with the real stakeholders

A lot of the work was iterating on wording — opening blurbs, measure descriptions,
"why it counts" text — from marked-up docs (e.g. the "Coltrane" edit rounds). Claude
applied those edits in small, reviewable commits.

### 7. Ship on GitHub Pages

The site deploys as static files via **GitHub Pages** — commit to `master`, push, and
the live site rebuilds. GitHub Pages is already accepted NCDPI hosting for this kind of
public static site. (`push = deploy`, so we're deliberate about when we push.)

### 8. Keep it current (the ongoing loop)

This is most of the day-to-day now. Three kinds of update, each with a repeatable routine:

- **Monthly-ish action statuses** — pulled from Smartsheet (project leads edit there),
  normalized, and rebuilt into the JSON.
- **Weekly stories from the field** — the CTG blog list is scraped, new posts matched
  to focus areas, reviewed, and folded in.
- **Annual measure actuals** — e.g. the 2025–26 graduation rate and proficiency numbers,
  carried over from the Accountability team's pipeline, verified, and published on
  embargo timing.

---

## The tools Claude used

**Front end (the website itself)**
- Hand-written **HTML, CSS, and vanilla JavaScript** — no framework
- JSON data files the pages fetch at load (`data/*.json`)

**Data pipeline**
- **Python** (pandas) build scripts: spreadsheets → JSON
- Source formats: Excel (`.xlsx`) and CSV dimension tables

**Live data sources**
- **Smartsheet connector** — pulls current action statuses straight from the tracker leads use
- **Blog scraping** — pulls the CTG blog list; parallel "matcher" passes map posts to focus areas

**Verification (before anything ships)**
- A folder of **Python `verify-*.py` scripts** (`tools/`) that check the built data:
  chart scales, value labels, the 2026 actuals, badge chips, "What's in Motion" logic
- **Headless browser (Playwright)** — Claude actually renders the pages at phone/laptop/wide
  widths and confirms there are zero console errors and that charts truly draw (not just that
  the page loads)
- **axe-core + pa11y** — automated accessibility scans

**Repeatable routines ("skills")**
- Project-specific commands Claude can invoke — `rebuild-data`, `refresh-blogs`,
  `check-data`, `check-images`, `review-dashboard`, `dashboard-accessibility`,
  `update-dashboard`. These package the multi-step routines above so they run the same
  way every time.

**Environment & delivery**
- **Dev container (Podman)** — identical toolchain across machines
- **git + GitHub Pages** — version control and hosting; every session recorded in `CHANGELOG.md`

---

## How a typical change actually goes

1. I describe what I want (e.g. "refresh the action statuses from Smartsheet").
2. Claude proposes a short plan; I approve it.
3. Claude pulls the source, runs the relevant build script, regenerates the JSON.
4. Claude runs the verify scripts and renders the pages headlessly to confirm nothing broke.
5. It commits the change locally with a clear message.
6. When I say so, it pushes — which deploys to the live site — and spot-checks production.

The guardrails matter as much as the speed: Claude plans before it builds, commits in
small reviewable chunks, never pushes without my go-ahead, and never fabricates a result —
if a check fails, it tells me and shows the output.

---

## What made this work well

- **Data separated from presentation.** Updates change JSON, not HTML. Non-technical
  content edits and data refreshes are low-risk.
- **Everything is verifiable and re-runnable.** The verify scripts and headless renders
  mean "it works" is demonstrated, not asserted.
- **Small commits + a written log.** `CHANGELOG.md` and `HANDOFF.md` mean any session
  (or any person) can pick up exactly where the last one left off.
- **The right tool for each job.** A website for text and navigation; Tableau/charts
  where charts shine; Python for the data plumbing; a browser for the visual truth check.

---

*Questions? The full project plan is in `PROJECT-PLAN.md`, and every session's work is
logged newest-first in `CHANGELOG.md`.*
