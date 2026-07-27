---
cc_status: hot
cc_strand: strategic-plan
cc_updated: 2026-07-27
---

# HANDOFF — NCDPI Strategic Plan Site

_Last updated: 2026-07-27 (third session of the day). The 7/27 export is fully
consumed; the export-gated queue is done. See CHANGELOG.md for the full record._

## Where things stand

**The data wave is finished.** Andy's 5 title edits + the February typo fix are in,
the fresh export is consumed, **Pillar 6 charts for the first time** (14 measures,
up from 12), and the DIM name sync cleared all 12 drift warnings. Zero data moved
in the existing 12 measures.

**Geoff is out until 8/3.** Check-in **8/3**, board meeting **8/5**.

## FIRST: Andy's review — it is the only thing gating the 8/3 table

**`notes/review-packet-20260727.md`** is written and is a single pass over
everything pending. Nothing in it blocks the site (it is all rendering live
already). What it blocks is the **MeasureMetricTxt table for Geoff**, which labels
five rows as unreviewed drafts until Andy signs off.

Covered in the packet:

- **5 descriptions** — `P6.M1a`, `P6.M1b` (drafted 7/27, new this wave), `P1.M17b`
  (drafted 7/27), `P2.M3a`, `P2.M4b` (drafted 7/24, unreviewed since).
- **4 hand-authored `sourceHtml`** lines — P2.M3a, P4.M7, P5.M3, P7.M2 — plus
  P1.M10's hand-set `sourceLabel`.
- **DIM changes** — the unreviewed 7/24 structural edits (P2.M3c→P2.M3b rename,
  P4.M6 split into a–d, P6.M1c removed) and this session's 12 name syncs.

**The one flag that genuinely needs Andy's eye:** the P6.M1a/b drafts state the
**statutory definition** of low-performing — performance grade of D or F with growth
not exceeding expected, and a district when a majority of its graded schools are.
That framing came from general knowledge, **not** from the repo or the sheet.
Confirm before it reaches Geoff.

**When a description is approved, remove its ID from `DRAFTED_SINCE_REVIEW`** near
the pillar loop in `tools/export-metric-text.py`, then re-run the tool. Leaving an
ID there under-claims; removing it early laundered unreviewed prose as approved
twice now (caught 7/27 both times — see CHANGELOG).

## Next session queue

1. **Andy's review pass** (above), then update `DRAFTED_SINCE_REVIEW` + regenerate
   `notes/measure-metric-text.tsv`.
2. **BiN disaggregation note — write text, do NOT import.** Settled earlier on 7/27
   from a Geoff email: there are **no separate URLs** for disaggregated results, so
   the plan is hand-written text on the relevant BiN Source lines, roughly *"the
   data source displays results disaggregated by subgroup."* **The exact wording is
   not recorded in this repo — get it from Andy's email before writing.** BiN rows
   are hand-curated, so this is a by-hand edit to `data/measures.json`.
   _(A prior version of this file said to import these "from the final export."
   That was wrong and cost a search: the export contains zero occurrences of
   "disaggregat" and never will.)_
3. **Refresh Smartsheet action statuses** — Geoff updated the tracker 7/25 before
   leaving. Still not done. Live-API path or connector; routine is in CHANGELOG
   2026-07-15 (second session). Fully independent of everything else.
4. **Watch for Shaun** (the four YRBS P4.M6 measures) and **Curtis** (low-performing
   schools) confirmation emails → Andy flips those asterisks to Y → that wave brings
   P4.M6a–d live. The 4 rows are currently flagged `*`, not `Y`. Expect parser
   warnings: P4.M6a's 2030 target cell is a literal `-%` and the YRBS series are
   biennial ("-" in off years).

## For the 8/3 Geoff check-in

**`notes/meeting-agenda-20260803.md`** is written and ready: the improvised defaults
to confirm (P4.M7 "five or fewer acts", P5.M3 "public school units", the P2.M3b
re-lettering), the P1.M17b caveats, the P2.M4a unit question, and the
**MeasureMetricTxt column** proposal (paste-ready table at
`notes/measure-metric-text.tsv`, now **28 measures**, no gaps).

**Two items to add to that agenda:**

- **The `Notes on Recommended Changes` worksheet.** The export has a second tab the
  pipeline never reads. It holds one row — P1.M5, with the "increase the
  **percentage number** of…" text — while the **main sheet's P1.M5 goal is clean**.
  So that is not Geoff's mid-edit typo awaiting his fix (as this file previously
  recorded); it is a *recommended change* parked in a side tab, matching the SPAC
  percentage idea. Ask Geoff whether he intends that tab as a change channel — if
  so, the pipeline should read it.
- **`MeasureContextNote`** is a new column in the export and is **empty in every
  row**, as is `WhyMeasureMatters`. Ask what he wants there.

## Longer-running carry-overs (not blocking)

- **P2.M4a says PSUs but may count LEAs.** The 7/27 retitle aligned the title with
  its approved description; it did **not** change what the sheet counts. Same family
  as the P5.M3 unit question. Note LEA is *genuinely correct* for P1.M17b (federal
  IDEA determination at LEA level), and "district" is correct for P6.M1b (district
  identification applies to LEAs; charters are not in districts). The site will
  legitimately use both words — be deliberate rather than normalizing them.
- **P5.M3 was retitled by Geoff**, not Andy: "Financial and Human Resource Systems"
  → **"School Business Systems Modernization"**. DIM followed. Worth a glance.
- **P1.M17b's "Annual Results" bar chart is ~200px of empty white** — all bars are
  zero-height. Deliberately left as-is; Geoff reacts 8/3.
- **P1.M17b's year suffix** uses the site-standard `(2024–25)` but the source is
  SPP/APR **FFY 2024**, a federal fiscal year. On the 8/3 agenda.
- **WhyMeasureMatters** for pillar measures (no `whyItCounts` on any).
- **P5.M2 chartability** — all-1s NCSIS milestone; excluded by name.
- **P1.M5** stays a **count** through at least 8/5 (see the side-tab note above).
- **P2.M3a `nextUpdate`** — "When Available?" cell is blank (no Next update line).
- **P2.M2b and P2.M3a derive no status pill** — both regressed vs. prior year; the
  rule refuses to print "Approaching target" over a decline. `statusOverride` if
  Geoff wants text there.

## Repo state notes

- Local `master` = `origin/master`; pushes deploy via GitHub Pages
  (production URL: abax70.github.io/NCDPI-strategic-plan-site).
- **Verification is now three tools**, all passing as of this wrapup:
  - `tools/verify-charts.py` — 8 pillars × 3 widths; cards, painted pixels,
    jump-strip contract, console clean.
  - `tools/verify-bin-chips.py` — 14 BiN measure-ID chips, tints, console.
  - `tools/verify-chart-scales.py` — **new 7/27.** Reads live Chart.js scale
    objects and asserts axis invariants (values inside the scale, no negative
    floor on a non-negative measure, final target on a labeled tick, non-degenerate
    axis). Catches the class of bug that `verify-charts.py` structurally cannot:
    painted pixels prove nothing about whether the axis is sane. Run
    `--self-test` (no browser) to confirm the checker itself still fires.
- `data/DIM_Measures.csv` **has ragged rows** — a Sheets export artifact where some
  rows carry 28 trailing empty fields and others 6. Edit it with line-level surgery,
  **not** a `csv` round-trip, or the whole file reformats.
- **`data/build-measures.py` treats DIM `MeasureName` as canonical for BiN
  measures.** Before renaming any DIM row, check its `BestInNationGoal` flag; if it
  is set, the rename changes the Best-in-Nation page too.
- `data/measure-gaps.md` is generated every run and deliberately tracked. It never
  quotes raw sheet prose (public repo) — **the same rule governs anything written
  into `notes/`.** Its date stamp changes every run, so it always shows in
  `git status`; that is expected, not drift.
- **Chart engine parity rule still in force** for the SHARED engine: bug fixes land
  in BOTH `pillar.html` and `best-in-nation.html` until the post-8/5 extraction.
  Deliberate departures, commented in place: the jump strip (pillar only), the
  pillar measure-card header markup, and the BiN measure-ID chip.
- Tracked notes: `punchlist-20260720.md`, `meeting-agenda-20260724.md`,
  `meeting-agenda-20260803.md`, `sheet-edits-20260727.md`,
  `review-packet-20260727.md`, `measure-metric-text.tsv`.
- **Stray file to relocate (not ours):**
  `images/HappyPeoplePhotos/reporting-process-guide.html` belongs in
  **EPP-Codebase** — Andy to move it from the host; unreachable from this container.
