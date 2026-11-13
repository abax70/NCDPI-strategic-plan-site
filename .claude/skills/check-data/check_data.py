"""
check_data.py — dashboard data-quality check

Inspects the two JSON files that feed the strategic plan dashboard
(`data/measures.json`, `data/pillar-data.json`) and the CSV/XLSX source
files in /data, emitting a tiered markdown report grouped by severity
(errors, warnings, info).

Checks performed (see .claude/plans/buzzing-cooking-harbor.md for the
original design):
  A. Completeness — measures.json (all measures; Best in Nation at higher severity)
  B. Completeness — pillar-data.json (pillars, focus areas, actions, stories)
  C. Date / status consistency (launch dates vs status, hasStarted, launchText)
  D. Referential integrity (ID regex, planRef resolution, duplicates)
  E. JSON ↔ source diff (value-by-value, plus mtime staleness)
  F. Blog freshness (newest internal publishDate vs today)
  G. Text quality (formula artifacts, placeholders, entity residue)

The live CTG page (https://www.dpi.nc.gov/news/celebrate-good/ctg-blog-list)
is NOT fetched by this script — Claude is expected to do that via WebFetch
in SKILL.md, since network access from the script is unreliable.

Exit code: 1 if any errors, 0 otherwise. Warnings and info do not change
the exit code.

Usage:
  python .claude/skills/check-data/check_data.py

Run from anywhere — the script resolves paths relative to its own location.

Author: Andy Baxter / Claude  |  2026-04-14
"""

import csv
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

# Ensure UTF-8 output on Windows — em-dashes and ellipses otherwise
# appear as � in cp1252 terminals. Safe no-op elsewhere.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, Exception):
    pass

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------
# Script lives at .claude/skills/check-data/check_data.py
# Project root is 3 parents up.
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

MEASURES_JSON = DATA_DIR / "measures.json"
PILLAR_DATA_JSON = DATA_DIR / "pillar-data.json"

DIM_PILLARS_CSV = DATA_DIR / "DIM_Pillars.csv"
DIM_FOCUS_AREAS_CSV = DATA_DIR / "DIM_FocusAreas.csv"
DIM_ACTIONS_CSV = DATA_DIR / "DIM_Actions.csv"
DIM_MEASURES_CSV = DATA_DIR / "DIM_Measures.csv"
MEASURE_RESULTS_CSV = DATA_DIR / "LandingPage_MeasureResults.csv"
MEASURE_DETAILS_CSV = DATA_DIR / "LandingPage_MeasureDetailsText.csv"
BLOG_POSTS_CSV = DATA_DIR / "blog_posts.csv"
BLOG_MATCHES_CSV = DATA_DIR / "blog_focus_area_matches_final.csv"
TRACKER_XLSX = DATA_DIR / "Strategic Plan Actions Tracker.xlsx"

TODAY = date.today()
EXPECTED_PILLAR_COUNT = 8
EXPECTED_FOCUS_AREA_COUNT = 26
BLOG_STALE_DAYS = 14
LAST_UPDATED_STALE_DAYS = 30
VALID_ACTION_STATUSES = {"In Progress", "Not Started", "Completed"}

# Fields required on every measure (rendered unconditionally by index.html).
# Subfields within whatsInMotion cards are checked separately.
REQUIRED_MEASURE_FIELDS = [
    "name", "pillarNumber", "pillarName", "goal", "definition",
    "currentValue", "currentDescription", "sourceLabel", "sourceUrl",
    "iconUrl", "whyItCounts", "nextUpdate",
]
# Extra fields required when a measure is flagged Best in Nation.
REQUIRED_BIN_FIELDS = ["badgeImageUrl", "badgeAltText", "statusLabel", "statusType"]

# Regex patterns for formula leakage and placeholders in rendered text.
# These show up when CSV cells weren't fully cleaned before JSON generation.
FORMULA_ARTIFACT_RE = re.compile(
    r"(=IFERROR|=IF\(|__xludf|DUMMYFUNCTION|COMPUTED_VALUE|#REF!|#N/A|#NAME\?)",
    re.IGNORECASE,
)
PLACEHOLDER_RE = re.compile(
    r"(\blorem ipsum\b|\bTBD\b|\bTODO\b|\bFIXME\b|\[Need to add|\[Add note|xxx+)",
    re.IGNORECASE,
)
HTML_ENTITY_RE = re.compile(r"&(amp|nbsp|quot|#39|apos|lt|gt);")

ACTION_ID_RE = re.compile(r"^P([1-8])\.F([1-5])\.A(\d+)$")
FOCUS_AREA_ID_RE = re.compile(r"^P([1-8])\.F([1-5])$")
MEASURE_ID_RE = re.compile(r"^P([1-8])\.M(\d+)$")


# ---------------------------------------------------------------------------
# Finding record + helpers
# ---------------------------------------------------------------------------
@dataclass
class Finding:
    """One data-quality issue. Severity drives sort order and exit code."""
    severity: str           # 'error' | 'warn' | 'info'
    category: str           # short label (e.g., 'Completeness (measures)')
    location: str           # "file/record-id" for quick lookup
    message: str
    fix: str = ""           # optional concrete remediation suggestion


findings: list[Finding] = []


def add(severity: str, category: str, location: str, message: str, fix: str = "") -> None:
    """Append a Finding to the global list. Thin wrapper for readability."""
    findings.append(Finding(severity, category, location, message, fix))


# ---------------------------------------------------------------------------
# Text normalization helpers (duplicated from build-pillar-data.py because
# that file has a hyphen in its name and can't be imported directly)
# ---------------------------------------------------------------------------
def clean_text(text: Any) -> str:
    """Strip formula wrapper text and collapse whitespace. Empty in → empty out."""
    if not text or not isinstance(text, str):
        return ""
    if text.startswith("="):
        return ""
    text = re.sub(r"=IFERROR\([^)]*\)", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_date(date_str: Any) -> date | None:
    """Parse date strings in the common formats we see in the sources."""
    if not date_str or not isinstance(date_str, str):
        return None
    s = date_str.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def norm(s: Any) -> str:
    """
    Normalize a string for source-vs-JSON diff comparison.
    Lowercases, strips punctuation-only differences, collapses whitespace.
    We don't want legitimate edits (e.g., a typo fix) to be swamped by
    trivial formatting differences.
    """
    if s is None:
        return ""
    s = str(s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def norm_strict(s: Any) -> str:
    """Stricter normalization: lowercase + strip trailing period."""
    return norm(s).lower().rstrip(".")


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_json(path: Path) -> Any:
    """Load a JSON file with useful failure mode (report & abort)."""
    if not path.exists():
        add("error", "Setup", str(path), "File not found.",
            fix="Check the file path is correct.")
        return None
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        add("error", "Setup", str(path),
            f"JSON parse failed: {e}",
            fix="Re-run .claude/hooks/validate-json.py to find the exact byte offset.")
        return None


def read_csv_dict(path: Path) -> list[dict]:
    """Read a CSV into a list of dicts, skipping fully-empty rows."""
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            # Skip rows where every value is empty/whitespace
            if any(v and v.strip() for v in row.values()):
                rows.append(row)
    return rows


def read_action_statuses_xlsx() -> dict[str, str]:
    """Pull {ActionID: status} from the Strategic Plan Actions Tracker."""
    statuses: dict[str, str] = {}
    if not TRACKER_XLSX.exists():
        add("info", "Setup", str(TRACKER_XLSX),
            "Actions Tracker XLSX not found — skipping source-vs-JSON status compare.")
        return statuses
    try:
        import openpyxl
    except ImportError:
        add("info", "Setup", "openpyxl",
            "openpyxl not installed — can't read the actions tracker XLSX.",
            fix="pip install openpyxl")
        return statuses
    try:
        wb = openpyxl.load_workbook(TRACKER_XLSX, data_only=True, read_only=True)
        ws = wb.active
        header = None
        action_col = None
        status_col = None
        for row in ws.iter_rows(values_only=True):
            if header is None:
                header = [str(c).strip() if c else "" for c in row]
                for i, h in enumerate(header):
                    hl = h.lower()
                    if hl in ("actionid", "action id") or "actionid" in hl:
                        action_col = i
                    elif "status" in hl and status_col is None:
                        status_col = i
                if action_col is None or status_col is None:
                    add("warn", "Setup", "Actions Tracker.xlsx",
                        f"Couldn't find ActionID/Status columns. Headers: {header}")
                    break
                continue
            cells = list(row)
            if len(cells) > max(action_col, status_col):
                aid = str(cells[action_col]).strip() if cells[action_col] else ""
                st = str(cells[status_col]).strip() if cells[status_col] else ""
                if aid and st:
                    statuses[aid] = st
        wb.close()
    except Exception as e:
        add("warn", "Setup", "Actions Tracker.xlsx", f"Error reading XLSX: {e}")
    return statuses


# ---------------------------------------------------------------------------
# A. Completeness — measures.json
# ---------------------------------------------------------------------------
def check_measures_completeness(measures: list[dict]) -> None:
    """Every measure must have the fields the UI unconditionally renders."""
    if not measures:
        add("error", "Completeness (measures)", "measures.json",
            "No measures found.",
            fix="Restore measures.json from version control or rebuild it.")
        return

    for m in measures:
        loc = f"measures.json/{m.get('measureId') or m.get('id') or '?'}"

        # Base fields every measure needs.
        for field_name in REQUIRED_MEASURE_FIELDS:
            v = m.get(field_name)
            if v is None or (isinstance(v, str) and not v.strip()):
                add("error", "Completeness (measures)", loc,
                    f"Missing or empty `{field_name}`.",
                    fix="Populate from LandingPage_MeasureDetailsText.csv "
                        "or DIM_Measures.csv and rebuild.")

        # dataSeries must have at least one entry with year + (actual or target).
        ds = m.get("dataSeries") or []
        if not ds:
            add("error", "Completeness (measures)", loc,
                "`dataSeries` is empty.",
                fix="Pull year/actual/target rows from LandingPage_MeasureResults.csv.")
        else:
            for i, yr in enumerate(ds):
                if yr.get("year") in (None, ""):
                    add("warn", "Completeness (measures)", f"{loc}/dataSeries[{i}]",
                        "Year missing.")
                if yr.get("actual") in (None, "") and yr.get("target") in (None, ""):
                    add("info", "Completeness (measures)", f"{loc}/dataSeries[{i}]",
                        "Both actual and target are empty for this year.")

        # whatsInMotion field was retired 2026-04-20 — the landing-page ticker
        # now pulls from pillar-data.json via renderMotionTicker() instead of a
        # per-measure linkage. No completeness check here.

        # Best-in-Nation extras (currently every measure in measures.json is BiN).
        is_bin = bool(m.get("badgeImageUrl")) or m.get("statusType") == "record-high"
        if is_bin:
            for field_name in REQUIRED_BIN_FIELDS:
                v = m.get(field_name)
                if v is None or (isinstance(v, str) and not v.strip()):
                    add("error", "Completeness (Best in Nation)", loc,
                        f"Best in Nation measure missing `{field_name}`.",
                        fix="Best in Nation measures need a badge, alt text, "
                            "statusLabel (e.g., 'Record High — 87.7%'), and statusType.")


# ---------------------------------------------------------------------------
# B. Completeness — pillar-data.json
# ---------------------------------------------------------------------------
def check_pillar_data_completeness(pd: dict) -> None:
    """Structural expectations + required fields on every record."""
    if not pd:
        return

    pillars = pd.get("pillars") or []
    if len(pillars) != EXPECTED_PILLAR_COUNT:
        add("error", "Completeness (pillars)", "pillar-data.json",
            f"Expected {EXPECTED_PILLAR_COUNT} pillars, found {len(pillars)}.",
            fix="Rebuild pillar-data.json via data/build-pillar-data.py.")

    total_focus_areas = 0
    for p in pillars:
        loc = f"pillar-data.json/P{p.get('pillarNum', '?')}"
        for f in ("pillarNum", "pillarName", "focusAreas"):
            if not p.get(f):
                add("error", "Completeness (pillars)", loc,
                    f"Pillar missing `{f}`.",
                    fix="Rebuild from DIM_Pillars.csv.")
        fas = p.get("focusAreas") or []
        total_focus_areas += len(fas)
        if not fas:
            add("error", "Completeness (pillars)", loc,
                "Pillar has no focus areas.",
                fix="Check DIM_FocusAreas.csv has rows for this pillar.")

        for fa in fas:
            fa_loc = f"pillar-data.json/{fa.get('focusAreaId', '?')}"
            for f in ("focusAreaId", "focusAreaName", "actions", "stories"):
                if fa.get(f) is None:
                    add("error", "Completeness (focus areas)", fa_loc,
                        f"Focus area missing `{f}`.")

            actions = fa.get("actions") or []
            stories = fa.get("stories") or []
            if not actions:
                add("error", "Completeness (focus areas)", fa_loc,
                    "Focus area has no actions.",
                    fix="Check DIM_Actions.csv has rows for this focus area.")
            if not stories:
                add("warn", "Completeness (focus areas)", fa_loc,
                    "Focus area has no stories.",
                    fix="Find blog posts that cover this focus area and add to "
                        "blog_focus_area_matches_final.csv.")

            for a in actions:
                a_loc = f"pillar-data.json/{a.get('actionId', '?')}"
                for f in ("actionId", "actionName", "status",
                          "launchDate", "launchText", "hasStarted"):
                    if a.get(f) in (None, ""):
                        add("error", "Completeness (actions)", a_loc,
                            f"Action missing `{f}`.")
                # actionDesc is optional per UI — warn only
                if not a.get("actionDesc"):
                    add("warn", "Completeness (actions)", a_loc,
                        "`actionDesc` is empty. UI will render without body text.")

            for s in stories:
                s_loc = f"pillar-data.json/{fa.get('focusAreaId', '?')}/story"
                for f in ("title", "url", "publishDate"):
                    if not s.get(f):
                        add("error", "Completeness (stories)", s_loc,
                            f"Story missing `{f}`.")

    if total_focus_areas != EXPECTED_FOCUS_AREA_COUNT:
        add("warn", "Completeness (pillars)", "pillar-data.json",
            f"Expected {EXPECTED_FOCUS_AREA_COUNT} focus areas total, "
            f"found {total_focus_areas}.",
            fix="Check DIM_FocusAreas.csv row count.")


# ---------------------------------------------------------------------------
# C. Date / status consistency
# ---------------------------------------------------------------------------
def check_date_status(pd: dict) -> None:
    if not pd:
        return

    # lastUpdated freshness
    lu_str = pd.get("lastUpdated", "")
    lu = parse_date(lu_str)
    if not lu:
        add("warn", "Date consistency", "pillar-data.json/lastUpdated",
            f"`lastUpdated` not parseable: {lu_str!r}")
    else:
        age = (TODAY - lu).days
        if age > LAST_UPDATED_STALE_DAYS:
            add("info", "Date consistency", "pillar-data.json/lastUpdated",
                f"`lastUpdated` is {age} days old ({lu_str}).",
                fix="Rebuild via data/build-pillar-data.py to stamp today's date.")

    for p in pd.get("pillars", []):
        for fa in p.get("focusAreas", []):
            # Action checks
            for a in fa.get("actions", []):
                a_loc = f"pillar-data.json/{a.get('actionId', '?')}"
                status = a.get("status", "")
                launch = parse_date(a.get("launchDate", ""))
                has_started = a.get("hasStarted")
                launch_text = a.get("launchText", "")

                # Status must be in the valid set
                if status and status not in VALID_ACTION_STATUSES:
                    add("error", "Date consistency", a_loc,
                        f"`status` is {status!r}; expected one of "
                        f"{sorted(VALID_ACTION_STATUSES)}.",
                        fix="Edit the Strategic Plan Actions Tracker.xlsx.")

                # Andy's check #4: launchDate in past but status says otherwise
                if launch and launch <= TODAY and status == "Not Started":
                    add("error", "Date consistency", a_loc,
                        f"launchDate {launch} has passed but status is "
                        f"'Not Started'.",
                        fix="Update status in Strategic Plan Actions Tracker.xlsx "
                            "to 'In Progress' (or 'Completed' if finished).")

                # hasStarted must agree with launchDate vs today
                if launch and has_started is not None:
                    expected_started = launch <= TODAY
                    if bool(has_started) != expected_started:
                        add("error", "Date consistency", a_loc,
                            f"`hasStarted` is {has_started} but launchDate "
                            f"{launch} suggests {expected_started}.",
                            fix="Rebuild pillar-data.json to recompute hasStarted.")

                # launchText should mention the month/year of launchDate
                if launch and launch_text:
                    expected_month = launch.strftime("%B")
                    expected_year = launch.strftime("%Y")
                    if expected_month not in launch_text or expected_year not in launch_text:
                        add("warn", "Date consistency", a_loc,
                            f"`launchText` is {launch_text!r} but launchDate "
                            f"is {launch} ({expected_month} {expected_year}).",
                            fix="Rebuild pillar-data.json to regenerate launchText.")

            # Story publishDate checks
            for s in fa.get("stories", []):
                pd_str = s.get("publishDate", "")
                pubdate = parse_date(pd_str)
                s_loc = f"pillar-data.json/{fa.get('focusAreaId', '?')}/" \
                        f"{s.get('title', '?')[:40]}"
                if pd_str and not pubdate:
                    add("warn", "Date consistency", s_loc,
                        f"`publishDate` not parseable: {pd_str!r}",
                        fix="Use 'Month DD, YYYY' format.")
                elif pubdate and pubdate > TODAY:
                    add("warn", "Date consistency", s_loc,
                        f"`publishDate` {pubdate} is in the future.")


# ---------------------------------------------------------------------------
# D. Referential integrity
# ---------------------------------------------------------------------------
def check_referential_integrity(pd: dict, measures: list[dict]) -> None:
    if not pd:
        return

    all_action_ids: set[str] = set()
    dup_action_ids: set[str] = set()
    all_focus_ids: set[str] = set()
    dup_focus_ids: set[str] = set()
    all_story_urls: set[str] = set()
    dup_story_urls: set[str] = set()

    # Collect IDs + check regex + pillar/focus-area number agreement
    for p in pd.get("pillars", []):
        pnum = p.get("pillarNum")
        for fa in p.get("focusAreas", []):
            fa_id = fa.get("focusAreaId", "")
            m = FOCUS_AREA_ID_RE.match(fa_id)
            if not m:
                add("error", "Referential integrity", f"pillar-data.json/{fa_id}",
                    f"`focusAreaId` {fa_id!r} does not match P[1-8].F[1-5].")
            elif int(m.group(1)) != pnum:
                add("error", "Referential integrity", f"pillar-data.json/{fa_id}",
                    f"focusAreaId pillar number ({m.group(1)}) does not match "
                    f"parent pillar number ({pnum}).")

            if fa_id in all_focus_ids:
                dup_focus_ids.add(fa_id)
            all_focus_ids.add(fa_id)

            for a in fa.get("actions", []):
                aid = a.get("actionId", "")
                am = ACTION_ID_RE.match(aid)
                if not am:
                    add("error", "Referential integrity", f"pillar-data.json/{aid}",
                        f"`actionId` {aid!r} does not match P[1-8].F[1-5].A\\d+.")
                elif int(am.group(1)) != pnum:
                    add("error", "Referential integrity", f"pillar-data.json/{aid}",
                        f"actionId pillar number ({am.group(1)}) does not match "
                        f"parent pillar number ({pnum}).")
                elif fa_id and f"P{am.group(1)}.F{am.group(2)}" != fa_id:
                    add("error", "Referential integrity", f"pillar-data.json/{aid}",
                        f"actionId focus area prefix does not match parent "
                        f"focus area {fa_id}.")

                if aid in all_action_ids:
                    dup_action_ids.add(aid)
                all_action_ids.add(aid)

            for s in fa.get("stories", []):
                url = s.get("url", "")
                if url:
                    if url in all_story_urls:
                        dup_story_urls.add(url)
                    all_story_urls.add(url)

    # Duplicate findings
    for aid in dup_action_ids:
        add("error", "Referential integrity", f"pillar-data.json/{aid}",
            "Duplicate actionId.",
            fix="Check DIM_Actions.csv — IDs must be unique.")
    for fid in dup_focus_ids:
        add("error", "Referential integrity", f"pillar-data.json/{fid}",
            "Duplicate focusAreaId.")
    # Duplicate story URLs WITHIN a focus area are a real problem; duplicates
    # ACROSS focus areas are expected (one blog covers multiple topics). So
    # we check per-focus-area instead.
    for p in pd.get("pillars", []):
        for fa in p.get("focusAreas", []):
            urls_here: dict[str, int] = {}
            for s in fa.get("stories", []):
                u = s.get("url", "")
                urls_here[u] = urls_here.get(u, 0) + 1
            for u, n in urls_here.items():
                if n > 1 and u:
                    add("error", "Referential integrity",
                        f"pillar-data.json/{fa.get('focusAreaId', '?')}",
                        f"Story URL appears {n}× in this focus area: {u}",
                        fix="Dedupe in blog_focus_area_matches_final.csv.")

    # Measure checks
    seen_measure_ids: set[str] = set()
    for m in measures:
        mid = m.get("measureId", "") or m.get("id", "")
        loc = f"measures.json/{mid}"
        pnum = m.get("pillarNumber")
        mm = MEASURE_ID_RE.match(m.get("measureId", ""))
        if not mm:
            add("warn", "Referential integrity", loc,
                f"`measureId` {m.get('measureId')!r} does not match P[1-8].M\\d+.")
        elif pnum is not None and int(mm.group(1)) != pnum:
            add("error", "Referential integrity", loc,
                f"measureId pillar prefix ({mm.group(1)}) does not match "
                f"pillarNumber ({pnum}).")

        mid_key = m.get("measureId") or m.get("id")
        if mid_key and mid_key in seen_measure_ids:
            add("error", "Referential integrity", loc,
                f"Duplicate measure id/measureId: {mid_key}")
        seen_measure_ids.add(mid_key)

        # whatsInMotion referential check retired 2026-04-20 — see note in the
        # Completeness section above. The new ticker pulls actions directly
        # from pillar-data.json, so there's no planRef to validate.


# ---------------------------------------------------------------------------
# E. JSON ↔ source diff
# ---------------------------------------------------------------------------
def check_source_diff(pd: dict, measures: list[dict]) -> None:
    """
    Compare mirrored fields between JSON and source CSV/XLSX files.
    Mismatches are warnings (JSON may have legitimate edits); mtime stale
    is info ("rebuild suggested").
    """
    # ---- pillar names ----
    pillars_csv = read_csv_dict(DIM_PILLARS_CSV)
    csv_pillar_names = {r.get("PillarID", "").strip():
                        norm_strict(r.get("PillarName", ""))
                        for r in pillars_csv if r.get("PillarID", "").startswith("P")}
    for p in pd.get("pillars", []) if pd else []:
        pid = f"P{p.get('pillarNum')}"
        csv_name = csv_pillar_names.get(pid)
        json_name = norm_strict(p.get("pillarName", ""))
        if csv_name and json_name and csv_name != json_name:
            add("warn", "Source vs JSON (pillars)",
                f"pillar-data.json/{pid}",
                f"pillarName differs from DIM_Pillars.csv. "
                f"JSON={p.get('pillarName')!r}, CSV={next((r.get('PillarName') for r in pillars_csv if r.get('PillarID', '').strip() == pid), '')!r}",
                fix="Decide which is authoritative. If CSV wins, rebuild JSON.")

    # ---- focus area names ----
    fa_csv = read_csv_dict(DIM_FOCUS_AREAS_CSV)
    csv_fa_names = {r.get("FocusAreaID", "").strip():
                    norm_strict(r.get("FocusAreaName", ""))
                    for r in fa_csv if FOCUS_AREA_ID_RE.match(r.get("FocusAreaID", "").strip())}
    for p in pd.get("pillars", []) if pd else []:
        for fa in p.get("focusAreas", []):
            fa_id = fa.get("focusAreaId", "")
            csv_name = csv_fa_names.get(fa_id)
            json_name = norm_strict(fa.get("focusAreaName", ""))
            if csv_name and json_name and csv_name != json_name:
                orig = next((r.get("FocusAreaName") for r in fa_csv
                             if r.get("FocusAreaID", "").strip() == fa_id), "")
                add("warn", "Source vs JSON (focus areas)",
                    f"pillar-data.json/{fa_id}",
                    f"focusAreaName differs from DIM_FocusAreas.csv. "
                    f"JSON={fa.get('focusAreaName')!r}, CSV={orig!r}")

    # ---- action names, descs, launchDate, status ----
    actions_csv = read_csv_dict(DIM_ACTIONS_CSV)
    # Build dict keyed by ActionID.
    csv_actions: dict[str, dict] = {}
    for r in actions_csv:
        aid = r.get("ActionID", "").strip()
        if ACTION_ID_RE.match(aid):
            csv_actions[aid] = {
                "name": r.get("ActionName", "").strip(),
                "desc": clean_text(r.get("ActionDesc", "")),
                "launchDate": parse_date(r.get("ActionLaunchDate", "").strip()),
            }
    tracker_statuses = read_action_statuses_xlsx()

    json_action_ids: set[str] = set()
    for p in pd.get("pillars", []) if pd else []:
        for fa in p.get("focusAreas", []):
            for a in fa.get("actions", []):
                aid = a.get("actionId", "")
                json_action_ids.add(aid)
                csv_a = csv_actions.get(aid)
                if not csv_a:
                    add("warn", "Source vs JSON (actions)",
                        f"pillar-data.json/{aid}",
                        "Action exists in JSON but not in DIM_Actions.csv.")
                    continue
                # Name
                if csv_a["name"] and norm_strict(a.get("actionName", "")) != norm_strict(csv_a["name"]):
                    add("warn", "Source vs JSON (actions)",
                        f"pillar-data.json/{aid}",
                        f"actionName differs. JSON={a.get('actionName')!r}, "
                        f"CSV={csv_a['name']!r}")
                # Desc
                json_desc = norm_strict(a.get("actionDesc", ""))
                csv_desc = norm_strict(csv_a["desc"])
                if json_desc and csv_desc and json_desc != csv_desc:
                    add("warn", "Source vs JSON (actions)",
                        f"pillar-data.json/{aid}",
                        "actionDesc differs from DIM_Actions.csv (after whitespace normalization).",
                        fix="Rebuild if CSV is authoritative; otherwise leave.")
                # Launch date
                if csv_a["launchDate"]:
                    json_launch = parse_date(a.get("launchDate", ""))
                    if json_launch != csv_a["launchDate"]:
                        add("warn", "Source vs JSON (actions)",
                            f"pillar-data.json/{aid}",
                            f"launchDate differs. JSON={json_launch}, "
                            f"CSV={csv_a['launchDate']}")
                # Status from tracker
                if tracker_statuses:
                    xl_status = tracker_statuses.get(aid)
                    if xl_status and a.get("status") and \
                            norm_strict(a.get("status", "")) != norm_strict(xl_status):
                        add("warn", "Source vs JSON (actions)",
                            f"pillar-data.json/{aid}",
                            f"status differs from Actions Tracker XLSX. "
                            f"JSON={a.get('status')!r}, XLSX={xl_status!r}")

    # Actions in CSV but missing from JSON
    missing_in_json = set(csv_actions) - json_action_ids
    for aid in sorted(missing_in_json):
        add("warn", "Source vs JSON (actions)", f"DIM_Actions.csv/{aid}",
            "Action in CSV is missing from pillar-data.json.",
            fix="Rebuild pillar-data.json.")

    # ---- story URL × focus area set ----
    # Build set of (focusAreaId, url) from both sides and diff.
    bfam_csv = read_csv_dict(BLOG_MATCHES_CSV)
    csv_pairs = {(r.get("FocusAreaID", "").strip(), r.get("StoryURL", "").strip())
                 for r in bfam_csv
                 if FOCUS_AREA_ID_RE.match(r.get("FocusAreaID", "").strip())}
    json_pairs: set[tuple[str, str]] = set()
    for p in pd.get("pillars", []) if pd else []:
        for fa in p.get("focusAreas", []):
            fa_id = fa.get("focusAreaId", "")
            for s in fa.get("stories", []):
                json_pairs.add((fa_id, s.get("url", "").strip()))
    missing_in_json_stories = csv_pairs - json_pairs
    missing_in_csv_stories = json_pairs - csv_pairs
    for fa_id, url in sorted(missing_in_json_stories):
        add("warn", "Source vs JSON (stories)",
            f"blog_focus_area_matches_final.csv/{fa_id}",
            f"Story URL in CSV but missing from JSON: {url}",
            fix="Rebuild pillar-data.json.")
    for fa_id, url in sorted(missing_in_csv_stories):
        add("warn", "Source vs JSON (stories)",
            f"pillar-data.json/{fa_id}",
            f"Story URL in JSON but missing from CSV: {url}",
            fix="Either re-add to blog_focus_area_matches_final.csv "
                "or rebuild to remove.")

    # ---- measure details text ----
    details_csv = read_csv_dict(MEASURE_DETAILS_CSV)
    csv_details: dict[str, dict] = {r.get("MeasureID", "").strip(): r for r in details_csv}
    for m in measures:
        mid = m.get("measureId", "")
        src = csv_details.get(mid)
        if not src:
            continue
        loc = f"measures.json/{mid}"
        pairs = [
            ("definition", src.get("NoteMeasureDefinition", "")),
            ("nextUpdate", src.get("NoteNextUpdateText", "")),
            ("sourceLabel", src.get("NoteDataSourceText", "")),
            ("sourceUrl", src.get("NoteDataSourceURL", "")),
            ("goal", src.get("MeasureGoal", "")),
        ]
        for field_name, csv_val in pairs:
            json_val = m.get(field_name, "")
            if csv_val and json_val and norm_strict(json_val) != norm_strict(csv_val):
                add("warn", "Source vs JSON (measures)", loc,
                    f"`{field_name}` differs from LandingPage_MeasureDetailsText.csv.")

    # ---- measure data series ----
    results_rows = read_csv_dict(MEASURE_RESULTS_CSV)
    # Build {measureId: {year: (actual, target)}}
    csv_results: dict[str, dict[str, tuple[str, str]]] = {}
    for r in results_rows:
        mid = r.get("MeasureID", "").strip()
        if not MEASURE_ID_RE.match(mid):
            continue
        y = r.get("Year", "").strip().rstrip("0").rstrip(".")  # "2024.0" → "2024"
        if not y:
            continue
        csv_results.setdefault(mid, {})[y] = (
            (r.get("ActualValue", "") or "").strip(),
            (r.get("TargetValue", "") or "").strip(),
        )
    def nums_equal(a: str, b: str) -> bool:
        """Parse both as floats and compare. False if either is unparseable."""
        try:
            return float(a) == float(b)
        except (ValueError, TypeError):
            # Fall back to string compare after stripping whitespace.
            return str(a).strip() == str(b).strip()

    for m in measures:
        mid = m.get("measureId", "")
        loc = f"measures.json/{mid}"
        src_years = csv_results.get(mid, {})
        for yr in m.get("dataSeries", []):
            y = str(yr.get("year", "")).strip()
            src = src_years.get(y)
            if not src:
                continue
            # Compare actual numerically (JSON may store 400000 as int, CSV as "400000.0")
            j_actual = str(yr.get("actual", "") or "").strip()
            s_actual = src[0].strip() if src[0] else ""
            if j_actual and s_actual and not nums_equal(j_actual, s_actual):
                add("warn", "Source vs JSON (measures)",
                    f"{loc}/dataSeries[{y}]",
                    f"actual differs. JSON={j_actual}, CSV={src[0]}")
            # Compare target numerically
            j_target = str(yr.get("target", "") or "").strip()
            s_target = src[1].strip() if src[1] else ""
            if j_target and s_target and not nums_equal(j_target, s_target):
                add("warn", "Source vs JSON (measures)",
                    f"{loc}/dataSeries[{y}]",
                    f"target differs. JSON={j_target}, CSV={src[1]}")

    # ---- mtime staleness ----
    # If any source file is newer than its JSON, suggest rebuild.
    def mtime(p: Path) -> float:
        return p.stat().st_mtime if p.exists() else 0

    pillar_json_mtime = mtime(PILLAR_DATA_JSON)
    for src in (DIM_PILLARS_CSV, DIM_FOCUS_AREAS_CSV, DIM_ACTIONS_CSV,
                BLOG_MATCHES_CSV, TRACKER_XLSX):
        if mtime(src) > pillar_json_mtime and pillar_json_mtime > 0:
            add("info", "Source staleness", src.name,
                f"{src.name} is newer than pillar-data.json.",
                fix="Rebuild: python data/build-pillar-data.py")

    measures_json_mtime = mtime(MEASURES_JSON)
    for src in (DIM_MEASURES_CSV, MEASURE_RESULTS_CSV, MEASURE_DETAILS_CSV):
        if mtime(src) > measures_json_mtime and measures_json_mtime > 0:
            add("info", "Source staleness", src.name,
                f"{src.name} is newer than measures.json.",
                fix="No build-measures.py exists yet — edit measures.json by hand "
                    "or build one (see follow-up skill `rebuild-data`).")


# ---------------------------------------------------------------------------
# F. Blog freshness
# ---------------------------------------------------------------------------
def check_blog_freshness(pd: dict) -> None:
    """Find the newest publishDate across all stories in pillar-data.json."""
    newest: date | None = None
    newest_title = ""
    for p in pd.get("pillars", []) if pd else []:
        for fa in p.get("focusAreas", []):
            for s in fa.get("stories", []):
                d = parse_date(s.get("publishDate", ""))
                if d and (newest is None or d > newest):
                    newest = d
                    newest_title = s.get("title", "")

    if newest is None:
        add("warn", "Blog freshness", "pillar-data.json",
            "No parseable publishDates found across all stories.")
        return

    age = (TODAY - newest).days
    loc = "pillar-data.json/stories"
    if age > BLOG_STALE_DAYS:
        add("warn", "Blog freshness", loc,
            f"Newest story is {age} days old "
            f"({newest} — '{newest_title[:50]}').",
            fix="Check https://www.dpi.nc.gov/news/celebrate-good/ctg-blog-list "
                "for new posts. See follow-up skill `refresh-blogs`.")
    else:
        add("info", "Blog freshness", loc,
            f"Newest story is {age} days old ({newest}).")


# ---------------------------------------------------------------------------
# G. Text quality
# ---------------------------------------------------------------------------
def check_text_quality(pd: dict, measures: list[dict]) -> None:
    """Walk every string in both JSON trees and flag suspicious content."""

    # Keys whose VALUE we use as the path segment when encountering a dict
    # that has one of them. This makes "measures.json/P1.M2/definition"
    # readable instead of "measures.json[1]/definition".
    ID_KEYS = ("measureId", "actionId", "focusAreaId", "pillarId", "id")

    def walk(obj: Any, path: str) -> None:
        if isinstance(obj, dict):
            # If this dict has an identifiable ID field, adjust the path
            # to use that ID instead of whatever index got us here.
            id_val = None
            for k in ID_KEYS:
                if k in obj and obj[k]:
                    id_val = str(obj[k])
                    break
            if id_val and path.endswith("]"):
                # Replace the trailing [N] with /<id>
                path = re.sub(r"\[\d+\]$", f"/{id_val}", path)
            for k, v in obj.items():
                walk(v, f"{path}/{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                walk(v, f"{path}[{i}]")
        elif isinstance(obj, str):
            if FORMULA_ARTIFACT_RE.search(obj):
                add("error", "Text quality", path,
                    f"Formula/error artifact in text: {obj[:80]}…",
                    fix="Clean the source CSV and rebuild.")
            if PLACEHOLDER_RE.search(obj):
                add("warn", "Text quality", path,
                    f"Placeholder text found: {obj[:80]}…",
                    fix="Replace with real content.")
            if HTML_ENTITY_RE.search(obj):
                add("warn", "Text quality", path,
                    f"HTML entity residue in rendered text: {obj[:80]}…",
                    fix="Replace &amp; → &, &#39; → ', etc.")
            if "  " in obj:
                add("info", "Text quality", path,
                    "Double space in rendered text.")

    if measures:
        walk(measures, "measures.json")
    if pd:
        walk(pd, "pillar-data.json")


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
SEV_ORDER = {"error": 0, "warn": 1, "info": 2}
SEV_LABEL = {"error": "Errors", "warn": "Warnings", "info": "Info"}


def print_report() -> int:
    """Emit a grouped markdown report. Returns exit code (1 if any errors)."""
    errors = [f for f in findings if f.severity == "error"]
    warns = [f for f in findings if f.severity == "warn"]
    infos = [f for f in findings if f.severity == "info"]

    print(f"# Dashboard Data Quality Report — {TODAY.isoformat()}\n")

    for sev, group in (("error", errors), ("warn", warns), ("info", infos)):
        label = SEV_LABEL[sev]
        print(f"## {label} ({len(group)})\n")
        if not group:
            print("_None_\n")
            continue
        # Group within severity by category for easier scanning.
        by_cat: dict[str, list[Finding]] = {}
        for f in group:
            by_cat.setdefault(f.category, []).append(f)
        for cat, items in sorted(by_cat.items()):
            print(f"### {cat} ({len(items)})\n")
            for f in items:
                line = f"- **[{f.location}]** {f.message}"
                if f.fix:
                    line += f" _Fix: {f.fix}_"
                print(line)
            print()

    print("## Summary\n")
    print(f"Errors: {len(errors)}  |  Warnings: {len(warns)}  |  Info: {len(infos)}\n")

    # Reminder about the live blog check Claude should do
    print("## Live CTG page check\n")
    print("This script only checks internal publishDates. To verify against the "
          "live blog listing, Claude should WebFetch "
          "https://www.dpi.nc.gov/news/celebrate-good/ctg-blog-list and compare "
          "the newest post date to the newest story above.\n")

    return 1 if errors else 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    measures = load_json(MEASURES_JSON) or []
    pillar_data = load_json(PILLAR_DATA_JSON) or {}

    check_measures_completeness(measures if isinstance(measures, list) else [])
    check_pillar_data_completeness(pillar_data if isinstance(pillar_data, dict) else {})
    check_date_status(pillar_data if isinstance(pillar_data, dict) else {})
    check_referential_integrity(pillar_data if isinstance(pillar_data, dict) else {},
                                measures if isinstance(measures, list) else [])
    check_source_diff(pillar_data if isinstance(pillar_data, dict) else {},
                      measures if isinstance(measures, list) else [])
    check_blog_freshness(pillar_data if isinstance(pillar_data, dict) else {})
    check_text_quality(pillar_data if isinstance(pillar_data, dict) else {},
                       measures if isinstance(measures, list) else [])

    return print_report()


if __name__ == "__main__":
    sys.exit(main())
