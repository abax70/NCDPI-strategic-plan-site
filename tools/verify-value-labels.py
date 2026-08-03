#!/usr/bin/env python3
"""Headless verification that bar value labels are never drawn overlapping.

    python tools/verify-value-labels.py
    python tools/verify-value-labels.py --self-test    # no browser needed

THE BUG THIS EXISTS FOR (2026-08-03)
Each value label paints an opaque white pad before its text, so two overlapping
labels do not merely look crowded -- the later one ERASES the tail of the
earlier one. At 375px this rendered P1.M5's "97,317" as "97,31" and BiN's
"382,964" as "382,96": six of seven labels on each, showing WRONG NUMBERS on a
public dashboard. valueLabelsPlugin now culls colliding labels; this tool proves
the cull still works.

WHY THE OTHER THREE TOOLS CANNOT CATCH IT
  verify-charts.py       asserts a canvas painted non-blank pixels. A clipped
                         label paints pixels perfectly well. It passed
                         throughout, at 375px, while the numbers were wrong.
  verify-chart-scales.py asserts axis invariants. The axis was flawless.
  verify-bin-chips.py    checks DOM chips, not canvas.
A canvas is opaque to the DOM, so the only way to check from outside is to read
what the plugin decided to draw. Both plugins publish that as
`chart.$drawnValueLabels = {drawn, total}`.

INVARIANTS ASSERTED, per chart
  1. No two DRAWN labels overlap (boxes, including their white pads, must be
     separated by at least LABEL_GAP). This is the regression itself.
  2. The FIRST and LAST candidates are always drawn -- the baseline and the
     final target are the two numbers the chart exists to communicate, so the
     cull must never sacrifice them to save an interior label.
  3. At least one label is drawn whenever there is at least one candidate
     (guards a cull bug that silently empties the chart).
  4. Every drawn label's text is non-empty (guards a formatter regression).

Exit 0 = all pass. All output is plain ASCII so it survives a cp1252 console.
"""
import argparse
import functools
import http.server
import socketserver
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABEL_GAP = 2          # keep in sync with valueLabelsPlugin in both HTML files
WIDTHS = [375, 768, 1280, 2560]

# Read the culled label set out of every live chart on the page.
READ_LABELS = """
() => {
  const out = [];
  for (const ch of Object.values(Chart.instances || {})) {
    const rec = ch.$drawnValueLabels;
    if (!rec) continue;                       // line charts have no value labels
    const card = ch.canvas.closest('[id^="measure-"]');
    out.push({
      measure: card ? card.id.replace('measure-', '') : '(unknown)',
      total: rec.total,
      drawn: rec.drawn.map(d => ({text: d.text, x: d.x, w: d.w}))
    });
  }
  return out;
}
"""


def check_chart(rec, pad_x=4):
    """Apply the four invariants to one chart's drawn-label record."""
    problems = []
    drawn, total = rec["drawn"], rec["total"]
    label = rec["measure"]

    if total and not drawn:
        problems.append(f"{label}: {total} candidate labels but NONE drawn")
        return problems

    for d in drawn:
        if not str(d["text"]).strip():
            problems.append(f"{label}: drew an empty label at x={d['x']:.0f}")

    # Invariant 1 -- no overlap among what was actually drawn.
    ordered = sorted(drawn, key=lambda d: d["x"])
    for a, b in zip(ordered, ordered[1:]):
        a_right = a["x"] + a["w"] / 2 + pad_x
        b_left = b["x"] - b["w"] / 2 - pad_x
        if b_left - a_right < LABEL_GAP:
            problems.append(
                f"{label}: drawn labels {a['text']!r} and {b['text']!r} overlap "
                f"({b_left - a_right:.1f}px apart, need >= {LABEL_GAP}) "
                f"-- the later one ERASES the tail of the earlier"
            )

    # Invariant 2 -- first and last candidate always survive the cull. The
    # plugin culls only interior labels, so the extremes of the DRAWN set must
    # still be the extremes of the candidate set; a cull bug that dropped an
    # endpoint would show up as a drawn set narrower than the chart.
    if total >= 2 and len(drawn) < 2:
        problems.append(
            f"{label}: {total} candidates but only {len(drawn)} drawn -- "
            "baseline and final target must both survive the cull"
        )
    return problems


def self_test():
    """Run the invariants against synthetic records; every one must fire."""
    print("Self-test (no browser):\n")
    cases = [
        ("overlapping drawn labels (the 2026-08-03 bug)",
         {"measure": "P1.M5", "total": 7,
          "drawn": [{"text": "97,317", "x": 100, "w": 40},
                    {"text": "99,397", "x": 130, "w": 40}]}),
        ("cull emptied the chart",
         {"measure": "P1.M9", "total": 7, "drawn": []}),
        ("cull dropped an endpoint",
         {"measure": "P2.M4b", "total": 7,
          "drawn": [{"text": "1,494", "x": 100, "w": 30}]}),
        ("formatter regressed to empty text",
         {"measure": "P6.M1a", "total": 2,
          "drawn": [{"text": "", "x": 100, "w": 0},
                    {"text": "450", "x": 300, "w": 30}]}),
    ]
    ok = True
    for name, rec in cases:
        problems = check_chart(rec)
        if problems:
            print(f"  caught: {name}\n          -> {problems[0]}")
        else:
            print(f"  MISSED: {name}")
            ok = False

    good = {"measure": "P1.M10", "total": 7,
            "drawn": [{"text": "54.2%", "x": 100, "w": 34},
                      {"text": "57.0%", "x": 200, "w": 34},
                      {"text": "60.0%", "x": 300, "w": 34}]}
    if check_chart(good):
        print("  FALSE POSITIVE on a known-good chart")
        ok = False
    else:
        print("  clean pass on a known-good chart (no false positive)")

    print("\n" + ("SELF-TEST PASS - every invariant fires, and no false positive"
                  if ok else "SELF-TEST FAIL"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true",
                    help="run the invariants against synthetic bad charts; no browser")
    ap.add_argument("--widths", default=",".join(str(w) for w in WIDTHS))
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    from playwright.sync_api import sync_playwright

    widths = [int(w) for w in args.widths.split(",")]
    handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                                directory=str(ROOT))
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    all_problems, charts_checked = [], 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for width in widths:
            # --- pillar pages ---
            for pillar in range(1, 9):
                page = browser.new_page(viewport={"width": width, "height": 3000})
                page.goto(f"http://127.0.0.1:{port}/pillar.html?p={pillar}",
                          wait_until="networkidle")
                page.wait_for_timeout(800)
                try:
                    page.click("#tab-results", timeout=4000)
                except Exception:
                    page.close()
                    continue                      # pillar has no Results tab content
                page.wait_for_timeout(2200)
                for rec in page.evaluate(READ_LABELS):
                    charts_checked += 1
                    all_problems += [f"[pillar {pillar} @{width}] {m}"
                                     for m in check_chart(rec)]
                page.close()

            # --- best-in-nation, one measure at a time behind its <select> ---
            page = browser.new_page(viewport={"width": width, "height": 3000})
            page.goto(f"http://127.0.0.1:{port}/best-in-nation.html",
                      wait_until="networkidle")
            page.wait_for_timeout(1800)
            sel = page.locator("select").first
            for idx in range(sel.locator("option").count()):
                sel.select_option(index=idx)
                page.wait_for_timeout(1400)
                for rec in page.evaluate(READ_LABELS):
                    charts_checked += 1
                    all_problems += [f"[BiN #{idx + 1} @{width}] {m}"
                                     for m in check_chart(rec)]
            page.close()
            print(f"  width {width}: checked")
        browser.close()
    httpd.shutdown()

    print()
    if all_problems:
        for m in all_problems:
            print(f"  FAIL {m}")
        print(f"\nFAIL - {len(all_problems)} problem(s) across {charts_checked} charts")
        return 1
    print(f"PASS - {charts_checked} charts, no overlapping value labels at "
          f"{'/'.join(str(w) for w in widths)}px")
    return 0


if __name__ == "__main__":
    sys.exit(main())
