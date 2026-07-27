---
cc_status: hot
cc_strand: strategic-plan
cc_updated: 2026-07-27
---

# HANDOFF — NCDPI Strategic Plan Site

_Last updated: 2026-07-27 (second session of the day). Both decisions that were
pending at the 7/24 wrapup are now made. See CHANGELOG.md for the full record._

## Where things stand

**Both open decisions are closed.** P1.M17b is **in** (its zeros are real data,
not missing data), and the title question was answered "clearer, not shorter."

**The flat-at-zero chart bug is fixed and verified.** P1.M17b rendered on a
`-0.10% .. 0.025%` axis; it now renders `0% .. 10%` with the flat line on the
floor. Root cause was `isDecreaseMeasure()` returning false for a hold-at-zero
measure (`0.0 < 0.0`), not just the zero-gap fallback. Fix landed in
`pillar.html`, `best-in-nation.html` (parity, unreachable today), and
`derive_y_axis_max()` in `data/build-pillar-measures.py`.

**Geoff is out until 8/3.** Check-in **8/3**, board meeting **8/5**.

## FIRST: Andy's sheet edits (nothing downstream can start without these)

Everything in the next-session queue depends on one fresh export, and the export
should be taken **after** Andy edits the sheet.

- **The edit list is `notes/sheet-edits-20260727.md`** — 5 MeasureName cells,
  3 deliberate no-ops, plus the `Febuary 2027` → `February 2027` typo in
  P1.M17b's "When Available?" cell (confirmed live on the rendered card).
- Then download one export → `data/source/StrategicPlan_measures.xlsx`
  (gitignored). That single download carries **both** Geoff's 7/25 updates and
  Andy's title edits.

## Also awaiting Andy's review

- **P1.M17b's `definition` + `currentDescription`** — drafted 2026-07-27, the
  measure previously had none. Not part of the 7/23 review round. Rendered on
  the card; read it there or in `data/pillar-measures.json`.
  - Open sub-question: the draft uses the site-standard `(2024–25)` school-year
    suffix, but the source is SPP/APR **FFY 2024**, a federal fiscal year.
- **Staged since the 7/24 wave, still unreviewed**: P2.M3a + P2.M4b
  `definition`/`currentDescription`; hand-authored `sourceHtml` for P2.M3a,
  P4.M7, P5.M3, P7.M2; the DIM diff (P2.M3c→P2.M3b rename, P4.M6 split into
  a–d, P6.M1c removed).

## Next session queue

1. **Andy's sheet edits + one fresh export** (see above), then re-run
   `python data/build-pillar-measures.py`.
2. **Sync `data/DIM_Measures.csv` names** to the final titles → the 10 drift
   warnings clear. (Sheet wins; DIM follows.)
3. **Manual BiN import** — Geoff was adding "disaggregated results available at
   the source link" notes to some BiN Source cells (Superintendent request).
   BiN rows are hand-curated and skipped by the pipeline, so these go into
   `data/measures.json` by hand from the final export.
4. **Refresh Smartsheet action statuses** — Geoff updated the tracker 7/25
   before leaving. Live-API path or connector; routine is in CHANGELOG
   2026-07-15 (second session). Fully independent of the export — good filler
   if the sheet work stalls.
5. `python tools/verify-charts.py` + `python tools/verify-bin-chips.py`, eyeball
   P1/P2, commit, push, verify the Pages deploy.
6. Watch for **Shaun** (the four YRBS P4.M6 measures) and **Curtis**
   (low-performing schools) confirmation emails → Andy flips those asterisks to
   Y in the sheet → that wave brings P4.M6a–d live. Expect parser warnings:
   P4.M6a's 2030 target cell is a literal `-%` and the YRBS series are biennial
   ("-" in off years).

## For the 8/3 Geoff check-in

**`notes/meeting-agenda-20260803.md`** is written and ready. Headline items:
the improvised defaults to confirm (P4.M7 "five or fewer acts", P5.M3 "public
school units", the P2.M3b re-lettering), the P1.M17b caveats, the P2.M4a unit
question, and a proposal to add a **MeasureMetricTxt column** to the sheet
(paste-ready table at `notes/measure-metric-text.tsv`, 26 measures, no gaps).

## Longer-running carry-overs (not blocking)

- **P2.M4a says PSUs but may count LEAs.** The 7/27 retitle aligned the title
  with its approved description; it did **not** change what the sheet counts.
  Same family as the P5.M3 unit question. Note LEA is *genuinely correct* for
  P1.M17b (federal IDEA determination at LEA level) — the site will legitimately
  use both words, so be deliberate rather than normalizing them.
- **P1.M17b's "Annual Results" bar chart is ~200px of empty white** — all bars
  are zero-height. Deliberately left as-is on 7/27 (collapsing it for one
  measure breaks card-to-card layout consistency); Geoff reacts 8/3.
- **WhyMeasureMatters** for pillar measures (no `whyItCounts` on any; the sheet
  column exists but is empty everywhere).
- **P5.M2 chartability** — all-1s NCSIS milestone; excluded by name.
- **P1.M5** stays a **count** through at least 8/5 (SPAC percentage idea parked
  with Sneha/Sam Beth). Its goal text has Geoff's mid-edit "percentage number
  of…" typo — his fix; the description is already correct.
- **P2.M3a `nextUpdate`** — "When Available?" cell is blank (no Next update line
  on the card).
- **P2.M2b and P2.M3a derive no status pill** — both regressed vs. prior year;
  the rule refuses to print "Approaching target" over a decline. `statusOverride`
  if Geoff wants text there.
- **P1.M10's source is a bare URL** — needs a human-readable label.

## Repo state notes

- Local `master` = `origin/master`; pushes deploy via GitHub Pages
  (production URL: abax70.github.io/NCDPI-strategic-plan-site).
- `data/measure-gaps.md` is generated every run and deliberately tracked. It
  never quotes raw sheet prose (public repo). Its date stamp changes on every
  run, so it always shows in `git status` — that is expected, not drift.
- **Chart engine parity rule still in force** for the SHARED engine: bug fixes
  land in BOTH `pillar.html` and `best-in-nation.html` until the post-8/5
  extraction. The 7/27 flat-series guard is the newest example (unreachable on
  the BiN side today, carried anyway). Deliberate departures, commented in
  place: the jump strip (pillar only), the pillar measure-card header markup,
  and the BiN measure-ID chip.
- Tracked notes: `punchlist-20260720.md`, `meeting-agenda-20260724.md`,
  `meeting-agenda-20260803.md`, `sheet-edits-20260727.md`,
  `measure-metric-text.tsv`.
- **`export-metric-text.py` has a `DRAFTED_SINCE_REVIEW` map** near the pillar
  loop. Add a measure ID there whenever you draft a new description, remove it
  once Andy signs off — otherwise the Origin column will label fresh drafts as
  Andy-approved in a table that goes to Geoff.
- **Stray file to relocate (not ours):**
  `images/HappyPeoplePhotos/reporting-process-guide.html` belongs in
  **EPP-Codebase** — Andy to move it from the host; unreachable from this
  container.
