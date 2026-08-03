---
cc_status: hot
cc_strand: strategic-plan
cc_updated: 2026-08-03
---

# HANDOFF — NCDPI Strategic Plan Site

_Last updated: 2026-08-03. See CHANGELOG.md for the full record of that session._

## Where things stand

**The board views the site Wednesday 8/5.** Everything below is pushed and live.

The 8/3 session was a pre-board integrity pass. It found and fixed **three false
claims** the site was making: 22 action cards saying "Launched" for actions that
had not started, bar value labels showing **wrong numbers** at mobile width
(`97,317` → `97,31`), and a sidebar stamp reading "Jul 15" while serving 7/27+
data. All four verify tools pass.

**Geoff is back.** No check-in was held 8/3.

## FIRST: finish the review pass — Andy said "first thing tomorrow"

`notes/review-packet-20260727.md` is **partially reviewed**.

**Done 8/3:**
- All 5 descriptions. P6.M1a verified accurate; **P6.M1b corrected** (denominator
  now requires both a performance grade *and* a growth score, per
  G.S. 115C-105.39A(a)); the other three read and nodded.

**Still open — nothing signed off:**
- **Section B** — the hand-authored `sourceHtml` lines. Note the packet says
  4; there are now **8** (P2.M2a/b were already missing from the count, and
  8/3 added P1.M1 and P1.M10).
- **Section C** — the 7/24 DIM structural edits: `P2.M3c → P2.M3b` rename,
  `P4.M6` split into a–d, `P6.M1c` removed. Also worth a deliberate glance:
  **P5.M3 was retitled by Geoff**, not Andy.

**`DRAFTED_SINCE_REVIEW` in `tools/export-metric-text.py` is UNTOUCHED** and still
lists all five IDs; `notes/measure-metric-text.tsv` was **not** regenerated. That
is deliberate. Removing an ID early has laundered unreviewed prose as approved
**twice** (7/27, both caught). When a description is signed off, remove its ID and
re-run the tool — not before.

## Next session queue

1. **Finish the review pass** (above), then update `DRAFTED_SINCE_REVIEW` +
   regenerate the TSV.
2. **Ask Geoff the 8/3 questions** — `notes/geoff-open-questions.md` is the
   short-form list (15 items, 8/3-new ones marked). The two most urgent, because
   they are about what the board sees Wednesday:
   - Is **"Planned for August, 2026"** the wording he wants on 22 action cards?
   - Did **P7.F3.A3** and **P8.F2.A1** regress to Not Started deliberately, or did
     a project lead mis-click? P7.F3.A3 has now moved twice.
3. **Watch for Shaun** (the four YRBS P4.M6 measures) and **Curtis** (low-performing
   schools) → Andy flips those asterisks to Y → that wave brings P4.M6a–d live.
   Expect parser warnings: P4.M6a's 2030 target cell is a literal `-%` and the
   YRBS series are biennial ("-" in off years).
4. **After 8/5:** the chart-engine extraction (see parity rule below).

## Longer-running carry-overs (not blocking)

- **P2.M4a says PSUs but may count LEAs.** The 7/27 retitle aligned the title with
  its approved description; it did **not** change what the sheet counts. Same family
  as the P5.M3 unit question. Note LEA is *genuinely correct* for P1.M17b (federal
  IDEA determination at LEA level), and "district" is correct for P6.M1b (district
  identification applies to LEAs; charters are not in districts). The site will
  legitimately use both words — be deliberate rather than normalizing them.
- **P1.M17b's "Annual Results" chart is ~200px of near-empty white** — all bars are
  zero-height, showing a row of `0.0%` labels on the baseline. More pronounced on
  mobile. Deliberately left as-is for Geoff's reaction; he has not yet seen it.
- **P1.M17b's year suffix** uses the site-standard `(2024–25)` but the source is
  SPP/APR **FFY 2024**, a federal fiscal year.
- **WhyMeasureMatters** for pillar measures (no `whyItCounts` on any); the export's
  `MeasureContextNote` and `WhyMeasureMatters` columns are empty in every row.
- **P5.M2 chartability** — all-1s NCSIS milestone; excluded by name.
- **P1.M5** stays a **count**; the percentage idea sits in the export's
  `Notes on Recommended Changes` side tab, which the pipeline never reads.
- **P2.M3a `nextUpdate`** — "When Available?" cell is blank (no Next update line).
- **P2.M2b and P2.M3a derive no status pill** — both regressed vs. prior year; the
  rule refuses to print "Approaching target" over a decline. `statusOverride` if
  Geoff wants text there.

## Repo state notes

- Local `master` = `origin/master`; pushes deploy via GitHub Pages
  (production URL: abax70.github.io/NCDPI-strategic-plan-site).
- **Verification is now FOUR tools**, all passing as of this wrapup:
  - `tools/verify-charts.py` — 8 pillars × 3 widths; cards, painted pixels,
    jump-strip contract, console clean.
  - `tools/verify-bin-chips.py` — 14 BiN measure-ID chips, tints, console.
  - `tools/verify-chart-scales.py` — reads live Chart.js scale objects and asserts
    axis invariants. `--self-test` runs without a browser.
  - `tools/verify-value-labels.py` — **new 8/3.** Asserts no two *drawn* value
    labels overlap, and that the first and last always survive the cull. Catches
    what the other three structurally cannot: **painted pixels prove nothing about
    whether the number is complete.** 108 charts across 4 widths. `--self-test`
    confirms all four invariants still fire.
  - **Each tool exists because a real bug slipped past the previous ones.** If a
    new bug class appears, the pattern is to add a fifth, not to widen one.
- **`tools/update-stamp.py` owns the "Last updated" date.** `build-pillar-data.py`
  now *preserves* the field rather than stamping `TODAY`. Run `update-stamp.py`
  after any data wave; `--check` exits 1 if content moved without a bump (good
  pre-push hook); `--force` for structural changes a fingerprint cannot detect.
  Baseline lives in tracked `data/stamp-state.json`.
- **Smartsheet live pull works from the container** — `data/.smartsheet-token`
  exists and `build-pillar-data.py` refreshes `data/action-statuses.csv`
  automatically. The CSV's 4th column is a pull date, so *every* row shows as
  changed in `git diff` even when no status moved; compare column 2 to see real
  churn.
- `data/DIM_Measures.csv` **has ragged rows** — a Sheets export artifact where some
  rows carry 28 trailing empty fields and others 6. Edit it with line-level surgery,
  **not** a `csv` round-trip, or the whole file reformats.
- **`data/build-measures.py` treats DIM `MeasureName` as canonical for BiN
  measures.** Before renaming any DIM row, check its `BestInNationGoal` flag; if it
  is set, the rename changes the Best-in-Nation page too.
- **`sourceHtml` is a PRESERVE field in both build scripts** and both renderers
  prefer it — it is the correct place for any hand-authored Source line. A
  `sourceLabel` edit gets overwritten by the next build.
- `data/measure-gaps.md` is generated every run and deliberately tracked. It never
  quotes raw sheet prose (public repo) — **the same rule governs anything written
  into `notes/`.** Its date stamp changes every run, so it always shows in
  `git status`; that is expected, not drift.
- **Chart engine parity rule still in force** for the SHARED engine: bug fixes land
  in BOTH `pillar.html` and `best-in-nation.html` until the post-8/5 extraction.
  The 8/3 label cull is the most recent example. Deliberate departures, commented
  in place: the jump strip (pillar only), the pillar measure-card header markup,
  and the BiN measure-ID chip.
- `pillar.html`'s deep-link param is **`?p=N`**, not `?pillar=N`.
- Tracked notes: `punchlist-20260720.md`, `meeting-agenda-20260724.md`,
  `meeting-agenda-20260803.md`, `sheet-edits-20260727.md`,
  `review-packet-20260727.md`, `measure-metric-text.tsv`,
  `geoff-open-questions.md`.
- **Stray file to relocate (not ours):**
  `images/HappyPeoplePhotos/reporting-process-guide.html` belongs in
  **EPP-Codebase** — Andy to move it from the host; unreachable from this container.

## Scratchpad harnesses NOT committed (recreate if needed)

The one-shot scripts from 8/3 live only in the session scratchpad and will vanish:
`set_disagg_source.py` (applies the disaggregation `sourceHtml`, aborts if the row's
`sourceUrl` drifts from the URL baked into the hand-authored HTML), and the ad-hoc
screenshot/sweep helpers. The sweeps were **superseded** by
`tools/verify-value-labels.py` and should not be resurrected — they measured
*candidate* labels with a fallback formatter and undercounted the bug by ~13x.
