"""Verify the 2025-26 actuals wave: values, valence, and P6 axis direction.

WHY THIS EXISTS (2026-09-01)
  First actuals ever entered the dataSeries `actual` field: four measures
  (P1.M1 CGR 89.0, P1.M10 proficiency 59.2, P6.M1a low-performing schools
  521, P6.M1b low-performing districts 10). All four MEET their 2026 target,
  so every 2026 bar must render teal "Meets Target" (#077890) — the four
  verify-*.py tools prove painted pixels, axis invariants, chips and label
  collisions, but none of them reads bar COLOR, and valence is the entire
  point of this wave. P6.M1a/b are also the first DECREASING-goal measures
  to chart an actual, so this asserts the flipped trajectory anchoring
  (final target on a labeled tick in the BOTTOM half of the lattice)
  actually engaged.

  Values here are the 2026-09-01 port from the Accountability-Team pipeline
  and remain subject to the accountability correction window until the
  10/1 SBE meeting (not 10/7 as first recorded). EXPECTED updated 2026-09-29
  to the corrected values (P1.M1 88.8 -> 89.0, P6.M1a 523 -> 521; brief:
  notes/STRAT-PLAN-PORT-2026-10-01.md).

Run: python tools/verify-2026-actuals.py   (needs playwright, like verify-charts)
"""
import asyncio
import socket
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PORT = 8917
TEAL = "#077890"

# measureId -> (page, expected 2026 actual, decreasing-goal?)
EXPECTED = {
    "P1.M1":  ("best-in-nation.html", 89.0, False),
    "P1.M10": ("pillar.html?p=1",     59.2, False),
    "P6.M1a": ("pillar.html?p=6",     521,  True),
    "P6.M1b": ("pillar.html?p=6",     10,   True),
}

# Same probe shape as verify-chart-scales.py, plus per-bar backgroundColor
# (a hatch CanvasPattern serializes as null — only string colors survive).
PROBE_JS = """
() => {
  const out = [];
  for (const c of Object.values(Chart.instances)) {
    const y = c.scales.y;
    if (!y) continue;
    const card = c.canvas.closest('[id^="measure-"]');
    out.push({
      type: c.config.type,
      canvasId: c.canvas.id || null,
      measureId: card ? card.id.replace(/^measure-/, '') : null,
      labels: c.data.labels,
      ticks: y.ticks.map(t => t.value),
      datasets: c.data.datasets.map(d => ({
        label: d.label || '(unlabeled)',
        data: d.data,
        backgroundColor: Array.isArray(d.backgroundColor)
          ? d.backgroundColor.map(x => typeof x === 'string' ? x : null)
          : d.backgroundColor
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


def check_bar(mid, chart, expected, failures):
    """The 2026 bar shows the expected actual and paints teal."""
    try:
        idx = chart["labels"].index("2026")
    except ValueError:
        failures.append(f"{mid}: bar chart has no 2026 label")
        return
    ds = chart["datasets"][0]
    val = ds["data"][idx]
    if val != expected:
        failures.append(f"{mid}: 2026 bar value is {val}, expected {expected}")
    bg = ds["backgroundColor"]
    color = bg[idx] if isinstance(bg, list) else bg
    if color != TEAL:
        failures.append(
            f"{mid}: 2026 bar color is {color!r}, expected teal {TEAL} "
            f"(Meets Target) -- valence wrong, stop and investigate")


def check_flipped_trajectory(mid, chart, measure_series, failures):
    """Decrease measure: final target is a labeled tick in the BOTTOM half."""
    targets = [d["target"] for d in measure_series if d["target"] is not None]
    final = targets[-1]
    ticks = chart["ticks"]
    on = [i for i, t in enumerate(ticks) if abs(t - final) < 1e-9]
    if not on:
        failures.append(f"{mid}: final target {final} not on trajectory ticks {ticks}")
    elif on[0] > (len(ticks) - 1) / 2:
        failures.append(
            f"{mid}: final target {final} sits in the TOP half of ticks {ticks} "
            f"-- decrease-measure axis flip did not engage")


async def run():
    import json
    from playwright.async_api import async_playwright

    series_by_id = {}
    for fname in ("measures.json", "pillar-measures.json"):
        for m in json.loads((REPO / "data" / fname).read_text(encoding="utf-8")):
            series_by_id[m["measureId"]] = m["dataSeries"]

    failures = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1400, "height": 3000})
        for url in sorted({u for u, _, _ in EXPECTED.values()}):
            await page.goto(f"http://127.0.0.1:{PORT}/{url}")
            if "pillar" in url:
                await page.click("text=Results")
            await page.wait_for_timeout(2000)
            charts = await page.evaluate(PROBE_JS)
            for mid, (page_url, expected, decrease) in EXPECTED.items():
                if page_url != url:
                    continue
                # BiN loads with measure 1 (P1.M1) active; its canvases have
                # fixed ids instead of measure-<ID> cards.
                if url.startswith("best-in-nation"):
                    bar = next((c for c in charts if c["canvasId"] == "measureChart"), None)
                else:
                    bar = next((c for c in charts
                                if c["measureId"] == mid and c["type"] == "bar"), None)
                if bar is None:
                    failures.append(f"{mid}: no bar chart found on {url}")
                else:
                    check_bar(mid, bar, expected, failures)
                if decrease:
                    traj = next((c for c in charts
                                 if c["measureId"] == mid and c["type"] == "line"), None)
                    if traj is None:
                        failures.append(f"{mid}: no trajectory chart found on {url}")
                    else:
                        check_flipped_trajectory(mid, traj, series_by_id[mid], failures)
                # The card legend must now advertise the teal swatch.
                if not url.startswith("best-in-nation"):
                    # Attribute selector: the id contains a dot (measure-P6.M1a),
                    # which a bare #id selector would parse as a class boundary.
                    legend = await page.text_content(f'[id="measure-{mid}"]') or ""
                    if "Meets Target" not in legend:
                        failures.append(f"{mid}: card shows no 'Meets Target' legend entry")
                print(f"  {mid} on {url}: checked")
        await browser.close()

    if failures:
        print(f"\nFAIL - {len(failures)} problem(s):")
        for f in failures:
            print(f"  * {f}")
        return 1
    print("\nPASS - all four 2026 actuals present, teal, and P6 axes flipped")
    return 0


def main():
    server = start_server()
    try:
        return asyncio.run(run())
    finally:
        server.terminate()


if __name__ == "__main__":
    sys.exit(main())
