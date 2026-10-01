---
cc_status: warm
cc_strand: strategic-plan
cc_updated: 2026-10-01
---

# HANDOFF — NCDPI Strategic Plan Site

_Last updated: 2026-10-01. Session records: CHANGELOG.md._

## State

- **10/1 SBE release DEPLOYED** — master = origin/master = `bc0b3f4`, Pages
  built 10:18 am ET 10/1. Live: P1.M1 89.0, P1.M10 59.2, P6.M1a 521, P6.M1b
  10 (all match the live accountability dashboards, checked 10/1); YRBS
  P4.M6a–d; 172 story matches; 110 actions; stamp 2026-10-01.
- `sbe-2026-10-01` is fully merged (local + origin both at `bc0b3f4`);
  safe to delete on Andy's say-so — not urgent, nothing rides on it.
- `notes/PLAN-SBE-2026-10-01.md` is CLOSED (its frontmatter says delete or
  archive after 10/1 — Andy's call; leave in place until he says).
- Accountability gate is over: the October correction window closed at the
  10/1 SBE. Next accountability values = 2026–27 cycle (Sept 2027).

## Traps (live)

- `build-measures.py` (BiN) still writes `actual: None` and derives status
  from baselines only — never regen `measures.json` without porting the 9/29
  pillar-builder fix (`61790d6`) first. `verify-2026-actuals.py` catches a wipe.
- Geoff's sheet still has "did not got to school" in P4.M6a's goal; JSON
  fixed (`770ab75`); a `build-pillar-measures.py` regen restores the typo
  until the sheet cell is fixed.
- Launch dates come from Smartsheet (`80843a8`); DIM_Actions'
  ActionLaunchDate is fallback only. Status is paired by action ID — DIM
  drift once shifted P2.F2 (fixed `9d0e74b`).
- Live-site spot-check gotchas (Playwright `inner_text`): pillar.html opens
  on the Actions tab with focus area F1 selected — click the Results /
  Stories tab and the target focus area (visible locator only) before
  asserting; chart headings are CSS-uppercased ("PATH TO …"); P1.M1 lives on
  best-in-nation.html, not pillar 1.

## Next session queue

1. **Geoff's open questions** — no answers since 9/4; all in
   `notes/geoff-open-questions.md` (past-due wording, etc.). Surface only if
   Andy brings Geoff news.
2. **Two BiN source links need a human** (`data/measures.json`): P8.M2's
   Statistical Profile link 403s to scripted clients
   (`apps.schools.nc.gov/public/f?p=145:11::::::`) — Andy must click it;
   P1.M8's Perkins link redirects `cte.ed.gov` → `octae.ed.gov` — update when
   convenient.
3. **Port the 9/29 preserve-actuals fix into `build-measures.py`** (BiN) —
   before any BiN regen.
4. **Curtis / future waves**: when sheet asterisks flip to Y, expect parser
   warnings (P4.M6a 2030 target literal `-%`; YRBS biennial). MeasureName
   drift check fires only on Y rows — keep DIM `MeasureLbl` short titles.
5. **Engine edge, low priority, both copies:** the *increasing* trajectory
   branch (best-in-nation.html AND pillar.html) anchors its lattice at `maxV`
   — breaks the day an actual overshoots its 2030 target (not yet: CGR
   2026 89.0 vs 2030 target 92.0). Mirror of `7a240ee`. `verify-chart-scales.py` catches it.
6. Chart-engine extraction (pending; parity rule below applies until then).
7. Open, not urgent: P6.M1a 2025 baseline — site 685 (ATR Table 41) vs
   Regional prior-year 682. Predates the correction; which is authoritative?
8. FYI: Mo's 8/28 blog letter says CGR 87.7% (site 87.8 since 8/14) —
   blog-side, not ours.

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
- **Verification is FIVE tools**, all passing 2026-10-01: `verify-charts.py`
  (8 pillars × 3 widths), `verify-bin-chips.py` (14 chips),
  `verify-chart-scales.py` (axis invariants; `--self-test`),
  `verify-value-labels.py` (label overlap, 108 charts × 4 widths;
  `--self-test`). Each exists because a real bug slipped past the previous
  ones; new bug class → add a sixth, don't widen one. The fifth,
  `verify-2026-actuals.py` (9/1), checks bar-color valence + P6 decrease-axis
  flip; its EXPECTED table is wave-specific (now the corrected 10/1 values).
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
