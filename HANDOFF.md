---
cc_status: hot
cc_strand: strategic-plan
cc_updated: 2026-07-27
---

# HANDOFF — NCDPI Strategic Plan Site

_Last updated: 2026-07-27, wrapping the 7/24 session (Geoff meeting + data
wave staged; two Andy decisions pending). See CHANGELOG.md for the full
record._

## Where things stand

**BiN measure-ID chips shipped and live** (Geoff's 7/24 email ask) —
every Best in Nation measure shows its measure ID above the title, same
treatment as the pillar cards. Pushed, Pages deploy verified.

**The 7/24 data wave is staged but NOT Andy-reviewed.** The fresh export
ran clean: **12 measures chart (was 9)** — new are P1.M17b (EC
disproportionality), P2.M3a (Beginning Teacher Retention), P2.M4b
(Teachers in ATR). Pillar 2 hit 5 measures → **the jump strip is live
for the first time** (verified). All 9 existing measures kept their data
and approved descriptions. Committed at wrapup so nothing is lost; the
drafts inside await review (below).

**Lock status (from the 7/24 Geoff meeting):** the lock was driven by
Geoff's vacation — he is **out the week of 7/27**, back for a check-in
**8/3**. Finalized (Y) set is locked-ish; asterisked measures resolve
next week; anything we improvised gets confirmed 8/3.

## FIRST: Andy's two pending decisions (from 7/24, unmade)

1. **P1.M17b in or out?** The sheet has baseline 0.0% and every target
   0.0 — renders as "Path to 0% by 2030" with an empty chart and a
   negative y-axis; next real data **Feb 2027**. Claude recommends
   **excluding it** until it has data (pipeline guard like the P5.M2
   rule; confirm with Geoff 8/3). It is Y-flagged, so exclusion
   overrides Geoff — Andy's call. Its "When Available" cell also says
   "**Febuary** 2027" (sheet typo — Andy fix in sheet).
2. **Title shortening.** Geoff invited shorter titles; they belong in
   the sheet's MeasureName column (sheet wins; DIM synced after).
   Claude's proposed shorter titles, longest first:
   - P1.M17b (67 chars) → "EC Identification Disproportionality"
   - P4.M7 (57) → "Schools with Few or No Violent Incidents"
   - P2.M2b (52) → "Educator Preparation Completion"
   - P2.M2a (51) → "Educator Preparation Enrollment"
   - P7.M2 (47) → "PIO Professional Development"
   - P2.M4b (43) → "Teachers in Advanced Teaching Roles"
   - P1.M10 (42) → "EOG and EOC Proficiency"
   - P2.M4a (41) → "PSUs with Advanced Teaching Roles"
   Sheet inconsistencies spotted: P2.M2a says "Educator" but P2.M2b says
   "Education"; P2.M4a's title says **LEAs** while its approved
   description says **PSUs** (same unit family as the P5.M3 question).
   Flow: Andy edits sheet MeasureName cells → re-run pipeline → update
   DIM names to match final → the 10 drift warnings clear.

## Also awaiting Andy's review (staged in the wave commit)

- **New-measure drafts** in `data/pillar-measures.json` (preserved
  fields, survive re-runs — verified): P2.M3a `definition` +
  `currentDescription` + sourceHtml "NCDPI State of the Teaching
  Profession report"; P2.M4b `definition` (mirrors approved P2.M4a ATR
  language) + `currentDescription`.
- **Hand-authored sources** for the prose-only cells: P4.M7 "NCDPI
  Consolidated Data Report", P5.M3 "Reports from public school units to
  NCDPI", P7.M2 "NCDPI Communication and Information Division".
- **DIM edits** (review via diff): P2.M3c→P2.M3b rename (Geoff
  re-lettered), P4.M6 split into a–d with drafted names ("Missed School
  Due to Feeling Unsafe", "Student Sense of Belonging", "Students
  Reporting Poor Mental Health", "Students Feeling Sad or Hopeless"),
  **P6.M1c row removed** (charter-schools measure gone from the sheet).
  DIM ↔ sheet now reconciles clean in both directions.
- P2.M2b and P2.M3a derive **no status pill** (regressed vs prior year —
  the regression rule working as intended; statusOverride if needed).

## 7/24 Geoff meeting outcomes (transcript was partial; Andy debriefed)

- **Schools of Character is OUT** — Mo wants an action plan first. The
  literal-`NEW`-ID row stops mattering.
- **Asterisked = awaiting confirmation**: Shaun (the four YRBS P4.M6
  measures) and Curtis (low-performing schools). Andy is CC'd on
  Geoff's emails; if they confirm, **Andy flips them to Y in the sheet**.
  Note: P4.M6a's 2030 target cell is a literal "-%" (sheet typo) and the
  YRBS series are biennial ("-" in off years) — expect parser warnings
  to work when they flip.
- **P1.M5 stays a count** at least until 8/5 (SPAC percentage idea
  parked with Sneha/Sam Beth). Approved description already says
  "number of" — no rework.
- **BiN measures**: Geoff is adding a note to some Source cells that
  disaggregated results are available at the source link (Superintendent
  request). BiN data is hand-curated (pipeline skips BiN rows) — import
  his source/next-update changes into the BiN entries **manually** from
  the final export.
- **Improvised defaults, confirm 8/3**: P4.M7 keeps "five or fewer
  acts"; P5.M3 keeps "public school units"; P2.M3b gap was resolved by
  Geoff's re-lettering (P2.M3c → P2.M3b).

## Next session queue

1. **Refresh Smartsheet action statuses** — Geoff updated the tracker
   before leaving (7/25). Live-API path or connector; see CHANGELOG
   2026-07-15 (second session) for the routine.
2. Andy makes the two decisions above; Claude applies (exclusion guard
   and/or title edits → re-run → DIM sync).
3. Andy reviews the staged drafts (descriptions, sources, DIM diff).
4. **Download the final export** (Geoff said he'd update the sheet
   before leaving — it should carry the BiN disaggregation notes) →
   re-run pipeline → import BiN source/next-update changes into the BiN
   measures.json by hand.
5. `python tools/verify-charts.py` + eyeball P1/P2, commit, push,
   verify Pages deploy.
6. Watch for Shaun/Curtis confirmation emails → flip asterisks to Y in
   the sheet → that wave brings P4.M6a–d (+ Curtis's measure) live.

## Longer-running carry-overs (not blocking)

- **WhyMeasureMatters** for pillar measures (no `whyItCounts` on any;
  the sheet column exists but is empty everywhere).
- **P5.M2 chartability** — all-1s milestone; excluded by name.
- **P1.M5 goal text** — Geoff's mid-edit "percentage number of…" (his
  fix; description already correct).
- **P2.M3a nextUpdate** — "When Available?" cell is blank (no Next
  update line on the card).

## Repo state notes

- Local `master` = `origin/master`; pushes deploy via GitHub Pages
  (production URL: abax70.github.io/NCDPI-strategic-plan-site).
- `data/measure-gaps.md` is generated every run and deliberately tracked.
  It never quotes raw sheet prose (public repo).
- Chart engine parity rule still in force for the SHARED engine: bug
  fixes land in BOTH pillar.html and best-in-nation.html until the
  post-8/5 extraction. Deliberate departures, commented in place: the
  jump strip (pillar only), the pillar measure-card header markup, and
  the BiN measure-ID chip (BiN-only markup mirroring the pillar chip).
- `notes/punchlist-20260720.md` and `notes/meeting-agenda-20260724.md`
  are tracked.
- **Stray file to relocate (not ours):**
  `images/HappyPeoplePhotos/reporting-process-guide.html` belongs in
  **EPP-Codebase** — Andy to move it from the host; unreachable from
  this container.
