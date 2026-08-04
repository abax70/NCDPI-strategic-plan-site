#!/usr/bin/env python3
"""
Spot-check that every hand-authored Source line renders as a real anchor.

WHY THIS EXISTS
  `sourceHtml` is a PRESERVE field carrying hand-written HTML, and it is the only
  field on the site where a human types raw markup that goes straight to the page.
  Nothing else checks it. The four verify-*.py tools all look at charts: painted
  pixels, axis objects, BiN chips, value-label collisions. A Source line could be
  a broken tag, a dead href, or plain text where a link was intended, and every
  one of them would pass clean.

WHAT THIS IS NOT
  Not a fifth verify tool. The four verify-*.py tools each exist because a real
  bug slipped past the previous ones; this one was written on 2026-08-04 to
  confirm a change (Section B's five source lines gaining links) rather than to
  catch a regression that bit us. It is kept because it is cheap and rerunnable,
  not because it has earned a place in the pre-push set.

WHAT IT CHECKS
  For every measure with a non-null sourceHtml, in BOTH data files:
    1. The Source line actually appears on the rendered page.
    2. Its anchor count matches the number of <a> tags in the source data
       (i.e. the markup was not silently mangled or escaped into text).
    3. Every href returns a non-error HTTP status  (skipped with --no-net).
  Serves the repo root over localhost itself; never file:// (fetch() needs http).

USAGE
  python tools/check-source-lines.py            # full check, including HTTP
  python tools/check-source-lines.py --no-net   # skip the network round-trips

EXIT
  0 = all source lines render as expected; 1 = at least one problem.

KNOWN QUIRKS (both produce WARN, not FAIL — this script cannot tell these apart
from real breakage, and crying wolf would make the whole report ignorable)
  - Some hosts refuse scripted clients regardless of user-agent. As of 2026-08-04
    P8.M2's apps.schools.nc.gov link returns 403 here but may be fine in a
    browser. A human still has to click it.
  - TLS cert validation fails inside this devcontainer for some federal hosts
    (missing root CA, not a bad site). P1.M8's cte.ed.gov is the live example:
    it fails here, but serves 200 to a browser and to `curl -k`. Separately, that
    URL now redirects to octae.ed.gov — a real thing to fix, just not this error.
"""

import argparse
import functools
import http.server
import json
import os
import re
import socketserver
import sys
import threading
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# (json file, page that renders it, navigation mode)
#
# The two pages navigate differently, and getting this wrong looks exactly like a
# site bug: best-in-nation.html is a CAROUSEL — only one measure is in the DOM at
# a time, so scraping it after a plain page load finds measure 1 and "loses" the
# other 13. Its <select> carries the array index as the option value
# (best-in-nation.html, buildDropdown), so we drive it by index.
SOURCES = [
    ("data/pillar-measures.json", "pillar.html", "deeplink"),
    ("data/measures.json", "best-in-nation.html", "carousel"),
]
BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def serve():
    """Background static server on an ephemeral port; returns the port."""
    handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                                directory=REPO)
    # Silence the per-request logging that would drown the report.
    handler.log_message = lambda *a, **k: None
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def check_url(url):
    """Return (ok, detail). ok=False only for hard failures, not 4xx blocks."""
    req = urllib.request.Request(url, headers={"User-Agent": BROWSER_UA})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return True, f"{r.status}"
    except urllib.error.HTTPError as e:
        # 403/401 are usually bot-blocking, not a dead link — warn, don't fail.
        return (e.code in (401, 403)), f"HTTP {e.code}"
    except urllib.error.URLError as e:
        # A cert failure here is far more often this container's missing root CA
        # than a genuinely broken link: cte.ed.gov fails cert validation inside
        # the devcontainer but serves 200 to a browser (and to `curl -k`). The
        # script cannot tell those apart, so warn rather than cry wolf.
        if "CERTIFICATE" in str(e.reason).upper():
            return True, "TLS cert not verifiable here (likely container CA)"
        return False, f"URLError: {e.reason}"
    except Exception as e:  # DNS, timeout — worth a human look either way
        return False, type(e).__name__


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--no-net", action="store_true",
                    help="skip HTTP checks on the hrefs")
    args = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright not available — this tool needs it to render the page.")
        return 1

    srv, port = serve()
    problems, warnings, checked = [], [], 0
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            for json_rel, page_rel, nav in SOURCES:
                measures = json.load(open(os.path.join(REPO, json_rel),
                                          encoding="utf-8"))
                todo = [(i, m) for i, m in enumerate(measures) if m.get("sourceHtml")]
                print(f"\n=== {json_rel} — {len(todo)} hand-authored source lines")
                base = f"http://127.0.0.1:{port}/{page_rel}"
                if nav == "carousel":
                    page.goto(base, wait_until="networkidle")
                for idx, m in todo:
                    mid, raw = m["measureId"], m["sourceHtml"]
                    if nav == "carousel":
                        # Select this measure, then wait for the badge to catch up
                        # so we scrape the new card and not the outgoing one.
                        page.select_option(".carousel-select", str(idx))
                        page.wait_for_function(
                            "id => document.querySelector('.action-id-badge')"
                            "?.textContent.trim() === id", arg=mid, timeout=10000)
                    else:
                        page.goto(f"{base}?p={m['pillarNumber']}",
                                  wait_until="networkidle")
                    html = page.content()
                    want = re.findall(r'<a\b[^>]*href="([^"]+)"', raw)

                    # Locate this measure's Source paragraph by a distinctive
                    # fragment of its own sourceHtml (first href, else the text).
                    needle = want[0] if want else re.sub(r"<[^>]+>", "", raw)[:40]
                    seg = None
                    for mt in re.finditer(r"<p><strong>Sources?:</strong>(.*?)</p>",
                                          html, re.S):
                        if needle and needle in mt.group(1):
                            seg = mt.group(1)
                            break
                    checked += 1
                    if seg is None:
                        problems.append(f"{mid}: Source line not found on {page_rel}")
                        print(f"  FAIL {mid}: not rendered")
                        continue
                    got = re.findall(r'<a\b[^>]*href="([^"]+)"', seg)
                    if len(got) != len(want):
                        problems.append(
                            f"{mid}: {len(want)} anchors in data, {len(got)} rendered")
                        print(f"  FAIL {mid}: anchor count {len(want)} -> {len(got)}")
                        continue
                    print(f"  OK   {mid}: {len(got)} anchor(s)")
                    if args.no_net:
                        continue
                    for href in got:
                        ok, detail = check_url(href)
                        if not ok:
                            problems.append(f"{mid}: {href} -> {detail}")
                            print(f"         FAIL {detail}  {href}")
                        elif not detail.startswith("2"):
                            warnings.append(f"{mid}: {href} -> {detail}")
                            print(f"         WARN {detail} — verify by hand  {href}")
            browser.close()
    finally:
        srv.shutdown()

    print()
    for w in warnings:
        print(f"WARN  {w}")
    if problems:
        print(f"\nFAIL - {len(problems)} problem(s) across {checked} source lines")
        for pr in problems:
            print(f"  - {pr}")
        return 1
    print(f"PASS - {checked} source lines render as expected"
          f"{' (network checks skipped)' if args.no_net else ''}"
          f"{f', {len(warnings)} need a human click' if warnings else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
