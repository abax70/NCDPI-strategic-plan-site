---
description: Rebuild data/pillar-data.json and data/measures.json from their CSV/XLSX sources, then run /check-data to confirm warnings dropped.
user_invocable: true
---

# Rebuild Dashboard Data

Regenerate the two JSON files that drive the dashboard from their source CSV/XLSX files, then auto-run the data-quality check. Use this whenever Andy edits a source CSV, the Actions Tracker xlsx, or the blog-match CSV.

## What it does

Three stages, executed in order. Stop on the first non-zero exit.

1. **Rebuild pillar-data.json** — runs `data/build-pillar-data.py`. Combines `DIM_Pillars.csv`, `DIM_FocusAreas.csv`, `DIM_Actions.csv`, `blog_focus_area_matches_final.csv`, and `Strategic Plan Actions Tracker.xlsx` into `data/pillar-data.json`.
2. **Rebuild measures.json** — runs `data/build-measures.py` in **merge mode**. Refreshes every CSV-sourced field and preserves hand-authored fields (`iconUrl`, `whatsInMotion`, `whyItCounts`, `badgeImageUrl`, `badgeAltText`, `statusType`, `statusLabel`, `moreDataText`, `notes`) from the existing JSON. New measures added to `DIM_Measures.csv` are written with null hand-authored fields so `/check-data` flags them for editorial.
3. **Run /check-data** — runs `.claude/skills/check-data/check_data.py`. Prints the grouped report and its summary line.

## How to run

From the project root:

```
python data/build-pillar-data.py
python data/build-measures.py
python .claude/skills/check-data/check_data.py
```

Claude should run these sequentially and stop if any stage exits non-zero. After each stage, surface the script's stdout. After stage 3, surface any errors **before** warnings/info so blocking problems are visible first.

## Source files read

**Stage 1 (pillar-data.json):**
- `data/DIM_Pillars.csv`
- `data/DIM_FocusAreas.csv`
- `data/DIM_Actions.csv`
- `data/blog_focus_area_matches_final.csv`
- `data/Strategic Plan Actions Tracker.xlsx`

**Stage 2 (measures.json):**
- `data/measures.json` (merge base — read first, hand-authored fields preserved)
- `data/DIM_Measures.csv`
- `data/DIM_Pillars.csv`
- `data/LandingPage_MeasureMenu.csv`
- `data/LandingPage_MeasureDetailsText.csv`
- `data/LandingPage_MeasureResults.csv`

## Merge-preserve policy (stage 2)

`build-measures.py` will **not** overwrite these fields on existing measures:

| Field | Why preserved |
|---|---|
| `iconUrl` | Hand-curated path under `images/Measure Graphics/`. |
| `whatsInMotion[]` | Editorial content lives in `data/whats-in-motion-review.md`; cards are applied manually. |
| `whyItCounts` | Narrative voice; not in any CSV. |
| `badgeImageUrl`, `badgeAltText` | Curated Best-in-Nation badge assets. |
| `statusType`, `statusLabel` | Manually curated based on latest publication. |
| `moreDataText` | Link label; not in any CSV. |
| `notes` | Always null today; reserved for editorial. |

Everything else (`goal`, `definition`, `metricText`, `dataSeries`, `sourceLabel`, `sourceUrl`, `moreDataUrl`, `menuLabel`, `menuSubLabel`, `menuTooltip`, `nextUpdate`, `pillarName`, `valueFormat`, `yAxisMax`) is refreshed from CSV every run. `currentValue` and `currentDescription` are derived from the freshly rebuilt `dataSeries`.

## What this skill does NOT do

- **Does not edit `whats-in-motion-review.md` or `measures.json`'s hand-authored fields.** Editorial changes to icon paths, `whyItCounts`, badges, and `whatsInMotion` cards happen manually; this skill only refreshes the CSV-sourced fields around them.
- **Does not fetch new blog posts from dpi.nc.gov.** That's the follow-up `refresh-blogs` skill. If `blog_focus_area_matches_final.csv` is stale, stories will be stale.
- **Does not validate external URLs resolve.** That's the optional follow-up `validate-urls` skill.
- **Does not touch `DIM_*.csv` or the Actions Tracker xlsx.** Those are read-only inputs.

## Exit codes

- `0` — all three stages exited 0 and `/check-data` found no errors.
- `1` — at least one stage failed, or `/check-data` surfaced an error. Fix and re-run before marking data work done.

## Related skills

- `/check-data` — standalone data-quality scan; run this between `rebuild-data` passes when diagnosing a specific issue.
- `/review-dashboard` — smoke-test the rendered dashboard after a rebuild.
- `/self-verify` — run this before reporting rebuild work complete.
