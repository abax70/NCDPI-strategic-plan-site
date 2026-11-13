"""
Static contrast regression check for pillar.html's hero.

Why this exists (S.025): pillar.html binds its hero colours to per-pillar CSS
custom properties at runtime, so neither a code-only review nor axe/pa11y on a
single URL can exhaustively check every pillar's contrast. In Session 25 we
shipped with P3/P4/P5/P6 heroes failing WCAG AA because nothing in the skill
exercised those pillar variants. This script is a deterministic, fast
(millisecond) static guard: parse the pillar tokens out of pillar.html,
compute the WCAG 2.x contrast for a chosen hero design variant, and fail
loudly if any pillar regresses.

Design variants this script can gate (see --variant):

  current — The shipping hybrid design (S.025).
    DARK family (P1/P2/P7/P8): hero-left solid var(--pillarN), text white.
    LIGHT family (P3/P4/P5/P6): continuous --pcolor → white gradient, text
    navy #003A70, worst-case contrast at the leftmost text pixel.

  a — Vertical light→dark gradient (PDF-style). Text is navy for ALL pillars
    and sits on the near-white top band of a `linear-gradient(to bottom,
    #FFFFFF 0% → #FFFFFF 55% → var(--pcolor) 100%)`. The white plateau covers
    the text anchor so contrast is structurally trivial; we still sample to
    guard against drift into the saturated band.

  d1 — Horizontal hard-stop, pcolor-dominant. Hero-left gradient:
    `linear-gradient(to right, var(--pcolor) 0% → var(--pcolor) 55% →
    #FFFFFF 100%)`. Text colour follows family (white/navy). In the text
    region (0–55% of the panel width) the bg is full --pcolor, so the
    contrast math is identical to `current`.

  d2 — Horizontal hard-stop, pale-tint end. Hero-left gradient:
    `linear-gradient(to right, var(--pcolor) 0% → mix(85% white, 15% pcolor)
    100%)`. For DARK pillars, the worst case for white text is the lightest
    point (rightmost, pale tint). For LIGHT pillars, navy's worst case is
    the leftmost (full --pcolor), same as current.

Regression behaviour:
  exit 0  — every pair meets its threshold (or exceeds it).
  exit 1  — at least one pair fails; a per-row table prints to stderr with the
            pillar, colours, ratio, threshold, and the recommended remediation
            hint (token swap, not a --pillarN value change — values are locked).
  exit 2  — couldn't parse pillar.html (file missing or :root block malformed).

Invocation:
    python verify_pillar_contrast.py [--pillar-html PATH] [--variant VARIANT]

Designed to be called as a pre-flight from run_external_audit.py and as a
standalone /dashboard-accessibility Phase-0 check. It is ALSO the ship gate
for Tweak 8 (hero-preview.html → pillar.html promotion).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Keep this file in sync with pillar.html's switchPillar() mapping.
LIGHT_PILLARS = {3, 4, 5, 6}
DARK_PILLARS = {1, 2, 7, 8}

# Hero text colours per family (matches pillar.html switchPillar() logic).
WHITE = (255, 255, 255)
NAVY = (0x00, 0x3A, 0x70)  # #003A70

# All hero text is >= 14pt bold, so the WCAG threshold is 3.0 ("large text").
# We keep a stricter 4.5 threshold available for reference / future tightening.
LARGE_TEXT_AA = 3.0
NORMAL_TEXT_AA = 4.5

VARIANTS = ("current", "a", "d1", "d2")


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rel_luminance(rgb: tuple[int, int, int]) -> float:
    def ch(c: int) -> float:
        s = c / 255.0
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    la, lb = rel_luminance(a), rel_luminance(b)
    lo, hi = sorted((la, lb))
    return (hi + 0.05) / (lo + 0.05)


def mix(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    """Linearly interpolate two sRGB colours. t=0 → a, t=1 → b. Matches the
    behaviour of CSS `color-mix(in srgb, a (1-t)*100%, b t*100%)` closely
    enough for contrast estimation (CSS does the math in sRGB by default)."""
    return (
        int(round(a[0] * (1 - t) + b[0] * t)),
        int(round(a[1] * (1 - t) + b[1] * t)),
        int(round(a[2] * (1 - t) + b[2] * t)),
    )


def parse_pillar_tokens(html_path: Path) -> dict[str, tuple[int, int, int]]:
    """Extract --pillarN and --pillarN-text declarations from the :root block.

    Deliberately conservative: reads the file as text, finds the first `:root`
    CSS block, pulls `--pillarN: #xxxxxx;` and `--pillarN-text: #xxxxxx;`
    lines out of it. If the file changes structure significantly, raise so a
    human notices instead of silently returning a partial map.
    """
    text = html_path.read_text(encoding="utf-8")
    # Grab everything from ":root {" to the matching "}".
    # Not bulletproof if someone puts a `}` inside a string, but pillar.html
    # doesn't do that today. If it ever does, this raises and we fix it.
    m = re.search(r":root\s*\{([^}]+)\}", text)
    if not m:
        raise SystemExit("ERROR: could not find :root block in pillar.html")
    root_body = m.group(1)

    tokens: dict[str, tuple[int, int, int]] = {}
    for match in re.finditer(
        r"--(pillar\d(?:-text)?)\s*:\s*(#[0-9A-Fa-f]{3,8})\s*;",
        root_body,
    ):
        name = match.group(1)
        value = match.group(2)
        tokens[name] = hex_to_rgb(value)
    return tokens


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def sample_points(variant: str, n: int, pcolor: tuple[int, int, int]) -> list[dict]:
    """Return the (text_colour, bg_colour, label) triples that matter for
    contrast on a given variant × pillar. Worst case per variant:

      current: as in S.025 hybrid. Single sample at the binding edge.
      a:       navy text on the near-white plateau (text anchor sits here).
               Also sample the saturated bottom as a reference.
      d1:      same binding edge as current (full --pcolor, text region).
      d2:      for dark pillars, sample at the pale-tint end (lightest, worst
               case for white text). For light pillars, navy worst case is the
               full-pcolor left edge (same as current).
    """
    is_dark = n in DARK_PILLARS
    family_text = WHITE if is_dark else NAVY
    pale_tint = mix(WHITE, pcolor, 0.15)  # mirrors CSS `color-mix(... 15%, white)`

    if variant == "current":
        if is_dark:
            return [{
                "text": WHITE, "bg": pcolor,
                "label": "white-on-pcolor (solid hero-left)",
                "binding": True,
            }]
        return [{
            "text": NAVY, "bg": pcolor,
            "label": "navy-on-pcolor (gradient left edge, worst case)",
            "binding": True,
        }]

    if variant == "a":
        return [
            {
                "text": NAVY, "bg": WHITE,
                "label": "navy-on-white (vertical gradient, text plateau)",
                "binding": True,
            },
            {
                "text": NAVY, "bg": pcolor,
                "label": "navy-on-pcolor (gradient bottom, reference only)",
                "binding": False,
            },
        ]

    if variant == "d1":
        # Gradient is pcolor 0%→55% then fades to white at 100%, but the text
        # region lives inside 0–55%, so bg is full --pcolor there. Binding
        # contrast is identical to `current`.
        if is_dark:
            return [{
                "text": WHITE, "bg": pcolor,
                "label": "white-on-pcolor (D1 text region is solid pcolor)",
                "binding": True,
            }]
        return [{
            "text": NAVY, "bg": pcolor,
            "label": "navy-on-pcolor (D1 text region is solid pcolor)",
            "binding": True,
        }]

    if variant == "d2":
        if is_dark:
            return [
                {
                    "text": WHITE, "bg": pale_tint,
                    "label": "white-on-pale-tint (D2 lightest end, worst for white)",
                    "binding": True,
                },
                {
                    "text": WHITE, "bg": pcolor,
                    "label": "white-on-pcolor (D2 left edge, reference)",
                    "binding": False,
                },
            ]
        return [{
            "text": NAVY, "bg": pcolor,
            "label": "navy-on-pcolor (D2 left edge, same binding as current)",
            "binding": True,
        }]

    raise SystemExit(f"ERROR: unknown variant {variant!r}; choose from {VARIANTS}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve()
    # Repo root is three levels up: .claude/skills/dashboard-accessibility/ -> repo root
    repo_root = here.parent.parent.parent.parent
    parser.add_argument(
        "--pillar-html",
        type=Path,
        default=repo_root / "pillar.html",
        help="Path to pillar.html (default: auto-located relative to this script)",
    )
    parser.add_argument(
        "--variant",
        choices=VARIANTS,
        default="current",
        help="Which hero design variant to evaluate (default: current).",
    )
    args = parser.parse_args()

    if not args.pillar_html.is_file():
        print(f"ERROR: pillar.html not found at {args.pillar_html}", file=sys.stderr)
        return 2

    tokens = parse_pillar_tokens(args.pillar_html)

    rows: list[dict[str, object]] = []
    any_fail = False

    for n in range(1, 9):
        pcolor_name = f"pillar{n}"
        if pcolor_name not in tokens:
            print(f"ERROR: missing --{pcolor_name} token in pillar.html", file=sys.stderr)
            return 2
        pcolor = tokens[pcolor_name]
        family = "dark" if n in DARK_PILLARS else "light"

        for sample in sample_points(args.variant, n, pcolor):
            ratio = round(contrast(sample["text"], sample["bg"]), 2)
            threshold = LARGE_TEXT_AA
            # Only BINDING samples gate pass/fail. Reference samples are
            # informational — they help the reader see why a variant is / is not
            # safer than another, without failing the run on a non-text pixel.
            passes = ratio >= threshold
            if sample["binding"] and not passes:
                any_fail = True
            rows.append({
                "pillar": n,
                "family": family,
                "pcolor_hex": rgb_to_hex(pcolor),
                "text_hex": rgb_to_hex(sample["text"]),
                "bg_hex": rgb_to_hex(sample["bg"]),
                "pairing": sample["label"],
                "ratio": ratio,
                "threshold": threshold,
                "binding": sample["binding"],
                "status": ("PASS" if passes else "FAIL") if sample["binding"] else "info",
            })

    # Print a readable table.
    print(f"Pillar hero contrast — variant: {args.variant}")
    print(
        f"{'P':>2}  {'fam':<5}  {'text':<8}  {'bg':<8}  "
        f"{'ratio':>6}  {'thr':>4}  status  pairing"
    )
    print("-" * 96)
    for r in rows:
        print(
            f"{r['pillar']:>2}  {r['family']:<5}  {r['text_hex']:<8}  "
            f"{r['bg_hex']:<8}  {r['ratio']:>6}  {r['threshold']:>4}  "
            f"{r['status']:<6}  {r['pairing']}"
        )

    if any_fail:
        print("", file=sys.stderr)
        print(
            f"FAIL: variant {args.variant!r} regresses WCAG AA for hero text on "
            "at least one pillar.",
            file=sys.stderr,
        )
        print(
            "Remediation: DO NOT edit --pillarN token VALUES (graphics-team-locked).\n"
            "Instead, adjust the VARIANT design — tighter gradient stops, a different\n"
            "text colour, or choose a different variant entirely.",
            file=sys.stderr,
        )
        return 1

    print("")
    print(
        f"PASS: all binding pairings for variant {args.variant!r} meet WCAG AA "
        "large-text threshold."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
