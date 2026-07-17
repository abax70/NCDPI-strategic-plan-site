# CHANGELOG — NCDPI Strategic Plan Site

Newest session first. Started 2026-07-15; earlier history lives in `git log`.

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
