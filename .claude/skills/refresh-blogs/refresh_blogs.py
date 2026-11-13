"""
refresh_blogs.py — helper for the `refresh-blogs` project skill

Two modes:

  --preflight
      Load existing blog CSVs + pillar-data.json, emit a JSON summary
      to stdout describing:
        - known_urls (sorted list) so Claude can diff the live CTG list
        - max_blog_num (integer) so Claude knows what BlogNum to assign
        - focus_areas ([{id, name, pillar_id, pillar_name}]) so Claude
          has the current 26-focus-area catalog in one place
      Exit 0 always (unless the data files are missing — then 2).

  --write --payload PATH
      Append new posts to blog_posts.csv and new focus-area mappings
      to blog_focus_area_matches_final.csv. Payload schema (JSON):
        {
          "new_posts": [
            {
              "title": str,
              "url": str,
              "publish_date": "YYYY-MM-DD",
              "county": str,         # may be ""
              "mappings": [
                {"focus_area_id": "P1.F3", "rationale": str},
                ...
              ]
            },
            ...
          ]
        }
      Existing rows are never touched. BlogNums are auto-assigned
      sequentially starting at (current max + 1). FocusAreaName and
      PillarID/PillarName are looked up from pillar-data.json so that
      Claude doesn't have to pass them and can't mistype them.
      Exit 0 on success, 1 on write failure, 2 on payload/schema error.

Run from anywhere — the script resolves paths relative to its own location.

Author: Andy Baxter / Claude
"""

import argparse
import csv
import json
import sys
from pathlib import Path

# Ensure UTF-8 stdout on Windows (matches check_data.py pattern)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, Exception):
    pass

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# Script lives at .claude/skills/refresh-blogs/refresh_blogs.py
# Project root is 3 parents up.
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

BLOG_POSTS_CSV = DATA_DIR / "blog_posts.csv"
BLOG_MATCHES_CSV = DATA_DIR / "blog_focus_area_matches_final.csv"
PILLAR_DATA_JSON = DATA_DIR / "pillar-data.json"

# CSVs use CRLF line endings throughout the project (verified on disk 2026-04-14).
CSV_LINE_TERMINATOR = "\r\n"

# Existing file convention: StoryPublishDate is written with a zero time
# component — "2025-08-20 00:00:00" — even though the time is never used.
# Mirror that so diffs stay clean.
DATE_SUFFIX = " 00:00:00"

# Columns in the two CSVs, in order. These are validated at write time so
# a schema drift on disk raises loudly instead of producing a broken file.
BLOG_POSTS_HEADER = ["StoryTitle", "StoryURL", "StoryPublishDate", "StoryCounty"]
BLOG_MATCHES_HEADER = [
    "BlogNum", "StoryTitle", "StoryURL", "StoryPublishDate", "StoryCounty",
    "FocusAreaID", "FocusAreaName", "PillarID", "PillarName", "MatchRationale",
]


# ---------------------------------------------------------------------------
# Shared loaders
# ---------------------------------------------------------------------------
def load_known_urls():
    """Return a list of URLs already present in blog_posts.csv (sorted)."""
    urls = []
    with open(BLOG_POSTS_CSV, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != BLOG_POSTS_HEADER:
            raise RuntimeError(
                f"blog_posts.csv header drift: expected {BLOG_POSTS_HEADER}, "
                f"got {reader.fieldnames}"
            )
        for row in reader:
            url = (row.get("StoryURL") or "").strip()
            if url:
                urls.append(url)
    return sorted(urls)


def load_max_blog_num():
    """Return the maximum BlogNum currently present in the matches CSV."""
    max_num = 0
    with open(BLOG_MATCHES_CSV, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != BLOG_MATCHES_HEADER:
            raise RuntimeError(
                f"blog_focus_area_matches_final.csv header drift: expected "
                f"{BLOG_MATCHES_HEADER}, got {reader.fieldnames}"
            )
        for row in reader:
            try:
                num = int(row.get("BlogNum", "0") or "0")
                if num > max_num:
                    max_num = num
            except ValueError:
                # Non-numeric BlogNum is a data error — let check-data catch it.
                continue
    return max_num


def load_focus_area_catalog():
    """
    Return [{id, name, pillar_id, pillar_name}] from pillar-data.json.

    Used by --preflight to hand Claude the focus-area list, and by --write
    to look up FocusAreaName / PillarID / PillarName from a FocusAreaID.
    """
    with open(PILLAR_DATA_JSON, "r", encoding="utf-8") as f:
        pd = json.load(f)
    catalog = []
    for pillar in pd.get("pillars", []):
        pillar_id = pillar.get("pillarId", "")
        pillar_name = pillar.get("pillarName", "")
        for fa in pillar.get("focusAreas", []):
            catalog.append({
                "id": fa.get("focusAreaId", ""),
                "name": fa.get("focusAreaName", ""),
                "pillar_id": pillar_id,
                "pillar_name": pillar_name,
            })
    return catalog


# ---------------------------------------------------------------------------
# --preflight
# ---------------------------------------------------------------------------
def cmd_preflight():
    try:
        urls = load_known_urls()
        max_num = load_max_blog_num()
        catalog = load_focus_area_catalog()
    except FileNotFoundError as e:
        print(f"ERROR: missing required file: {e}", file=sys.stderr)
        return 2

    out = {
        "known_url_count": len(urls),
        "known_urls": urls,
        "max_blog_num": max_num,
        "next_blog_num": max_num + 1,
        "focus_area_count": len(catalog),
        "focus_areas": catalog,
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


# ---------------------------------------------------------------------------
# --write
# ---------------------------------------------------------------------------
def validate_payload(payload):
    """
    Raise ValueError with a readable message if the payload is malformed.
    Keep this strict — a broken payload that slips past here will corrupt
    the CSVs.
    """
    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object")

    posts = payload.get("new_posts")
    if not isinstance(posts, list):
        raise ValueError("payload.new_posts must be a list")

    if not posts:
        raise ValueError("payload.new_posts is empty — nothing to write")

    for i, post in enumerate(posts):
        label = f"new_posts[{i}]"
        if not isinstance(post, dict):
            raise ValueError(f"{label} must be an object")
        for field in ("title", "url", "publish_date"):
            if not (isinstance(post.get(field), str) and post[field].strip()):
                raise ValueError(f"{label}.{field} is required and must be non-empty")
        # county is allowed to be empty string
        if "county" in post and not isinstance(post["county"], str):
            raise ValueError(f"{label}.county must be a string (may be empty)")

        mappings = post.get("mappings")
        if not isinstance(mappings, list) or not mappings:
            raise ValueError(f"{label}.mappings must be a non-empty list")
        for j, m in enumerate(mappings):
            mlabel = f"{label}.mappings[{j}]"
            if not isinstance(m, dict):
                raise ValueError(f"{mlabel} must be an object")
            for field in ("focus_area_id", "rationale"):
                if not (isinstance(m.get(field), str) and m[field].strip()):
                    raise ValueError(
                        f"{mlabel}.{field} is required and must be non-empty"
                    )


def cmd_write(payload_path):
    try:
        with open(payload_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: payload file not found: {payload_path}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"ERROR: payload is not valid JSON: {e}", file=sys.stderr)
        return 2

    try:
        validate_payload(payload)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    try:
        known_urls = set(load_known_urls())
        max_num = load_max_blog_num()
        catalog_by_id = {fa["id"]: fa for fa in load_focus_area_catalog()}
    except FileNotFoundError as e:
        print(f"ERROR: missing required file: {e}", file=sys.stderr)
        return 2
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    # Build the rows in memory first so a validation failure doesn't leave
    # a half-written CSV on disk.
    new_post_rows = []      # rows for blog_posts.csv
    new_match_rows = []     # rows for blog_focus_area_matches_final.csv
    duplicate_urls = []
    unknown_focus_areas = []

    next_num = max_num + 1
    for post in payload["new_posts"]:
        url = post["url"].strip()
        title = post["title"].strip()
        publish_date = post["publish_date"].strip()
        county = (post.get("county") or "").strip()

        if url in known_urls:
            duplicate_urls.append(url)
            continue

        # blog_posts.csv row
        new_post_rows.append([title, url, publish_date + DATE_SUFFIX, county])

        # One match row per focus-area mapping for this post
        blog_num = next_num
        for m in post["mappings"]:
            fa_id = m["focus_area_id"].strip()
            rationale = m["rationale"].strip()
            fa = catalog_by_id.get(fa_id)
            if not fa:
                unknown_focus_areas.append((url, fa_id))
                continue
            new_match_rows.append([
                blog_num,
                title,
                url,
                publish_date + DATE_SUFFIX,
                county,
                fa_id,
                fa["name"],
                fa["pillar_id"],
                fa["pillar_name"],
                rationale,
            ])
        next_num += 1

    # Hard-fail if any focus area couldn't be resolved — don't silently
    # drop mappings the user approved.
    if unknown_focus_areas:
        print("ERROR: unknown FocusAreaID(s) in payload:", file=sys.stderr)
        for url, fa_id in unknown_focus_areas:
            print(f"  {url} -> {fa_id}", file=sys.stderr)
        print("Fix the payload and re-run. No files were modified.",
              file=sys.stderr)
        return 2

    if not new_post_rows:
        # Everything was a duplicate — nothing to write.
        print(json.dumps({
            "posts_appended": 0,
            "matches_appended": 0,
            "duplicates_skipped": len(duplicate_urls),
            "duplicate_urls": duplicate_urls,
        }, indent=2, ensure_ascii=False))
        return 0

    # Actually append the rows. `newline=""` is required so csv.writer
    # emits its configured lineterminator (CRLF) cleanly on Windows.
    try:
        with open(BLOG_POSTS_CSV, "a", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator=CSV_LINE_TERMINATOR,
                           quoting=csv.QUOTE_MINIMAL)
            for row in new_post_rows:
                w.writerow(row)

        with open(BLOG_MATCHES_CSV, "a", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator=CSV_LINE_TERMINATOR,
                           quoting=csv.QUOTE_MINIMAL)
            for row in new_match_rows:
                w.writerow(row)
    except OSError as e:
        print(f"ERROR: write failed: {e}", file=sys.stderr)
        return 1

    print(json.dumps({
        "posts_appended": len(new_post_rows),
        "matches_appended": len(new_match_rows),
        "duplicates_skipped": len(duplicate_urls),
        "duplicate_urls": duplicate_urls,
        "first_blog_num": max_num + 1,
        "last_blog_num": next_num - 1,
    }, indent=2, ensure_ascii=False))
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Helper for the refresh-blogs skill."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true",
                      help="Emit JSON summary of current blog state.")
    mode.add_argument("--write", action="store_true",
                      help="Append rows from --payload JSON to the two CSVs.")
    parser.add_argument("--payload", type=str,
                        help="Path to JSON payload file (required with --write).")
    args = parser.parse_args(argv)

    if args.preflight:
        return cmd_preflight()

    if args.write:
        if not args.payload:
            print("ERROR: --write requires --payload PATH", file=sys.stderr)
            return 2
        return cmd_write(args.payload)

    # argparse enforces the mode group above, so this is unreachable.
    return 2


if __name__ == "__main__":
    sys.exit(main())
