---
cc_status: hot
cc_strand: strategic-plan
cc_updated: 2026-07-15
---

# HANDOFF — NCDPI Strategic Plan Site

_Last updated: 2026-07-15 (graphics-team hero updates + stories refresh session).
This is the sole pick-up doc; see CHANGELOG.md for the session-by-session record._

## Where things stand

**Anchor: the 2026-08-05 state board meeting** (backward plan in
`Central-Command/plan/anchors.md`). **Meeting with Geoff is 2026-07-16.**

- **Graphics-team updates (2026-06-10 delivery): DONE.** Landing + pillar heroes
  reworked per their requests; verified headlessly at mobile/normal/wide widths.
  Uncommitted as of this writing — commit at wrapup.
- **Stories refresh: DRAFTED, in Andy's review.** 32 new blog posts
  (Jan 29–Jun 25) added to `data/blog_posts.csv`; 70 proposed focus-area matches
  in `data/blog_focus_area_matches_draft_2026-07.csv`. After Andy's review:
  fold survivors into `blog_focus_area_matches_final.csv`, rerun
  `data/build-pillar-data.py`, verify Stories tabs render.

## Next up

- Finish the stories pipeline once Andy's review lands (see above).
- Set up the Smartsheet connector → automate the flow of activities into the
  dashboard. (The connector is available in the devcontainer sessions now —
  unblocked; possible talking point with Geoff.)
- Start building the pillar-page measure results.
- Nudge graphics team (Hallie) if the hero implementation needs their sign-off;
  logo opacity (0.85) and navy baseline thickness (5px) were our calls.

## Awaiting Andy

- Review `data/blog_focus_area_matches_draft_2026-07.csv`.
- Deletions (Claude never deletes): `drupal-delivery/` (stale — Drupal route is
  dead), `images/StratPlan-BIN-Dashboard-Graphics/` (delivery folder, fully
  absorbed into images/ proper), and the draft matches CSV once it graduates
  to final.
