#!/usr/bin/env python3
"""Headless verification of pillar.html's Results-tab measure charts.

Promoted from session scratchpads (rebuilt three times before this file
existed — see CHANGELOG 2026-07-20). Run after any change to the chart
engine, the pipeline output, or a data wave:

    python tools/verify-charts.py

What it checks, per pillar (1-8) x viewport width (375 / 1280 / 2560):

  1. Page loads with ZERO console errors and zero uncaught page errors.
  2. Card count: the number of .measure-block cards on the Results tab
     equals the number of measures for that pillar in
     data/pillar-measures.json. Pillars with no measures must show the
     .results-placeholder state instead.
  3. Painted-pixel test: every chart canvas actually painted non-blank
     pixels (Chart.js can "succeed" while rendering nothing — page-load
     alone proves little).
  4. Jump strip contract (punch #6): the .results-jump-strip nav appears
     if and only if the pillar has 4+ measures, with one anchor link per
     measure, each resolving to an existing card id.

Options:
  --widths 375,1280,2560   comma-separated viewport widths to test
  --screenshots DIR        save a per-pillar screenshot at the widest
                           width. Uses a viewport TALLER than the page
                           instead of full_page=True: a full-page capture
                           of a taller-than-viewport page expands the
                           window mid-shot and freezes Chart.js mid-
                           resize-animation, so bars pile up at the left
                           edge and look broken (not a site bug — see
                           CHANGELOG 2026-07-20).
  --json PATH              measures JSON to check against
                           (default data/pillar-measures.json)

Serves the repo root over localhost itself (never file:// — fetch() of
the JSON files fails under the file scheme). Exit code 0 = all pass.
All output is plain ASCII so it survives a Windows cp1252 console.
"""

import argparse
import json
import socket
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PILLARS = range(1, 9)
DEFAULT_WIDTHS = [375, 1280, 2560]
# Taller than the rendered page at every width so charts are laid out
# at their final size with no scroll-driven resizes (and so screenshots
# avoid the full_page freeze described above).
VIEWPORT_HEIGHT = 4500
JUMP_STRIP_MIN = 4  # keep in sync with buildResultsTab() in pillar.html


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):  # silence per-request stderr noise
        pass


def start_server():
    """Serve the repo root on an OS-assigned free port."""
    handler = partial(QuietHandler, directory=str(REPO_ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, server.server_address[1]


def expected_counts(json_path):
    measures = json.loads(json_path.read_text(encoding="utf-8"))
    counts = {n: 0 for n in PILLARS}
    for m in measures:
        counts[m["pillarNumber"]] = counts.get(m["pillarNumber"], 0) + 1
    return counts


# Runs in the page. Chart.js paints async after the Results tab becomes
# visible, so the painted-pixel check is polled from Python until it
# passes or times out.
CANVAS_PAINT_JS = """
() => {
  const canvases = document.querySelectorAll('#resultsContent canvas');
  let painted = 0;
  for (const c of canvases) {
    if (c.width === 0 || c.height === 0) continue;
    const data = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
    for (let i = 3; i < data.length; i += 4) {
      if (data[i] !== 0) { painted++; break; }
    }
  }
  return { total: canvases.length, painted };
}
"""

JUMP_STRIP_JS = """
() => {
  const strip = document.querySelector('#resultsContent .results-jump-strip');
  if (!strip) return { present: false };
  const links = [...strip.querySelectorAll('a')];
  return {
    present: true,
    linkCount: links.length,
    deadAnchors: links
      .map(a => a.getAttribute('href'))
      .filter(h => !h || !h.startsWith('#') ||
                   !document.getElementById(decodeURIComponent(h.slice(1)))),
  };
}
"""


def check_pillar(page, base_url, pillar, width, expected, failures):
    """Load one pillar at one width and run all checks. Appends to failures."""
    tag = "p%d@%d" % (pillar, width)
    console_errors = []
    page_errors = []
    on_console = lambda msg: console_errors.append(msg.text) if msg.type == "error" else None
    on_pageerror = lambda exc: page_errors.append(str(exc))
    page.on("console", on_console)
    page.on("pageerror", on_pageerror)
    try:
        page.goto("%s/pillar.html?p=%d" % (base_url, pillar), wait_until="networkidle")
        page.click("#tab-results")

        if expected == 0:
            if not page.query_selector("#resultsContent.results-placeholder"):
                failures.append("%s: expected placeholder (0 measures), not found" % tag)
        else:
            cards = page.query_selector_all("#resultsContent .measure-block")
            if len(cards) != expected:
                failures.append("%s: %d cards, expected %d" % (tag, len(cards), expected))

            # Poll the painted-pixel check: 2 canvases per card (trajectory
            # + annual bars), each must have painted something.
            want = expected * 2
            paint = {"total": 0, "painted": 0}
            deadline = 20  # x 250ms = 5s
            for _ in range(deadline):
                paint = page.evaluate(CANVAS_PAINT_JS)
                if paint["total"] == want and paint["painted"] == want:
                    break
                page.wait_for_timeout(250)
            if paint["total"] != want:
                failures.append("%s: %d canvases, expected %d" % (tag, paint["total"], want))
            elif paint["painted"] != want:
                failures.append("%s: only %d/%d canvases painted pixels"
                                % (tag, paint["painted"], want))

            # Jump strip iff 4+ measures; every link must hit a real card.
            strip = page.evaluate(JUMP_STRIP_JS)
            if expected >= JUMP_STRIP_MIN:
                if not strip["present"]:
                    failures.append("%s: jump strip missing (%d measures)" % (tag, expected))
                elif strip["linkCount"] != expected:
                    failures.append("%s: jump strip has %d links, expected %d"
                                    % (tag, strip["linkCount"], expected))
                elif strip["deadAnchors"]:
                    failures.append("%s: jump strip dead anchors: %s"
                                    % (tag, strip["deadAnchors"]))
            elif strip["present"]:
                failures.append("%s: jump strip shown with only %d measures" % (tag, expected))

        for err in console_errors:
            failures.append("%s: console error: %s" % (tag, err))
        for err in page_errors:
            failures.append("%s: page error: %s" % (tag, err))
    finally:
        page.remove_listener("console", on_console)
        page.remove_listener("pageerror", on_pageerror)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--widths", default=",".join(map(str, DEFAULT_WIDTHS)))
    ap.add_argument("--screenshots", metavar="DIR")
    ap.add_argument("--json", default="data/pillar-measures.json")
    args = ap.parse_args()
    widths = [int(w) for w in args.widths.split(",")]

    json_path = REPO_ROOT / args.json
    if not json_path.exists():
        print("FATAL: %s not found" % json_path)
        return 1
    counts = expected_counts(json_path)
    print("Expected measures per pillar: %s"
          % " ".join("p%d=%d" % (p, counts[p]) for p in PILLARS))

    from playwright.sync_api import sync_playwright

    server, port = start_server()
    base_url = "http://127.0.0.1:%d" % port
    failures = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for width in widths:
                ctx = browser.new_context(viewport={"width": width, "height": VIEWPORT_HEIGHT})
                page = ctx.new_page()
                for pillar in PILLARS:
                    check_pillar(page, base_url, pillar, width, counts[pillar], failures)
                    print("  checked p%d@%d" % (pillar, width))
                    if (args.screenshots and width == max(widths) and counts[pillar] > 0):
                        shot_dir = Path(args.screenshots)
                        shot_dir.mkdir(parents=True, exist_ok=True)
                        page.screenshot(path=str(shot_dir / ("pillar%d_%d.png" % (pillar, width))))
                ctx.close()
            browser.close()
    finally:
        server.shutdown()

    print()
    if failures:
        print("FAIL - %d problem(s):" % len(failures))
        for f in failures:
            print("  - " + f)
        return 1
    print("PASS - %d pillars x %d widths clean (cards, painted pixels, "
          "jump-strip contract, console)" % (len(PILLARS), len(widths)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
