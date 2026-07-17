---
cc_status: hot
cc_strand: strategic-plan
cc_updated: 2026-07-17
---

# HANDOFF — NCDPI Strategic Plan Site

_Last updated: 2026-07-17 (chunk C shipped). See CHANGELOG.md for full record._

## Where things stand

**Anchor: the 2026-08-05 state board meeting.** Deadline chain: **Y-set
populated by Mon 7/20 noon** (Geoff reviews with Supt. Mo Green that day; SPAC
7/21) → additional data by Fri 7/24 EOD → holding pattern to 8/5.

**The approved plan is `notes/plan-pillar-measures-20260717.md`.** Progress:

| Chunk | Scope | Status |
|---|---|---|
| A | Sheet triage + mapping (the plan doc) | ✅ done 7/17 |
| B | `data/build-pillar-measures.py` pipeline | ✅ done 7/17, commit `73f84d9` |
| C | Results-tab rendering in pillar.html | ✅ done 7/17 (this session) |
| D | Populate + verify on real Y set | ✅ current wave verified with C; **re-run per wave** |
| E | Accessibility + final review, deploy check | **next** |

**Chunk C shipped:** pillar.html's Results tab renders the BiN two-chart
component for finalized measures (P1/P4/P5/P7 today), stacked cards, new
status pills (`on-target` green / `approaching-target` blue / `baseline`
gray, `statusOverride` wins, null = no pill), direction-aware charts (P4.M4
decreases), `$#,###` format wired, lazy render (charts wait for the tab to be
visible). Verified headlessly at 375/1280/2560 on all 8 pillars, zero console
errors. The chart engine is a deliberate near-verbatim copy of
best-in-nation.html — **bug fixes must land in both files** until the planned
post-8/5 shared-file extraction.

## Next session (Monday 7/20 morning — deadline is noon)

0. **FIRST, before touching data — run the line-ending renormalize sweep.**
   `.gitattributes` (`* text=auto eol=lf`) was committed 7/17 to kill the
   CRLF/LF churn, but the already-tracked files still need a one-time rewrite
   to LF. Do this *before* the data wave so the line-ending-only diff stays
   isolated from real work:
   ```bash
   git add --renormalize .        # rewrites any CRLF-stored tracked files to LF
   git status                     # review the line-ending-only diff
   git commit -m "Renormalize tracked files to LF"   # only if the diff is non-empty
   ```
   The `.gitattributes` file carries a comment explaining this. After the
   sweep, the "CRLF/LF churn" note under Repo state notes is obsolete.
1. **New data wave:** download the fresh sheet export to
   `data/source/StrategicPlan_measures.xlsx`, re-run
   `python data/build-pillar-measures.py`, work the warning list. Hand-authored
   fields survive rebuilds. Charts for new measures appear with **no code
   changes** unless a new pillar goes from 0 → some measures (then just
   verify) or a new `valueFormat` shows up.
2. **Chunk E:** accessibility pass (canvas aria-labels exist from the BiN
   pattern; check contrast on the new blue/gray pills, keyboard order,
   plain-language descriptions), then commit, push, verify the Pages deploy.
   **Note: the chunk-C push already put the charts on production** (2026-07-17,
   deploy verified) — E is a polish pass on a live feature, not a launch.
3. Re-verify headlessly after the data refresh (the chunk-C Playwright
   routine: every canvas paints, all 8 pillars, 3 widths, console clean).

## Awaiting Andy

- **Hand-author `sourceHtml`** for P4.M4, P4.M7, P5.M3, P7.M2 — their cards
  still render **no Source line**. Edit `data/pillar-measures.json` directly;
  preserved across re-runs. (P1.M10's `sourceLabel` is now done — set to
  "NCDPI Proficiency dashboard" on 7/17; note the render logic has no branch
  for a bare `sourceUrl`, so a label is required for the Source link to show.)
- **Raise with Geoff:** P5.M2 chartability (all-1s milestone); P1.M5 goal text
  mid-edit ("percentage number of…" — visible on the live P1 card now).
- **Carried over:** investigate P2.F2.A4 (Smartsheet tracker vs
  DIM_Actions.csv). _(Done 7/17: deleted the draft blog-match CSV and the
  raw braindump note.)_

## Repo state notes

- Local `master` = `origin/master`; pushes deploy via GitHub Pages.
- `.gitattributes` (`* text=auto eol=lf`) committed 7/17; the tracked-file
  renormalize sweep is still pending — see step 0.
- CRLF/LF churn appears intermittently between Windows host and container —
  verify with `git diff --ignore-cr-at-eol` before treating a modified-file
  list as real work; discard with `git restore .` if empty. **Being fixed
  permanently by step 0** (the `.gitattributes` + renormalize); this note
  retires once that lands.
