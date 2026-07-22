---
cc_status: hot
cc_strand: strategic-plan
cc_updated: 2026-07-22
---

# HANDOFF — NCDPI Strategic Plan Site

_Last updated: 2026-07-22 (Geoff's punch list shipped; description drafts
awaiting Andy's review). See CHANGELOG.md for the full record._

## Where things stand

**Geoff's 7/22 feedback round is shipped** (all four items — footnote
moved to top of Results, Description line renders on measure cards,
descriptions drafted for all 9 measures, MeasureName pipeline prep).
Nothing contested; no further leadership feedback expected before the
data wave.

**New anchor: measures LOCK at EOD Fri 7/24** for the 8/5 board meeting
(Andy + Geoff agreed 7/22). After that: holding pattern —
leadership-required changes + actions/stories only.

**Geoff's 7/24 promises** (both land with the data wave):
- A **MeasureName column** in the sheet → becomes the display-title
  source. The pipeline already prefers it (tolerant header match, DIM
  fallback, drift warning). Expect possible sheet≠DIM warnings on the
  first run — update DIM to match.
- **Updated Source cells** → the auto-split/warn logic handles them; the
  5 measures with no Source line (P4.M4, P4.M7, P5.M3, P7.M2, P2.M4a)
  should mostly resolve. Hand-author `sourceHtml` for whatever survives
  the warning list.

## FIRST: Andy reviews the drafted descriptions (pre-lock)

All 9 measures now have Claude-drafted `definition` (the "Description:"
line) and `currentDescription` (the phrase beside the big number) in
`data/pillar-measures.json` — **committed but not yet reviewed**. They
render live, so review before the 7/24 lock. Four specific flags:

1. **Year suffixes.** BiN's "(2024–25)" school-year style used
   throughout; P5.M3 says "(as of 2025)" (cumulative adoption count).
   Confirm the period is right for P1.M5 (fall enrollment snapshot?),
   P2.M2a/b (EPP reporting year), and P7.M2.
2. **P5.M3 unit question — needs Geoff.** His raw source cell says
   "16 PSUs (15 LEAs) have migrated"; the charted value is 15. If 15
   counts LEAs, the drafted phrase "public school units" is wrong.
3. **P4.M7 threshold.** Draft says "five or fewer acts" (grounded in the
   sheet's "0-5 acts" source cell) instead of the goal's vague "limited
   number". Flag if Geoff prefers vague.
4. **P1.M5 count vs percentage.** The draft describes a *count* (what
   the data is); the goal text still reads "percentage number of…"
   (Geoff's known mid-edit text — his fix, already on his list).

Edit any draft directly in the JSON (both fields are preserved — safe
against re-runs) or tell Claude the changes.

## Next session: the 7/24 data wave

1. Andy downloads the fresh export to `data/source/StrategicPlan_measures.xlsx`.
2. `python data/build-pillar-measures.py` → work the warning list + both
   sections of `data/measure-gaps.md` (missing fields, DIM reconciliation,
   and any new MeasureName-drift warnings).
3. **New measures need `definition` + `currentDescription` drafts** —
   same voice as the existing 9; Claude drafts, Andy reviews.
4. `python tools/verify-charts.py`. If a pillar hit 4+ measures, the jump
   strip goes live — eyeball it once.
5. Commit, push, verify the Pages deploy.
   Watch for: a brand-new `valueFormat`, another pillar going 0 → some
   measures, and the P4.M6 situation below.

## Awaiting Andy / Geoff

- **Sheet anomalies — status after the 7/22 meeting unknown** (Andy
  didn't report whether these came up; re-confirm before the wave):
  - **P4.M6 shared by 4 YRBS rows** — needs distinct sub-letters before
    any goes Y (2+ Y aborts the build).
  - Row 2's literal `NEW` Measure ID (Schools of Character).
  - P2.M3a and P2.M3c exist but no P2.M3b — deliberate?
  - Carried over: WhyMeasureMatters for pillar measures, P5.M2
    chartability (all-1s milestone), P1.M5's mid-edit goal text.

## Repo state notes

- Local `master` = `origin/master`; pushes deploy via GitHub Pages
  (production URL: abax70.github.io/NCDPI-strategic-plan-site).
- `data/measure-gaps.md` is generated every run and deliberately tracked.
  It never quotes raw sheet prose (public repo) — IDs and row numbers only
  in the reconciliation section.
- Chart engine parity rule still in force for the SHARED engine: bug fixes
  land in BOTH pillar.html and best-in-nation.html until the post-8/5
  extraction. Deliberate departures, commented in place: the jump strip
  (pillar only) and the measure-card header (the new Description line is
  pillar-card markup, not shared engine).
- `notes/punchlist-20260720.md` is tracked.
