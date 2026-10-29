---
name: refresh-site
description: Routine refresh of the NCDPI Strategic Plan site — check dpi.nc.gov/blog for new stories and draft focus-area matches for Andy's approval, pull Smartsheet action statuses, rebuild pillar-data.json, bump the "Last updated" stamp, run the five verify tools, commit, and (on Andy's go) push to deploy via GitHub Pages and spot-check live. Use when Andy says "refresh the site", "/refresh-site", "check for new stories", "pull Smartsheet", "update implementation progress", or asks for the monthly/routine update. NOT for measure/actual values (accountability waves follow their own plan files in notes/) or HTML/CSS changes.
---

# Refresh the Strategic Plan site

Written 2026-10-12 from a run that worked end to end. It replaces the
OneDrive-era `/update-dashboard`, `/refresh-blogs` and `/rebuild-data`
skills, which were local-only, built for the old xlsx Actions Tracker
and Drupal delivery, and were lost in the move to `Projects/`.
This skill is tracked in git on purpose (`.gitignore` lets
`.claude/skills/` through) so it can't vanish again. Public repo: no
tokens, no raw sheet prose, no staff names in this file.

Run from the repo root. Stages are sequential; the two gates (story
approval, push) are Andy's.

## 0. Pre-flight

- `git fetch`, `git status -sb`: clean, and level with origin/master
  (Andy's VS Code shares this tree and can Sync mid-session).
- Note the current stamp (`python tools/update-stamp.py --check`) and
  the newest `StoryPublishDate` in `data/blog_posts.csv`. That date is
  the boundary for stage 1.

## 1. Stories (dpi.nc.gov/blog)

1. Walk `https://www.dpi.nc.gov/blog?page=0,1,…` with
   `curl -sL -A "Mozilla/5.0"` (save into the scratchpad) until a page's
   newest post is older than the boundary date. Pull post links with
   `href="/blog/YYYY/MM/DD/slug"`. Listing order is not strictly by
   date, so collect everything after the boundary from every page you walk.
2. Fetch each new post and read the `<article>` text (strip tags).
   Title comes from `<title>` minus ` | NC DPI`; date from the URL.
3. **Archive first:** `cp data/blog_posts.csv
   data/_Archive/blog_posts_<today>_pre-update.csv`.
4. Append rows to `data/blog_posts.csv`
   (`StoryTitle,StoryURL,StoryPublishDate,StoryCounty`) using Python
   `csv.writer(..., lineterminator="\n")`, UTF-8, and date format
   `YYYY-MM-DD 00:00:00`. **StoryCounty is hand-derived** from the town
   or district the post names (Greenville → Pitt, Elizabeth City →
   Pasquotank); comma-separate several counties, and leave it blank for
   statewide posts.
   **BlogNum = data-row order in blog_posts.csv** (header excluded), so
   only ever append, and only remove from the end.
5. Draft matches in `data/blog_focus_area_matches_draft_<today>.csv`
   (same 10 columns as `_final.csv`: BlogNum, StoryTitle, StoryURL,
   StoryPublishDate, StoryCounty, FocusAreaID, FocusAreaName, PillarID,
   PillarName, MatchRationale). Focus-area names are in
   `data/DIM_FocusAreas.csv`. Copy PillarName from the most recent rows
   of `_final.csv`, because older rows carry legacy pillar names.
   - Draft **1–3 substantive matches per post**, each with a one-line
     rationale written for the public site (no internal review language).
   - **Grep `_final.csv` for precedent** on the topic before choosing. For
     example, every attendance/AttendNC story is P4.F2 (Reduce Chronic
     Absenteeism is a named action) + P6.F1 (Office of Research and
     Promising Practices).
   - Mark anything borderline as borderline. Andy strikes those more
     often than not.
6. **GATE — Andy approves the matches.** Show each post with its drafted
   matches and a one-clause reason. Recommend what to do with statements:
   - Legal/governance statements (SB 227, Leandro, the 10/1/2026 CMS
     finance joint statement): Andy's latest call (10/12) was to **leave
     them out of blog_posts.csv entirely**, not keep them as unmatched
     rows. Recommend that, and confirm.
   - Statements whose substance is policy (8/26 Meta settlement →
     P4.F2) do get matched.
7. Apply his edits to the draft, then append the approved rows to
   `data/blog_focus_area_matches_final.csv`. Keep the draft file; it's
   the review record.

## 2. Smartsheet (implementation progress)

- `python data/build-pillar-data.py` pulls live statuses (token in
  gitignored `data/.smartsheet-token`) and rebuilds
  `data/pillar-data.json` in the same run. It has **no `--help`**;
  running it with any unknown argument still builds. `--as-of
  YYYY-MM-DD` exists for building against a future date.
- **Real churn check.** Pulls come back in a different row order with
  CRLF, and column 4 is the pull date, so the raw diff is always noise.
  Compare sorted columns 1–3:
  `diff <(git show HEAD:data/action-statuses.csv | tr -d '\r' | cut -d, -f1-3 | sort) <(tr -d '\r' < data/action-statuses.csv | cut -d, -f1-3 | sort)`
  - No difference → restore the snapshot so the pull date isn't committed:
    `git show HEAD:data/action-statuses.csv > data/action-statuses.csv`.
  - Real changes → keep the file, and list each status/launch change for
    Andy.
- Read the builder's summary lines: action count (110), story-match
  count (should equal the old count plus approved rows), past-due labels
  ("Reconciled N launch labels") and current-month "Launches in" count.
  When a month rolls over, Not Started actions flip to past-due "Planned
  for <Month>" labels. Report that count change.
- Launch dates come from Smartsheet; DIM_Actions is fallback only.

## 3. Rebuild, stamp, verify

1. If stories changed after the stage-2 run, rerun
   `python data/build-pillar-data.py` (and restore the snapshot again if
   there's no churn).
2. `python tools/update-stamp.py`: it bumps "Last updated" only if the
   content fingerprint moved (`--check` = dry run).
3. Run all five verify tools **in sequence** (they're Playwright-heavy
   and start their own servers; run in parallel they time out as
   contention):
   `verify-charts`, `verify-bin-chips`, `verify-chart-scales`,
   `verify-value-labels`, `verify-2026-actuals` (all `python
   tools/<name>.py`). Log each to the scratchpad and read the PASS/FAIL
   tail. Any FAIL stops the run. `verify-2026-actuals` EXPECTED values
   are wave-specific; a fail after an accountability wave may mean the
   table needs updating, not that the site broke. Say which.
4. Do **not** run `build-measures.py` (BiN) or
   `build-pillar-measures.py` as part of a routine refresh. Both carry
   traps (see HANDOFF "Traps").

## 4. Commit (local, no approval needed)

Stage explicit paths only, in two checkpoints:
- `Stories <M/D>: …`: blog_posts.csv, `_final.csv`, the draft, the
  archive copy.
- `data: rebuild as of <M/D>, stamp Last updated <date>`: pillar-data.json,
  stamp-state.json (+ action-statuses.csv only if real churn). Put the
  Smartsheet result (churn or none) in the body.

## 5. Deploy — GATE: Andy says push

- `git push origin master` deploys via GitHub Pages
  (`https://abax70.github.io/NCDPI-strategic-plan-site/`).
- Wait for Pages: poll the live `data/pillar-data.json` (cache-busting
  `?t=<epoch>`) until its `lastUpdated` equals the new stamp.
- Live spot-check with Playwright (see HANDOFF "Live-site spot-check
  gotchas"): pillar.html opens on the Actions tab at F1, so click the
  Stories tab and the target focus area (visible locators only) before
  asserting the new story titles appear; check the footer shows the new
  "Last updated" date; zero console errors.
- Remind Andy to hard-refresh (Ctrl+Shift+R).

## 6. Record

Add a CHANGELOG.md entry (posts added/excluded and why, match count
old → new, Smartsheet churn, label counts, stamp, verify results, push
time) and update HANDOFF.md "State". If this skill turned out wrong
anywhere, fix this file in the same session.
