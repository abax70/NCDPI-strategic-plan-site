---
description: Sync data/blog_posts.csv and data/blog_focus_area_matches_final.csv with the live CTG blog list (https://www.dpi.nc.gov/news/celebrate-good/ctg-blog-list), then hand off to /rebuild-data. Run when /check-data Category F warns that stories are >14 days stale, or when Andy says "refresh the blogs".
user_invocable: true
---

# Refresh CTG Blog Posts

Pull any new posts from the live CTG blog list into the project's two blog CSVs, with Andy confirming focus-area categorization for each post, then hand off to `/rebuild-data` to regenerate `pillar-data.json` and run `/check-data`.

Automates the manual loop that closes a Category F warning from `/check-data`.

## What it does

Five phases. Stop on the first unrecoverable error. Ask Andy before moving past any pause gate.

### Phase 0 — Preflight

1. Run the helper to snapshot current state:
   ```
   python .claude/skills/refresh-blogs/refresh_blogs.py --preflight
   ```
   This prints a JSON object with `known_urls` (URLs already in `blog_posts.csv`), `max_blog_num`, and `focus_areas` (the 26-focus-area catalog loaded from `pillar-data.json`).

2. Verify working tree is clean-ish with `git status`. If `blog_posts.csv` or `blog_focus_area_matches_final.csv` already show uncommitted edits, **pause and ask Andy** before appending — their edits could collide with new rows.

### Phase 1 — Fetch the live CTG list

Use WebFetch on `https://www.dpi.nc.gov/news/celebrate-good/ctg-blog-list`:

> Prompt: "List every blog post linked on this page as a plain-text table with these columns, in order: Title | URL | Publish Date (as YYYY-MM-DD). Do not include promotional items, menu links, or non-blog entries — only posts under /blog/."

If the fetch fails or returns zero posts: **stop**. Report the failure and exit. Do not retry silently — the CTG page may have moved and silent retries will mask that.

### Phase 2 — Diff live against known

Classify each post from Phase 1 against `known_urls` from Phase 0:

| Class | Condition | Action |
|---|---|---|
| **Known & matches** | URL in `known_urls`, title and publish date agree with existing row | skip |
| **Known but drifted** | URL in `known_urls`, but title or publish date differs | add to `drift[]`, never auto-fix |
| **New** | URL not in `known_urls` | add to `new[]` |

If `new[]` is empty: print a one-paragraph summary (known, drift, no new posts) and **skip to Phase 5's summary only** — nothing to rebuild.

**Pause gate:** if `new[]` has more than 10 posts, stop and ask Andy. That's unusual and probably means the WebFetch parsed the page differently this time.

### Phase 3 — Categorize each new post (human-in-the-loop)

For each post in `new[]`, loop through these steps. Do **one post at a time** so Andy can make decisions without losing context.

1. **Read the post.** WebFetch the post URL with this prompt:
   > "Summarize this blog post in 2 sentences. Then list every North Carolina county explicitly named in the body. Then list 2–4 main themes (e.g. 'career readiness', 'educator compensation', 'dual language immersion')."

2. **Suggest focus areas.** Cross-reference the themes against the 26 focus areas from Phase 0. Pick **1–3 best matches**. For each, draft a 12–25-word MatchRationale in the same voice as existing rows in `blog_focus_area_matches_final.csv`. Examples of the voice:
   - *"Dual language immersion and Global Ready District are rigorous academic pathways"*
   - *"Educator compensation explicitly named as a strategic plan theme"*
   - *"Career/college readiness is a central theme, aligning with career development plans"*

3. **Ask Andy to confirm focus areas.** Use AskUserQuestion (multiSelect: true):
   - **Question:** `Focus areas for "[post title]"?`
   - **Options:** one per suggested focus area. Label format: `P1.F3 — Promote excellence for all`. Description: the draft rationale.
   - **Header:** `Focus areas`
   - If Andy selects **none**, ask a follow-up AskUserQuestion with the full 26-focus-area catalog grouped by pillar so he can pick directly.

4. **Confirm county if found.** If the WebFetch identified any NC counties:
   - AskUserQuestion — **Question:** `Counties mentioned in "[short title]": [Wake, Durham]. Keep these?`
   - **Options:** `Keep all` / `Keep some (Andy edits)` / `Clear`
   - **Header:** `County`
   - If "Keep some", ask a follow-up free-form to collect the final list.

5. **Stash the confirmed row.** Hold the title, URL, publish date, county, and one rationale per confirmed focus area in memory. Do not write yet.

### Phase 4 — Write the CSVs

Build a single JSON payload with every confirmed new post and its mappings, save to a temp file, and run the helper's write mode:

Payload schema:
```json
{
  "new_posts": [
    {
      "title": "Exact title from CTG",
      "url": "https://www.dpi.nc.gov/blog/YYYY/MM/DD/slug",
      "publish_date": "YYYY-MM-DD",
      "county": "Wake, Durham",
      "mappings": [
        {"focus_area_id": "P1.F3", "rationale": "..."},
        {"focus_area_id": "P2.F1", "rationale": "..."}
      ]
    }
  ]
}
```

Invoke:
```
python .claude/skills/refresh-blogs/refresh_blogs.py --write --payload <temp-file>
```

The helper:
- Assigns sequential `BlogNum` values starting at `max_blog_num + 1`.
- Looks up `FocusAreaName`, `PillarID`, `PillarName` from `pillar-data.json` based on each `focus_area_id` — Claude never hand-codes these, to prevent typos.
- Appends rows to `data/blog_posts.csv` and `data/blog_focus_area_matches_final.csv` using CRLF line endings and the existing quoting conventions. Existing rows are untouched.
- Exits **0** on success, **1** on write failure, **2** on payload/schema error or unknown FocusAreaID.

If the helper exits non-zero: **stop, report, do not rerun**. A failure means CSVs may be partially written and need manual inspection.

### Phase 5 — Hand off to /rebuild-data

1. Print a summary table **before** handing off, so Andy sees what changed:
   - New posts added: N
   - New focus-area mappings: M
   - Drift detected (not fixed): K entries — show `URL | old title/date | new title/date` for each
   - Counties auto-filled: C

2. Invoke `/rebuild-data` via the Skill tool. It owns the downstream chain: `build-pillar-data.py` → `build-measures.py` → `/check-data`. Its exit code is this skill's exit code.

3. If `new[]` was empty in Phase 2, skip the handoff — nothing changed, no reason to rebuild.

## Pause gates (stop and ask Andy)

- WebFetch on the CTG page fails, returns empty, or returns 0 blog URLs.
- More than 10 new posts in a single run.
- A new post doesn't cleanly map to any focus area.
- `blog_posts.csv` or `blog_focus_area_matches_final.csv` has uncommitted edits at Phase 0.
- Helper script exits non-zero on write.

## What this skill does NOT do

- **Does not rewrite existing rows.** If a CTG post's title or date has drifted on the live site, the skill reports the drift and leaves the row alone — CSVs may have been hand-edited intentionally.
- **Does not regenerate `pillar-data.json` directly.** That belongs to `/rebuild-data`.
- **Does not validate external URLs resolve.** That's the (still-unbuilt) `validate-urls` skill.
- **Does not touch `blog_focus_area_matches_draft.csv` or `_reviewed.csv`** — those are historical review artifacts; only `_final.csv` is authoritative.

## Exit codes

- `0` — no new posts, or new posts appended and `/rebuild-data` exited 0.
- `1` — helper script failed, `/rebuild-data` surfaced an error, or a user-cancelled pause gate.
- `2` — payload schema error from the helper (unlikely unless Claude built a bad payload).

## Related skills

- `/check-data` — run before and after to confirm Category F (Blog freshness) flips from warn → info.
- `/rebuild-data` — called by Phase 5; regenerates `pillar-data.json` + `measures.json` from sources.
- `/self-verify` — run after a full refresh + rebuild before marking work complete.
