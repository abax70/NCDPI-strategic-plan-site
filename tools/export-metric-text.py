"""
export-metric-text.py — build a paste-ready MeasureMetricTxt table for Geoff's sheet
====================================================================================
Reads:
  - data/measures.json          (Best in Nation, hand-curated — has metricText already)
  - data/pillar-measures.json   (pillar measures, pipeline-generated — metricText is
                                 empty on every row as of 2026-07-27)

Writes:
  - notes/measure-metric-text.tsv   (tab-separated; paste straight into Google Sheets
                                     and it splits into columns)

Why this exists (2026-07-27):
  Geoff's measures sheet has no MeasureMetricTxt column. We're proposing shorter,
  topical MeasureNames, which only works if the precise "what is actually counted"
  text lives somewhere adjacent. The 14 Best-in-Nation measures already follow that
  pattern; the 12 pillar measures don't. This script assembles both sides into one
  table Andy can paste in.

Where the pillar text comes from — IMPORTANT:
  The pillar measures have no metricText. They DO have currentDescription, which on
  the BiN side is provably just metricText + " (year)":
      metricText         = "Percentage of 9th-graders graduating ... four years later"
      currentDescription = "Percentage of 9th-graders graduating ... four years later (2024-25)"
  So pillar metric text is derived by stripping the trailing year parenthetical off
  currentDescription. That text was drafted 2026-07-22 and reviewed + approved by
  Andy on 2026-07-23, so it is not fresh invention — it has been through a review.
  The Origin column records this per row so Geoff can see which is which.

Quirk guarded against:
  Only a trailing parenthetical CONTAINING A DIGIT is stripped. Some BiN metric text
  legitimately ends in a non-year parenthetical (e.g. "... national assessment (NAEP)"),
  and a blind strip would eat it. Pillar rows currently end in "(2024-25)" or
  "(as of 2025)"; both match, "(NAEP)" does not.

Usage:
  python tools/export-metric-text.py

Author: Andy Baxter / Claude  |  2026-07-27
"""

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BIN_JSON = REPO / "data" / "measures.json"
PILLAR_JSON = REPO / "data" / "pillar-measures.json"
OUT_TSV = REPO / "notes" / "measure-metric-text.tsv"

# Trailing "(...)" only when it contains a digit — see the quirk note above.
YEAR_PAREN = re.compile(r"\s*\([^)]*\d[^)]*\)\s*$")


def strip_year(text):
    """'Percentage of X (2024-25)' -> 'Percentage of X'. Leaves '(NAEP)' alone."""
    return YEAR_PAREN.sub("", text).strip()


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    rows = []
    gaps = []

    # --- Best in Nation: metricText already authored, use verbatim ---------------
    for m in load(BIN_JSON):
        metric = (m.get("metricText") or "").strip()
        if metric:
            origin = "BiN - existing MeasureMetricTxt"
        else:
            # Fall back the same way the pillar side works, so a BiN row that ever
            # loses its metricText still produces something rather than a blank.
            metric = strip_year(m.get("currentDescription") or "")
            origin = "BiN - derived from currentDescription"
            if not metric:
                gaps.append((m["measureId"], m.get("name"), "no metricText, no currentDescription"))
                origin = "BiN - NEEDS DRAFTING"
        rows.append((m["measureId"], m.get("name") or "", metric, origin))

    # --- Pillar measures: derive from the approved currentDescription ------------
    # The blanket "approved (Andy 7/23)" label is only true for descriptions that
    # were actually in that review. Anything drafted afterwards must say so — this
    # table goes to Geoff, and mislabelling fresh Claude prose as Andy-approved
    # would launder an unreviewed draft into the sheet. Add the measure ID here
    # when you draft a new description; remove it once Andy signs off.
    # Any measure whose description was drafted AFTER Andy's 2026-07-23 review round.
    # Without an entry here a fresh draft is labeled "approved (Andy 7/23)" in a table
    # that goes to Geoff -- i.e. unreviewed prose laundered as Andy-signed-off.
    # Add on drafting; REMOVE once Andy signs off.
    DRAFTED_SINCE_REVIEW = {
        # Staged in the 7/24 data wave, still unreviewed as of 2026-07-27.
        "P2.M3a": "Pillar - DRAFTED 2026-07-24, pending Andy review",
        "P2.M4b": "Pillar - DRAFTED 2026-07-24, pending Andy review",
        # Drafted 2026-07-27.
        "P1.M17b": "Pillar - DRAFTED 2026-07-27, pending Andy review",
        # New in the 7/27 export (Pillar 6 went live this wave).
        "P6.M1a": "Pillar - DRAFTED 2026-07-27, pending Andy review",
        "P6.M1b": "Pillar - DRAFTED 2026-07-27, pending Andy review",
    }
    for m in load(PILLAR_JSON):
        metric = strip_year(m.get("currentDescription") or "")
        if metric:
            origin = DRAFTED_SINCE_REVIEW.get(
                m["measureId"], "Pillar - from approved description (Andy 7/23)")
        else:
            gaps.append((m["measureId"], m.get("name"), "no currentDescription to derive from"))
            metric = ""
            origin = "Pillar - NEEDS DRAFTING"
        rows.append((m["measureId"], m.get("name") or "", metric, origin))

    # Sort by pillar number then measure number then any letter suffix, so the table
    # reads in the same order as the sheet rather than BiN-then-pillar.
    def sort_key(row):
        mo = re.match(r"P(\d+)\.M(\d+)([a-z]*)", row[0])
        return (int(mo.group(1)), int(mo.group(2)), mo.group(3)) if mo else (99, 99, row[0])

    rows.sort(key=sort_key)

    OUT_TSV.parent.mkdir(exist_ok=True)
    with open(OUT_TSV, "w", encoding="utf-8", newline="") as fh:
        fh.write("MeasureID\tMeasureName\tMeasureMetricTxt\tOrigin\n")
        for r in rows:
            # Tabs/newlines inside a cell would break the paste; neither appears
            # today, but collapse defensively rather than silently corrupt columns.
            fh.write("\t".join(str(c).replace("\t", " ").replace("\n", " ") for c in r) + "\n")

    print("Wrote %s (%d measures)" % (OUT_TSV.relative_to(REPO), len(rows)))
    if gaps:
        print("\nNEEDS DRAFTING (%d):" % len(gaps))
        for mid, name, why in gaps:
            print("  %-8s %-45s %s" % (mid, (name or "")[:45], why))
    else:
        print("No gaps: every measure has metric text.")


if __name__ == "__main__":
    main()
