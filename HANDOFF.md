---
cc_status: hot
cc_strand: strategic-plan
cc_updated: 2026-07-15
---

# HANDOFF — NCDPI Strategic Plan Site

_Last updated: 2026-07-15 end-of-session. See CHANGELOG.md for the full record._

## Where things stand

**Anchor: the 2026-08-05 state board meeting.** Meeting with Geoff 2026-07-16.

Everything from the 2026-07-15 session is **shipped and live** (commit `a4fba10`
+ wrapup commit; GitHub Pages verified serving the new build):

- Graphics-team hero updates (2026-06-10 delivery) — landing + pillar heroes
  reworked, verified at mobile/normal/wide widths. Hallie's sizing question
  answered: assets worked as-is.
- Stories refresh — 32 new posts (through 2026-06-25), 164 total focus-area
  matches live on the pillar Stories tabs.
- `drupal-delivery/` removed (Drupal-embed route abandoned).

## Next session: Smartsheet connector (Andy's call, 2026-07-15)

Set up the Smartsheet connector → automate the flow of activities into the
dashboard. Notes going in:

- The connector's MCP tools are available in devcontainer sessions (verified
  present 2026-07-15; call `get_resource_guide` first per server instructions).
- **Design target worth considering:** replace the `Strategic Plan Actions
  Tracker.xlsx` dependency in `data/build-pillar-data.py`. That file is absent
  in the devcontainer and the script's date-based fallback silently flips
  action statuses (bit us 2026-07-15; statuses had to be restored by hand from
  the committed JSON). Smartsheet-sourced statuses would kill the trap.

## Backlog (after the connector)

- Start building the pillar-page measure results.
- Nudge graphics team if hero implementation needs sign-off (logo opacity 0.85
  and 5px navy baseline were our calls).

## Awaiting Andy (deletions are always Andy's)

- Delete `images/StratPlan-BIN-Dashboard-Graphics/` (delivery folder — fully
  absorbed into images/ proper; contains `__MACOSX`/`.DS_Store` junk; untracked,
  so it will pollute any future commit sweep until removed).
- Delete `data/blog_focus_area_matches_draft_2026-07.csv` (graduated to final;
  untracked).
