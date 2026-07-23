---
cc_status: hot
cc_strand: strategic-plan
cc_updated: 2026-07-23
---

# HANDOFF — NCDPI Strategic Plan Site

_Last updated: 2026-07-23 (descriptions reviewed + approved; Geoff
questions emailed and pending). See CHANGELOG.md for the full record._

## Where things stand

**Descriptions are reviewed and approved.** Andy walked all 9 drafted
measure descriptions on 7/23 — every one stands as written, no JSON
edits. Two are locked *pending Geoff's answers* (see below); the current
text is the default and only changes if he pushes back.

**Geoff's 7/22 feedback round is shipped** (footnote moved to top of
Results, Description line on measure cards, descriptions for all 9
measures, MeasureName pipeline prep). Nothing contested.

**Anchor holds: measures LOCK at EOD Fri 7/24** for the 8/5 board meeting.
After that: holding pattern — leadership-required changes + actions/stories
only.

## Awaiting Geoff (emailed 7/23, before the Fri lock)

Two answers change site text; three are sheet hygiene for the data wave:

1. **P4.M7 wording** — description says "**five or fewer acts**" (from the
   sheet's "0–5 acts" cell); goal says vague "none to a limited number."
   Keep concrete, or soften? *Default = keep.* If he softens, reword
   `definition` + `currentDescription`.
2. **P5.M3 unit** — source cell "16 PSUs (**15 LEAs**)"; charted value 15.
   PSU or LEA? Description says "public school units" — reword if it's LEAs.
3. **P4.M6** shared by 4 YRBS rows — needs distinct sub-letters (2+ Y aborts
   the build).
4. Row 2's literal **`NEW`** Measure ID (Schools of Character).
5. **P2.M3a and P2.M3c but no P2.M3b** — deliberate, or missing row?

**Geoff's 7/24 promises** (both land with the data wave):
- A **MeasureName column** in the sheet → becomes the display-title
  source. The pipeline already prefers it (tolerant header match, DIM
  fallback, drift warning). Expect possible sheet≠DIM warnings on the
  first run — update DIM to match.
- **Updated Source cells** → the auto-split/warn logic handles them; the
  5 measures with no Source line (P4.M4, P4.M7, P5.M3, P7.M2, P2.M4a)
  should mostly resolve. Hand-author `sourceHtml` for whatever survives
  the warning list.

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

## Longer-running carry-overs (not blocking the lock)

- **WhyMeasureMatters** for pillar measures (no `whyItCounts` on any yet).
- **P5.M2 chartability** — all-1s milestone; excluded by name in the pipeline.
- **P1.M5 goal text** — Geoff's mid-edit "percentage number of…" (his fix; the
  description already says "number" correctly).

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
- **Stray file to relocate (not ours):**
  `images/HappyPeoplePhotos/reporting-process-guide.html` is a 1,044-line EPP
  Performance Reporting guide (dated 2026-05-07) that belongs in **EPP-Codebase**
  — misplaced here in early May, never tracked. Andy to move it from the host;
  it's unreachable from this container. Left untouched at 7/23 cleanup.
