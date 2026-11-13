---
description: End-to-end routine data refresh. Runs /rebuild-data and verifies the preview. Use when source CSVs or the Actions Tracker xlsx changed but HTML/CSS/images did not.
user_invocable: true
---

# Update Dashboard

Orchestrates a routine data refresh after source CSVs or the Actions Tracker xlsx change. Rebuilds the JSONs and verifies the preview renders correctly, stopping before anything that requires Andy's review (commit, push).

## When to use

Use this when:
- `data/LandingPage_Measure*.csv` or `data/DIM_*.csv` changed (new measure values, new target years, etc.).
- `data/Strategic Plan Actions Tracker.xlsx` changed (action statuses updated).
- `data/blog_focus_area_matches_final.csv` changed *manually* (prefer `/refresh-blogs` for new blog posts).

Do NOT use this when:
- HTML, CSS, or JS in `index.html` / `pillar.html` changed — run `/dashboard-accessibility` after editing so the a11y audit runs.
- Images in `/images/` were added, renamed, or replaced — run `/check-images` first.
- You only want to regenerate JSON without the preview smoke test — run `/rebuild-data` directly.
- New blog posts need to be pulled in from dpi.nc.gov — run `/refresh-blogs` (it chains to `/rebuild-data` at the end).

## What it does

Four stages, stop-on-error. Report at each stage so Andy can follow along.

### Stage 1 — Pre-flight

1. Stat each source file and confirm it exists:
   - `data/LandingPage_MeasureResults.csv`
   - `data/LandingPage_MeasureMenu.csv`
   - `data/LandingPage_MeasureDetailsText.csv`
   - `data/DIM_Pillars.csv`, `data/DIM_FocusAreas.csv`, `data/DIM_Actions.csv`, `data/DIM_Measures.csv`
   - `data/blog_focus_area_matches_final.csv`
   - `data/Strategic Plan Actions Tracker.xlsx`
2. Print a small table of source mtimes vs `data/pillar-data.json` and `data/measures.json` mtimes. Flag sources newer than the JSONs with a ▲ — those are the drivers for this rebuild.
3. If **no** source is newer than both JSON outputs, ask Andy (AskUserQuestion, Yes/No) whether to proceed anyway. Rebuilding when nothing changed is harmless but probably not what he wanted.

### Stage 2 — Rebuild data

Rebuild the JSONs and compare the data-quality errors before/after so the skill only halts on errors **this refresh introduced**. Longstanding, accepted errors (e.g. the P1.M15 Character placeholder) shouldn't block routine refreshes.

1. **Snapshot the baseline error set** — before running any build script, invoke `python .claude/skills/check-data/check_data.py` and capture the list of ERROR-level bullet lines. Each bullet has the form `- **[file/path]** message.` — the tuple `(path, message)` is the error identity. Save these as `baseline_errors`.
2. **Run the builds** — in order, stop on non-zero:
   - `python data/build-pillar-data.py`
   - `python data/build-measures.py`
3. **Snapshot the refreshed error set** — invoke `python .claude/skills/check-data/check_data.py` again. Capture the same `(path, message)` tuples as `refreshed_errors`.
4. **Compute new errors** — `new_errors = refreshed_errors - baseline_errors`.
5. **Stop condition**:
   - If any build script (step 2) exited non-zero: **stop**, surface the script's stderr. Do NOT run stages 3–4.
   - If `new_errors` is non-empty: **stop**, surface only those new errors verbatim with a `NEW` label, then list `baseline_errors` separately under "Pre-existing (not blocking)". Do NOT run stages 3–4.
   - Otherwise: continue. Surface the full `/check-data` report (errors, warnings, info) so Andy sees the whole picture, but don't block.

This is NOT the same as invoking `/rebuild-data`; we need the before/after baseline, which that skill doesn't produce. The three stage-2 commands duplicate what `/rebuild-data` does, with the extra pre-build check-data call at step 1.

### Stage 2.5 — Verify the What's in Motion ticker

After data rebuilds cleanly, confirm the landing-page "What's in Motion" ticker will render legitimate actions. The ticker auto-selects the 3 most recently launched actions from `pillar-data.json`; this gate catches the case where a data refresh would put a future-dated or mis-flagged action on the landing page.

1. Run `python .claude/skills/verify-motion/verify_motion.py`.
2. **Stop condition**: non-zero exit (any error from the script). Surface the script's report verbatim and abort — do NOT proceed to the preview smoke test. The ticker would mislead stakeholders.
3. On success, include the 3 picked actions (id + pillar + launch date) in the Stage 4 handoff so Andy can sanity-check the selection.

See `/verify-motion` for the full check list.

### Stage 3 — Preview smoke test (fast path, not full `/review-dashboard`)

1. Start the preview server: `preview_start` with name `static-preview` (see `.claude/launch.json`). Reuses the server if already running.
2. Load `index.html`. Also load `pillar.html?p=1` to exercise the pillar renderer.
3. `preview_console_logs` with `level: "error"` on both pages. Any JS/fetch error is a **stop** condition — surface and abort.
4. `preview_eval` to sanity-check shape:
   - `window.allMeasures ? window.allMeasures.length : null` → expect **14**
   - `window.pillarData && window.pillarData.pillars ? window.pillarData.pillars.length : null` → expect **8**
5. **Spot-check one refreshed value.** Pick the first measure in the menu (currently CGRS / P1.M1):
   - Read the most-recent `ActualValue` row for that measure from `data/LandingPage_MeasureResults.csv` (the row where `MaxYearWithData = 1`).
   - Read `window.allMeasures[0].currentValue` via `preview_eval`.
   - They should match once `valueFormat` is applied (e.g. `87.7` in CSV → `"87.7%"` in the rendered card).
   - If they don't match, **stop** — the merge or format logic regressed.
6. `preview_screenshot` of the landing page as a visual proof point.

### Stage 4 — Handoff summary

Print a single report section with:

1. **Data refresh diff** — counts of what actually changed:
   - Measures with a different `currentValue` or `dataSeries`: diff new `data/measures.json` against `git show HEAD:data/measures.json`.
   - Actions with a changed `status`: diff new `data/pillar-data.json` against `git show HEAD:data/pillar-data.json`.
   - If `HEAD` lacks either file (first-ever refresh), skip the diff and say so.
2. **`/check-data` warnings** (if any) — terse, grouped by category.
3. **Preview check** — pass/fail, with the spot-checked measure and value.
4. **Uncommitted changes** — `git status --short` of `data/*.json` and anything else that moved.
5. **Next steps reminder**:
   - Commit is manual (golden rule #2).
   - If HTML/CSS changed today, run `/dashboard-accessibility`.
   - If new/renamed images landed today, run `/check-images`.

## Source files read

Inherited from `/rebuild-data` (see that skill for the full list). This skill adds no new reads of its own.

## Files written

- `data/pillar-data.json` — via `/rebuild-data` (Stage 2).
- `data/measures.json` — via `/rebuild-data` (Stage 2).

Nothing else is touched. No HTML, CSS, or JS in the project root is modified.

## What this skill does NOT do

- **Does not edit HTML/CSS or dashboard code.** Runtime JSON fetch means no page rebuild is needed when only data changes.
- **Does not run `/check-images`.** Routine data refreshes don't touch images.
- **Does not run `/dashboard-accessibility`.** The a11y audit only needs to re-run when layout changes.
- **Does not run `/refresh-blogs`.** That's the blog-pipeline skill. `/refresh-blogs` itself calls `/rebuild-data` at the end.
- **Does not commit.** Per golden rule #2, Andy reviews diffs and commits manually.
- **Does not rebuild the Drupal delivery package.** The Drupal handoff was shelved (2026-04-17); `drupal-delivery/` is a frozen snapshot of the last handoff and is no longer kept current.

## Exit codes

- `0` — all four stages succeeded; preview spot-check passed.
- `1` — any stage failed (`/rebuild-data` errors, preview console error, spot-check mismatch, missing source file).

## Related skills

- `/rebuild-data` — called by Stage 2; this skill is a superset with preview verification.
- `/check-data` — called transitively by `/rebuild-data`.
- `/review-dashboard` — heavier manual review checklist; run this separately if the refresh turns up anything suspicious.
- `/check-images` — run separately when images changed.
- `/dashboard-accessibility` — run separately when HTML/CSS changed.
- `/refresh-blogs` — run separately when blog posts are stale.
- `/self-verify` — optional final sweep before declaring work complete.
