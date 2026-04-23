"""
build-measures.py — Merge CSV sources into data/measures.json (merge mode)
============================================================================
Reads:
  - data/measures.json                        (merge base; hand-authored fields preserved)
  - data/LandingPage_MeasureMenu.csv          (AUTHORITATIVE list of landing-page measures + labels/tooltips)
  - data/LandingPage_MeasureDetailsText.csv   (goal, definition, sources, etc.)
  - data/LandingPage_MeasureResults.csv       (time-series data)
  - data/DIM_Measures.csv                     (lookup only: BestInNationGoal flag + MeasureName fallback)
  - data/DIM_Pillars.csv                      (pillar names)

NOTE: DIM_Measures.csv contains all 49 strategic plan measures, but only the
landing-page subset (14 as of 2026-04) appears in measures.json. The menu CSV
is the authoritative source for WHICH measures appear on the landing page;
DIM_Measures is a lookup only.

Produces:
  - data/measures.json                        (regenerated in place; hand-authored fields preserved)

Usage:
  python data/build-measures.py

Why this exists:
  Before today, measures.json was hand-edited and drifted from its CSV sources.
  This script refreshes the fields that have CSV sources on every run and
  PRESERVES the hand-authored fields that don't (iconUrl, whyItCounts,
  badgeImageUrl, badgeAltText, statusType, statusLabel, moreDataText, notes).
  New measures added to DIM_Measures.csv are written with null hand-authored
  fields so /check-data flags them for editorial. Measures removed from
  DIM_Measures.csv are dropped with a warning.

  History: `whatsInMotion` used to be a hand-authored per-measure list of
  linked Strategic Plan actions, rendered in the right sidebar of the landing
  page. That mapping was retired on 2026-04-20 — leadership objected to the
  measure->action linkage. The sidebar now shows a global "recently launched
  actions" ticker sourced directly from pillar-data.json, so the field has
  been dropped from both the schema and this build script.

Author: Andy Baxter / Claude  |  2026-04-14
"""

import csv
import json
import os
import re
import sys

# Windows console encoding — needed for em-dash / en-dash / curly quote output.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, Exception):
    pass


# --- Configuration --------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

MEASURES_JSON = os.path.join(SCRIPT_DIR, "measures.json")
DIM_MEASURES = os.path.join(SCRIPT_DIR, "DIM_Measures.csv")
DIM_PILLARS = os.path.join(SCRIPT_DIR, "DIM_Pillars.csv")
MENU_CSV = os.path.join(SCRIPT_DIR, "LandingPage_MeasureMenu.csv")
DETAILS_CSV = os.path.join(SCRIPT_DIR, "LandingPage_MeasureDetailsText.csv")
RESULTS_CSV = os.path.join(SCRIPT_DIR, "LandingPage_MeasureResults.csv")

# Fields that are NEVER overwritten from CSV — hand-authored content only.
# Listed here for documentation; the build_measure() fn references existing JSON directly.
PRESERVE_FIELDS = (
    "iconUrl",
    "whyItCounts",
    "badgeImageUrl",
    "badgeAltText",
    "statusType",     # preserved for existing measures; placeholder written for NEW measures
    "statusLabel",
    "moreDataText",
    "notes",
    "sourceHtml",     # optional narrative HTML with inline hyperlinks (used when a
                      # measure cites multiple distinct sources — the CSV only has
                      # one URL column, so this field is hand-authored in measures.json)
)


# --- Helpers (duplicated from build-pillar-data.py; hyphen blocks import) --

def clean_text(text):
    """Strip formula artifacts (IFERROR, etc.) and collapse embedded whitespace."""
    if not text or not isinstance(text, str):
        return ""
    if text.startswith("="):
        return ""
    text = re.sub(r"=IFERROR\([^)]*\)", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def slugify(name):
    """Lowercase, punctuation→hyphens, used for the `id` slug."""
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def _to_float(raw):
    """Parse a CSV cell as float; return None for blank, formula, or unparseable."""
    if raw is None:
        return None
    s = str(raw).strip()
    if not s or s.startswith("="):
        return None
    try:
        return float(s)
    except ValueError:
        return None


# --- Readers -------------------------------------------------------------

def load_existing_measures():
    """Load measures.json into a dict keyed by measureId. Tolerates missing/invalid file."""
    if not os.path.exists(MEASURES_JSON):
        print(f"  Note: {MEASURES_JSON} doesn't exist yet; starting fresh.")
        return {}
    try:
        with open(MEASURES_JSON, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"  WARN: could not parse {MEASURES_JSON}: {e}. Starting fresh.")
        return {}
    out = {}
    for m in data:
        mid = m.get("measureId")
        if mid:
            out[mid] = m
    return out


def read_pillars():
    """Return {PillarID: PillarName}."""
    pillars = {}
    with open(DIM_PILLARS, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = (row.get("PillarID") or "").strip()
            if not pid or not re.match(r"^P\d+$", pid):
                continue
            name = clean_text(row.get("PillarName") or "")
            if name:
                pillars[pid] = name
    return pillars


def read_dim_measures():
    """Return {MeasureID: {name, bestInNation, goalFallback}} from DIM_Measures.csv.

    Lookup only — not the authoritative list (which is LandingPage_MeasureMenu.csv).
    """
    measures = {}
    with open(DIM_MEASURES, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mid = (row.get("MeasureID") or "").strip()
            if not mid or not re.match(r"^P\d+\.M\d+$", mid):
                continue
            name = clean_text(row.get("MeasureName") or "")
            bin_raw = (row.get("BestInNationGoal") or "").strip()
            measures[mid] = {
                "name": name,
                "goalFallback": clean_text(row.get("MeasureGoal") or ""),
                "bestInNation": bool(bin_raw and _to_float(bin_raw)),
            }
    return measures


def read_menu():
    """Return ordered list of landing-page measures from LandingPage_MeasureMenu.csv.

    This is the AUTHORITATIVE list of which measures appear on the dashboard.
    Menu CSV order (by MeasureMenuKey) determines measures.json output order.

    NOTE: the CSV header for the ID column is literally 'Measure ID' with a space.
    """
    menu = []
    with open(MENU_CSV, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mid = (row.get("Measure ID") or "").strip()
            if not mid or not re.match(r"^P\d+\.M\d+$", mid):
                continue
            try:
                key = float(row.get("MeasureMenuKey") or 999)
            except ValueError:
                key = 999
            menu.append({
                "measureId": mid,
                "menuKey": key,
                "menuLabel": clean_text(row.get("MeasureMenu") or ""),
                "menuSubLabel": clean_text(row.get("MeasureSubMenu") or "") or None,
                "menuTooltip": clean_text(row.get("MeasureMenuTooltip") or ""),
            })
    menu.sort(key=lambda m: m["menuKey"])
    return menu


def read_details():
    """Return {MeasureID: {goal, definition, metricText, nextUpdate, sourceLabel,
    sourceUrl, moreDataUrl, badgePressReleaseUrl}}."""
    details = {}
    with open(DETAILS_CSV, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mid = (row.get("MeasureID") or "").strip()
            if not mid:
                continue
            details[mid] = {
                "goal": clean_text(row.get("MeasureGoal") or ""),
                "metricText": clean_text(row.get("MeasureMetricTxt") or ""),
                "definition": clean_text(row.get("NoteMeasureDefinition") or ""),
                "nextUpdate": clean_text(row.get("NoteNextUpdateText") or ""),
                "sourceLabel": clean_text(row.get("NoteDataSourceText") or ""),
                "sourceUrl": clean_text(row.get("NoteDataSourceURL") or ""),
                "moreDataUrl": (clean_text(row.get("CallOutMoreDataURL") or "") or None),
                # Optional per-measure press-release link. Only the 4 "record-high"
                # measures have one (graduation rate, AP participation, AP
                # performance, CTE credentials); blank for everything else. The
                # landing-page render wraps the shield badge in an anchor to this
                # URL when populated — see index.html `.record-badge` render block.
                "badgePressReleaseUrl": (clean_text(row.get("BadgePressReleaseUrl") or "") or None),
            }
    return details


def read_results():
    """Return {MeasureID: {yearRows: [{year, actual, target}], valueFormat, yAxisMax}}.

    Skips rows where both ActualValue and TargetValue are blank (filler).
    yAxisMax / valueFormat are captured from the first non-blank, non-formula cell per measure.
    """
    results = {}
    with open(RESULTS_CSV, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mid = (row.get("MeasureID") or "").strip()
            if not mid:
                continue
            entry = results.setdefault(
                mid, {"yearRows": [], "valueFormat": None, "yAxisMax": None}
            )

            # Year: stored as 2024.0 etc. in the source file.
            year_raw = (row.get("Year") or "").strip()
            try:
                year_int = int(float(year_raw))
            except (ValueError, TypeError):
                continue

            actual = _to_float(row.get("ActualValue"))
            target = _to_float(row.get("TargetValue"))

            # Keep rows even when both actual and target are blank: the Year row
            # itself is metadata that signals "this year is part of the series".
            # Chart rendering depends on consistent year spacing, so dropping
            # empty years would shift the x-axis visually.
            entry["yearRows"].append({
                "year": str(year_int),
                "actual": actual,
                "target": target,
            })

            # valueFormat: first non-empty, non-formula cell wins.
            if entry["valueFormat"] is None:
                vf = (row.get("ValueFormat") or "").strip()
                if vf and not vf.startswith("="):
                    entry["valueFormat"] = vf

            # yAxisMax: first numeric cell wins (rows with formulas skipped).
            if entry["yAxisMax"] is None:
                ym_val = _to_float(row.get("Y-axis max"))
                if ym_val is not None:
                    entry["yAxisMax"] = ym_val

    # Sort year rows ascending by year.
    for entry in results.values():
        entry["yearRows"].sort(key=lambda r: int(r["year"]))

    return results


# --- Transformers --------------------------------------------------------

def build_data_series(year_rows):
    """Convert CSV year rows to measures.json dataSeries format.

    Convention (matches existing measures.json for all 14 current measures):
      - ActualValue in the source CSV maps to `baseline` in the JSON.
      - TargetValue maps to `target`.
      - `actual` is reserved for future post-baseline tracking; null for now.
    """
    return [
        {
            "year": r["year"],
            "baseline": r["actual"],
            "target": r["target"],
            "actual": None,
        }
        for r in year_rows
    ]


def format_current_value(value, value_format):
    """Format a numeric value per its valueFormat string."""
    if value is None:
        return None
    if value_format == "#.#%":
        return f"{value:.1f}%"
    if value_format == "#.#":
        return f"{value:.1f}"
    if value_format == "#":
        return f"{int(round(value))}"
    if value_format == "#,###":
        return f"{int(round(value)):,}"
    # Unknown format — fall back to a safe representation and warn.
    print(f"  WARN: unknown valueFormat '{value_format}'; using str() fallback.")
    return f"{value:g}"


def derive_current(data_series, metric_text, value_format, existing):
    """Derive currentValue and currentDescription from the freshly built dataSeries.

    Idempotency: if the derived value equals the existing currentValue, preserve
    both value and description (don't churn on hand-polished description wording).
    Otherwise regenerate the value and build a default description with a
    school-year back-shift (e.g., Year=2025 → '(2024–25)').
    """
    current_year = None
    current_num = None
    for entry in reversed(data_series):
        if entry["actual"] is not None:
            current_year = entry["year"]
            current_num = entry["actual"]
            break
        if entry["baseline"] is not None:
            current_year = entry["year"]
            current_num = entry["baseline"]
            break

    if current_num is None:
        return existing.get("currentValue"), existing.get("currentDescription")

    new_value = format_current_value(current_num, value_format)

    # Idempotency preserve: if value unchanged and we have an existing description, keep it.
    if new_value == existing.get("currentValue") and existing.get("currentDescription"):
        return existing["currentValue"], existing["currentDescription"]

    # Default description: '{metricText} (YYYY–YY)' with en-dash (U+2013), school-year back-shift.
    try:
        y = int(current_year)
        year_range = f"({y - 1}\u2013{str(y)[-2:]})"
    except ValueError:
        year_range = f"({current_year})"

    new_desc = (
        f"{metric_text} {year_range}".strip()
        if metric_text
        else existing.get("currentDescription")
    )
    return new_value, new_desc


def build_measure(menu_entry, pillars, dim_lookup, details, results, existing_map):
    """Build one measure dict, merging CSV sources with preserved fields."""
    mid = menu_entry["measureId"]
    existing = existing_map.get(mid, {})
    is_new = mid not in existing_map

    # pillarId is derived from MeasureID prefix (P1.M1 → P1).
    pillar_id = mid.split(".")[0]
    try:
        pillar_num = int(pillar_id[1:])
    except (ValueError, IndexError):
        pillar_num = None
    pillar_name = pillars.get(pillar_id, existing.get("pillarName", ""))

    # Name: DIM_Measures is the canonical source. Fall back to existing JSON.
    dim_entry = dim_lookup.get(mid, {})
    name = dim_entry.get("name") or existing.get("name") or mid

    details_entry = details.get(mid, {})
    results_entry = results.get(mid, {"yearRows": [], "valueFormat": None, "yAxisMax": None})

    data_series = build_data_series(results_entry["yearRows"])

    # valueFormat / yAxisMax: prefer CSV; fall back to existing JSON; else None.
    value_format = results_entry["valueFormat"] or existing.get("valueFormat")
    y_axis_max = (
        results_entry["yAxisMax"]
        if results_entry["yAxisMax"] is not None
        else existing.get("yAxisMax")
    )

    metric_text_resolved = (
        details_entry.get("metricText") or existing.get("metricText", "")
    )
    current_value, current_desc = derive_current(
        data_series, metric_text_resolved, value_format, existing
    )

    # Preserve-on-blank helper: refresh from CSV when present, else keep existing value.
    def refresh(csv_value, existing_value):
        return csv_value if csv_value else existing_value

    # Status type: preserve for existing measures; for new measures, place a
    # BIN placeholder if DIM flag is set so the editor knows to curate it.
    if is_new:
        status_type = "best-in-nation" if dim_entry.get("bestInNation") else None
    else:
        status_type = existing.get("statusType")

    measure = {
        "id": slugify(name),
        "measureId": mid,
        "name": name,
        "pillarNumber": pillar_num,
        "pillarName": pillar_name,
        "menuLabel": refresh(menu_entry.get("menuLabel"), existing.get("menuLabel")),
        "menuSubLabel": menu_entry.get("menuSubLabel") if menu_entry.get("menuSubLabel") is not None else existing.get("menuSubLabel"),
        "menuTooltip": refresh(menu_entry.get("menuTooltip"), existing.get("menuTooltip", "")),
        "iconUrl": existing.get("iconUrl"),  # PRESERVE
        "goal": (
            details_entry.get("goal")
            or existing.get("goal")
            or dim_entry.get("goalFallback", "")
        ),
        "definition": refresh(details_entry.get("definition"), existing.get("definition", "")),
        "metricText": refresh(details_entry.get("metricText"), existing.get("metricText", "")),
        "valueFormat": value_format,
        "yAxisMax": y_axis_max,
        "sourceLabel": refresh(details_entry.get("sourceLabel"), existing.get("sourceLabel", "")),
        "sourceUrl": refresh(details_entry.get("sourceUrl"), existing.get("sourceUrl", "")),
        "sourceHtml": existing.get("sourceHtml"),  # PRESERVE
        "moreDataUrl": (
            details_entry["moreDataUrl"]
            if ("moreDataUrl" in details_entry and details_entry["moreDataUrl"])
            else existing.get("moreDataUrl")
        ),
        "moreDataText": existing.get("moreDataText"),  # PRESERVE
        "badgeImageUrl": existing.get("badgeImageUrl"),  # PRESERVE
        "badgeAltText": existing.get("badgeAltText"),  # PRESERVE
        # Refresh from CSV if the BadgePressReleaseUrl column has a value;
        # otherwise preserve whatever is already in the JSON. Mirrors moreDataUrl.
        "badgePressReleaseUrl": (
            details_entry["badgePressReleaseUrl"]
            if ("badgePressReleaseUrl" in details_entry and details_entry["badgePressReleaseUrl"])
            else existing.get("badgePressReleaseUrl")
        ),
        "statusType": status_type,
        "statusLabel": existing.get("statusLabel"),  # PRESERVE
        "currentValue": current_value,
        "currentDescription": current_desc,
        "whyItCounts": existing.get("whyItCounts"),  # PRESERVE
        "nextUpdate": refresh(details_entry.get("nextUpdate"), existing.get("nextUpdate", "")),
        "notes": existing.get("notes"),  # PRESERVE
        "dataSeries": data_series,
    }
    return measure, is_new


# --- Main ----------------------------------------------------------------

def main():
    print(f"Reading sources from {SCRIPT_DIR}")

    existing_map = load_existing_measures()
    pillars = read_pillars()
    dim_lookup = read_dim_measures()
    menu_list = read_menu()
    details = read_details()
    results = read_results()

    total_year_rows = sum(len(r["yearRows"]) for r in results.values())
    print(f"  - measures.json: {len(existing_map)} existing measures loaded")
    print(f"  - DIM_Pillars.csv: {len(pillars)} pillars")
    print(f"  - DIM_Measures.csv: {len(dim_lookup)} measures (lookup only)")
    print(f"  - LandingPage_MeasureMenu.csv: {len(menu_list)} measures (AUTHORITATIVE)")
    print(f"  - LandingPage_MeasureDetailsText.csv: {len(details)} details entries")
    print(f"  - LandingPage_MeasureResults.csv: {total_year_rows} year rows across {len(results)} measures")

    # LandingPage_MeasureMenu.csv is authoritative for landing-page measures.
    # Menu CSV order (by MeasureMenuKey) is already preserved by read_menu().
    menu_ids = {m["measureId"] for m in menu_list}

    out_measures = []
    refreshed = 0
    new_count = 0
    new_ids = []

    for menu_entry in menu_list:
        measure, is_new = build_measure(
            menu_entry, pillars, dim_lookup, details, results, existing_map
        )
        out_measures.append(measure)
        if is_new:
            new_count += 1
            new_ids.append(menu_entry["measureId"])
        else:
            refreshed += 1

    # Measures present in JSON but missing from Menu CSV → dropped with warning.
    dropped = [mid for mid in existing_map if mid not in menu_ids]
    for mid in dropped:
        print(f"  WARN: {mid} exists in measures.json but not in LandingPage_MeasureMenu.csv — DROPPED")
    for mid in new_ids:
        print(f"  NEW: {mid} added from LandingPage_MeasureMenu.csv — hand-authored fields null; flag for editorial.")

    # Write output. ensure_ascii=False preserves em-dash / curly quotes in prose.
    with open(MEASURES_JSON, "w", encoding="utf-8") as f:
        json.dump(out_measures, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"\n  Output: {MEASURES_JSON}")
    print(
        f"  {len(out_measures)} measures written · "
        f"{refreshed} refreshed · {new_count} new · {len(dropped)} dropped"
    )
    print("  Done!")


if __name__ == "__main__":
    main()
