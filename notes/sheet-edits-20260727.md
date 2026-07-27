# Sheet edits — MeasureName + typos (2026-07-27)

Andy's title decisions from the 7/27 session. These are edits **Andy makes by
hand in Geoff's live Google Sheet**; the sheet is the source of truth for
`MeasureName` and the pipeline reads a download of it
(`data/source/StrategicPlan_measures.xlsx`, gitignored).

**Do these first, then download one fresh export** — the same download picks up
Geoff's 7/25 updates *and* these edits, so only one export is needed.

## MeasureName column — 5 cells to change

| Measure | Change to |
|---|---|
| P1.M17b | `Exceptional Child Identification Disproportionality` |
| P2.M2b  | `Traditional Educator Preparation Program Completion` |
| P4.M7   | `Schools with Few or No Violent Incidents` |
| P7.M2   | `Public Information Officer Professional Development` |
| P2.M4a  | `PSUs Implementing Advanced Teaching Roles` |

## No edit needed (proposed text already matches the sheet)

- **P2.M2a** — already `Traditional Educator Preparation Program Enrollment`
- **P1.M10** — already `End-of-Grade and End-of-Course Proficiency`
- **P2.M4b** — keeping `Teachers Serving in Advanced Teaching Roles`
  (parallels P2.M4a's "PSUs Implementing…"; deliberately not shortened)

## Other sheet typo to fix while you're in there

- **P1.M17b**, "When Available?" cell: `Febuary 2027` → `February 2027`

## Rationale notes (for the record)

- The direction here is **spell out, not shorten**: EC → Exceptional Child,
  PIOs → Public Information Officer. Andy's call, 7/27, overriding the
  shorten-everything proposal drafted at the 7/24 wrapup.
- **P2.M2b** was the only pure typo fix in the name column: the sheet read
  "Traditional **Education** Preparation…" where P2.M2a reads "**Educator**".
- **P4.M7** is the one genuine shortening (57 → 40 chars). Safe because the
  approved `currentDescription` still carries the concrete "five or fewer acts"
  threshold — the title loses the number, the description keeps it.
- **P2.M4a LEAs → PSUs** aligns the title with its already-approved description,
  which says PSUs. **This does not change what the sheet counts.** If the
  underlying figure is a count of LEAs, the new title misstates it — flagged for
  Geoff on 8/3 alongside the same open unit question on P5.M3.

## After the edits

1. Download the fresh export → `data/source/StrategicPlan_measures.xlsx`
2. Re-run `python data/build-pillar-measures.py`
3. Sync `data/DIM_Measures.csv` names to match → the 10 drift warnings clear
