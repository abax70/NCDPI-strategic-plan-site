---
description: Check the dashboard data files for missing fields, source/JSON drift, stale blogs, date-vs-status inconsistencies, and text quality issues.
user_invocable: true
---

# Check Dashboard Data

Run a comprehensive data-quality scan of the strategic plan dashboard's data files before sharing the site with stakeholders. Detect-only — does not modify any files.

## What it checks

Seven categories, each emitting findings at severity **error / warn / info**:

- **A. Completeness (measures.json)** — every measure has `name`, `goal`, `definition`, `currentValue`, `whyItCounts`, `nextUpdate`, `sourceLabel`, `sourceUrl`, and populated `dataSeries`. Best in Nation measures additionally need `badgeImageUrl`, `badgeAltText`, `statusLabel`. (The retired `whatsInMotion` field is no longer checked — the landing-page ticker now reads pillar-data.json directly; see `/verify-motion`.)
- **B. Completeness (pillar-data.json)** — 8 pillars, 26 focus areas, every focus area has ≥ 1 action and ≥ 1 story, every action/story has its required fields.
- **C. Date / status consistency** — catches actions with past `launchDate` but status `"Not Started"`; `hasStarted` booleans that disagree with `launchDate`; `launchText` that doesn't match the month/year of `launchDate`; invalid `status` values; stale `lastUpdated`.
- **D. Referential integrity** — `actionId` / `focusAreaId` / `measureId` regex; pillar numbers agree with parent; no duplicate IDs.
- **E. JSON ↔ source diff** — every mirrored field is compared against its CSV/XLSX source: pillar names (DIM_Pillars.csv), focus area names (DIM_FocusAreas.csv), action name/desc/launchDate (DIM_Actions.csv), action status (Strategic Plan Actions Tracker.xlsx), stories (blog_focus_area_matches_final.csv), measure details (LandingPage_MeasureDetailsText.csv), measure data series (LandingPage_MeasureResults.csv). Source mtime newer than JSON → **info** ("rebuild suggested").
- **F. Blog freshness** — newest `publishDate` across all stories > 14 days → warn.
- **G. Text quality** — formula leakage (`=IFERROR`, `#REF!`, `__xludf`, etc.), placeholder text (`Lorem ipsum`, `TBD`, `[Need to add...]`), HTML entity residue (`&amp;`, `&#39;`), double spaces.

## How to run

1. From the project root, run the check script:
   ```
   python .claude/skills/check-data/check_data.py
   ```
   The script resolves all paths from its own location, so it works from any CWD.

2. The script prints a grouped markdown report to stdout and exits with code **1** if any errors were found, **0** otherwise.

3. After the script finishes, do the **live CTG check** (the script can't do this part reliably):
   - WebFetch `https://www.dpi.nc.gov/news/celebrate-good/ctg-blog-list`
   - Extract the publish date of the most recent post listed there
   - Compare it to the "newest story" date surfaced in the script's Blog freshness section
   - If the live CTG has newer posts → info finding: "N new CTG posts not yet ingested into blog_posts.csv"
   - If the live CTG's newest post is itself > 14 days old → info finding: "CTG publishing has paused"

## How to present results

1. **Always run the script first before answering any data-related question about the dashboard.** It's fast and catches things that are easy to miss by eye.
2. Surface **blocking errors first** — anything in the Errors section that would break the UI or mislead readers (e.g., missing required fields, broken `planRef`, past-launched actions marked "Not Started").
3. Then surface warnings, then info.
4. For each finding, include the location (file + record ID) so Andy can jump straight to the offending row.
5. If the live CTG check finds drift, note it as a separate finding at the bottom of the report.

## What this skill does NOT do

- **Does not fix anything.** Remediation lives in follow-up skills (not yet built): `rebuild-data` (regenerate JSON from sources) and `refresh-blogs` (pull new CTG posts into blog_posts.csv).
- **Does not validate external URLs resolve.** URL validity checking could be added later.
- **Does not compare against the deployed GitHub Pages site** — only local files.

## Exit codes

- `0` — no errors (warnings and info findings are fine)
- `1` — at least one error. Don't mark data-related tasks complete until errors are resolved.
