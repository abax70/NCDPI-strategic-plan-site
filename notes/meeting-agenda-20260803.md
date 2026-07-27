# Geoff check-in — Mon 8/3/2026

Geoff is out the week of 7/27, back 8/3. Board meeting is **8/5**, so this is
the last working session before the deck matters. Items below accumulated from
the 7/24 meeting and the 7/27 working session.

Ordered by "what breaks if we don't resolve it."

---

## 1. Decisions we improvised — need his yes/no

These are live on the site right now with a default we picked. None is wrong,
but none was his call.

| Item | What we did | Ask |
|---|---|---|
| **P4.M7 wording** | Description keeps the concrete "five or fewer acts" (from the sheet's "0–5 acts" cell), not the goal's vague "none to a limited number" | Keep, or soften? |
| **P5.M3 unit** | Description says "public school units"; source cell reads "16 PSUs (15 LEAs)" and the charted value is 15 | PSU or LEA? |
| **P2.M3b** | Gap resolved by his own re-lettering (P2.M3c → P2.M3b) | Confirm that was intentional |

## 2. P1.M17b — included, with a caveat he should see

Andy's call 7/27: **include it**, because the 0.0% baseline and the 0.0 targets
are *real measured values*, not placeholders — NC is at zero and the goal is to
stay there. (An earlier recommendation to exclude it was based on reading the
zeros as missing data. That was wrong.)

Consequences worth his eyes:

- The chart is now a **flat line at 0% across 2024–2030** on a 0–10% axis. That
  is truthful, but it is visually unusual next to every other measure. The 10%
  ceiling was chosen so the zero line reads as a real floor with room for the
  **Feb 2027** data to land inside it. **Does he want a different ceiling?**
- Its `currentDescription` **did not exist** and was drafted 2026-07-27. It has
  not been through the description review the other measures got on 7/23.
  Flagged as such in the metric-text table. Draft text:
  > Percentage of local education agencies with disproportionate representation
  > in Exceptional Children programs resulting from inappropriate identification
  > (2024–25)
- **Year label to confirm:** the source is SPP/APR **FFY 2024**, a federal
  fiscal year, but the draft uses the site's standard "(2024–25)" school-year
  suffix. Is that the right label for this measure?

## 3. P2.M4a — LEA vs PSU, and it is not just cosmetic

The title said **LEAs**; the approved description says **PSUs**. Andy retitled
to `PSUs Implementing Advanced Teaching Roles` on 7/27 to make the two agree.

**But retitling does not change what the sheet counts.** If the underlying
figure is a count of LEAs, the new title now misstates it. Needs his answer,
and it is the same family of question as P5.M3 above.

Note the contrast with P1.M17b, where **LEA is genuinely correct** — SPP/APR
Indicator 9 is a federal IDEA determination made at the LEA level. So the site
will legitimately use both words. Worth being deliberate about that.

## 4. Proposal: add a MeasureMetricTxt column to the sheet

The 14 Best-in-Nation measures already carry a short, precise "what is actually
counted" string. The 12 pillar measures do not. Andy's 7/27 title edits pushed
names toward being **more readable** (EC → Exceptional Child, PIOs → Public
Information Officer), which only holds up if the precise wording lives adjacent.

Paste-ready table for all 26 measures: `notes/measure-metric-text.tsv`
(tab-separated — pastes straight into Sheets and splits into columns). The
Origin column marks which rows are existing BiN text, which are derived from
Andy-approved descriptions, and which are fresh drafts.

## 5. Titles — final list (FYI, he invited these)

He asked for shorter titles; the answer came back mostly "clearer, not shorter."
Final edits in `notes/sheet-edits-20260727.md`. One genuine shortening
(P4.M7, 57 → 40 chars); the rest spell acronyms out.

## 6. Still waiting on other people

- **Shaun** — the four YRBS P4.M6 measures. Andy is CC'd; when confirmed he
  flips them to Y. Heads-up: P4.M6a's 2030 target cell is a literal `-%`
  (sheet typo) and the YRBS series are biennial ("-" in off years), so expect
  parser warnings the first wave they go live.
- **Curtis** — low-performing schools measure. Same flow.
- **P1.M5** — stays a **count** at least through 8/5; the SPAC percentage idea
  is parked with Sneha/Sam Beth.

## 7. Smaller things, only if there's time

- **P5.M2** is excluded from charting — NCSIS milestone measure, values are all
  1, not chartable in the two-chart format. He should know it is not on the site.
- **P2.M2b and P2.M3a show no status pill** — both regressed vs. the prior year,
  and the rule deliberately refuses to print "Approaching target" over a
  decline. Does he want hand-authored status text for either?
- **P1.M10's source is a bare URL** — needs a human-readable source label.
- **BiN Source cells** — he was adding "disaggregated results available at the
  source link" notes (Superintendent request). BiN rows are hand-curated and
  skipped by the pipeline, so those get imported by hand from the final export.
