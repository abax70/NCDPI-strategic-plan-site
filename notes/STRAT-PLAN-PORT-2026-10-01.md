---
title: Strat-plan site — corrected 2025–26 values for the 10-01 switch
purpose: >
  The NCDPI strategic plan site must show the CORRECTED 2025–26
  accountability values by 9:00 a.m. Thu 2026-10-01, the morning the public
  accountability dashboards switch to the corrected (09-15 / SPG 09-17)
  files. This is the value table for that update, with provenance and the
  exact figure each public dashboard will print. Andy copies it into the
  site repo's notes/. Supersedes the values table in
  STRAT-PLAN-PORT-2026.md (9/1) for these four measures only.
created: 2026-09-29
computed_from: local corrected builds of 2026-09-28 (nothing deployed; read-only)
companion: _Reference/STRAT-PLAN-PORT-2026.md, _Reference/PLAN-DATA-CORRECTION-OCT1.md
---

# Strat-plan site — corrected values for Thu 2026-10-01

## The table

| Site id | Measure | Live on site now (9/1) | Corrected 2025–26 | Changed? | Source file | What the public dashboard prints on 10/1 |
|---|---|---|---|---|---|---|
| P1.M1 | Cohort graduation rate (4-year, All) | 88.8 | **89.0** | **moved** (+0.2) | `CohortGradRate/_Output/CohortGraduationRateDashboardState.txt`, NC-SEA / STD / ALL, Year 2026 | CGR app: **89.0%** (tenths). Landing: **89.0%**. LTG app: **88.8%** — see note 2 |
| P1.M10 | EOG/EOC proficiency (GLP, all subjects and grades, All) | 59.2 | **59.2** | unchanged | `Proficiency/_Data/FACT_DPITestScores_2026.parquet` (rebuilt 09-28), state All Grades / GLP / ALL | Proficiency app and Landing: **59%** (whole number) — see note 1 |
| P6.M1a | Low-performing schools | 523 | **521** | **moved** (−2) | `Regional/_Output/LandingPageDesignations.txt`, NC-SEA "Low-performing schools", numCY | **No public dashboard prints this statewide count** — see note 3 |
| P6.M1b | Low-performing districts | 10 | **10** | unchanged | same file, NC-SEA "Low-performing districts" | same — not printed statewide |

## Other site values — ruled in or out

| Site id / value | Verdict | Why |
|---|---|---|
| P1.M1 2025 baseline 87.8 | unchanged | Corrected CGR file still says 87.8 for 2025 |
| P1.M10 2025 baseline 55.0 | unchanged | Same in the corrected and pre-correction builds |
| P6.M1a 2025 baseline 685 | unchanged by the correction | From ATR Table 41, which was not re-issued. See note 4 |
| P6.M1b 2025 baseline 23 | unchanged | ATR Table 41 and the Regional file both say 23 |
| P1.M2 ACT composite (2025: 18.3) | not fed by these files | The corrected files hold only 2025–26 rows, and none carries an average ACT composite (SPG has only the ACT indicator score; Regional has expected-tester counts) |
| P1.M6 / P1.M7 dual enrollment | not fed by these files | No such measure in any corrected file |
| P1.M9 CTE credentials | not fed by these files | No such measure in any corrected file |
| P4.M4 chronic absenteeism (2025: 24.3) | not fed by these files | No such measure in any corrected file |

The corrected drop is four files: CGR_Disag, Disag (proficiency),
SPG_Disag (Jaime's 09-17 re-drop) and Regional rc114. Every one carries
`reporting_year` 2026 only, so none can move a 2025 value.

## Notes

1. **Proficiency rounding does not match the site today.** The site shows
   59.2; the public Proficiency app and Landing print **59%**. This was
   already true on 9/1 and the correction does not change it. Keeping 59.2
   on the site is a choice for Andy (the site's own charts use tenths); it
   is not a correction error.
2. **The LTG app still prints 88.8% for graduation.** Its file never took
   the correction. Andy's ruling on how to fix it is pending (he is asking
   Jaime; see root `HANDOFF.md`). The CGR app — the source of record — prints
   89.0, and so does Landing. The site should carry **89.0**. If the LTG app
   still reads 88.8 on Thursday, that is the LTG app lagging, not the site.
3. **Why 521, and why it is not the deck function's answer.**
   `bin_chart.lowperf_counts()` still returns **523**, because it reads
   ATR Table 41 (`atrfilexls_2026/`, dated 2026-08-21), which was never
   re-issued. Curtis's re-issued designations workbook
   (`SchoolDesignations/_Data/2026-09-28_School Identifications 2026.xlsx`)
   removes Low Performing from two schools (340460 and 670379), giving
   **521**. The Regional pipeline's corrected statewide row agrees: 523 before
   the correction, 521 after. Regional ships that statewide row in its data
   but only prints region rows, so no public page shows 521 or 10. Thursday's
   check for these two is therefore against the data file, not a page.
4. **A difference that predates the correction.** The Regional file's
   prior-year column says **682** low-performing schools for 2024–25; the
   site's baseline (from ATR Table 41) is **685**. Both numbers are the
   same before and after the correction, so the correction did not cause
   this. Nothing to change on 10/1.
5. **Trap for anyone re-running the 9/1 functions.**
   `bin_chart.cgr_state_rates()` still returns **88.8**. It goes through the
   `resolve_cgr_state()` bridge, which prefers the stale August state-only
   build in `CohortGradRate/_Output-2026/`. The corrected export is in
   `CohortGradRate/_Output/`. Read that file directly, or retire the bridge
   folder (a set-aside, never a delete) before trusting the function.
   `prof_2026_actual()` is fine: it reads the rebuilt 09-28 parquet.

## Thursday morning check (after the dashboards deploy)

On each live page, statewide view, 2025–26:

- `cgr.accountability-dashboards.net` → headline **89.0%**
- `accountability-dashboards.net` (Landing) → CGR well **89.0%**, proficiency well **59%**
- `proficiency.accountability-dashboards.net` → headline **59%**
- `ltg.accountability-dashboards.net` → graduation reads **88.8%** unless
  Andy's LTG fix shipped (then **89.0%**)
- Low-performing 521 / 10: not on any page; confirm the deployed Regional
  `landing.json` carries `NC-SEA, Low-performing schools, 682, 521` and
  `Low-performing districts, 23, 10`
