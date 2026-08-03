---
purpose: Rolling list of open questions for Geoff — the thing to actually read
         off in a check-in, one line per ask. The detailed reasoning behind each
         lives in notes/meeting-agenda-20260803.md; this is the short form.
created: 2026-08-03
status: open — no check-in held 8/3; board meeting 8/5
---

# Open questions for Geoff

Short form. Backing detail in `meeting-agenda-20260803.md`.
Marked **[NEW 8/3]** where the question came out of the 8/3 working session.

---

## Answer before the 8/5 board meeting

1. **[NEW 8/3] 22 action cards now read "Planned for August, 2026" instead of
   "Launched August, 2026."** Their planned launch date passed but the tracker
   still says Not Started, so the old label was a false claim — the card shows
   the launch text *instead of* the status, so "Not Started" appeared nowhere.
   13 of the 22 are a single 2026-08-01 cohort. **Is "Planned for" the wording
   he wants on the board's screen Wednesday?**

2. **[NEW 8/3] Two actions regressed in Smartsheet since 7/15** — `P7.F3.A3`
   and `P8.F2.A1` moved In Progress → Not Started. P7.F3.A3 is notable because
   it flipped *forward* in the 7/15 refresh. **Deliberate reassessment, or a
   mis-click by a project lead?**

3. **P4.M7 wording** — description keeps the concrete "five or fewer acts"
   rather than the goal's "none to a limited number." Keep, or soften?

4. **P5.M3 unit** — description says "public school units"; the source cell
   reads "16 PSUs (15 LEAs)" and the charted value is 15. PSU or LEA?

5. **P2.M4a — LEA vs PSU, and not cosmetic.** Retitled to "PSUs Implementing
   Advanced Teaching Roles" so title and description agree, but retitling does
   not change what the sheet counts. If the figure counts LEAs, the title now
   misstates it. (Note LEA is *genuinely correct* for P1.M17b — federal IDEA
   determination is LEA-level. The site will legitimately use both words.)

## Confirmations — quick yes/no

6. **P2.M3b re-lettering** (P2.M3c → P2.M3b) was his own edit. Confirm intended.

7. **[NEW 8/3] Disaggregation note — we did not duplicate the link.** He asked
   for "For data disaggregated by student sub-groups, click here [dashboard
   link]" on Cohort Graduation Rate and EOG/EOC Proficiency. Both Source lines
   *already* link that exact dashboard, so a literal reading puts the same URL
   on screen twice. Now renders as:
   > Source: **NCDPI Proficiency dashboard** (includes results disaggregated by student subgroups)
   **OK?** Also: we used "subgroups" (one word, ESSA standard); he wrote
   "sub-groups."

8. **P1.M17b year label** — source is SPP/APR **FFY 2024**, a federal fiscal
   year, but the site's standard suffix "(2024–25)" is used. Right label here?

9. **P1.M17b chart ceiling** — flat line at 0% on a 0–10% axis. Truthful but
   visually unusual; 10% leaves room for the Feb 2027 data. Different ceiling?

## Proposals awaiting his decision

10. **MeasureMetricTxt column for the sheet.** The 14 BiN measures carry a
    precise "what is actually counted" string; the pillar measures do not.
    Paste-ready table for all 28 measures at `notes/measure-metric-text.tsv`.
    _(Andy's description review is still in progress as of 8/3 — five rows are
    still labeled unreviewed drafts in that table.)_

11. **The `Notes on Recommended Changes` worksheet.** The export has a second
    tab the pipeline never reads. It holds one row — P1.M5, with the "increase
    the **percentage number** of…" text — while the main sheet's P1.M5 goal is
    clean. So it is a *recommended change* parked in a side tab, matching the
    SPAC percentage idea, not a mid-edit typo. **Does he intend that tab as a
    change channel?** If so the pipeline should read it.

12. **`MeasureContextNote` and `WhyMeasureMatters`** are new columns in the
    export and are **empty in every row**. What does he want in them?

## Smaller, only if there's time

13. **P5.M2** is excluded from charting (NCSIS milestone, all values are 1). He
    should know it is not on the site.

14. **P2.M2b and P2.M3a show no status pill** — both regressed vs. prior year
    and the rule refuses to print "Approaching target" over a decline.
    Hand-authored status text for either?

15. **P1.M5** stays a **count** through at least 8/5; the SPAC percentage idea
    is parked with Sneha/Sam Beth.

## Waiting on other people (FYI, not asks)

- **Shaun** — the four YRBS `P4.M6` measures; Andy flips them to Y on confirm.
  Expect parser warnings: P4.M6a's 2030 target cell is a literal `-%` and the
  YRBS series are biennial ("-" in off years).
- **Curtis** — low-performing schools measure, same flow.

---

## Resolved 8/3 — no longer needs asking

- ~~BiN Source disaggregation notes~~ — wording received from Andy's email and
  applied to P1.M1 and P1.M10. Confirm the phrasing only (item 7 above).
  _Correction to the old agenda: these were never going to come "from the final
  export" — the export contains zero occurrences of "disaggregat."_
- ~~P1.M10's source is a bare URL~~ — hand-authored `sourceLabel` already in
  place, and now carries the disaggregation note.
