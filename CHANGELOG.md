# CHANGELOG — NCDPI Strategic Plan Site

Newest session first. Started 2026-07-15; earlier history lives in `git log`.

## 2026-07-15 — Graphics-team hero updates + stories refresh (pre-Geoff-meeting session)

**Context:** Meeting with Geoff 2026-07-16; state board meeting 2026-08-05.

### Graphics team assets & suggestions (from 2026-06-10 meeting; Hallie's delivery)

- **Landing hero (`index.html`):** blue-boxes pattern now spans the full banner
  width (was clipped to the left panel — read as cut off on wide monitors).
  Replaced the white right panel with the new transparent-background white AEE
  lockup (`StratPlan-Dashboard-HomeHdr-HiRes.png`) floating over the pattern at
  85% opacity, still anchored to the 1440px content frame on wide viewports.
- **Pillar hero (`pillar.html`):** adopted the recreated gradient SVGs (graphics
  team removed the baked-in 10px navy bottom bar); the navy baseline is now a
  CSS `.pillar-hero::after` — full hero width (it previously stopped at the
  right panel) and thinner (5px, matching the landing strip weight). Right panel
  swapped to the new `StratPlan-Dashboard-PillarHdr-HiRes.png` lockup as a
  full-panel white block — this retired the per-pillar recolored patterns
  (`PILLAR_HERO_BG` removed from the JS).
- **Assets:** new logos → `images/Achieving Academic Excellence Logos/Dashboard
  Header Logos/`; new gradients replaced the old in `images/Background
  Patterns/_pillars/` (old SVGs archived to
  `images/_Archive/2026-07-15_pillar-gradients-with-navy-bar/`). Re-delivered
  `Header_Blue` PNGs were byte-identical to existing — no change.
- **Verified** headlessly (Playwright) at 375/1280/2560px on index + pillars 1,
  2, 4, 7 — no console errors.

### Stories refresh (32 new posts, 2026-01-29 → 2026-06-25)

- Scraped dpi.nc.gov/blog; appended 32 new posts to `data/blog_posts.csv`
  (now 62), counties extracted from post text.
- Matched posts to focus areas via four parallel matcher agents using the
  established conventions (1–4 substantive matches per post, one-line
  rationale). Result: 70 proposed matches across 30 posts;
  the Leandro and SB 227 legal statements intentionally unmatched.
- Draft for Andy's review: `data/blog_focus_area_matches_draft_2026-07.csv`.
  After review: fold into `blog_focus_area_matches_final.csv`, rerun
  `data/build-pillar-data.py`, ship the new `pillar-data.json`.
- Pre-update `blog_posts.csv` archived to
  `data/_Archive/blog_posts_2026-07-15_pre-update.csv`.

### Decisions

- `drupal-delivery/` declared stale (the Drupal-embed route is dead) — left
  untouched this session; Andy to delete. Hero changes were NOT mirrored there.
- `next-session-prompt.md` is gone (never committed); HANDOFF.md is the sole
  pick-up doc going forward.
- Landing logo opacity 0.85 and pillar baseline 5px are Claude's eyeball calls,
  flagged for Andy/graphics-team veto.
