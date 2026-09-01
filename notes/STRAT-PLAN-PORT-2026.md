---
title: Port brief — populate the strat-plan site's BiN charts with 2025-26 actuals
purpose: >
  Leadership asked (2026-09-01) to populate the strategic plan dashboard's
  Best-in-Nation charts for the three topics the SBE deck already carries:
  cohort graduation rate, EOG/EOC proficiency, and low-performing
  schools/districts. This file is the hand-carry package: the verified
  2025-26 values with provenance, the timing gates, and a paste-ready prompt
  for a Claude session in the NCDPI-strategic-plan-site repo. Copy this file
  there (no earlier than 2026-09-02) and paste the prompt.
created: 2026-09-01
companion: _Reference/STRAT-PLAN-BIN-EMBARGO.md (the two-repo working agreement)
---

# Strat-plan site port — 2025-26 actuals for the BiN charts

## Timing gates — read before touching the other repo

1. **Embargo (hard):** no 2026 / 2025-26 value enters the
   NCDPI-strategic-plan-site working tree before **Wednesday 2026-09-02**.
   That includes this file. The site auto-deploys from `master` (legacy
   GitHub Pages, no staging), so anything merged there is public.
2. **Correction window (caution, not a block):** accountability numbers can
   still be revised until the **2026-10-07** SBE meeting. Leadership has
   asked for the charts now, so proceed — but record provenance in the
   commit message so a later correction is a one-line follow-up, and expect
   a re-verify pass after 10/7.
3. **RESOLVED (2026-09-01, ~5:30 pm):** Geoff's earlier call to hold these
   measures until the 2026-10-07 SBE meeting was revised by Geoff himself,
   by email. "Populate now" stands. The correction-window caution in gate 2
   still applies — expect a re-verify pass after 10/7.

## The verified values

All four verified **live on 2026-09-01** by running the deck pipeline's own
data functions in the Accountability-Team container
(`PowerPointPresentation/_Scripts/bin_chart.py`: `cgr_state_rates()`,
`prof_2026_actual()`, `lowperf_counts()`):

| Measure | Site id | 2026 actual | 2026 target | Source of truth |
|---|---|---|---|---|
| P1.M1 Cohort Graduation Rate | `cohort-graduation-rate` | **88.8** | 88.0 | CGR pipeline State export, ALL subgroup, 4-year (STD) rate |
| P1.M10 EOG/EOC Proficiency | `end-of-grade-and-end-of-course-proficiency` | **59.2** | 56.0 | `Proficiency/_Data/FACT_DPITestScores_2026.parquet`, state "All Grades" GLP, ALL subgroup |
| P6.M1a Low-Performing Schools | `low-performing-schools` | **523** | 650 | ATR drop, `ATR_Table_41_Slide_63.xlsx` via `create_ppt_data.build_lowperf` |
| P6.M1b Low-Performing School Districts | `low-performing-school-districts` | **10** | 21 | same Table 41 |

All four **meet** their 2026 target, so all four actual bars should render
teal ("Meets Target").

**One baseline correction rides along:** the site's P1.M1 2025 baseline is
**87.7 and is wrong — the true value is 87.8** (leadership feedback
2026-08-13, item 1; confirmed from the CGR pipeline). Fix it in the same
pass.

**A stale number to ignore:** some older Accountability-Team records
(HANDOFF, CHANGELOG) say **522** low-performing schools. The current ATR
Table 41 says **523** — re-verified by running `build_lowperf` on
2026-09-01. 523 is correct.

## Files to copy to the strat-plan repo

Copy **from** `C:\Users\AndyBaxter\Projects\Accountability-Team\` **to**
`C:\Users\AndyBaxter\Projects\NCDPI-strategic-plan-site\` (a scratch or docs
location there — the session can decide where it belongs):

1. `_Reference/STRAT-PLAN-PORT-2026.md` — this file (values + prompt).
2. `_Reference/STRAT-PLAN-BIN-EMBARGO.md` — the two-repo working agreement;
   its own frontmatter asks for a copy to live there. Mostly spent after
   9/2, but its September cutover checklist is still open.

**Nothing else needs to move.** The chart engine already lives in that repo
(the deck's copy was vendored *from* it, commit `2331810`), and valence
(teal/rust vs target) already shipped upstream before we vendored. The
deck's deliberate visual deviations are logged in
`PowerPointPresentation/_Scripts/_vendor/bin-chart/README.md` — reference
only; do NOT port them back.

## Paste-ready prompt for the strat-plan session

```
Populate the strategic plan site's Best-in-Nation charts with the 2025-26
actuals. Leadership asked for this on 2026-09-01. The values, provenance,
and constraints are in STRAT-PLAN-PORT-2026.md (copied into this repo from
the Accountability-Team repo) — read it first and treat its values table as
the source of truth.

The change:
1. Find where the live site stores measure data. In the vendored snapshot
   (Accountability-Team, commit 2331810 of this repo) it is
   measures_config.json: each measure has a dataSeries of
   {year, baseline, target, actual}. Confirm the live equivalent here.
2. Set the 2026 "actual" for four measures:
   - P1.M1  cohort-graduation-rate: 88.8
   - P1.M10 end-of-grade-and-end-of-course-proficiency: 59.2
   - P6.M1a low-performing-schools: 523
   - P6.M1b low-performing-school-districts: 10
3. Fix the P1.M1 2025 baseline: 87.7 -> 87.8 (documented correction,
   confirmed from the CGR pipeline).

Verification, before anything merges:
- All four 2026 actuals meet their targets, so all four actual bars must
  render teal / "Meets Target". If any renders rust, stop and investigate.
- P6.M1a and P6.M1b are DECREASING-goal measures (fewer is better) and this
  is their first actual-vs-target render. The engine derives direction from
  the data (final target below first observed value) and the pillar page
  uses the pillar_decrease.js variant (axis anchoring flip, valence flip).
  Verify both P6 charts on the pillar page render with the flipped axis and
  teal valence.
- The engine exists as TWO copies kept in parity by in-code "parity rule"
  comments: inline in best-in-nation.html (~lines 1255-1925 at commit
  2331810) and a duplicate in pillar.html. A data-only change should feed
  both, but verify every page that renders these four measures. If any code
  change is needed, change both copies per the parity rule.
- Render/serve the pages locally and confirm the charts actually draw —
  not just that the pages load.

Repo and deploy facts (verify, don't assume they still hold):
- Default branch is `master`, and a push to master auto-deploys via legacy
  GitHub Pages with no staging. Do the work on a branch; merging to master
  IS publishing. Confirm today's date is 2026-09-02 or later before merge.
- A pre-commit hook refusing 2026 / 2025-26 patterns may exist (planned as
  an embargo tripwire in Aug 2026 — check whether it was built). If it
  exists, the embargo has lifted: REMOVE the hook in this same pass rather
  than bypassing it, per the September cutover checklist in
  STRAT-PLAN-BIN-EMBARGO.md.
- Commit message should record provenance: values verified 2026-09-01 from
  the Accountability-Team pipeline (CGR State export / FACT_DPITestScores
  parquet / ATR Table 41), and note that numbers remain subject to the
  accountability correction window until the 2026-10-07 SBE meeting.

Out of scope: do not port the deck's visual deviations (they are logged in
the Accountability-Team repo's _vendor/bin-chart/README.md and are
deck-only), and do not touch any other measure's data.
```

## After the port (back in Accountability-Team)

- Log the port in the root `CHANGELOG.md`.
- The September cutover checklist in `STRAT-PLAN-BIN-EMBARGO.md` can then be
  closed out (valence port-back was already moot; the remaining items are
  the hook removal and the identical-render check, both covered above).
