# CHANGELOG — NCDPI Strategic Plan Site

Newest session first. Started 2026-07-15; earlier history lives in `git log`.

## 2026-07-15 (second session) — Smartsheet connector: tracker xlsx dependency replaced

**Context:** HANDOFF's queued task; meeting with Geoff 2026-07-16.

### Smartsheet-sourced action statuses (commit `2fe9658`, pushed + deploy verified)

- Discovered the tracker via the claude.ai Smartsheet connector: "Strategic
  Plan Actions Tracker" (sheet ID `6831169615122308`, NCDPI Strategic Plan
  Workspace), 110 rows with clean `Action ID` + `Status` picklist columns —
  a direct replacement for the manually downloaded xlsx.
- `build-pillar-data.py` status source is now a chain: **Smartsheet REST API
  (live, stdlib urllib, no new deps) → committed `data/action-statuses.csv`
  snapshot → legacy xlsx → hard abort.** A successful live pull rewrites the
  snapshot, so the committed copy self-refreshes.
- **The silent date-based fallback is deleted** — the trap that flipped 16
  statuses on 2026-07-15 when the xlsx was absent. The build now refuses to
  run rather than guess (tested: aborts with exit 1 before writing output).
- Token plumbing: `SMARTSHEET_API_TOKEN` env var or gitignored
  `data/.smartsheet-token` (one-line file; gitignore rule verified — repo is
  public via Pages, token must never be committed). Andy created the token
  file; the live-API path was tested with a real pull.
- **Data refresh shipped:** 5 actions flipped Not Started → In Progress per
  the live tracker (P5.F1.A3, P5.F1.A4, P7.F1.A4, P7.F3.A3, P8.F1.A1) —
  edits project leads made in Smartsheet since the last xlsx download.
  Verified rendering headlessly (pillars 5 and 8, no console errors; note
  pillar.html's query param is `?p=N`, not `?pillar=N`) and confirmed the
  GitHub Pages deploy serves the new statuses.

### Decisions

- Smartsheet's picklist value "Complete" is normalized to the site's
  historical display text "Completed" (`STATUS_DISPLAY` map in the script).
- **P2.F2.A4 exists in Smartsheet but not `DIM_Actions.csv`** — deliberately
  excluded pending Andy's investigation; the merge ignores unknown IDs, so it
  sits harmlessly in the snapshot.
- Two refresh routes now exist: ask Claude to "refresh statuses from
  Smartsheet" in any session (connector), or run the build on a machine with
  the token (live API). The scheduled download reminder Andy floated is moot.

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
- Andy reviewed and approved the draft as-is → folded into
  `blog_focus_area_matches_final.csv` (94 → 164 matches), reran
  `data/build-pillar-data.py`, verified Stories tabs render locally.
- Pre-update `blog_posts.csv` archived to
  `data/_Archive/blog_posts_2026-07-15_pre-update.csv`.

### Shipped

- Commit `a4fba10` pushed to master; GitHub Pages deploy verified **live**
  (production serves `lastUpdated: 2026-07-15`, 164 story matches; live-site
  hero screenshot checked at 2560px).
- `drupal-delivery/` removal (Andy deleted; committed at wrapup).

### Decisions

- `drupal-delivery/` declared stale (the Drupal-embed route is dead) — left
  untouched this session; Andy to delete. Hero changes were NOT mirrored there.
- `next-session-prompt.md` is gone (never committed); HANDOFF.md is the sole
  pick-up doc going forward.
- Landing logo opacity 0.85 and pillar baseline 5px are Claude's eyeball calls,
  flagged for Andy/graphics-team veto.
- **Rebuild trap found:** `build-pillar-data.py` needs
  `data/Strategic Plan Actions Tracker.xlsx`, which is absent in the
  devcontainer — the date-based fallback silently flipped 16 action statuses
  (including regressing a Completed action). Caught by diffing against the
  committed JSON; the previous build's statuses were restored before shipping.
  Any future rebuild here has the same trap until the tracker lives in-container
  or the Smartsheet connector replaces it.
