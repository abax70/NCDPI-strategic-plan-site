---
cc_status: hot
cc_strand: strategic-plan
cc_updated: 2026-08-04
---

# HANDOFF — NCDPI Strategic Plan Site

_Last updated: 2026-08-04. See CHANGELOG.md for the full record of that session._

## Where things stand

**The board views the site Wednesday 8/5 — that is today or yesterday by the time
anyone reads this.** Everything below is pushed and live.

The 8/4 session finished the review packet. `notes/review-packet-20260727.md` is
now **fully reviewed** — Section A closed 8/3, Sections B and C closed 8/4, and
Section D's three questions are all answered (D1 on 8/3; D2 needs no action; D3 is
the `DRAFTED_SINCE_REVIEW` decision below). Five source lines now carry real,
verified links. All four verify tools pass; stamp is 2026-08-04.

The 8/3 session before it was a pre-board integrity pass that found and fixed
**three false claims** the site was making: 22 action cards saying "Launched" for
actions that had not started, bar value labels showing **wrong numbers** at mobile
width (`97,317` → `97,31`), and a sidebar stamp reading "Jul 15" while serving
7/27+ data.

**Geoff is back.** No check-in was held 8/3 or 8/4.

## FIRST: the one open decision from the review pass

**`DRAFTED_SINCE_REVIEW` in `tools/export-metric-text.py` is still UNTOUCHED** and
still lists all five IDs (P2.M3a, P2.M4b, P1.M17b, P6.M1a, P6.M1b);
`notes/measure-metric-text.tsv` was **not** regenerated.

That was correct while the packet was open. **It is now the only thing left in the
packet** — Section D3 asks literally "anything to change before these five drafts
lose their 'pending review' label?", and the answer is now no. So the remaining
step is: clear the five IDs and re-run `tools/export-metric-text.py`.

**It was deliberately NOT done on 8/4 without Andy saying so.** Removing an ID early
has laundered unreviewed prose as approved **twice** (7/27, both caught), and the
day before a board meeting is the wrong time to test that guardrail. Confirm with
Andy, then clear and re-run.

## Next session queue

1. **Clear `DRAFTED_SINCE_REVIEW` + regenerate the TSV** (above) — needs one yes.
2. **Sort out the P4.M6a–d names** — see the trap below. Andy: "we'll get it
   straightened out but not by tomorrow."
3. **Ask Geoff the 8/3 questions** — `notes/geoff-open-questions.md` is the
   short-form list (15 items, 8/3-new ones marked). The two most urgent, because
   they are about what the board saw Wednesday:
   - Is **"Planned for August, 2026"** the wording he wants on 22 action cards?
   - Did **P7.F3.A3** and **P8.F2.A1** regress to Not Started deliberately, or did
     a project lead mis-click? P7.F3.A3 has now moved twice.
4. **Two Best-in-Nation source links need a human** (found 8/4, both pre-existing,
   both in `data/measures.json`, neither ever reviewed):
   - **P8.M2's Statistical Profile link 403s** to a scripted client even with a
     browser user-agent — `apps.schools.nc.gov/public/f?p=145:11::::::`. Could be
     an APEX app refusing non-browsers or a dead deep link; **indistinguishable
     from the container, so Andy has to click it.**
   - **P1.M8's Perkins link moved** — `cte.ed.gov/pcrn/explorer` now redirects to
     `octae.ed.gov/pcrn/explorer`. Works; update when convenient.
5. **Watch for Shaun** (the four YRBS P4.M6 measures) and **Curtis** (low-performing
   schools) → Andy flips those asterisks to Y → that wave brings P4.M6a–d live.
   Expect parser warnings: P4.M6a's 2030 target cell is a literal `-%` and the
   YRBS series are biennial ("-" in off years). **Do not let that wave land before
   the name trap below is resolved.**
6. **After 8/5:** the chart-engine extraction (see parity rule below).

## TRAP: the P4.M6a–d names will be overwritten by descriptions

The sheet now carries authored `MeasureName` values for P4.M6a–d that **are not
names** — they are metric descriptions in the wrong column (Andy's read, 8/4):

| ID | DIM — correct as the *name* | Sheet — really a *description* |
|---|---|---|
| P4.M6a | Missed School Due to Feeling Unsafe | Percentage of High School Students Who Felt Unsafe at School or On Their Way to School |
| P4.M6b | Student Sense of Belonging | Percentage of High School Students Who Feel Like They Belong at Their School |
| P4.M6c | Students Reporting Poor Mental Health | Percentage of High School Students Who Reported That Their Mental Health Was Not Good |
| P4.M6d | Students Feeling Sad or Hopeless | Percentage of High School Students Who Felt Sad or Hopeless |

**Nothing in the pipeline will warn you.** The MeasureName drift check fires only on
`Y`-flagged rows and these are `*`; the "in sync" reconciliation compares IDs, not
names. This surfaced only because someone read Section C.

**Why it bites:** under the standing *sheet wins, DIM follows* rule, the moment
Shaun confirms and these flip to `Y`, the sheet text becomes the card titles — at
**86 / 75 / 84 / 58 characters**, against live titles that are far shorter.

**The lever, currently unused:** `menuLabel` falls back to `name` only when DIM's
`MeasureLbl` is empty (`data/build-pillar-measures.py:596`), and `MeasureLbl` is
blank on **every** pillar measure today. A short `MeasureLbl` alongside the long
official `MeasureName` satisfies both without renegotiating anyone's wording.

## Longer-running carry-overs (not blocking)

- **P2.M4a says PSUs but may count LEAs.** The 7/27 retitle aligned the title with
  its approved description; it did **not** change what the sheet counts. Same family
  as the P5.M3 unit question. Note LEA is *genuinely correct* for P1.M17b (federal
  IDEA determination at LEA level), and "district" is correct for P6.M1b (district
  identification applies to LEAs; charters are not in districts). The site will
  legitimately use both words — be deliberate rather than normalizing them.
  **8/4:** the sheet's P5.M3 Source cell was re-cleaned to "Reports from LEAs", but
  the site deliberately **keeps "Reports from public school units to NCDPI"** (Andy's
  call). The question stays open rather than being silently resolved by a sheet edit.
- **P2.M2a/b's `sourceLabel` is mangled** — `"…NCDPI ( calculated as number of
  candidates…"`, unbalanced paren, truncated mid-word, straight from the sheet cell.
  **Invisible on the site** because `sourceHtml` wins in rendering, so this is not
  urgent — but it is waiting for whoever next touches that field.
- **P1.M17b's "Annual Results" chart is ~200px of near-empty white** — all bars are
  zero-height, showing a row of `0.0%` labels on the baseline. More pronounced on
  mobile. Deliberately left as-is for Geoff's reaction; he has not yet seen it.
- **P1.M17b's year suffix** uses the site-standard `(2024–25)` but the source is
  SPP/APR **FFY 2024**, a federal fiscal year.
- **WhyMeasureMatters** for pillar measures (no `whyItCounts` on any); the export's
  `MeasureContextNote` and `WhyMeasureMatters` columns are empty in every row.
- **P5.M2 chartability** — all-1s NCSIS milestone; excluded by name.
- **P1.M5** stays a **count**; the percentage idea sits in the export's
  `Notes on Recommended Changes` side tab, which the pipeline never reads.
- **P2.M3a `nextUpdate`** — "When Available?" cell is blank (no Next update line).
- **P2.M2b and P2.M3a derive no status pill** — both regressed vs. prior year; the
  rule refuses to print "Approaching target" over a decline. `statusOverride` if
  Geoff wants text there.

## Repo state notes

- Local `master` = `origin/master`; pushes deploy via GitHub Pages
  (production URL: abax70.github.io/NCDPI-strategic-plan-site).
- **Verification is now FOUR tools**, all passing as of this wrapup:
  - `tools/verify-charts.py` — 8 pillars × 3 widths; cards, painted pixels,
    jump-strip contract, console clean.
  - `tools/verify-bin-chips.py` — 14 BiN measure-ID chips, tints, console.
  - `tools/verify-chart-scales.py` — reads live Chart.js scale objects and asserts
    axis invariants. `--self-test` runs without a browser.
  - `tools/verify-value-labels.py` — **new 8/3.** Asserts no two *drawn* value
    labels overlap, and that the first and last always survive the cull. Catches
    what the other three structurally cannot: **painted pixels prove nothing about
    whether the number is complete.** 108 charts across 4 widths. `--self-test`
    confirms all four invariants still fire.
  - **Each tool exists because a real bug slipped past the previous ones.** If a
    new bug class appears, the pattern is to add a fifth, not to widen one.
- **`tools/check-source-lines.py` — new 8/4, and deliberately NOT a fifth verify
  tool.** It was written to confirm a change, not to catch a regression that bit
  us, so it has not earned a place in the pre-push set. It checks all 10
  hand-authored `sourceHtml` lines across both data files: that each renders on
  its page, that its rendered anchor count matches the source data (catching
  mangled or escaped markup), and that each href responds. **PASS as of 8/4**, with
  the two known WARNs (P1.M8, P8.M2) described in queue item 4.
  - Worth knowing if you extend it: **`best-in-nation.html` is a carousel** — only
    one measure is in the DOM at a time, so a plain page-load scrape finds measure
    1 and silently "loses" the other 13. It looks exactly like a site bug and is
    not one. The tool drives the `.carousel-select` by array index instead.
  - It downgrades TLS-cert failures and 401/403 to WARN on purpose: inside this
    container neither is distinguishable from real breakage, and a tool that cries
    wolf gets ignored.
- **`tools/update-stamp.py` owns the "Last updated" date.** `build-pillar-data.py`
  now *preserves* the field rather than stamping `TODAY`. Run `update-stamp.py`
  after any data wave; `--check` exits 1 if content moved without a bump (good
  pre-push hook); `--force` for structural changes a fingerprint cannot detect.
  Baseline lives in tracked `data/stamp-state.json`.
- **Smartsheet live pull works from the container** — `data/.smartsheet-token`
  exists and `build-pillar-data.py` refreshes `data/action-statuses.csv`
  automatically. The CSV's 4th column is a pull date, so *every* row shows as
  changed in `git diff` even when no status moved; compare column 2 to see real
  churn.
- `data/DIM_Measures.csv` **has ragged rows** — a Sheets export artifact where some
  rows carry 28 trailing empty fields and others 6. Edit it with line-level surgery,
  **not** a `csv` round-trip, or the whole file reformats.
- **`data/build-measures.py` treats DIM `MeasureName` as canonical for BiN
  measures.** Before renaming any DIM row, check its `BestInNationGoal` flag; if it
  is set, the rename changes the Best-in-Nation page too.
- **`sourceHtml` is a PRESERVE field in both build scripts** and both renderers
  prefer it — it is the correct place for any hand-authored Source line. A
  `sourceLabel` edit gets overwritten by the next build.
  - **Corollary, learned the hard way 8/4: editing the Source cell in the sheet does
    NOT change the site.** Two independent reasons — the build preserves `sourceHtml`
    rather than regenerating it, *and* a multi-part or prose Source cell is refused
    by the parser anyway (it warns "needs hand review" and leaves the field null).
    Sheet edits are still worth making as the durable record, but the site only moves
    when `sourceHtml` is hand-edited in `data/pillar-measures.json`.
  - **There are 10 hand-authored source lines, not 4 or 8.** The 7/27 packet said 4;
    an earlier HANDOFF corrected it to 8. The true count is 7 in
    `data/pillar-measures.json` + 3 in `data/measures.json` (P1.M1, P1.M8, P8.M2).
    **P1.M8 and P8.M2 are BiN-only and have never been through a review pass** — see
    queue item 4.
  - As of 8/4, six of the ten carry live links, all verified 200 and confirmed to
    render as real anchors. P2.M3a's is labelled **"(PDF)"** because the URL is a
    direct 920 KB download. P5.M3 and P7.M2 carry no link by design.
- `data/measure-gaps.md` is generated every run and deliberately tracked. It never
  quotes raw sheet prose (public repo) — **the same rule governs anything written
  into `notes/`.** Its date stamp changes every run, so it always shows in
  `git status`; that is expected, not drift.
- **Chart engine parity rule still in force** for the SHARED engine: bug fixes land
  in BOTH `pillar.html` and `best-in-nation.html` until the post-8/5 extraction.
  The 8/3 label cull is the most recent example. Deliberate departures, commented
  in place: the jump strip (pillar only), the pillar measure-card header markup,
  and the BiN measure-ID chip.
- `pillar.html`'s deep-link param is **`?p=N`**, not `?pillar=N`.
- Tracked notes: `punchlist-20260720.md`, `meeting-agenda-20260724.md`,
  `meeting-agenda-20260803.md`, `sheet-edits-20260727.md`,
  `review-packet-20260727.md`, `measure-metric-text.tsv`,
  `geoff-open-questions.md`.
- **Stray file to relocate (not ours):**
  `images/HappyPeoplePhotos/reporting-process-guide.html` belongs in
  **EPP-Codebase** — Andy to move it from the host; unreachable from this container.

## Scratchpad harnesses NOT committed (recreate if needed)

**8/4:** nothing left in the scratchpad worth keeping — the session's one-shot
source-line checker was promoted to `tools/check-source-lines.py` rather than left
to vanish.

The one-shot scripts from 8/3 live only in the session scratchpad and will vanish:
`set_disagg_source.py` (applies the disaggregation `sourceHtml`, aborts if the row's
`sourceUrl` drifts from the URL baked into the hand-authored HTML), and the ad-hoc
screenshot/sweep helpers. The sweeps were **superseded** by
`tools/verify-value-labels.py` and should not be resurrected — they measured
*candidate* labels with a fallback formatter and undercounted the bug by ~13x.
