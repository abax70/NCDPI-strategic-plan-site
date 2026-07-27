"""Verify the BiN measure-ID chips (best-in-nation.html).

verify-charts.py covers the 8 pillar pages but not the BiN carousel; this
is its BiN companion, born from the 7/24 chip build. Checks, for all 14
measures as the carousel advances:
  - chip text equals measures.json's measureId
  - chip background resolves to a real pillar tint (not transparent),
    and follows the measure's pillar (P8.M2 is the one non-P1 measure)
  - zero console/page errors
Run: python tools/verify-bin-chips.py   (needs playwright, like verify-charts)
"""
import json
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parent.parent
PORT = 8813

measures = json.loads((REPO / "data/measures.json").read_text(encoding="utf-8"))
expected = [(m["measureId"], m["pillarNumber"], m["name"]) for m in measures]

server = subprocess.Popen(
    [sys.executable, "-m", "http.server", str(PORT)], cwd=REPO,
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)

failures = []
try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 2400})
        errors = []
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(f"http://localhost:{PORT}/best-in-nation.html")
        page.wait_for_timeout(2000)

        for i, (mid, pnum, name) in enumerate(expected):
            if i > 0:
                page.click('.carousel-btn[aria-label="Next measure"]')
                page.wait_for_timeout(400)
            badge = page.locator(".measure-header .action-id-badge")
            text = badge.inner_text().strip()
            bg = badge.evaluate("el => getComputedStyle(el).backgroundColor")
            ok = text == mid
            tint_ok = bg not in ("rgba(0, 0, 0, 0)", "transparent", "")
            status = "OK " if (ok and tint_ok) else "FAIL"
            if not (ok and tint_ok):
                failures.append((mid, text, bg))
            print(f"{status} {i+1:2d}. chip={text:8s} expect={mid:8s} P{pnum} bg={bg}  ({name})")

        if errors:
            failures.append(("console", errors, ""))
            print("CONSOLE ERRORS:", errors)
        browser.close()
finally:
    server.terminate()

print("RESULT:", "FAIL " + repr(failures) if failures else "PASS - 14 chips, tints, console clean")
sys.exit(1 if failures else 0)
