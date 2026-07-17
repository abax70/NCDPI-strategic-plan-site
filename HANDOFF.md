---
cc_status: hot
cc_strand: strategic-plan
cc_updated: 2026-07-17
---

# HANDOFF — NCDPI Strategic Plan Site

_Last updated: 2026-07-17 (chunk B shipped). See CHANGELOG.md for full record._

## Where things stand

**Anchor: the 2026-08-05 state board meeting.** Deadline chain: **Y-set
populated by Mon 7/20 noon** (Geoff reviews with Supt. Mo Green that day; SPAC
7/21) → additional data by Fri 7/24 EOD → holding pattern to 8/5.

**The approved plan is `notes/plan-pillar-measures-20260717.md`** (chunk table,
column mapping, decision rules). Progress through the chunks:

| Chunk | Scope | Status |
|---|---|---|
| A | Sheet triage + mapping (the plan doc) | ✅ done 7/17 |
| B | `data/build-pillar-measures.py` pipeline | ✅ done 7/17, commit `73f84d9` |
| C | Results-tab rendering in pillar.html | **next** — plan recommends Opus, fresh session |
| D | Populate + verify on real Y set | after C (data side already real) |
| E | Accessibility + final review, deploy | last |

**Chunk B shipped:** `python data/build-pillar-measures.py` reads the
downloaded xlsx export (`data/source/StrategicPlan_measures.xlsx`, gitignored —
staff names + Geoff's notes, public repo) and emits `data/pillar-measures.json`
in the measures.json schema. First real run charted 6 measures (P1.M5, P1.M10,
P4.M4, P4.M7, P5.M3, P7.M2); P5.M2 excluded; 13 BiN rows skipped. **Per-wave
refresh routine:** download the sheet to `data/source/`, re-run the script,
work the warning list. Hand-authored fields (`sourceHtml`, `statusOverride`,
descriptions) survive rebuilds.

## Next session — chunk C (rendering)

- Transplant the BiN two-chart component + status band from
  `best-in-nation.html` into `pillar.html`'s `buildResultsTab()`, reading
  `data/pillar-measures.json` (already real data — filter by `pillarNumber`).
- Per-pillar conditional: charts for finalized measures; the existing
  "data coming" note otherwise; per-measure note when a pillar has
  some-but-not-all. "View the Best in the Nation measures" link (P1/P8
  especially — decision 1, no duplication).
- **New status vocabulary to render:** `on-target` / `approaching-target` /
  `baseline` + preserved `statusOverride` `{type, label}` which should WIN over
  the derived fields. BiN's pill only knows `record-high`; this is new UI.
- **`formatValue` in pillar.html needs a `$#,###` case** before any dollar
  measure goes Y (script infers the format; BiN renderer doesn't speak it).
- Chart.js pinned at 4.4.7 + annotation 3.1.0 — keep. Verify charts actually
  render (not just page-load); size check 375/1280/2560; `?p=N` param.

## Awaiting Andy (warning-list from chunk B's first run)

- **Hand-author `sourceHtml`** for P4.M4, P4.M7, P5.M3, P7.M2 (source cells are
  Geoff's scratchpad — left null on purpose) and a human `sourceLabel` for
  P1.M10's bare Tableau URL. Edit `data/pillar-measures.json` directly; these
  fields are preserved across re-runs.
- **Raise with Geoff:** P5.M2 chartability (all-1s milestone); P1.M5 goal text
  mid-edit in the sheet ("percentage number of…" — flows into the JSON as-is).
- **Carried over:** investigate P2.F2.A4 (in Smartsheet tracker, not in
  DIM_Actions.csv); delete `data/blog_focus_area_matches_draft_2026-07.csv`;
  decide whether to keep or delete `notes/pillar-measures-20260717.md` (the
  raw braindump — its content graduated into the committed plan doc).

## Repo state notes

- Local `master` = `origin/master`; pushes deploy via GitHub Pages (the new
  JSON is inert until chunk C references it).
- CRLF/LF churn appears intermittently between Windows host and container —
  verify with `git diff --ignore-cr-at-eol` before treating a modified-file
  list as real work; discard with `git restore .` if empty. No `.gitattributes`
  yet (permanent fix, deferred).
