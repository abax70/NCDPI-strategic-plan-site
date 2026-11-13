---
description: Verify the landing-page "What's in Motion" ticker points to genuinely launched Strategic Plan actions. Reads pillar-data.json, replicates the selection logic used by index.html, and reports the 3 actions the ticker will show with their dates, pillar, and deep-link URLs.
user_invocable: true
---

# Verify What's in Motion ticker

Sanity-checks the "What's in Motion" ticker on `index.html`. The ticker renders the 3 most recently launched Strategic Plan actions from `data/pillar-data.json`. This skill replicates that selection server-side and verifies each pick is genuinely launched, avoiding the embarrassment of shipping a card that points to an action with `hasStarted: false` or a future launch date.

## When to use

- Before sharing a refreshed dashboard with stakeholders.
- As an automated step inside `/update-dashboard` (Stage 2.5) — see that skill.
- Any time `data/pillar-data.json` changes and you want a quick sanity check.

## How to run

```
python .claude/skills/verify-motion/verify_motion.py
```

Exits `0` on success, `1` on error. Warnings never fail.

## What it checks

For each of the 3 ticker actions the landing page will render:

1. **`hasStarted` + `launchDate ≤ today`** — the action must genuinely be launched. Future-dated actions with stale `hasStarted: true` flags fail here.
2. **`launchText` starts with "Launched "** — catches data-pipeline bugs where `hasStarted` and `launchText` disagree (e.g., text still says "Launches in August, 2026" while the flag flipped true).
3. **`actionId` resolves** — the deep link `pillar.html?p=N&action=<actionId>` must land on a real action so the ticker card click doesn't dead-end.

It also surfaces the resolved pillar number, focus area, launch date, and pillar.html URL for each pick so Andy can eyeball whether the story makes sense.

## Selection logic (must match `index.html renderMotionTicker()`)

1. Collect every action across all pillars with `hasStarted === true` AND a non-empty `launchDate`.
2. Sort by `launchDate` descending, tie-break by `actionId` ascending.
3. Take the first 3.

If fewer than 3 launched actions exist in `pillar-data.json`, the script fails with an error — the ticker would render an incomplete row.

## Exit codes

- `0` — all 3 ticker actions pass the checks.
- `1` — at least one error. The ticker data is not safe to ship until fixed.

## What this skill does NOT do

- **Does not render or screenshot the ticker.** That's verified in `/update-dashboard` Stage 3's preview smoke test.
- **Does not fix data problems.** Remediation lives in the upstream source (`DIM_Actions.csv`, Actions Tracker xlsx) plus `/rebuild-data`.
- **Does not re-validate `check-data`'s broader data-quality rules.** Run `/check-data` separately for the full sweep.
