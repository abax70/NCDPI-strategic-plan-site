#!/usr/bin/env python3
"""
verify_motion.py
Verifies that the 3 actions the landing page's "What's in Motion" ticker will
render today are all genuinely launched — i.e. they point to real actions in
pillar-data.json with `hasStarted: true` and `launchDate <= today`.

Exits 0 on success, 1 on any error. Warnings do not fail the script.

Why this exists:
  The ticker JS in index.html picks the top 3 launched actions by launchDate.
  This script replicates that selection server-side and sanity-checks each
  pick, so routine data refreshes can't ship a ticker pointing to an action
  that hasn't actually launched yet (or has bad metadata).

Selection rule (must match index.html renderMotionTicker()):
  - collect every action across all pillars with hasStarted=true and a
    non-empty launchDate
  - sort by launchDate desc, tie-break by actionId asc
  - take the first 3
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent  # .claude/skills/verify-motion → project root
PILLAR_DATA = PROJECT_ROOT / "data" / "pillar-data.json"

TODAY = date.today()


def load_pillar_data() -> dict:
    if not PILLAR_DATA.exists():
        print(f"ERROR: {PILLAR_DATA} not found.", file=sys.stderr)
        sys.exit(1)
    return json.loads(PILLAR_DATA.read_text(encoding="utf-8"))


def parse_iso(d: str) -> date | None:
    try:
        return date.fromisoformat(d[:10])
    except (ValueError, TypeError):
        return None


def collect_launched(pillar_data: dict) -> tuple[list[dict], list[dict]]:
    """Collect launched actions and flag any data-drift cases.

    Matches the JS filter in index.html renderMotionTicker(): an action is
    "launched" only when hasStarted=true AND launchDate<=today. Actions with
    hasStarted=true but a future launchDate are data-drift (fix upstream) —
    they're returned separately so we can warn without failing.
    """
    launched: list[dict] = []
    drift: list[dict] = []
    today_iso = TODAY.isoformat()
    for p in pillar_data.get("pillars", []):
        pnum = p.get("pillarNum")
        for fa in p.get("focusAreas", []) or []:
            for a in fa.get("actions", []) or []:
                if not a:
                    continue
                if not (a.get("hasStarted") and a.get("launchDate")):
                    continue
                entry = {
                    "actionId": a.get("actionId", ""),
                    "actionName": a.get("actionName", ""),
                    "launchDate": a.get("launchDate", ""),
                    "launchText": a.get("launchText", ""),
                    "status": a.get("status", ""),
                    "pillarNum": pnum,
                    "focusAreaId": fa.get("focusAreaId", ""),
                }
                if entry["launchDate"] <= today_iso:
                    launched.append(entry)
                else:
                    drift.append(entry)
    return launched, drift


def pick_top_3_stable(launched: list[dict]) -> list[dict]:
    """Sort primarily by launchDate desc, secondarily by actionId asc.

    Must match the JS selection in index.html renderMotionTicker().
    Python sort is stable, so sort by secondary key first then primary.
    """
    by_id = sorted(launched, key=lambda x: x["actionId"])
    by_date = sorted(by_id, key=lambda x: x["launchDate"], reverse=True)
    return by_date[:3]


def resolve_action(pillar_data: dict, action_id: str) -> tuple[int, str] | None:
    """Return (pillarNum, focusAreaId) for a given actionId, or None."""
    for p in pillar_data.get("pillars", []):
        for fa in p.get("focusAreas", []) or []:
            for a in fa.get("actions", []) or []:
                if a.get("actionId") == action_id:
                    return p.get("pillarNum"), fa.get("focusAreaId", "")
    return None


def main() -> int:
    pillar_data = load_pillar_data()
    launched, drift = collect_launched(pillar_data)

    print("# /verify-motion report\n")
    print(f"- Today: **{TODAY.isoformat()}**")
    print(f"- Launched actions found (hasStarted=true, launchDate<=today): **{len(launched)}**")

    if drift:
        print(
            f"\n## Warnings — hasStarted/launchDate drift ({len(drift)} actions)\n"
        )
        print(
            "These actions have `hasStarted: true` but `launchDate` in the "
            "future. The ticker correctly skips them, but pillar.html's "
            "Actions tab will show them as 'In Progress' with a future launch "
            "month — likely a data-pipeline bug. Fix in the Actions Tracker "
            "xlsx and rerun `/rebuild-data`.\n"
        )
        for item in drift:
            print(
                f"- `{item['actionId']}` ({item['actionName']}) — "
                f"launchDate {item['launchDate']}, launchText {item['launchText']!r}"
            )
        print()

    if len(launched) < 3:
        print(
            "\n**ERROR**: fewer than 3 launched actions in pillar-data.json — "
            "the ticker will render an incomplete row."
        )
        return 1

    top3 = pick_top_3_stable(launched)

    print("\n## Ticker picks (top 3, newest first)\n")
    errors: list[str] = []
    warnings: list[str] = []

    for i, item in enumerate(top3, 1):
        aid = item["actionId"]
        ldate = parse_iso(item["launchDate"])
        ltext = item["launchText"] or ""
        pnum = item["pillarNum"]
        print(f"### {i}. {aid} — {item['actionName']}")
        print(f"- pillar: {pnum} · focusArea: {item['focusAreaId']}")
        print(f"- launchDate: {item['launchDate']} · launchText: {ltext!r}")
        print(f"- status: {item.get('status', '')!r}")
        url = f"pillar.html?p={pnum}&action={aid}"
        print(f"- resolved URL: `{url}`")

        # Check 1: hasStarted=true (guaranteed by collector, assert defensively)
        # Check 2: launchDate <= today
        if ldate is None:
            errors.append(f"{aid}: launchDate {item['launchDate']!r} is not a valid ISO date.")
        elif ldate > TODAY:
            errors.append(
                f"{aid}: launchDate {ldate.isoformat()} is in the future — "
                f"hasStarted=true contradicts the date."
            )

        # Check 3: launchText should be "Launched …", not "Launches in …"
        if ltext and not ltext.lower().startswith("launched"):
            errors.append(
                f"{aid}: launchText {ltext!r} does not start with 'Launched' — "
                f"hasStarted/launchText disagree."
            )

        # Check 4: actionId resolves (should always, since it was collected from
        # pillar-data, but verifies the deep-link target exists).
        if resolve_action(pillar_data, aid) is None:
            errors.append(f"{aid}: actionId does not resolve in pillar-data.json.")

        print()

    if errors:
        print("## Errors\n")
        for e in errors:
            print(f"- **{e}**")
    if warnings:
        print("\n## Warnings\n")
        for w in warnings:
            print(f"- {w}")

    print()
    if errors:
        print(f"**FAIL** — {len(errors)} error(s). Ticker data is not safe to ship.")
        return 1

    print("**PASS** — all 3 ticker actions are genuinely launched and resolvable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
