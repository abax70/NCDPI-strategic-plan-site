---
cc_status: hot
cc_strand: strategic-plan
cc_updated: 2026-07-16
---

# HANDOFF — NCDPI Strategic Plan Site

_Last updated: 2026-07-16 (Geoff debrief folded in). See CHANGELOG.md for full record._

## Where things stand

**Anchor: the 2026-08-05 state board meeting.** The Geoff meeting (7/16) is now
debriefed and folded in. The primary remaining development goal for the board
update is the **pillar measure charts** — identical in form to the best-in-nation
(BiN) charts already built, but showing the measures tied to the *non-BiN*
pillars. Geoff expects ~15 of these to have data by 8/5.

**Source & pipeline.** Measure data currently lives in a rough Google Sheet on
Google Drive, `StratPlanMeasures` — Geoff's live scratchpad as he meets with
teams to define measures. It is NOT chart-ready. An intermediate cleaning step
turns it into the chart source. Rows that are finalized and ready to populate are
flagged `Y` in the sheet's **Finalized** column.

- **Design call (Andy + Claude, 7/16):** make the cleaning step a *repeatable
  script*, not a one-time hand-clean. Data arrives in waves (the `Y` set now, more
  by 7/24, and likely edits after the Mo/SPAC reviews), so the script should read
  `StratPlanMeasures` and emit exactly the data contract the BiN charts already
  consume — each new wave becomes a re-run, not a re-clean.

Shipped the prior session (single commit, hero polish):

- Landing + Best-in-Nation heroes now use the tagline-free `WhiteOrange` AEE
  lockup on a full-width blue-squares field. BiN got the biggest rework — its old
  split-panel layout was replaced with landing's continuous-pattern treatment.
- Pillar hero baseline strip trimmed 5px → 4px.
- Landing hero title anchored to the 1440px content frame so it aligns with
  `STRATEGIC PILLARS` on wide monitors (laptop unchanged).
- Project `CLAUDE.md` refreshed: old "diverged forever" warning retired; new note
  on the CRLF/LF line-ending churn between Windows host and container.

## Next session — pillar measure charts

Backward chain to the board meeting:

- **[by Mon 7/20, noon]** Populate all currently-finalized (`Y`) measures into the
  pillar charts. Geoff reviews with Supt. Mo Green that day; SPAC (the
  strategic-plan governing committee) the next day, 7/21. Expect feedback after.
- **[by Fri 7/24, EOD]** Populate any additional measure data that has come in (the
  ball is in Geoff's court on what lands).
- **[7/24 → 8/5]** Holding pattern — only leadership-required changes, plus routine
  actions/stories updates.

First moves:

- Pull up `StratPlanMeasures` via the Google Drive connector and read its real
  columns.
- Confirm the BiN charts' data contract — the file/shape they read today is the
  cleaning script's output target.
- Build the cleaning script, then populate the `Y` set.

## Open threads

- **Size-the-effort questions (raise with Geoff / resolve early):**
  - How were the BiN charts built — templated/scripted (point at new data → chart
    appears) or bespoke per chart? Single biggest driver of whether 15 charts is a
    day or a week.
  - How many rows are `Y` *right now*? Sizes the 7/20 pass specifically (vs. the
    ~15 expected by 8/5).

## Awaiting Andy

- **Investigate P2.F2.A4** — still exists in the Smartsheet tracker (launch
  2027-07-01, Not Started) but not in `DIM_Actions.csv`, so it's not on the site.
  Carried over.
- Delete `data/blog_focus_area_matches_draft_2026-07.csv` (graduated to final;
  untracked — deletions are always Andy's). Carried over.
- Nudge graphics team if hero implementation needs sign-off — last session the
  answer was "yes, they gave us tagline-free variants in April; just needed to
  point at them."

## Repo state notes

- Local `master` = `origin/master` now. The old "intentionally diverged, do not
  reconcile" warning is retired.
- CRLF/LF line-ending churn appears intermittently between Windows host and
  container. Always verify with `git diff --ignore-cr-at-eol` before treating a
  modified-file list as real work; discard with `git restore .` if empty.
- No `.gitattributes` in the repo — adding one would be the permanent fix, but
  deferred.
