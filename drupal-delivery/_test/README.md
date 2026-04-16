# Demo sandbox — `_test/`

These are **simulation pages** for trying the dashboard inside a
fake Drupal-like host. They are NOT part of the delivery to the
webmaster. Do not copy `_test/` to the server.

## How to run the demo

Double-click `START-DEMO.bat`.

That launches a local Python web server on port 8765 and opens
two browser tabs:

- **Landing page:** `http://localhost:8765/drupal-delivery/_test/landing.html`
- **Pillar page:** `http://localhost:8765/drupal-delivery/_test/pillar.html?p=2`

Keep the black console window open during the demo. Closing it
stops the server.

## Why a local server?

The dashboard loads measure and pillar data by `fetch()`-ing
JSON files at runtime. Browsers refuse to let `fetch()` read
local files when you open an `.html` via `file:///` — it's a
cross-origin security rule. A tiny localhost server bypasses
that restriction without installing anything.

Python ships with Windows' recent versions, which is why
START-DEMO.bat uses `python -m http.server`. If Python isn't on
PATH, see "Troubleshooting" below.

## What the host chrome is doing

The black bar at the top of each page (`[Drupal-sim site header]`)
is deliberately styled with Georgia serif and red link colors.
It's there to prove a point: even with an aggressive host theme
that sets `:root { --navy: red !important }` and
`h1, h2, h3 { color: red }`, the dashboard below renders with
our Source Sans Pro, our navy, and our pillar colors — because
every rule in `sp-landing.css` and `sp-pillar.css` is scoped
under `.sp-dashboard`.

If scoping ever breaks, you'll see the dashboard go red/Georgia.
That's the canary.

## Troubleshooting

**Nothing happens when I double-click `START-DEMO.bat`.**
Python isn't on PATH. Open PowerShell, `cd` into this folder,
and run `python -m http.server 8765` manually, then visit the
URLs above in a browser.

**Port 8765 is already in use.**
Edit `START-DEMO.bat` and change `8765` to any other free port
(e.g. `9000`). Update the two `start "" http://localhost:...`
lines to match.

**The server runs but pages are blank.**
Check the console for Python errors. Most commonly: the CWD
walked to the wrong place — confirm you see
`Serving HTTP on :: port 8765` and not a 404 when you navigate.

**Images are missing.**
The JS in `sp-landing.js` / `sp-pillar.js` rewrites every
`images/...` path through `SP_CONFIG.basePath`. If your test
host pages have a broken `SP_CONFIG.basePath`, images will 404.
These test pages use `basePath: "../assets/"` which is correct
when served from `/drupal-delivery/_test/`.
