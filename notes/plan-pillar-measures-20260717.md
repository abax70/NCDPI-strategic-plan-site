# Plan — Pillar Measure Charts (approved 2026-07-17)

Approved by Andy 2026-07-17 in the planning session. This is the pickup doc for
the implementation chunk sessions. Deadline chain: **Y-set populated by Mon
7/20 noon** (Geoff → Supt. Green; SPAC 7/21) → additional data by Fri 7/24 EOD
→ holding pattern to the 8/5 state board meeting.

## Goal

Replicate the Best-in-Nation two-chart format (zoomed trajectory strip +
annual-results bars + status band) on each pillar page's Results tab, for
finalized (`Y`) non-BiN measures. ~15 expected to have data by 8/5; **7 are Y
today** (6 clean + 1 excluded, see below).

## Source

Google Sheet `StrategicPlan_measures`, file ID
`1QZygNNSdtG2mCWP-tB_DbTi9PMD6ezwAB1nTWZJPBGU` (owner Geoff Coltrane; Andy's
work Drive). Readable via the claude.ai Google Drive connector (verified
2026-07-17 — grants took time to propagate to this container; if reads come
back empty, retry before debugging). **Canonical script input is a downloaded
xlsx/CSV export in the repo** (`data/source/`); the connector is a convenience
for reading Geoff's live copy. It is Geoff's working scratchpad — expect
mid-edit rows, prose in flag columns, duplicate IDs.

## Decisions (Andy, 2026-07-17)

1. **BiN measures appear only on the BiN page.** Pillar Results tabs show only
   non-BiN finalized measures, plus a "View the Best in the Nation measures"
   link (P1/P8 especially). No duplication.
2. **P5.M2 (NCSIS milestone measure, values all `1`) is excluded from
   charting** with a build warning; raise with Geoff. No new component for it
   under deadline.
3. **Status text is derived, not hand-authored** — compare latest actual vs.
   that year's target ("On target" / "Approaching target" / baseline-year
   wording), with a hand-override field preserved in the JSON.
   Direction-aware: for decrease measures (e.g. P4.M4 chronic absenteeism),
   direction = sign(2030 target − earliest value); "on target" inverts.
4. **Sub-measure IDs (Geoff's splits, e.g. P2.M2 → P2.M2a/P2.M2b):**
   - ID pattern widens to `P\d+\.M\d+[a-z]?` in the new pipeline only.
   - **DIM_Measures.csv is the site-side registry.** Andy adds a row per
     sub-ID (short name + MeasureSort) as Geoff splits; base row may remain.
   - Y-flagged ID not in DIM → **excluded with a loud warning** (not an
     abort, not a guess). The end-of-run warning list is Andy's per-wave
     to-do list. Mirrors the P2.F2.A4 unknown-action precedent.
   - Both base and sub-ID Y simultaneously → warn + exclude the pair
     (Geoff mid-split).
   - Previously-charted ID missing from the Y set → drop with warning
     (build-measures.py convention).
   - BiN pipeline (`build-measures.py`) keeps its strict regex, so DIM
     sub-ID rows are invisible to it — no interference.
5. **Separate output file** `data/pillar-measures.json` (not folded into
   pillar-data.json): different refresh cadence, smaller diffs, mirrors the
   BiN pattern of one JSON per page concern.
6. **Chief / NCDPI Business Owner / Responsible DPI Person columns never
   enter the JSON** — staff names, public repo, not displayed on the site.

## Column mapping (sheet → contract)

Contract = the measures.json schema that best-in-nation.html already consumes
(see `data/build-measures.py` and `data/measures.json` for reference shapes).

| Sheet column | Contract field | Notes |
|---|---|---|
| `Finalized?` | filter | strict `== "Y"` after trim/case-fold — column contains prose ("Question removed from YRBS survey") |
| `Pillar` | cross-check | warn if ≠ ID prefix |
| `Measure ID` | `measureId` | `P\d+\.M\d+[a-z]?`; duplicate exact IDs among Y rows → hard abort |
| `Measure` | `goal` | full sentence; `name`/`menuLabel` come from DIM join (`MeasureName`/`MeasureLbl`) |
| `When Available?` | `nextUpdate` | free text; pass through cleaned |
| `Current (2024)` | dataSeries 2024 → `baseline` | BiN convention: actuals live in `baseline` |
| `2025 (Actual)` | dataSeries 2025 → `baseline` | |
| `2026`–`2030 (Target)` | dataSeries year N → `target` | |
| `Source` | `sourceLabel` + `sourceUrl` | split prose/URL heuristically; warn on multi-source cells (e.g. P1.M8) for hand review via `sourceHtml` |
| `WhyMeasureMatters` | `whyItCounts` | empty in sheet today; wired for when Geoff fills it |
| `MeasureContextNote` | `notes` | |
| — (derived) | `valueFormat` | inferred from cell strings: `%` → `#.#%`, `$` → **new `$#,###` format** (also needs a chart axis/label formatter — BiN has no dollar measures), commas → `#,###`, else `#`/`#.#` |
| — (derived) | `yAxisMax` | headroom above series max, BiN-style rounding |
| — (derived) | `statusType`/`statusLabel` | per decision 3; hand-override preserved on rebuild |
| — (DIM join) | `name`, `menuLabel`, sort order | `DIM_Measures.csv` |
| — (DIM_Pillars) | `pillarNumber`, `pillarName` | |

**Parsing rules:** `-`, `TBD`, `?`, blank → null, never 0. Strip `$`, `%`,
thousands commas before float parse. Values like `72.10%` normalize fine.

## Today's Y inventory (2026-07-17)

20 Y rows − 13 already on BiN (12 P1 + P8.M2) = **7 net-new**:
P1.M5 (raw counts; goal text mid-edit), P1.M10, P4.M4 (decrease measure),
P4.M7 (no 2024 baseline), P5.M2 (**excluded** — all-1s milestone), P5.M3,
P7.M2 (no baseline year). BiN's P1.M15 is *not* Y in the sheet (consistent
with its "Data coming soon" state).

**Flag-to-Geoff list (script warns, Andy carries):** P1.M8 goal text 41% vs
2030 column 42.0%; P1.M3 text 29% vs column 30.0%; P5.M2 chartability.

## Chunks

| # | Chunk | Scope | Model | Status |
|---|---|---|---|---|
| A | Sheet triage + mapping | done in planning session — this doc is the output | Fable | ✅ done |
| B | `data/build-pillar-measures.py` | sheet export → `pillar-measures.json`; strict-Y, dup-abort, sub-ID rules (decision 4), null-safe parse, `$` format, source splitter, DIM join, derived status, loud warning summary; model on build-measures.py's merge-mode (preserve hand-authored overrides) | Fable or Opus | |
| C | Results-tab rendering | transplant BiN two-chart component + status band into pillar.html `buildResultsTab()`; per-pillar conditional — charts for finalized measures, existing "data coming" note otherwise (and per-measure note when a pillar has some-but-not-all); BiN link per decision 1; size check 375/1280/2560 | Opus | |
| D | Populate + verify | run pipeline on real Y set; headless pass on every affected pillar (P1, P4, P5, P7 today); console errors, rendering, `?p=N` param (not `?pillar=`) | Sonnet | |
| E | Accessibility + final review | aria labels on canvases, plain-language chart descriptions (BiN pattern), contrast, keyboard; deploy + live check | Fable | |

Sequencing: B → D; C independent of B (build against the 14 BiN measures as
test data). C can run parallel to B in separate sessions.

## Chunk-session notes

- Pin CDN versions if any new script tags are added (Chart.js is pinned at
  4.4.7 + annotation 3.1.0 — keep).
- Charts must be verified to actually *render*, not just page-load.
- Hard-refresh reminder after visual changes.
- Container: no concurrent heavy stages (7.7 GB RAM); logs not pipes.
- Each chunk session ends with its own commit (Andy approves) — don't batch
  the whole project into one.
