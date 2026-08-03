#!/usr/bin/env python3
"""Own the site's public "Last updated" date.

The sidebar of every page renders `lastUpdated` from data/pillar-data.json as
"Last updated <date>". It is a public claim about the freshness of what the
visitor is looking at, so it needs to be true.

WHAT THE DATE MEANS (Andy, 2026-08-03) -- the dashboard changed for a user:
  (a) updated measure data, Smartsheet action data, or stories, OR
  (b) a structural change big enough that we would put it in a user-facing
      changelog.

(a) is mechanical, so this tool detects it: it fingerprints the built JSON the
site actually serves and bumps the date only when that content really moved.
(b) is a judgment call no fingerprint can make -- a one-word code comment and a
redesigned measure card both "change the HTML" -- so it is `--force`.

WHY THIS EXISTS
Before 2026-08-03 the date was stamped with today's date by build-pillar-data.py
on every run. That was wrong in both directions:
  - a rebuild with no data change still bumped the date, and
  - the 7/24 and 7/27 measure waves run build-pillar-measures.py, which never
    touched the field at all -- so the live site advertised 2026-07-15 while
    serving 7/27 data, including two brand-new Pillar 6 measures.
build-pillar-data.py now PRESERVES the field and this tool owns it.

USAGE
  python tools/update-stamp.py            # bump to today iff content changed
  python tools/update-stamp.py --check    # exit 1 if stale; changes nothing
  python tools/update-stamp.py --force    # bump regardless (rule (b))
  python tools/update-stamp.py --date 2026-07-27   # bump to a specific date

Run it after any data wave, and before pushing. `--check` is the one to wire
into a pre-push or the verify suite: it turns a silent stale claim into a
failure. Exit 0 = stamp is correct, 1 = stale (--check only), 2 = error.
All output is plain ASCII so it survives a Windows cp1252 console.
"""
import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PILLAR_DATA = ROOT / "data" / "pillar-data.json"
STAMP_STATE = ROOT / "data" / "stamp-state.json"

# The built JSON the site actually serves. Everything a visitor can see comes
# from these three; anything else in data/ is an input or a build artifact.
#
# Deliberately NOT fingerprinted:
#   - the .html files  -> rule (b), a judgment call; use --force
#   - measure-gaps.md  -> regenerated with a fresh date stamp every run, so it
#                         would report a change on every build forever
CONTENT_FILES = [
    ("data/pillar-data.json", ("lastUpdated",)),   # 2nd item: keys to ignore
    ("data/pillar-measures.json", ()),
    ("data/measures.json", ()),
]


def fingerprint():
    """Stable hash of the user-visible built content.

    Re-serializes each file with sorted keys so that pure formatting churn (key
    order, indentation) does not read as a content change.
    """
    h = hashlib.sha256()
    for relpath, ignore_keys in CONTENT_FILES:
        path = ROOT / relpath
        if not path.exists():
            raise SystemExit(f"ERROR: missing {relpath} -- run the build scripts first.")
        data = json.loads(path.read_text(encoding="utf-8"))
        if ignore_keys and isinstance(data, dict):
            data = {k: v for k, v in data.items() if k not in ignore_keys}
        h.update(relpath.encode("utf-8"))
        h.update(json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8"))
    return h.hexdigest()


def read_stamp():
    return json.loads(PILLAR_DATA.read_text(encoding="utf-8")).get("lastUpdated")


def write_stamp(new_date):
    """Rewrite only lastUpdated, preserving the file's existing formatting style."""
    data = json.loads(PILLAR_DATA.read_text(encoding="utf-8"))
    data["lastUpdated"] = new_date
    PILLAR_DATA.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="report staleness without changing anything; exit 1 if stale")
    ap.add_argument("--force", action="store_true",
                    help="bump even if content is unchanged (rule (b): structural change)")
    ap.add_argument("--date", metavar="YYYY-MM-DD",
                    help="date to stamp (default: today)")
    args = ap.parse_args()

    if args.date:
        try:
            new_date = date.fromisoformat(args.date).isoformat()
        except ValueError:
            print(f"ERROR: --date must be YYYY-MM-DD, got {args.date!r}")
            return 2
    else:
        new_date = date.today().isoformat()

    current = fingerprint()
    stored = None
    if STAMP_STATE.exists():
        stored = json.loads(STAMP_STATE.read_text(encoding="utf-8")).get("contentFingerprint")
    stamp = read_stamp()
    changed = (stored != current)

    print(f"  stamp in pillar-data.json : {stamp}")
    print(f"  content fingerprint       : {current[:16]}...")
    print(f"  content changed since last: {'YES' if changed else 'no'}"
          + ("  (no baseline recorded yet)" if stored is None else ""))

    if args.check:
        if changed:
            print("\nSTALE - site content changed but 'Last updated' was not bumped.")
            print("Run: python tools/update-stamp.py")
            return 1
        print("\nOK - 'Last updated' matches the content being served.")
        return 0

    if not changed and not args.force:
        print("\nNo content change; stamp left at "
              f"{stamp}. Use --force for a structural change (rule (b)).")
        return 0

    write_stamp(new_date)
    STAMP_STATE.write_text(
        json.dumps({
            "contentFingerprint": current,
            "stampedOn": new_date,
            "note": "Written by tools/update-stamp.py -- do not hand-edit.",
        }, indent=2) + "\n",
        encoding="utf-8",
    )
    why = "forced (structural change)" if (not changed and args.force) else "content changed"
    print(f"\nUPDATED - 'Last updated' {stamp} -> {new_date}  ({why})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
