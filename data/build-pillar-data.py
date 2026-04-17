"""
build-pillar-data.py — Combine CSVs + XLSX into pillar-data.json
=================================================================
Reads:
  - DIM_Pillars.csv        (8 pillars with descriptions)
  - DIM_FocusAreas.csv     (26 focus areas, each mapped to a pillar)
  - DIM_Actions.csv        (109 actions, each mapped to a focus area)
  - blog_focus_area_matches_final.csv  (94 blog-to-focus-area links)
  - Strategic Plan Actions Tracker.xlsx (action statuses)

Produces:
  - pillar-data.json       (single nested JSON for the pillar dashboard)

Usage:
  python data/build-pillar-data.py

Why this exists:
  The pillar dashboard (pillar.html) needs a single JSON file to enable
  instant pillar switching without separate fetches. This script handles
  all the data cleaning (formula artifacts, trailing empty rows, embedded
  newlines) so the HTML page gets clean data.

Author: Andy Baxter / Claude  |  2026-04-09
"""

import csv
import json
import os
import re
from datetime import datetime, date

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PILLARS_CSV = os.path.join(SCRIPT_DIR, "DIM_Pillars.csv")
FOCUS_AREAS_CSV = os.path.join(SCRIPT_DIR, "DIM_FocusAreas.csv")
ACTIONS_CSV = os.path.join(SCRIPT_DIR, "DIM_Actions.csv")
BLOGS_CSV = os.path.join(SCRIPT_DIR, "blog_focus_area_matches_final.csv")
TRACKER_XLSX = os.path.join(SCRIPT_DIR, "Strategic Plan Actions Tracker.xlsx")
OUTPUT_JSON = os.path.join(SCRIPT_DIR, "pillar-data.json")

# Today's date for determining hasStarted
TODAY = date.today()


def clean_text(text):
    """
    Remove formula artifacts (IFERROR, COMPUTED_VALUE, DUMMYFUNCTION, etc.)
    and collapse embedded newlines into spaces.
    """
    if not text or not isinstance(text, str):
        return ""
    # If the entire value is a formula reference, return empty
    if text.startswith("="):
        return ""
    # Strip formula wrapper artifacts that sometimes leak from Google Sheets CSV export
    text = re.sub(r'=IFERROR\([^)]*\)', '', text)
    # Collapse embedded newlines and extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_date(date_str):
    """
    Parse date strings from the CSV. Expected formats:
      - "2026-01-01 00:00:00"
      - "2026-01-01"
      - "January, 2026"  (from ActionLaunchText)
    Returns a date object or None.
    """
    if not date_str or not isinstance(date_str, str):
        return None
    date_str = date_str.strip()
    # Try ISO format with time
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


def format_launch_text(launch_date):
    """
    Given a date, produce 'Launches in January, 2026' style text.
    If the date is in the past, return 'Launched [Month, Year]'.
    """
    if not launch_date:
        return ""
    month_year = launch_date.strftime("%B, %Y")
    if launch_date <= TODAY:
        return f"Launched {month_year}"
    return f"Launches in {month_year}"


def read_pillars():
    """
    Read DIM_Pillars.csv → dict keyed by PillarID.
    Only the first 8 data rows are real; the rest are trailing empties.
    Uses the 7th column (index 6, header 'PillarDesc') which contains the
    full description text with embedded newlines.
    """
    pillars = {}
    with open(PILLARS_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)

        # Read rows, accumulating multi-line description fields.
        # The CSV has embedded newlines in the PillarDesc column, so a single
        # logical row can span multiple physical lines. We detect logical row
        # boundaries by checking for a PillarID pattern (P1, P2, ...).
        current_row = None
        for raw_row in reader:
            # Skip fully empty rows
            if not any(cell.strip() for cell in raw_row):
                if current_row:
                    # Flush the last accumulated row
                    _process_pillar_row(pillars, current_row)
                    current_row = None
                continue

            # Check if this is a new logical row (starts with PillarID like "P1")
            if raw_row[0].strip() and re.match(r'^P\d+$', raw_row[0].strip()):
                if current_row:
                    _process_pillar_row(pillars, current_row)
                current_row = list(raw_row)
            elif current_row:
                # Continuation line — append to the description fields
                for i in range(len(raw_row)):
                    if i < len(current_row):
                        current_row[i] = current_row[i] + "\n" + raw_row[i]
                    else:
                        current_row.append(raw_row[i])

        # Flush final row
        if current_row:
            _process_pillar_row(pillars, current_row)

    return pillars


def _process_pillar_row(pillars, row):
    """Process one logical pillar row into the pillars dict."""
    pillar_id = row[0].strip()
    if not re.match(r'^P\d+$', pillar_id):
        return

    # PillarNum may be "1.0" — convert to int
    try:
        pillar_num = int(float(row[1].strip()))
    except (ValueError, IndexError):
        return

    pillar_name = row[2].strip()
    title_line1 = row[3].strip() if len(row) > 3 else ""
    title_line2 = row[4].strip() if len(row) > 4 else ""
    pillar_url = row[5].strip() if len(row) > 5 else ""

    # PillarDesc is column index 6. Clean up embedded newlines.
    raw_desc = row[6] if len(row) > 6 else ""
    # Collapse embedded newlines and extra whitespace
    pillar_desc = re.sub(r'\s+', ' ', raw_desc).strip()

    pillars[pillar_id] = {
        "pillarId": pillar_id,
        "pillarNum": pillar_num,
        "pillarName": pillar_name,
        "titleLine1": title_line1,
        "titleLine2": title_line2,
        "pillarUrl": pillar_url,
        "pillarDesc": pillar_desc,
        "focusAreas": []  # populated later
    }


def read_focus_areas():
    """
    Read DIM_FocusAreas.csv → dict keyed by FocusAreaID.
    FocusAreaNum column has Excel formulas — extract the number from the ID instead.
    """
    focus_areas = {}
    with open(FOCUS_AREAS_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fa_id = row["FocusAreaID"].strip()
            if not fa_id or not re.match(r'^P\d+\.F\d+$', fa_id):
                continue
            pillar_id = row["PillarID"].strip()
            fa_name = row["FocusAreaName"].strip()
            # Extract the focus area number from the ID (e.g., "P1.F3" → 3)
            fa_num = int(fa_id.split(".F")[1])
            focus_areas[fa_id] = {
                "focusAreaId": fa_id,
                "focusAreaNum": fa_num,
                "focusAreaName": fa_name,
                "pillarId": pillar_id,
                "actions": [],   # populated later
                "stories": []    # populated later
            }
    return focus_areas


def read_actions():
    """
    Read DIM_Actions.csv → list of action dicts.
    Uses only clean columns: PillarID, FocusAreaID, ActionID, ActionName,
    ActionDesc (col F — the raw text, not the formula-wrapped variants),
    ActionLaunchDate.
    """
    actions = []
    with open(ACTIONS_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)

        # Find column indices by header name
        col_map = {h.strip(): i for i, h in enumerate(header)}

        for raw_row in reader:
            # Skip empty rows
            if not any(cell.strip() for cell in raw_row):
                continue

            pillar_id = raw_row[col_map.get("PillarID", 0)].strip()
            if not pillar_id or not pillar_id.startswith("P"):
                continue

            action_id = raw_row[col_map.get("ActionID", 3)].strip()
            action_name = raw_row[col_map.get("ActionName", 4)].strip()
            action_desc = clean_text(raw_row[col_map.get("ActionDesc", 5)])

            # FocusAreaID may be a formula — derive from ActionID instead
            # e.g., "P1.F1.A1" → "P1.F1"
            parts = action_id.split(".")
            if len(parts) >= 2:
                focus_area_id = f"{parts[0]}.{parts[1]}"
            else:
                focus_area_id = raw_row[col_map.get("FocusAreaID", 2)].strip()

            # Launch date
            launch_date_str = raw_row[col_map.get("ActionLaunchDate", 7)].strip()
            launch_date = parse_date(launch_date_str)

            has_started = launch_date is not None and launch_date <= TODAY
            launch_text = format_launch_text(launch_date)

            actions.append({
                "actionId": action_id,
                "actionName": action_name,
                "actionDesc": action_desc,
                "pillarId": pillar_id,
                "focusAreaId": focus_area_id,
                "launchDate": launch_date.isoformat() if launch_date else None,
                "launchText": launch_text,
                "hasStarted": has_started,
                "status": "In Progress" if has_started else "Not Started"
            })

    return actions


def read_action_statuses():
    """
    Read the Strategic Plan Actions Tracker XLSX to get the real status
    for each action. Returns a dict: {ActionID: status_string}.
    Falls back gracefully if the file doesn't exist or openpyxl isn't available.
    """
    statuses = {}
    if not os.path.exists(TRACKER_XLSX):
        print(f"  [WARN] Tracker XLSX not found: {TRACKER_XLSX}")
        print("  Using date-based status fallback.")
        return statuses

    try:
        import openpyxl
        wb = openpyxl.load_workbook(TRACKER_XLSX, data_only=True, read_only=True)
        # Try the first sheet
        ws = wb.active
        header = None
        action_id_col = None
        status_col = None

        for row in ws.iter_rows(values_only=True):
            if header is None:
                # Find column indices
                header = [str(c).strip() if c else "" for c in row]
                for i, h in enumerate(header):
                    h_lower = h.lower()
                    if "actionid" in h_lower or "action id" in h_lower or h_lower == "actionid":
                        action_id_col = i
                    if "status" in h_lower:
                        status_col = i
                if action_id_col is None or status_col is None:
                    print(f"  [WARN] Could not find ActionID/Status columns in tracker.")
                    print(f"  Headers found: {header}")
                    break
                continue

            # Data rows
            cells = list(row)
            if len(cells) > max(action_id_col, status_col):
                aid = str(cells[action_id_col]).strip() if cells[action_id_col] else ""
                status = str(cells[status_col]).strip() if cells[status_col] else ""
                if aid and status:
                    statuses[aid] = status

        wb.close()
        print(f"  Loaded {len(statuses)} action statuses from tracker XLSX.")
    except ImportError:
        print("  [WARN] openpyxl not installed — using date-based status fallback.")
    except Exception as e:
        print(f"  [WARN] Error reading tracker XLSX: {e}")
        print("  Using date-based status fallback.")

    return statuses


def read_blog_matches():
    """
    Read blog_focus_area_matches_final.csv → list of story dicts.
    Each row is one blog-to-focus-area match (a blog can appear in multiple focus areas).
    """
    stories = []
    with open(BLOGS_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fa_id = row.get("FocusAreaID", "").strip()
            if not fa_id:
                continue

            # Parse the publish date for sorting
            pub_date_str = row.get("StoryPublishDate", "").strip()
            pub_date = parse_date(pub_date_str)
            # Format for display: "August 26, 2025"
            pub_display = pub_date.strftime("%B %d, %Y") if pub_date else pub_date_str

            stories.append({
                "blogNum": int(row.get("BlogNum", 0)),
                "title": row.get("StoryTitle", "").strip(),
                "url": row.get("StoryURL", "").strip(),
                "publishDate": pub_display,
                "publishDateSort": pub_date.isoformat() if pub_date else "",
                "county": row.get("StoryCounty", "").strip(),
                "rationale": row.get("MatchRationale", "").strip(),
                "focusAreaId": fa_id,
                "pillarId": row.get("PillarID", "").strip()
            })

    return stories


def build_pillar_data():
    """
    Assemble the full nested JSON structure:
    {
      "lastUpdated": "2026-04-09",
      "pillars": [
        {
          "pillarId": "P1", "pillarNum": 1, "pillarName": "...",
          "focusAreas": [
            {
              "focusAreaId": "P1.F1", "focusAreaName": "...",
              "actions": [...],
              "stories": [...]
            }
          ]
        }
      ]
    }
    """
    print("Building pillar-data.json...")

    # 1. Read all source data
    print("  Reading DIM_Pillars.csv...")
    pillars = read_pillars()
    print(f"  Found {len(pillars)} pillars.")

    print("  Reading DIM_FocusAreas.csv...")
    focus_areas = read_focus_areas()
    print(f"  Found {len(focus_areas)} focus areas.")

    print("  Reading DIM_Actions.csv...")
    actions = read_actions()
    print(f"  Found {len(actions)} actions.")

    print("  Reading action statuses from tracker XLSX...")
    statuses = read_action_statuses()

    print("  Reading blog_focus_area_matches_final.csv...")
    stories = read_blog_matches()
    print(f"  Found {len(stories)} blog-focus-area matches.")

    # 2. Merge action statuses from tracker XLSX
    for action in actions:
        if action["actionId"] in statuses:
            action["status"] = statuses[action["actionId"]]
            # Override hasStarted based on status
            status_lower = action["status"].lower()
            if "in progress" in status_lower or "complete" in status_lower:
                action["hasStarted"] = True
            elif "not started" in status_lower:
                action["hasStarted"] = False

    # 3. Nest actions into focus areas
    for action in actions:
        fa_id = action["focusAreaId"]
        if fa_id in focus_areas:
            # Remove the focusAreaId and pillarId from the action (redundant in nested structure)
            action_clean = {k: v for k, v in action.items() if k not in ("focusAreaId", "pillarId")}
            focus_areas[fa_id]["actions"].append(action_clean)

    # 4. Nest stories into focus areas (sorted by publish date descending)
    for story in stories:
        fa_id = story["focusAreaId"]
        if fa_id in focus_areas:
            story_clean = {k: v for k, v in story.items() if k not in ("focusAreaId", "pillarId")}
            focus_areas[fa_id]["stories"].append(story_clean)

    # Sort stories by publish date descending within each focus area
    for fa in focus_areas.values():
        fa["stories"].sort(key=lambda s: s.get("publishDateSort", ""), reverse=True)
        # Remove the sort key from the output
        for story in fa["stories"]:
            story.pop("publishDateSort", None)

    # 5. Nest focus areas into pillars
    for fa in focus_areas.values():
        pillar_id = fa["pillarId"]
        if pillar_id in pillars:
            fa_clean = {k: v for k, v in fa.items() if k != "pillarId"}
            pillars[pillar_id]["focusAreas"].append(fa_clean)

    # Sort focus areas by number within each pillar
    for p in pillars.values():
        p["focusAreas"].sort(key=lambda fa: fa["focusAreaNum"])

    # 6. Build the final sorted list of pillars
    pillar_list = sorted(pillars.values(), key=lambda p: p["pillarNum"])

    output = {
        "lastUpdated": TODAY.isoformat(),
        "pillars": pillar_list
    }

    # 7. Write JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n  Output: {OUTPUT_JSON}")
    print(f"  {len(pillar_list)} pillars, "
          f"{sum(len(p['focusAreas']) for p in pillar_list)} focus areas.")

    # Summary stats
    total_actions = sum(
        len(fa["actions"])
        for p in pillar_list
        for fa in p["focusAreas"]
    )
    total_stories = sum(
        len(fa["stories"])
        for p in pillar_list
        for fa in p["focusAreas"]
    )
    print(f"  Total: {total_actions} actions, {total_stories} story matches.")
    print("  Done!")


if __name__ == "__main__":
    build_pillar_data()
