#!/usr/bin/env python3
"""Verify the y-axis SCALE of every pillar measure chart.

Companion to verify-charts.py and verify-bin-chips.py.

WHY THIS EXISTS
---------------
verify-charts.py proves a canvas painted non-blank pixels. It cannot tell a
correct axis from an absurd one. On 2026-07-27 P1.M17b rendered a flat-at-zero
series on a -0.10%..0.025% axis -- a metric that cannot go below zero, drawn as
though zero were its ceiling. Every existing check passed. It was caught by eye.

This script asserts the axis INVARIANTS instead, by reading the live Chart.js
scale objects in a real browser rather than inspecting pixels:

  1. Every plotted value lies inside [scale.min, scale.max].
     (A point outside the scale is clipped and silently misleads.)
  2. A non-negative measure never gets a negative axis floor.
     (The exact P1.M17b bug.)
  3. The final target lands ON a labeled tick for the trajectory strip.
     (The stated invariant of the increase/decrease branches in pillar.html;
     the 7/27 non-negative floor guard shifts tickStart by WHOLE steps
     specifically to preserve it.)
  4. The axis is not degenerate (min < max, at least two ticks).

Exit code 0 = all invariants hold. Non-zero = at least one violation.

USAGE
    python tools/verify-chart-scales.py            # all 8 pillars
    python tools/verify-chart-scales.py --pillars 1,6
"""

import argparse
import asyncio
import json
import os
import socket
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8899

# Value formats that cannot be negative. Anything counted, measured as a
# percentage, or denominated in dollars has a hard floor at zero.
NON_NEGATIVE_FORMATS = {"#", "#.#%", "#%", "$#,###", "#,###"}

# Charts are matched to their measure by walking up from the canvas to the
# enclosing card, whose id is "measure-<MeasureID>". Matching on the aria-label
# text is NOT safe: P2.M2a "...Program Enrollment" and P2.M2b "...Program
# Completion" share their first 30 characters, so a name-prefix match silently
# assigns both charts to the first measure and invents violations.
PROBE_JS = """
() => {
  const out = [];
  for (const c of Object.values(Chart.instances)) {
    const y = c.scales.y;
    if (!y) continue;
    const card = c.canvas.closest('[id^="measure-"]');
    out.push({
      type: c.config.type,
      measureId: card ? card.id.replace(/^measure-/, '') : null,
      label: (c.canvas.getAttribute('aria-label') || '').slice(0, 80),
      min: y.min,
      max: y.max,
      ticks: y.ticks.map(t => t.value),
      datasets: c.data.datasets.map(d => ({
        label: d.label || '(unlabeled)',
        data: d.data
      }))
    });
  }
  return out;
}
"""


def start_server():
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(PORT)],
        cwd=REPO, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        try:
            socket.create_connection(("127.0.0.1", PORT), 0.2).close()
            return proc
        except OSError:
            time.sleep(0.1)
    proc.terminate()
    raise RuntimeError(f"local server never came up on port {PORT}")


def load_measures():
    """{pillarNumber: [measure, ...]} from the generated pillar JSON."""
    path = os.path.join(REPO, "data", "pillar-measures.json")
    by_pillar = {}
    with open(path, encoding="utf-8") as fh:
        for m in json.load(fh):
            by_pillar.setdefault(m["pillarNumber"], []).append(m)
    return by_pillar


def check_chart(chart, measures, failures, notes):
    """Apply the four invariants to one live chart object."""
    lab = chart["label"] or f"({chart['type']} chart)"
    lo, hi = chart["min"], chart["max"]
    ticks = chart["ticks"]

    # (4) degenerate axis
    if lo is None or hi is None or lo >= hi:
        failures.append(f"{lab}: degenerate axis min={lo} max={hi}")
        return
    if len(ticks) < 2:
        failures.append(f"{lab}: only {len(ticks)} tick(s) -- unreadable axis")
        return

    values = [v for ds in chart["datasets"] for v in ds["data"] if v is not None]
    if not values:
        notes.append(f"{lab}: no plotted values (placeholder chart)")
        return

    # (1) every value inside the scale
    for v in values:
        if not (lo <= v <= hi):
            failures.append(
                f"{lab}: value {v} outside axis [{lo}, {hi}] -- point is clipped")

    # (2) non-negative floor. The chart knows its own measure ID via the
    # enclosing card, so this is an exact match, not a name guess.
    measure = next((m for m in measures if m["measureId"] == chart["measureId"]), None)
    if measure is None:
        failures.append(
            f"{lab}: chart is not inside a measure-<ID> card "
            f"(measureId={chart['measureId']!r}) -- cannot verify its scale")
        return

    fmt = measure.get("valueFormat")
    if fmt in NON_NEGATIVE_FORMATS and min(values) >= 0 and lo < 0:
        failures.append(
            f"{lab}: axis floor {lo} is negative for a '{fmt}' measure "
            f"whose values are all >= 0 (the 2026-07-27 P1.M17b bug)")

    # (3) final target on a labeled tick -- trajectory (line) chart only.
    # The bar chart is a plain 0..yAxisMax scale and has no such contract.
    if chart["type"] == "line":
        targets = [p.get("target") for p in measure["dataSeries"]
                   if p.get("target") is not None]
        if targets:
            final = targets[-1]
            if not any(abs(final - t) < 1e-9 for t in ticks):
                failures.append(
                    f"{lab}: final target {final} is not on a labeled tick "
                    f"{ticks} -- trajectory anchor invariant broken")


async def run(pillars):
    from playwright.async_api import async_playwright

    by_pillar = load_measures()
    failures, notes, checked = [], [], 0

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1400, "height": 3000})
        for n in pillars:
            measures = by_pillar.get(n, [])
            await page.goto(f"http://127.0.0.1:{PORT}/pillar.html?p={n}")
            if not measures:
                print(f"  pillar {n}: no charted measures (placeholder) -- skipped")
                continue
            await page.click("text=Results")
            await page.wait_for_timeout(2000)
            charts = await page.evaluate(PROBE_JS)
            if not charts:
                failures.append(f"pillar {n}: Results tab rendered no charts at all")
                continue
            for chart in charts:
                check_chart(chart, measures, failures, notes)
                checked += 1
            print(f"  pillar {n}: {len(charts)} charts, "
                  f"{len(measures)} measures -- checked")
        await browser.close()

    print()
    for note in notes:
        print(f"  NOTE  {note}")
    if failures:
        print(f"\nFAIL - {len(failures)} axis invariant violation(s):")
        for f in failures:
            print(f"  * {f}")
        return 1
    print(f"PASS - {checked} charts, all axis invariants hold")
    return 0


def self_test():
    """Prove the invariants actually fire. A checker that has only ever passed
    is not evidence. Each fixture is a chart the site MUST reject."""
    cases = [
        (
            "P1.M17b bug: negative axis on a non-negative measure",
            {"type": "line", "measureId": "P1.M17b", "label": "flat at zero",
             "min": -0.10, "max": 0.025, "ticks": [-0.10, -0.05, 0.0, 0.025],
             "datasets": [{"label": "Current", "data": [0.0, 0.0]}]},
            [{"measureId": "P1.M17b", "name": "EC", "valueFormat": "#.#%",
              "dataSeries": [{"target": 0.0}]}],
        ),
        (
            "value plotted outside the axis (silently clipped)",
            {"type": "bar", "measureId": "P4.M4", "label": "clipped",
             "min": 0, "max": 100, "ticks": [0, 50, 100],
             "datasets": [{"label": "Actual", "data": [140]}]},
            [{"measureId": "P4.M4", "name": "CA", "valueFormat": "#.#%",
              "dataSeries": [{"target": 15.0}]}],
        ),
        (
            "final target floating between ticks (anchor invariant broken)",
            {"type": "line", "measureId": "P5.M3", "label": "off-tick",
             "min": 0, "max": 30, "ticks": [0, 10, 20, 30],
             "datasets": [{"label": "Target", "data": [15, 23]}]},
            [{"measureId": "P5.M3", "name": "SBS", "valueFormat": "#",
              "dataSeries": [{"target": 23.0}]}],
        ),
        (
            "degenerate axis (min == max)",
            {"type": "line", "measureId": "P7.M2", "label": "degenerate",
             "min": 4, "max": 4, "ticks": [4, 4],
             "datasets": [{"label": "Current", "data": [4]}]},
            [{"measureId": "P7.M2", "name": "PIO", "valueFormat": "#",
              "dataSeries": [{"target": 4.0}]}],
        ),
    ]
    bad = 0
    for name, chart, measures in cases:
        failures, notes = [], []
        check_chart(chart, measures, failures, notes)
        if failures:
            print(f"  caught: {name}")
            print(f"          -> {failures[0]}")
        else:
            print(f"  MISSED: {name}")
            bad += 1

    # And a known-good chart must NOT trip anything.
    failures, notes = [], []
    check_chart(
        {"type": "line", "measureId": "P6.M1a", "label": "good",
         "min": 400, "max": 750, "ticks": [450, 550, 650, 750],
         "datasets": [{"label": "Target", "data": [685, 650, 450]}]},
        [{"measureId": "P6.M1a", "name": "LPS", "valueFormat": "#",
          "dataSeries": [{"target": 650.0}, {"target": 450.0}]}],
        failures, notes)
    if failures:
        print(f"  FALSE POSITIVE on a valid chart: {failures}")
        bad += 1
    else:
        print("  clean pass on a known-good chart (no false positive)")

    print()
    if bad:
        print(f"SELF-TEST FAIL - {bad} case(s) wrong")
        return 1
    print("SELF-TEST PASS - every invariant fires, and no false positive")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pillars", default="1,2,3,4,5,6,7,8",
                    help="comma-separated pillar numbers (default: all 8)")
    ap.add_argument("--self-test", action="store_true",
                    help="check the checker against synthetic bad charts; no browser")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    pillars = [int(x) for x in args.pillars.split(",") if x.strip()]

    server = start_server()
    try:
        return asyncio.run(run(pillars))
    finally:
        server.terminate()


if __name__ == "__main__":
    sys.exit(main())
