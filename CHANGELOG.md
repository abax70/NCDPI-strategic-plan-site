# CHANGELOG — NCDPI Strategic Plan Site

Newest session first. Started 2026-07-15; earlier history lives in `git log`.

## 2026-07-22 — Geoff's punch list: descriptions, footnote move, MeasureName prep

**Context:** Geoff + leadership's "last" feedback round (from the 7/22 3pm
meeting), four items, none contested. New anchor date agreed: **measures
lock EOD Fri 7/24** for the 8/5 board meeting. Andy ran out of gas before
reviewing the drafted description text — review carries to next session
(four specific flags in HANDOFF).

### Shipped

- **"Additional measures…" footnote moved to the top** of the Results
  panel (item 4) — now directly under the Actions/Stories/Results picker,
  above the jump strip and cards; BiN link stays at the bottom.
  `.results-footnote` margins retuned for the new position.
- **Description line on measure cards** (item 2): pillar.html now renders
  hand-authored `definition` as "**Description:** …" between the Goal and
  the status pill — same order and typographic treatment as BiN's measure
  header (CSS mirrored, incl. the ≤480px size step).
- **Drafted `definition` + `currentDescription` for all 9 live measures**
  into `data/pillar-measures.json` (both PRESERVED pipeline fields; a
  re-run after the edits was **byte-identical**, proving they survive
  waves). Voice matches BiN's LandingPage_MeasureDetailsText.csv style:
  plain language, jargon defined, big-number phrase + "(2024–25)"-style
  period suffix. P4.M7's draft uses the sheet's concrete threshold
  ("five or fewer acts", from the raw source cell) instead of the goal's
  vague "limited number".
- **MeasureName prep** (item 1, sheet column lands by 7/24): the pipeline
  now prefers the sheet's MeasureName when present and non-blank
  (tolerant header match — "MeasureName"/"Measure Name"/any case, since
  Geoff's actual spelling is unknown), falls back to DIM, and warns into
  the gaps report on sheet≠DIM drift. DIM keeps owning IDs, sort, and
  the BiN flag.
- Item 3 (sources) needed no code — Geoff updates the sheet's Source
  cells by 7/24; the existing auto-split/warn logic handles them.

### Verified

- `tools/verify-charts.py` full PASS (8 pillars × 3 widths).
- Screenshots eyeballed at 1280 and 375 (P1, P4): footnote position,
  Description line, big-number phrases all render correctly.
- Pipeline regression: re-run on the real 7/20 export → byte-identical
  JSON (MeasureName change is neutral while the column is absent).
- Synthetic-xlsx test of the MeasureName path: "Measure Name" header
  matched, sheet name wins + drift warning fires, identical name stays
  quiet. Confirmed the name-derived `id` slug is renderer-inert
  (pillar.html anchors key on `measureId`).

### Found while working

- **P5.M3 unit discrepancy**: Geoff's raw source cell says "16 PSUs
  (15 LEAs) have migrated" but the charted value is 15 — confirm with
  Geoff whether the measure counts PSUs or LEAs (affects the drafted
  phrase "public school units").

## 2026-07-21 — Graphics-team feedback round: three small visual fixes

**Context:** Graphics team reviewed the site and sent three requests (with
screenshots). All three shipped in one commit (`8d8aeab`, pushed + Pages
deploy verified live in ~75s). Andy meets Geoff 7/22 3pm for the "last"
feedback round before the 7/24 data wave.

### Shipped

- **Pillar 4 pink → Medium Orange (#C75128)**: the `--pillar4-text` token
  (was #CB5277) in index.html, pillar.html, best-in-nation.html, plus the
  `PILLAR_TEXT` JS map in pillar.html. Drives the active tab text and
  Stories links. **Contrast improved both places it renders**: 4.53:1 on
  white (the old pink was 4.19:1 — a latent AA miss for the 16px story
  links, despite the JS map's "4.5:1 on white" comment) and 4.22:1 vs
  3.90:1 on the panel bg for the large-text tabs. WCAG comment at the
  tab-btn rule updated with the new numbers.
- **Homepage photo-stack swap**: track girl (arms raised) to the top,
  painter to the bottom — her raised arms directly below the recycle-bin
  photo read as if she were holding the bin. HTML comment updated (the old
  one documented the opposite ordering rationale).
- **Mobile hero logo breathing room**: root cause — the 5px pillar-color
  bar (`.hero-banner::after`) overlaps the bottom of the logo strip once
  the hero stacks, and at ≤480px the 50px logo in a 60px strip had **0px**
  visible space above the bar. Fix: strip 80→88px (≤768px) / 60→72px
  (≤480px) + `padding-bottom: 5px` on the overlay so the flex-centered
  logo re-centers in the space *above* the bar (~12px / ~8.5px clear now,
  matching the pillar pages' logo band).

### Verified

- `tools/verify-charts.py` full suite PASS (first real use since it was
  promoted to a tool — 8 pillars × 3 widths, zero console errors).
- Headless screenshots of all three fixes at 375/700/1280; computed colors
  confirmed `rgb(199, 81, 40)` on the P4 active tab and story link.
- Production spot-checked after push: #C75128 serving on all three pages,
  new strip heights live, photo order flipped.
- Gotcha for future screenshot scripts: Playwright's `clip` uses
  *document* coordinates, not viewport — clipping y:0 after a scroll
  still shoots the top of the page.

## 2026-07-20 (second session) — Pre-7/24 prep: jump strip, DIM reconciliation, verify tool

**Context:** Prep session between the noon deadline and the 7/24 EOD data wave.
All three queued HANDOFF items landed, plus both open decisions resolved
(punch list now tracked; verify routine promoted to a tool).

### Shipped

- **Jump strip (punch #6)** in `pillar.html`: when a pillar has 4+ measures,
  `buildResultsTab()` prepends a nav card of anchor links — measure name left,
  status pill right — doubling as an at-a-glance status summary. Measure cards
  got `id="measure-<ID>"` anchors. **Deliberately NOT mirrored in
  best-in-nation.html** (parity-rule departure, commented in place: BiN's
  carousel renders one measure at a time, so anchors into stacked cards have
  no equivalent). No pillar triggers it yet (max is P2's 3), so it was
  verified synthetically: fetch-intercepted a 4th P2 measure → strip appears,
  all anchors resolve, all pill variants render (incl. no-pill for
  null-status P2.M2b), anchor click scrolls the card into view.
- **`tools/verify-charts.py`** — the twice-rebuilt scratchpad verify routine
  is now a real tool. Serves the repo on localhost, drives headless Chromium
  over 8 pillars × 3 widths (375/1280/2560): zero console/page errors, card
  counts vs pillar-measures.json (placeholder when 0), painted-pixel test on
  every canvas, and the jump-strip contract (present iff 4+ measures, one
  link per measure, no dead anchors). `--screenshots DIR` uses a
  taller-than-page viewport instead of `full_page` (the Chart.js mid-resize
  freeze gotcha from 7/20). Full run: PASS.
- **DIM two-way audit (punch #3)**: the sheet had restructured **five base
  measures into sub-splits** — P1.M17→a/b, P2.M2→a/b, P2.M3→a/c, P2.M4→a/b,
  P6.M1→a/b/c. Removed the 5 stale base rows from `DIM_Measures.csv`, added
  the 8 missing sub-ID rows (55 rows total, both directions now fully
  reconciled). Short names for the new rows are Claude drafts for Andy's
  diff review (e.g. "Beginning Teacher Retention", "Low-performing
  Districts"). Safe for the BiN build (DIM is lookup-only there; all 5
  removed bases were non-BiN). Pipeline re-run after the edits produced a
  **byte-identical pillar-measures.json** — neutral to the 9 live measures.
- **Gaps report now self-audits DIM (punch #3 follow-through)**:
  `build-pillar-measures.py` censuses ALL sheet Measure IDs (not just
  Y-flagged) and writes a "DIM ↔ sheet reconciliation" section into
  `data/measure-gaps.md` every run — unregistered sheet IDs, stale DIM IDs,
  malformed IDs, duplicate-ID rows. Registry drift can't silently recur.
- **`notes/punchlist-20260720.md` is now tracked** (Andy's call).

### Sheet anomalies found (for Geoff, via the gaps report)

- **P4.M6 is shared by 4 rows** (40–43, the YRBS mental-health items; one
  marked "Question removed from YRBS survey"). Needs distinct sub-letters:
  2+ flagged Y aborts the build; exactly one Y would chart under the
  ambiguous shared ID.
- Row 2 has a literal **`NEW`** as its Measure ID (Schools of Character).
- The sheet has **P2.M3a and P2.M3c but no P2.M3b** — possibly deliberate;
  confirm while pinging Geoff.

## 2026-07-20 — Deadline-day data wave + chunk E + punch-list build-out

**Context:** The noon deadline (Y-set populated; Geoff → Supt. Green today,
SPAC 7/21). Everything shipped and deploy-verified live well before noon.
**The pillar-measure-charts plan is now complete, chunks A–E.**

### Shipped (3 commits: `1e2b9a2`, `0c7bcb0`, `5fc264d`, all pushed + live)

- **Renormalize sweep** (`1e2b9a2`): one-time LF rewrite of 3 CRLF-stored
  CSVs (244 lines, content-identical under `--ignore-cr-at-eol`). The
  CRLF/LF churn issue is permanently closed.
- **Data wave** (`0c7bcb0`): fresh sheet export → **3 new P2 measures**
  (P2.M2a EPP Enrollment, P2.M2b EPP Completion, P2.M4a PSUs with Advanced
  Teaching Roles) — Pillar 2 went 0 → 3 charts with zero renderer changes
  (the conditional is data-driven, as designed). Added the DIM_Measures.csv
  registry rows for Geoff's finalized sub-IDs; fixed 3 DIM typos ("Rolese",
  "Stuff Pay", "$67 ,641"). The 6 existing measures came through
  byte-identical (no data changes this wave; preserved fields survived).
  Hand-authored `sourceHtml` for P2.M2a/b — Geoff's parenthetical
  methodology note had auto-split into the *link text*; now "NCDPI EPP
  Dashboard" links with the note trailing in parens. P2.M2b derives **no**
  status pill (2,096 → 2,088; the regression rule working as intended).
- **Chunk E accessibility** (`5fc264d`): audit came back strong — axe-core
  WCAG A/AA **zero violations** on Results tabs, status-pill text contrast
  8.9–13.7:1, every canvas already `role="img"` with plain-language labels,
  keyboard order sane. One real gap found and fixed: charts ignored OS
  **prefers-reduced-motion**; now `Chart.defaults.animation = false` under
  it, in BOTH pillar.html and best-in-nation.html (parity rule).
- **Punch list** (from Andy's review, `notes/punchlist-20260720.md`) —
  adjudicated all 6 items; approved recs built same-day in `5fc264d`:
  - **#1 Measure-ID chips** on measure cards (`.action-id-badge` reuse).
  - **#2 Gaps report**: pipeline now writes `data/measure-gaps.md` every
    run — per-measure missing sheet fields (for pinging Geoff) + the
    warning list. Tracked via a `.gitignore` negation of `data/*.md`.
    **Deliberately never quotes raw sheet cell text** (public repo; same
    rationale as gitignored `data/source/`). Day one: 9/9 measures have
    gaps (no WhyMeasureMatters anywhere; only P1.M5 has a Next update).
  - **#4a Nice-number y-max**: derived yAxisMax now rounds up to a nice
    mantissa (68.4 → 70, 3,720 → 4,000, 131,400 → 150,000) — matches the
    convention Andy's hand-set BiN maxes already followed (1.2× then round).

### Decisions

- **Stacked cards stay; no carousel** (punch #6). Decisive argument: the
  BiN carousel renders one measure's DOM at a time, so a print/PDF for a
  board packet would capture one chart of N; stacking prints the whole
  dossier, keeps Ctrl+F working, and keeps free heading navigation for
  screen readers. Independent design-agent opinion concurred. Mitigation
  for long pages: a **jump strip** (measure name + status pill as anchor
  links) when a pillar hits **4+ measures** — queued, no pillar triggers
  it yet.
- **Single source of truth** (punch #3): the JSON is *not* it. Three
  layers, each owning its slice — Geoff's sheet: data + what's finalized;
  DIM_Measures.csv: site-facing identity (official IDs incl. sub-splits,
  short titles, sort); pillar-measures.json: generated output + Andy's
  hand-authored presentation overlay. Claude edits DIM directly (Andy
  reviews via diff). Two-way DIM-vs-sheet audit queued.
- **Status vocabulary clarified** (punch #5): "baseline" was never
  blanket-replaced — it still applies to single-actual measures. The
  ladder: meets same-or-next upcoming target → On Target; improved vs
  prior year → Approaching Target; regressed → no pill. P1.M5 is
  Approaching because it improved but hasn't met the *2026* target
  (no 2025 target needed). BiN's statuses are hand-curated
  (record-high/baseline) and stay that way until a post-8/5 unification.
- **Screenshot-artifact gotcha** (worth remembering): a Playwright
  `full_page` capture of a page *taller than the viewport* expands the
  window mid-shot and freezes Chart.js mid-resize-animation — bars pile
  up at the left edge and look badly broken. Not a site bug. Use a
  viewport taller than the page when screenshotting chart pages.

### Session mechanics

- The chunk-C verify routine was rebuilt from scratch (prior session's
  scratchpad was gone): 8 pillars × 3 widths, per-canvas painted-pixel
  check, card counts vs JSON, console clean. Still scratchpad-only —
  candidate for `tools/verify-charts.py` if we keep rebuilding it.

## 2026-07-17 (evening) — Housekeeping before the Monday deadline

**Context:** Short end-of-day session to knock off quick, low-risk items ahead
of the 7/20 noon data wave. No feature work.

- **Deleted two stale untracked files** (both flagged in HANDOFF): the draft
  blog→focus-area match CSV (`data/blog_focus_area_matches_draft_2026-07.csv`)
  and the raw braindump note (`notes/pillar-measures-20260717.md`, content
  already graduated into the plan doc).
- **P1.M10 `sourceLabel` set** to "NCDPI Proficiency dashboard" in
  `data/pillar-measures.json`. Root cause found: the pillar.html render logic
  has no branch for a bare `sourceUrl`, so a measure with only a URL and no
  label renders **no Source line at all** — the label is what makes the
  Tableau link appear. (Still open: hand-authored `sourceHtml` for P4.M4,
  P4.M7, P5.M3, P7.M2.)
- **Added `.gitattributes`** (`* text=auto eol=lf`) to permanently fix the
  intermittent CRLF/LF churn between the Windows host and the Linux container.
  The one-time `git add --renormalize .` sweep of already-tracked files is
  deferred to the start of the next session (HANDOFF step 0) so its
  line-ending-only diff stays isolated from the data-wave work.

## 2026-07-17 (chunk C) — Pillar Results tabs render measure charts

**Context:** Third chunk of the pillar-measure-charts plan; same deadline chain
(Y-set populated by Mon 7/20 noon → 7/24 → 8/5 board meeting). Chunk D's
verification effectively rode along, since `data/pillar-measures.json` is
already real data.

### Shipped (pillar.html only, +918 lines)

- **BiN chart engine transplanted into pillar.html** — formatters, style-guide
  colors, hatch pattern, trajectory strip + annual bars, legend, notes/source
  block. Kept near-verbatim against best-in-nation.html on purpose (fix a bug
  in one → fix it in both; shared-file extraction is a planned post-8/5
  cleanup). Chart.js pinned at 4.4.7 + annotation 3.1.0, same as BiN.
- **Four deliberate departures from the BiN engine**, each commented in place:
  1. Measures stack vertically in `.measure-block` cards (no carousel);
     element lookups are per-block instead of fixed IDs; titles are h3.
  2. `$#,###` value format added to all three formatters (BiN has no dollar
     measures; the pipeline can emit one any wave).
  3. **Direction awareness** — for decrease measures (P4.M4 chronic
     absenteeism, 25% → 15%) the trajectory anchors the target as the *bottom*
     labeled tick (BiN hardcodes upward) and the meets/below bar coloring
     inverts via `isDecreaseMeasure()`.
  4. **New status band** — green pill for `on-target`/`record-high`, blue for
     `approaching-target`, muted gray for `baseline`/unknown; hand-authored
     `statusOverride {type, label}` always wins over derived fields; null
     status renders no pill (the pipeline's regression rule).
- **Lazy chart rendering** — tab panels are `display:none` when inactive, so
  a canvas rendered there sizes to 0×0. `buildResultsTab()` builds DOM
  immediately but defers Chart.js creation until the Results tab is visible;
  `switchTab()` flushes the pending render. Chart instances are tracked and
  destroyed on pillar switch.
- **Per-pillar conditionals** — P1/P4/P5/P7 get stacked measure cards + a
  "more measures coming" footnote + BiN link; P2/P3/P6/P8 keep the original
  placeholder (which already carries the BiN link). Decision 1 (no BiN
  duplication) holds.
- `pillar-measures.json` is fetched alongside pillar-data.json at init;
  a fetch failure degrades to the placeholder and never blocks
  Actions/Stories.

### Verified

- Headless Playwright at 375/1280/2560 across all 8 pillars: every canvas
  confirmed to **paint non-blank pixels** (not just page-load), placeholder
  states correct, pillar-switching while on the Results tab rebuilds cleanly,
  zero console/page errors. P1 + P4 screenshots eyeballed.
- Synthetic tests for paths real data doesn't exercise yet: `$#,###`
  formatting, `statusOverride` precedence (with star icon for record-high),
  null-status → no pill.

## 2026-07-17 (chunk B) — Pillar-measures pipeline built and verified

**Context:** First implementation chunk of the pillar-measure-charts plan
(deadline chain: Y-set populated by Mon 7/20 noon → more data by 7/24 → holding
pattern to the 8/5 board meeting).

### Shipped (commits `73f84d9` code + docs commit, both pushed)

- **`data/build-pillar-measures.py`** — repeatable cleaning script: reads the
  downloaded xlsx export of Geoff's `StrategicPlan_measures` sheet
  (`data/source/`, gitignored) and emits **`data/pillar-measures.json`** in the
  measures.json schema, so pillar.html can reuse the BiN chart component.
  Each data wave = re-run + work the warning list, not a re-clean.
- All plan decision rules implemented and tested (synthetic xlsx tests for the
  guards the real data doesn't exercise): strict-Y filter, duplicate-ID hard
  abort (no output clobber), widened `P#.M#[a-z]` sub-ID pattern with
  DIM_Measures.csv as registry (unknown / mid-split IDs excluded with loud
  warnings), P5.M2 excluded by name, format-aware parsing (percent cells are
  *fractions* with `%` number formats → converted to percent points; `-`/`.`/
  `TBD` → null), direction-aware derived status, BiN-style yAxisMax (1.2 ×
  series max, percent-capped at 100), end-of-run warning summary.
- **First real run: 6 measures charted** (P1.M5, P1.M10, P4.M4, P4.M7, P5.M3,
  P7.M2), 13 BiN rows skipped, P5.M2 excluded — matches the plan inventory.
  Output is contract-identical to a BiN measures.json entry (verified
  field-by-field) plus one new field, `statusOverride`.
- Testing caught and fixed a real bug: the sub-ID sibling check used
  `startswith`, which would have false-matched P1.M10 as a sub-ID of P1.M1.

### Decisions

- **New derived-status vocabulary** (chunk C renders it): `on-target` /
  `approaching-target` / `baseline`, labels like "Approaching Target — 24.3%".
  Derived fields regenerate every run; the hand-override lives in
  `statusOverride` `{type, label}` (preserved, renderer should prefer it). A
  regression vs. prior year derives *no* status (null + warning) rather than
  printing "Approaching target" over a decline.
- **Scratchpad prose never auto-publishes.** Most Source cells are Geoff's
  meeting notes (one literally contains an open question). Only clean
  "prose + one URL" or bare-URL cells auto-split; everything else stays null
  with a hand-review warning — fix-up channel is hand-authored `sourceHtml`
  (preserved field, BiN renderer already prefers it).
- **`data/source/` is gitignored** — the export carries staff-name columns
  (Chief / Business Owner / Responsible Person) and Geoff's raw notes; repo is
  public via Pages. The script never reads the staff columns (plan decision 6).
  Each machine downloads its own export; the generated JSON is tracked.

### Andy's warning-list to-dos (from the first run)

- Hand-author `sourceHtml` for P4.M4, P4.M7, P5.M3, P7.M2; add a human
  `sourceLabel` for P1.M10 (bare Tableau URL).
- P5.M2 chartability + P1.M5 mid-edit goal text ("percentage number of…") →
  raise with Geoff.

## 2026-07-17 (planning session) — Chunked pillar-measure-charts plan approved

- Sheet triage + column mapping session (chunk A of the work). Output:
  **`notes/plan-pillar-measures-20260717.md`** (commit `9675a19`) — the pickup
  doc for all implementation chunks: source/column mapping to the measures.json
  contract, sub-ID handling rules, today's Y inventory (20 Y rows − 13 BiN =
  7 net-new, P5.M2 excluded), and the chunk table (B pipeline / C rendering /
  D populate+verify / E accessibility) with per-chunk model recommendations.

## 2026-07-16 (pm) — Geoff meeting debrief folded into the plan

**Context:** Debrief of today's Geoff meeting (state board 2026-08-05). Worked as a
session from Central Command; the plan lands here per the new "notes local, dates up"
convention (Central Command keeps only the anchor dates).

### Plan
- **Primary remaining deliverable for the board update: the pillar measure charts** —
  identical in form to the best-in-nation (BiN) charts already built, but showing the
  measures tied to the non-BiN pillars. Geoff expects ~15 to have data by 8/5.
- **Source & pipeline:** measure data lives in a rough Google Sheet, `StratPlanMeasures`
  (Geoff's live scratchpad), not chart-ready. Finalized rows flagged `Y` in the
  **Finalized** column. Design call: build a *repeatable cleaning script* (not a
  one-time hand-clean) that reads the sheet and emits the BiN charts' data contract,
  since data arrives in waves.
- **Backward chain:** populate `Y` measures by Mon 7/20 noon (Geoff → Supt. Mo Green
  that day, SPAC 7/21); additional data by Fri 7/24 EOD; holding pattern
  (leadership-required changes + actions/stories only) to 8/5.
- **Open size-the-effort questions** parked in HANDOFF: were the BiN charts
  templated/scripted or bespoke? How many rows are `Y` right now?

### Docs
- `HANDOFF.md` rewritten around the pillar-chart plan (Where things stand / Next
  session / Open threads).

## 2026-07-16 — Hero polish before the Geoff meeting

**Context:** Meeting with Geoff today (state board 2026-08-05). Andy reviewed
yesterday's site edits and came in with a small punchlist. Kickoff synced the
laptop with the desktop's 5 unpushed commits (line-ending-only churn discarded
via `git restore .`, then fast-forward pull).

### Hero updates

- **Landing (`index.html`):** swapped the taglined `StratPlan-Dashboard-HomeHdr`
  lockup out; now uses `Logo-AchEdExc-WhiteOrange.png` — same clean AEE mark
  without the "Best in the Nation — Our 2030 Plan..." tagline, per graphics
  team's tagline-free preference. Also anchored the hero title ("Best in the
  Nation") to the same 1440px content frame as the sidebar heading, so on wide
  monitors it aligns with `STRATEGIC PILLARS` below instead of hugging the
  viewport edge (`max(40px, calc((100vw - 1440px) / 2 + 20px))` — mirror of the
  AEE-logo margin-right anchor on the right panel).
- **Best-in-Nation (`best-in-nation.html`):** biggest change of the session. Was
  a split hero (navy squares on left, WHITE panel with decorative corner squares
  on right, navy taglined logo). Now matches the landing treatment — one
  continuous blue-squares field spanning the full hero width with the
  `WhiteOrange` AEE lockup floating over the right side. Required hoisting the
  `.hero-banner-bg` <img> out of `.hero-banner-left` to be a direct child of
  `.hero-banner`, dropping `.hero-banner-left`'s solid navy background so the
  pattern shows through, and giving `.hero-banner` the navy fill + `overflow:
  hidden` treatment.
- **Pillar (`pillar.html`):** narrowed the CSS navy baseline strip from 5px to
  4px (~25%) — Andy's read was that it still felt thick. Logo asset unchanged
  (already tagline-free / squares-free).

### Docs

- Refreshed the "diverged forever — DO NOT reconcile" warning in the project
  `CLAUDE.md`: the divergence resolved itself once the desktop pushed its
  history and this laptop fast-forwarded; replaced the warning with a note
  about the recurring CRLF/LF line-ending churn between Windows host and
  container (verify with `git diff --ignore-cr-at-eol` before assuming files
  really changed). `CLAUDE.md` remains untracked in the repo by convention.

### Session mechanics

- Anthropic's Bash safety classifier was down intermittently through the
  session — auto mode kept blocking on any shell call. Workarounds: dropped
  out of auto mode for manual approvals, then switched to Opus 4.7 which
  cleared it. Preview server also needed `run_in_background: true` to stay
  alive between shell invocations (a plain `nohup` inside a wrapped Bash call
  gets reaped when the wrapper exits).

## 2026-07-15 (second session) — Smartsheet connector: tracker xlsx dependency replaced

**Context:** HANDOFF's queued task; meeting with Geoff 2026-07-16.

### Smartsheet-sourced action statuses (commit `2fe9658`, pushed + deploy verified)

- Discovered the tracker via the claude.ai Smartsheet connector: "Strategic
  Plan Actions Tracker" (sheet ID `6831169615122308`, NCDPI Strategic Plan
  Workspace), 110 rows with clean `Action ID` + `Status` picklist columns —
  a direct replacement for the manually downloaded xlsx.
- `build-pillar-data.py` status source is now a chain: **Smartsheet REST API
  (live, stdlib urllib, no new deps) → committed `data/action-statuses.csv`
  snapshot → legacy xlsx → hard abort.** A successful live pull rewrites the
  snapshot, so the committed copy self-refreshes.
- **The silent date-based fallback is deleted** — the trap that flipped 16
  statuses on 2026-07-15 when the xlsx was absent. The build now refuses to
  run rather than guess (tested: aborts with exit 1 before writing output).
- Token plumbing: `SMARTSHEET_API_TOKEN` env var or gitignored
  `data/.smartsheet-token` (one-line file; gitignore rule verified — repo is
  public via Pages, token must never be committed). Andy created the token
  file; the live-API path was tested with a real pull.
- **Data refresh shipped:** 5 actions flipped Not Started → In Progress per
  the live tracker (P5.F1.A3, P5.F1.A4, P7.F1.A4, P7.F3.A3, P8.F1.A1) —
  edits project leads made in Smartsheet since the last xlsx download.
  Verified rendering headlessly (pillars 5 and 8, no console errors; note
  pillar.html's query param is `?p=N`, not `?pillar=N`) and confirmed the
  GitHub Pages deploy serves the new statuses.

### Decisions

- Smartsheet's picklist value "Complete" is normalized to the site's
  historical display text "Completed" (`STATUS_DISPLAY` map in the script).
- **P2.F2.A4 exists in Smartsheet but not `DIM_Actions.csv`** — deliberately
  excluded pending Andy's investigation; the merge ignores unknown IDs, so it
  sits harmlessly in the snapshot.
- Two refresh routes now exist: ask Claude to "refresh statuses from
  Smartsheet" in any session (connector), or run the build on a machine with
  the token (live API). The scheduled download reminder Andy floated is moot.

## 2026-07-15 — Graphics-team hero updates + stories refresh (pre-Geoff-meeting session)

**Context:** Meeting with Geoff 2026-07-16; state board meeting 2026-08-05.

### Graphics team assets & suggestions (from 2026-06-10 meeting; Hallie's delivery)

- **Landing hero (`index.html`):** blue-boxes pattern now spans the full banner
  width (was clipped to the left panel — read as cut off on wide monitors).
  Replaced the white right panel with the new transparent-background white AEE
  lockup (`StratPlan-Dashboard-HomeHdr-HiRes.png`) floating over the pattern at
  85% opacity, still anchored to the 1440px content frame on wide viewports.
- **Pillar hero (`pillar.html`):** adopted the recreated gradient SVGs (graphics
  team removed the baked-in 10px navy bottom bar); the navy baseline is now a
  CSS `.pillar-hero::after` — full hero width (it previously stopped at the
  right panel) and thinner (5px, matching the landing strip weight). Right panel
  swapped to the new `StratPlan-Dashboard-PillarHdr-HiRes.png` lockup as a
  full-panel white block — this retired the per-pillar recolored patterns
  (`PILLAR_HERO_BG` removed from the JS).
- **Assets:** new logos → `images/Achieving Academic Excellence Logos/Dashboard
  Header Logos/`; new gradients replaced the old in `images/Background
  Patterns/_pillars/` (old SVGs archived to
  `images/_Archive/2026-07-15_pillar-gradients-with-navy-bar/`). Re-delivered
  `Header_Blue` PNGs were byte-identical to existing — no change.
- **Verified** headlessly (Playwright) at 375/1280/2560px on index + pillars 1,
  2, 4, 7 — no console errors.

### Stories refresh (32 new posts, 2026-01-29 → 2026-06-25)

- Scraped dpi.nc.gov/blog; appended 32 new posts to `data/blog_posts.csv`
  (now 62), counties extracted from post text.
- Matched posts to focus areas via four parallel matcher agents using the
  established conventions (1–4 substantive matches per post, one-line
  rationale). Result: 70 proposed matches across 30 posts;
  the Leandro and SB 227 legal statements intentionally unmatched.
- Andy reviewed and approved the draft as-is → folded into
  `blog_focus_area_matches_final.csv` (94 → 164 matches), reran
  `data/build-pillar-data.py`, verified Stories tabs render locally.
- Pre-update `blog_posts.csv` archived to
  `data/_Archive/blog_posts_2026-07-15_pre-update.csv`.

### Shipped

- Commit `a4fba10` pushed to master; GitHub Pages deploy verified **live**
  (production serves `lastUpdated: 2026-07-15`, 164 story matches; live-site
  hero screenshot checked at 2560px).
- `drupal-delivery/` removal (Andy deleted; committed at wrapup).

### Decisions

- `drupal-delivery/` declared stale (the Drupal-embed route is dead) — left
  untouched this session; Andy to delete. Hero changes were NOT mirrored there.
- `next-session-prompt.md` is gone (never committed); HANDOFF.md is the sole
  pick-up doc going forward.
- Landing logo opacity 0.85 and pillar baseline 5px are Claude's eyeball calls,
  flagged for Andy/graphics-team veto.
- **Rebuild trap found:** `build-pillar-data.py` needs
  `data/Strategic Plan Actions Tracker.xlsx`, which is absent in the
  devcontainer — the date-based fallback silently flipped 16 action statuses
  (including regressing a Completed action). Caught by diffing against the
  committed JSON; the previous build's statuses were restored before shipping.
  Any future rebuild here has the same trap until the tracker lives in-container
  or the Smartsheet connector replaces it.
