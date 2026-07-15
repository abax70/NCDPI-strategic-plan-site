---
cc_status: hot
cc_strand: strategic-plan
cc_updated: 2026-07-15
---

# HANDOFF — NCDPI Strategic Plan Site

_Last updated: 2026-07-15 end of second session. See CHANGELOG.md for the full record._

## Where things stand

**Anchor: the 2026-08-05 state board meeting.** Meeting with Geoff **2026-07-16
(tomorrow)** — the site is current for it: statuses now come straight from
Smartsheet and the live deploy was verified serving them.

Shipped this session (commit `2fe9658`, live on Pages):

- **Smartsheet integration done; the tracker-xlsx trap is dead.**
  `data/build-pillar-data.py` reads statuses via: live Smartsheet API (token)
  → committed `data/action-statuses.csv` snapshot → legacy xlsx → hard abort
  (no more silent date-based guessing). A live pull auto-refreshes the
  snapshot CSV.
- 5 actions flipped Not Started → In Progress from the live tracker; deploy
  verified.

**To refresh statuses in any future session:** just say "refresh statuses from
Smartsheet" (Claude connector pull), or rerun `python data/build-pillar-data.py`
on a machine with the token — `SMARTSHEET_API_TOKEN` env var or the gitignored
one-line file `data/.smartsheet-token` (exists on the devcontainer host as of
2026-07-15; never commit it — the repo is public).

## Next session

- **Start building the pillar-page measure results** (backlog item, now the
  main thread).
- Debrief the Geoff meeting — fold any direction changes into the August-board
  plan.

## Awaiting Andy

- **Investigate P2.F2.A4** — exists in the Smartsheet tracker (launch
  2027-07-01, Not Started) but not in `DIM_Actions.csv`, so it's not on the
  site. If it's a real new action, add it to `DIM_Actions.csv` (its text can
  be pulled from the sheet) and rebuild.
- Delete `data/blog_focus_area_matches_draft_2026-07.csv` (graduated to final;
  untracked — deletions are always Andy's).
- Nudge graphics team if hero implementation needs sign-off (logo opacity 0.85
  and 5px navy baseline were our calls).
