---
cc_status: warm
cc_strand: strategic-plan
cc_updated: 2026-09-01
---

# HANDOFF — NCDPI Strategic Plan Site

_Last updated: 2026-09-01. Session records: CHANGELOG.md._

## Where things stand

9/1 session done and **deployed**: Smartsheet pull (zero status churn since 8/3),
two summer blog posts matched and live (164 → 168 matches), stamp 2026-09-01,
all four verify tools pass. The 8/14 CGR baseline fix (87.7 → 87.8, `cd736fe`)
is merged. Remote = local = deployed.

## HARD GATE — no measure updates until the October SBE meeting

The 2025-26 accountability data released publicly **Wed 9/2**, but **Geoff's
explicit call (via Andy, 9/1): do NOT update the site's accountability-fed
measures (CGR, proficiency, etc.) until the October SBE meeting — Wed
2026-10-07 — after the data correction window closes.** "The data is public
now" is irrelevant to this gate. Stories and action statuses are unaffected.
Memory: `project-strat-plan-measures-wait-october-sbe`.

## Next session queue

1. **Friday 9/4: Andy meets Geoff.** Standing agenda:
   - The 28 past-due launch labels — 22 "Planned for August, 2026" + 6 new
     September ones (P5.F3.A4, P6.F2.A1, P6.F2.A2, P6.F3.A3, P8.F1.A2,
     P8.F1.A3). Is that the wording he wants?
   - P7.F3.A3 / P8.F2.A1: still Not Started as of the 9/1 pull — deliberate
     regression or mis-click? (P7.F3.A3 has moved twice.)
   - `notes/geoff-open-questions.md` — 15 items.
   - FYI: Mo's 8/28 blog letter says CGR 87.7%; site corrected to 87.8 on 8/14.
     Blog-side fix, not ours.
   - Parked from 8/4: the TSV's `"from approved description (Andy 7/23)"`
     provenance on five rows actually approved 8/3 — date them separately?
2. **Sort out the P4.M6a–d names** before Shaun's wave lands — see TRAP below.
3. **Two BiN source links need a human** (both in `data/measures.json`, never
   reviewed): P8.M2's Statistical Profile link 403s to scripted clients
   (`apps.schools.nc.gov/public/f?p=145:11::::::`) — **Andy must click it**;
   P1.M8's Perkins link redirects `cte.ed.gov` → `octae.ed.gov` — update when
   convenient.
4. **Watch for Shaun** (YRBS P4.M6a–d) and **Curtis** (low-performing schools)
   → asterisks flip to Y → that wave goes live. Expect parser warnings (P4.M6a
   2030 target is literal `-%`; YRBS is biennial). **Do not let it land before
   the name trap is resolved.**
5. **October SBE (10/7): the measure-update wave** — CGR, proficiency, etc.,
   from the corrected accountability data. First measure-data touch since the
   gate; re-read the gate section above when it lands.
6. Chart-engine extraction (post-8/5 item, still pending; parity rule below
   applies until then).

## TRAP: the P4.M6a–d names will be overwritten by descriptions

The sheet carries authored `MeasureName` values for P4.M6a–d that are metric
descriptions, not names (86/75/84/58 chars vs. short DIM names like "Missed
School Due to Feeling Unsafe" / "Student Sense of Belonging" / "Students
Reporting Poor Mental Health" / "Students Feeling Sad or Hopeless").

**Nothing in the pipeline will warn you**: the MeasureName drift check fires
only on `Y`-flagged rows (these are `*`), and reconciliation compares IDs, not
names. Under *sheet wins, DIM follows*, the moment they flip to `Y` the long
text becomes the card titles.

**The lever, currently unused:** `menuLabel` falls back to `name` only when
DIM's `MeasureLbl` is empty (`data/build-pillar-measures.py:596`), and
`MeasureLbl` is blank on every pillar measure today. A short `MeasureLbl`
alongside the long official `MeasureName` satisfies both.

## Longer-running carry-overs (not blocking)

- **P2.M4a says PSUs but may count LEAs** (family: P5.M3 unit question). LEA is
  *genuinely correct* for P1.M17b (federal IDEA determination); "district" is
  correct for P6.M1b. Be deliberate, don't normalize. The sheet's P5.M3 Source
  cell says "Reports from LEAs"; the site deliberately keeps "public school
  units" (Andy's call) — question stays open.
- **P2.M2a/b `sourceLabel` is mangled** (unbalanced paren, truncated) —
  invisible because `sourceHtml` wins in rendering; waiting for whoever next
  touches the field.
- **P1.M17b "Annual Results" chart is near-empty white** (all bars zero-height)
  — deliberately left for Geoff's reaction; he has not seen it.
- **P1.M17b year suffix** is site-standard `(2024–25)` but the source is
  SPP/APR FFY 2024.
- **WhyMeasureMatters/whyItCounts** empty on all pillar measures.
- **P5.M2** excluded by name (all-1s NCSIS milestone).
- **P1.M5** stays a count; the percentage idea lives in the export's side tab,
  which the pipeline never reads.
- **P2.M3a `nextUpdate`** blank ("When Available?" cell empty).
- **P2.M2b and P2.M3a derive no status pill** (regressed vs. prior year; rule
  refuses "Approaching target" over a decline). `statusOverride` if Geoff wants
  text.

## Repo state notes (durable)

- `master` pushes deploy via GitHub Pages
  (abax70.github.io/NCDPI-strategic-plan-site). **Andy's VS Code shares this
  working tree and can Sync mid-session** — it did on 9/1, pushing the
  checkpoint trail before wrapup. Check `git ls-remote` before assuming
  unpushed.
- **Verification is FOUR tools**, all passing 2026-09-01: `verify-charts.py`
  (8 pillars × 3 widths), `verify-bin-chips.py` (14 chips),
  `verify-chart-scales.py` (axis invariants; `--self-test`),
  `verify-value-labels.py` (label overlap, 108 charts × 4 widths;
  `--self-test`). Each exists because a real bug slipped past the previous
  ones; new bug class → add a fifth, don't widen one.
- `tools/check-source-lines.py` — NOT a fifth verify tool (written to confirm a
  change, hasn't earned pre-push status). Checks the 10 hand-authored
  `sourceHtml` lines; downgrades TLS/401/403 to WARN on purpose.
  `best-in-nation.html` is a carousel — only one measure in the DOM at a time;
  the tool drives `.carousel-select` by index.
- **`tools/update-stamp.py` owns "Last updated"** — run after any data wave;
  `--check` exits 1 if content moved without a bump; baseline in tracked
  `data/stamp-state.json`.
- **Smartsheet live pull works from the container** (`data/.smartsheet-token`;
  `build-pillar-data.py` refreshes `action-statuses.csv`). The 4th column is
  the pull date, so every row diffs; compare column 2 for real churn.
- `data/DIM_Measures.csv` has ragged rows — line-level surgery only, no `csv`
  round-trip.
- `build-measures.py` treats DIM `MeasureName` as canonical for BiN — check
  `BestInNationGoal` before renaming any DIM row.
- **`sourceHtml` is a PRESERVE field** in both build scripts; both renderers
  prefer it. Sheet Source-cell edits do NOT reach the site (build preserves,
  and the parser refuses multi-part/prose cells). **10 hand-authored source
  lines**: 7 in `pillar-measures.json` + 3 in `measures.json` (P1.M1, P1.M8,
  P8.M2). P1.M8/P8.M2 are BiN-only, never reviewed (queue item 3). Six carry
  live links; P2.M3a's is labelled "(PDF)" (920 KB download); P5.M3 and P7.M2
  have no link by design.
- `data/measure-gaps.md` is generated and tracked; never quotes raw sheet prose
  (public repo) — same rule for anything in `notes/`. Its date stamp always
  shows in `git status`; expected, not drift.
- **Chart-engine parity rule in force**: shared-engine fixes land in BOTH
  `pillar.html` and `best-in-nation.html` until the extraction. Deliberate
  departures are commented in place (jump strip, pillar card header, BiN chip).
- `pillar.html` deep-link param is **`?p=N`**, not `?pillar=N`.
- Blog refresh pattern (last run 9/1): walk dpi.nc.gov/blog pagination past the
  boundary date, append to `blog_posts.csv` (archive pre-update copy first),
  BlogNum = row order in `blog_posts.csv`, draft matches for Andy (1–4
  substantive per post, one-line rationale; pure legal statements stay
  unmatched — SB 227/Leandro precedent), fold approved rows into
  `blog_focus_area_matches_final.csv`, rebuild, stamp, verify.
- Tracked notes: `punchlist-20260720.md`, `meeting-agenda-20260724.md`,
  `meeting-agenda-20260803.md`, `sheet-edits-20260727.md`,
  `review-packet-20260727.md` (CLOSED 8/4), `measure-metric-text.tsv`,
  `geoff-open-questions.md`.
- **Stray file to relocate (not ours):**
  `images/HappyPeoplePhotos/reporting-process-guide.html` belongs in
  EPP-Codebase — Andy to move from the host; unreachable from this container.

## Scratchpad harnesses NOT committed

9/1: nothing worth keeping — the pre-pull `action-statuses-pre.csv` snapshot
and raw post HTML were one-shot inputs, superseded by the committed CSVs.
