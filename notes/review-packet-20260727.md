# Review packet - 2026-07-27 (session 3)

Everything awaiting Andy's sign-off, in one pass. Mark each item **OK** or note an
edit. None of it blocks the site - it is all rendering already. What it does block:
the **8/3 metric-text table for Geoff** labels these rows as unreviewed drafts until
you approve them (`DRAFTED_SINCE_REVIEW` in `tools/export-metric-text.py` - remove
an ID there once it is signed off).

> **Note on raw sheet text:** this repo is public via GitHub Pages, so tracked files
> never quote Geoff's raw sheet prose (same rule as `data/measure-gaps.md`). Where
> you need to compare a rendered line against what Geoff actually typed, read the
> cell in the sheet or the console output of `python data/build-pillar-measures.py`.

## A. Measure descriptions (5)

`definition` renders as the **Description:** line on the measure card.
`currentDescription` is the phrase under the big number, and is what the
MeasureMetricTxt table derives from (year parenthetical stripped).

### P6.M1a - Low-Performing Schools  _(NEW this wave)_

_Drafted 2026-07-27. Pillar 6 went live in this export._

- **Goal (sheet):** Establish a baseline and decrease the number of identified low performing schools annually.
- **Current value / pill:** 685 / Baseline Year — 685

**definition:**  North Carolina identifies low-performing schools each year under state law: a school is low-performing when it earns a school performance grade of D or F and does not exceed expected academic growth. This measure is the number of public schools on that list; fewer is better.

**currentDescription:**  Number of public schools identified as low-performing (2024–25)

### P6.M1b - Low-Performing School Districts  _(NEW this wave)_

_Drafted 2026-07-27. Pillar 6 went live in this export._

- **Goal (sheet):** Establish a baseline and decrease the number of identified low performing school districts annually.
- **Current value / pill:** 23 / Baseline Year — 23

**definition:**  A school district is identified as low-performing under state law when a majority of its schools that receive a performance grade are themselves identified as low-performing. This measure is the number of North Carolina school districts on that list; fewer is better.

**currentDescription:**  Number of school districts identified as low-performing (2024–25)

### P1.M17b - Exceptional Child Identification Disproportionality  _(drafted 7/27)_

_Drafted 2026-07-27; not part of the 7/23 review round._

- **Goal (sheet):** Establish a baseline and decrease disproportionality in identification of students for Exceptional Children (EC) programs.
- **Current value / pill:** 0.0% / Baseline Year — 0.0%

**definition:**  Federal law requires states to review each local education agency (LEA) every year for disproportionate representation — whether students of a given racial or ethnic group are identified for Exceptional Children (EC) programs at rates out of line with their share of enrollment — and to determine whether that disproportionality is the result of inappropriate identification. This measure is the percentage of LEAs where that determination was made; zero is the goal, and North Carolina is currently at zero.

**currentDescription:**  Percentage of local education agencies with disproportionate representation in Exceptional Children programs resulting from inappropriate identification (2024–25)

### P2.M3a - Beginning Teacher Retention  _(staged 7/24)_

_Drafted in the 7/24 data wave; unreviewed since._

- **Goal (sheet):** Establish a baseline and increase retention of beginning teachers, especially in low-performing and high-poverty schools.
- **Current value / pill:** 85.3% / (no pill)

**definition:**  Beginning teachers are those in their first three years in the classroom. This measure tracks the percentage of North Carolina's beginning teachers who continue teaching in the state's public schools from one year to the next.

**currentDescription:**  Percentage of beginning teachers who remained teaching in NC public schools (2024–25)

### P2.M4b - Teachers Serving in Advanced Teaching Roles  _(staged 7/24)_

_Drafted in the 7/24 data wave; unreviewed since._

- **Goal (sheet):** Establish a baseline and increase the number of teachers serving in advanced roles (Advanced Teaching Roles) that support peer learning.
- **Current value / pill:** 1,494 / Approaching Target — 1,494

**definition:**  Advanced Teaching Roles (ATR) let excellent teachers lead teams of colleagues or take on larger rosters for additional pay, extending their impact without leaving the classroom. This measure is the number of teachers statewide serving in an advanced role.

**currentDescription:**  Number of teachers serving in Advanced Teaching Roles (2024–25)

### Flags on section A

1. **P6.M1a / P6.M1b lean on the statutory definition** of low-performing
   (performance grade of D or F **and** growth not exceeding expected; a district
   is low-performing when a majority of its graded schools are). That framing is
   from general knowledge, **not** from anything in this repo or the sheet -
   please confirm it is stated correctly before it goes to Geoff.
2. **P6.M1b says "school districts," not PSUs.** Deliberate: district
   identification applies to LEAs, and charters are not in districts. Same
   LEA-vs-PSU family as P2.M4a and P5.M3, but here the narrow word looks correct.
3. **P1.M17b's year suffix** reads `(2024-25)` per site standard, but the source is
   SPP/APR **FFY 2024**, a federal fiscal year. Already on the 8/3 agenda.

## B. Hand-authored `sourceHtml` (4)

These four sheet Source cells are scratchpad prose the pipeline refuses to
auto-publish, so the Source line is hand-written. Check each reads as a real,
attributable source:

| Measure | Rendered Source line |
|---|---|
| P2.M3a | NCDPI State of the Teaching Profession report |
| P4.M7 | NCDPI Consolidated Data Report |
| P5.M3 | Reports from public school units to NCDPI |
| P7.M2 | NCDPI Communication and Information Division |

Also worth a look: **P1.M10's** `sourceLabel` is the hand-set
"NCDPI Proficiency dashboard" (the sheet cell is a bare Tableau URL, which would
otherwise render no Source line at all).

## C. DIM_Measures.csv changes

### C1. Structural edits from the 7/24 wave (still unreviewed)

| Change | Detail |
|---|---|
| Rename | `P2.M3c` -> `P2.M3b` (Early-Career Administrator Retention) - Geoff re-lettered |
| Split | `P4.M6` (Youth Risk Behavior Survey) -> `P4.M6a-d`, names drafted by Claude |
| Removed | `P6.M1c` (Low-performing Charter Schools) - gone from the sheet |

The four P4.M6 names are Claude drafts and stay dormant until Shaun confirms:
`Missed School Due to Feeling Unsafe`, `Student Sense of Belonging`,
`Students Reporting Poor Mental Health`, `Students Feeling Sad or Hopeless`.

### C2. Name sync done this session (12 rows)

Sheet wins, DIM follows - this clears all 12 drift warnings. None of these rows
are Best-in-Nation measures, and `data/measures.json` was verified byte-identical
afterward, so the BiN page is untouched.

| Measure | DIM was | DIM now (= sheet) |
|---|---|---|
| P1.M5 | AP At Least 1 Course | AP Course Participation |
| P1.M10 | Proficiency | End-of-Grade and End-of-Course Proficiency |
| P1.M17b | EC Identification Disproportionality | Exceptional Child Identification Disproportionality |
| P2.M2a | EPP Enrollment | Traditional Educator Preparation Program Enrollment |
| P2.M2b | EPP Completion | Traditional Educator Preparation Program Completion |
| P2.M4a | PSUs with Advanced Teaching Roles | PSUs Implementing Advanced Teaching Roles |
| P2.M4b | Teachers in Advanced Teaching Roles | Teachers Serving in Advanced Teaching Roles |
| P4.M7 | School Violence | Schools with Few or No Violent Incidents |
| P5.M3 | Financial and Human Resource Systems | School Business Systems Modernization |
| P6.M1a | Low-performing Schools | Low-Performing Schools |
| P6.M1b | Low-performing Districts | Low-Performing School Districts |
| P7.M2 | Communication Professional Development | Public Information Officer Professional Development |

Note **P5.M3**: the sheet retitled it to "School Business Systems Modernization"
(a Geoff edit, not one of your five). DIM followed. Worth a glance.

## D. Questions that need an answer from you

1. Are the P6.M1a/b statutory definitions stated correctly? (flag A1)
2. P6 measures are **baseline-only** - one 2025 value, then targets to 2030. Same
   shape as P4.M7 / P5.M3 / P7.M2, which render fine, so no action assumed.
3. Anything to change before these five drafts lose their "pending review" label?
