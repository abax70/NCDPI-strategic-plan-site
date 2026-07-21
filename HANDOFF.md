---
cc_status: hot
cc_strand: strategic-plan
cc_updated: 2026-07-21
---

# HANDOFF — NCDPI Strategic Plan Site

_Last updated: 2026-07-21 (graphics-feedback round shipped). See
CHANGELOG.md for the full record._

## Where things stand

**Geoff meeting: Tue 7/22 at 3pm.** Andy gets the "last" round of feedback
prior to the 7/24 data wave — expect a small punch list from it, likely the
final leadership-driven changes before the holding pattern to 8/5.

**Graphics team feedback is fully resolved (7/21, commit `8d8aeab`,
deploy verified):** Pillar 4 pink → Medium Orange #C75128 (tabs + Stories
links, contrast improved to 4.53:1 on white), homepage photo stack
reordered (track girl top — her raised arms under the recycle-bin photo
read as holding the bin), and mobile hero logo now clears the pillar-color
bar (~8–12px, was 0px at ≤480px). Their sign-off: "once those are wrapped
up, we're good to go."

**All pre-7/24 prep is done.** The 7/20-noon deadline was met (9 measures
live across P1/P2/P4/P5/P7); the 7/20 second session landed the three
queued items:

- **Jump strip (punch #6) is built and verified, currently dormant** — it
  appears automatically when any pillar reaches 4+ measures (max today is
  P2's 3). Verified synthetically; no action needed when the 7/24 wave
  triggers it for real, but eyeball it.
- **DIM_Measures.csv is fully reconciled with the sheet** (two-way audit,
  punch #3): 5 stale base rows removed, 8 sub-ID rows added (55 total).
  The pipeline re-run confirmed byte-identical pillar-measures.json.
  **Andy: review the drafted short names in the diff** (commit `HEAD`).
- **The gaps report now self-audits DIM every run** — a "DIM ↔ sheet
  reconciliation" section in `data/measure-gaps.md` catches unregistered /
  stale / malformed / duplicate IDs each wave.
- **`tools/verify-charts.py` exists** — the headless verify routine is a
  real tool now (8 pillars × 3 widths, painted-pixel per canvas, card
  counts vs JSON, console clean, jump-strip contract). Run it after any
  chart-engine or data change: `python tools/verify-charts.py`.

**Remaining deadline chain:** additional data by **Fri 7/24 EOD** → holding
pattern (leadership-required changes + actions/stories only) → **8/5 state
board meeting**.

## Next session: the 7/24 data wave

1. Andy downloads the fresh export to `data/source/StrategicPlan_measures.xlsx`.
2. `python data/build-pillar-measures.py` → work the warning list + both
   sections of `data/measure-gaps.md` (missing fields AND the new DIM
   reconciliation section).
3. `python tools/verify-charts.py` (replaces the old scratchpad routine).
   If a pillar hit 4+ measures, the jump strip goes live — eyeball it once.
4. Commit, push, verify the Pages deploy.
   Watch for: a brand-new `valueFormat`, another pillar going 0 → some
   measures (data-driven, just verify), and the P4.M6 situation below.

## Awaiting Andy

- **`sourceHtml` for 5 measures** — P4.M4, P4.M7, P5.M3, P7.M2, P2.M4a
  still render **no Source line**. Andy drafts text (or sends URLs), Claude
  writes the JSON. The gaps report nags about these every run.
- **Raise with Geoff — the 7/22 3pm meeting is the natural venue** (list
  is pasteable from `data/measure-gaps.md`):
  - **P4.M6 is shared by 4 sheet rows** (YRBS items) — needs distinct
    sub-letters before any goes Y (2+ Y aborts the build; exactly one Y
    charts under the ambiguous ID).
  - Row 2's literal `NEW` Measure ID (Schools of Character) needs a real ID.
  - P2.M3a and P2.M3c exist but **no P2.M3b** — deliberate?
  - Carried over: WhyMeasureMatters for pillar measures (Andy guesses no),
    P5.M2 chartability (all-1s milestone), P1.M5's mid-edit goal text
    ("percentage number of…", visible on the live P1 card).

## Repo state notes

- Local `master` = `origin/master`; pushes deploy via GitHub Pages
  (production URL: abax70.github.io/NCDPI-strategic-plan-site).
- `data/measure-gaps.md` is generated every run and deliberately tracked.
  It never quotes raw sheet prose (public repo) — IDs and row numbers only
  in the reconciliation section.
- Chart engine parity rule still in force for the SHARED engine: bug fixes
  land in BOTH pillar.html and best-in-nation.html until the post-8/5
  extraction. The jump strip is a documented deliberate departure
  (pillar.html only — BiN's carousel has no stacked cards to anchor into).
- `notes/punchlist-20260720.md` is tracked as of this session.
