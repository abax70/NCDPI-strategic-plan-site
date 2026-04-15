"""
Build script for the Drupal delivery package.

Reads the standalone index.html and pillar.html, splits CSS + JS + HTML,
scopes CSS under .sp-dashboard, IIFE-wraps JS with a configurable SP_CONFIG,
rewrites image paths for renamed (no-spaces) directories, and writes:

    assets/css/sp-landing.css
    assets/css/sp-pillar.css
    assets/js/sp-landing.js
    assets/js/sp-pillar.js
    assets/data/measures.json         (paths rewritten)
    assets/data/pillar-data.json      (unchanged copy)
    option-a-embed/landing-page.html  (self-contained paste block)
    option-a-embed/pillar-page.html
    option-b-library/fragment-landing.html
    option-b-library/fragment-pillar.html
    option-b-library/strategic_plan.libraries.yml

Run from the project root:
    python drupal-delivery/_build.py

The original index.html and pillar.html are NOT modified.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from textwrap import dedent

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DELIVERY = ROOT / "drupal-delivery"
ASSETS = DELIVERY / "assets"
CSS_DIR = ASSETS / "css"
JS_DIR = ASSETS / "js"
DATA_DIR = ASSETS / "data"
OPT_A = DELIVERY / "option-a-embed"
OPT_B = DELIVERY / "option-b-library"

# ---------------------------------------------------------------------------
# Image path rewrites: original-standalone -> drupal-delivery (no spaces).
# These apply to CSS url(), inline HTML src=/href=, and JSON fields.
# ---------------------------------------------------------------------------
IMAGE_PATH_REWRITES = [
    ("images/Background Patterns/", "images/background-patterns/"),
    ("images/Pillar Icons/Icons Only/", "images/pillar-icons/"),
    ("images/Measure Graphics/", "images/measure-graphics/"),
    ("images/Badges/", "images/badges/"),
    # Flatten the logo tree to a single folder.
    (
        "images/Achieving Academic Excellence Logos/AEE Logos with Tagline/",
        "images/logos/",
    ),
]


def rewrite_image_paths(text: str) -> str:
    """Apply all image path rewrites in order."""
    for old, new in IMAGE_PATH_REWRITES:
        text = text.replace(old, new)
    return text


# ---------------------------------------------------------------------------
# CSS scoping.
#
# Everything inside the <style> block gets prefixed with `.sp-dashboard `,
# except:
#   :root             -> .sp-dashboard             (variables live on wrapper)
#   body              -> .sp-dashboard             (body rules move to wrapper)
#   body.drawer-open  -> REMOVED                   (handled via JS inline style
#                                                    so we never touch body)
#   *                 -> .sp-dashboard *           (box-sizing scope only;
#                                                    the margin/padding reset
#                                                    is REMOVED — the plan
#                                                    explicitly drops it to
#                                                    avoid clobbering Drupal
#                                                    defaults)
#
# We handle nested @media { ... } blocks by rewriting rules at any depth.
# ---------------------------------------------------------------------------
WRAPPER = ".sp-dashboard"


def scope_selector(sel: str) -> str:
    """Rewrite a single selector (no commas) under .sp-dashboard."""
    s = sel.strip()
    if not s:
        return s
    # :root becomes the wrapper so --css-vars apply inside.
    if s == ":root":
        return WRAPPER
    # body becomes the wrapper (wrapper carries font-family, color, etc.)
    if s == "body":
        return WRAPPER
    # We drop body.drawer-open (handled via inline JS style) — caller filters it.
    if s == "body.drawer-open":
        return ""
    # Universal selector: we only want the box-sizing rule, scoped to wrapper.
    if s == "*":
        return f"{WRAPPER} *, {WRAPPER} *::before, {WRAPPER} *::after"
    # Everything else: prefix with wrapper.
    return f"{WRAPPER} {s}"


def scope_selector_list(sel_list: str) -> str:
    """Rewrite a comma-separated selector list under .sp-dashboard."""
    parts = [scope_selector(s) for s in sel_list.split(",")]
    parts = [p for p in parts if p]
    return ", ".join(parts)


def scope_css(css: str) -> str:
    """
    Walk the CSS character-by-character, rewriting selectors before each `{`
    while preserving @media blocks, comments, and whitespace.

    We also DELETE these rules entirely:
      * { margin: 0; padding: 0; box-sizing: border-box; }   (drop the reset)
      body.drawer-open { overflow: hidden; }                  (JS-driven now)
    ...and replace them with a minimal .sp-dashboard *, ::before, ::after
    box-sizing rule so we don't lose that.
    """
    out = []
    i = 0
    n = len(css)

    # Stack of context chars: '{' for normal rule block, 'M' for @media block.
    # We only rewrite selectors at top level or inside @media.
    def find_block_end(start: int) -> int:
        """Return index of the closing `}` matching the `{` at position start."""
        depth = 0
        j = start
        while j < n:
            ch = css[j]
            if ch == '/' and j + 1 < n and css[j + 1] == '*':
                # Skip comment.
                end = css.find('*/', j + 2)
                j = n if end == -1 else end + 2
                continue
            if ch == '"' or ch == "'":
                # Skip string.
                quote = ch
                j += 1
                while j < n and css[j] != quote:
                    if css[j] == '\\':
                        j += 2
                    else:
                        j += 1
                j += 1
                continue
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return j
            j += 1
        return n

    def rewrite_rule_block(chunk: str) -> str:
        """Rewrite selectors inside a rule-level chunk (top level or @media body)."""
        out_chunk = []
        j = 0
        m = len(chunk)
        while j < m:
            ch = chunk[j]
            # Comment
            if ch == '/' and j + 1 < m and chunk[j + 1] == '*':
                end = chunk.find('*/', j + 2)
                if end == -1:
                    out_chunk.append(chunk[j:])
                    j = m
                else:
                    out_chunk.append(chunk[j:end + 2])
                    j = end + 2
                continue
            # Whitespace: copy through
            if ch in ' \t\r\n':
                out_chunk.append(ch)
                j += 1
                continue
            # At-rule? (we shouldn't see @media here because caller slices them out,
            # but we might see @supports etc. Treat them as top-level passthrough.)
            if ch == '@':
                # find first `{` to learn whether it's a block at-rule
                brace = chunk.find('{', j)
                semi = chunk.find(';', j)
                if brace == -1 or (semi != -1 and semi < brace):
                    # at-rule statement like @charset;
                    end = semi if semi != -1 else m
                    out_chunk.append(chunk[j:end + 1])
                    j = end + 1
                    continue
                # block at-rule (keep prelude, recurse into body)
                prelude = chunk[j:brace]
                # Find matching close
                depth = 0
                k = brace
                while k < m:
                    c = chunk[k]
                    if c == '{':
                        depth += 1
                    elif c == '}':
                        depth -= 1
                        if depth == 0:
                            break
                    k += 1
                inner = chunk[brace + 1:k]
                out_chunk.append(prelude)
                out_chunk.append('{')
                out_chunk.append(rewrite_rule_block(inner))
                out_chunk.append('}')
                j = k + 1
                continue
            # Regular rule: grab selectors up to the next `{`
            brace = chunk.find('{', j)
            if brace == -1:
                out_chunk.append(chunk[j:])
                break
            # Find matching closing `}` for this block
            depth = 0
            k = brace
            while k < m:
                c = chunk[k]
                if c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0:
                        break
                k += 1
            selector_raw = chunk[j:brace]
            body = chunk[brace + 1:k]

            # Skip body.drawer-open rule entirely (JS handles scroll lock).
            if selector_raw.strip() == "body.drawer-open":
                # swallow the whole rule, preserving no leading whitespace
                j = k + 1
                continue
            # Drop the `*` reset — replace it with a box-sizing-only rule,
            # plus force color/font-family inheritance. Without the second
            # rule, Drupal themes that set element selectors directly (e.g.
            # `h1 { color: red }` or `a { font-family: Georgia }`) would
            # leak into the dashboard, because our class selectors like
            # `.sp-dashboard .pillar-hero-title` do not restate color/font
            # (they inherit). Forcing `color: inherit` here makes every
            # descendant walk back to the `.sp-dashboard` wrapper's color,
            # which is our navy. Our own class rules (higher specificity)
            # still win when they explicitly set color or font-family.
            if selector_raw.strip() == "*":
                out_chunk.append(
                    f"{WRAPPER} *, {WRAPPER} *::before, {WRAPPER} *::after "
                    "{ box-sizing: border-box; color: inherit; "
                    "font-family: inherit; }"
                )
                j = k + 1
                continue

            scoped = scope_selector_list(selector_raw)
            out_chunk.append(scoped)
            out_chunk.append('{')
            out_chunk.append(body)
            out_chunk.append('}')
            j = k + 1
        return ''.join(out_chunk)

    return rewrite_rule_block(css)


# ---------------------------------------------------------------------------
# JS transformation
#
# 1) Wrap the page script in an IIFE with 'use strict'.
# 2) Replace `document.body.classList.add/remove('drawer-open')` with direct
#    `document.body.style.overflow` manipulation (our scroll-lock alternative).
# 3) Replace `document.documentElement.style.setProperty(...)` with the wrapper
#    element (.sp-dashboard) so CSS vars apply in scope.
# 4) Change hardcoded fetch('data/...') to use SP_CONFIG.basePath.
# 5) Rewrite `images/...` paths in JS string literals (PILLAR_ICONS, etc.) to
#    prefix with SP_CONFIG.basePath.
# 6) Rewrite hardcoded `pillar.html?p=...` hrefs at runtime to use
#    SP_CONFIG.pillarPageUrl. Handled in a post-mount helper we inject.
# 7) Replace window.allMeasures/window.currentMeasureIndex with scoped vars.
# ---------------------------------------------------------------------------


def transform_js(js: str, page: str) -> str:
    """
    page: 'landing' or 'pillar' — determines which boilerplate helpers to inject.
    """
    src = js

    # 1. Rewrite image paths in string literals. Any 'images/...' becomes
    #    SP_CONFIG.basePath + 'images/...' by first normalizing the dir name,
    #    then string-concatenating the config prefix.
    src = rewrite_image_paths(src)

    # 2. Rewrite fetch() calls to prepend SP_CONFIG.basePath
    src = re.sub(
        r"fetch\(\s*(['\"])(data/[^'\"]+)\1\s*\)",
        r"fetch(SP_CONFIG.basePath + \1\2\1)",
        src,
    )

    # 3. Rewrite `images/` paths in quoted strings to use SP_CONFIG.basePath.
    #    This handles iconUrl fallbacks and PILLAR_ICONS dict values.
    src = re.sub(
        r"(['\"])(images/[^'\"]+)\1",
        r"SP_CONFIG.basePath + \1\2\1",
        src,
    )

    # 4. Scroll-lock: replace drawer-open class manipulation with
    #    direct overflow manipulation on body. This avoids any CSS collision
    #    with Drupal's own body selectors.
    src = src.replace(
        "document.body.classList.add('drawer-open');",
        "document.body.style.overflow = 'hidden'; /* scroll lock */",
    )
    src = src.replace(
        "document.body.classList.remove('drawer-open');",
        "document.body.style.overflow = ''; /* scroll unlock */",
    )

    # 5. Target the wrapper element instead of documentElement for CSS vars.
    #    We assume SP_ROOT is the .sp-dashboard wrapper element, resolved at boot.
    src = src.replace(
        "var root = document.documentElement;",
        "var root = SP_ROOT;",
    )

    # 6. window.* globals -> locals (IIFE-scoped).
    src = src.replace("window.allMeasures", "allMeasures")
    src = src.replace("window.currentMeasureIndex", "currentMeasureIndex")
    src = src.replace("window.pillarData", "pillarData")
    # Declare these at the top of the IIFE below.

    # 7. Scope DOM queries that hit global document -> scope to SP_ROOT
    #    where feasible. The wrapper contains all our dashboard markup, so
    #    selectors become scoped lookups. Keep document.* for things that
    #    must live outside (resize, keydown, fonts.ready, URL history).
    #    We target only the specific selectors used in the HTML.
    scoped_targets = [
        # landing
        ".carousel-select", ".carousel-counter",
        '.carousel-btn[aria-label="Previous measure"]',
        '.carousel-btn[aria-label="Next measure"]',
        ".measure-header", ".current-value .big-number",
        ".current-value .context", ".notes-section",
        ".sidebar-right", ".pillar-link",
        ".carousel-header", ".sidebar-panel-title",
        ".sidebar-panel", ".sidebar-panel.collapsed",
        ".sidebar-panel.collapsed > *:not(.sidebar-panel-title)",
        # pillar
        ".pillar-link[data-pillar]", ".tab-btn", ".tab-panel",
        ".pillar-switcher", ".pillar-content",
    ]
    # document.querySelector("X") -> SP_ROOT.querySelector("X")
    src = re.sub(
        r"document\.querySelector(\s*\()",
        r"SP_ROOT.querySelector\1",
        src,
    )
    src = re.sub(
        r"document\.querySelectorAll(\s*\()",
        r"SP_ROOT.querySelectorAll\1",
        src,
    )
    # document.getElementById is OK to keep (IDs are unique inside the wrapper)
    # — but Drupal pages may have ID collisions. Safer to scope:
    src = re.sub(
        r"document\.getElementById\(\s*(['\"])([^'\"]+)\1\s*\)",
        r"SP_ROOT.querySelector('#\2')",
        src,
    )

    # 8. Rewrite pillar.html / index.html links.
    #    Replace string literals `pillar.html?p=N` with template using SP_CONFIG.
    #    We match both `'pillar.html?p=' +` and `"pillar.html?p=1"` forms.
    src = re.sub(
        r"(['\"])pillar\.html\?p=(\1)",
        r"\1\1 + SP_CONFIG.pillarPageUrl + '?p=\1\1",
        src,
    )
    # Simpler: handle the concrete case `'pillar.html?p='` used in a concat.
    src = src.replace(
        "'pillar.html?p='",
        "SP_CONFIG.pillarPageUrl + '?p='",
    )
    src = src.replace(
        '"pillar.html?p="',
        'SP_CONFIG.pillarPageUrl + "?p="',
    )

    # 9. Final IIFE + config-resolution boilerplate.
    header_lines = [
        "/* Scoped strategic-plan dashboard script — do not edit directly.",
        f"   Generated from source; page = '{page}'. */",
        "(function () {",
        "  'use strict';",
        "",
        "  /* SP_CONFIG: defaults merged with any page-level override set",
        "     BEFORE this script is loaded. See README for the shape. */",
        "  var SP_CONFIG_DEFAULTS = {",
        "    basePath: '/sites/default/files/strategic-plan/',",
        "    pillarPageUrl: '/strategic-plan/pillar',",
        "    landingPageUrl: '/strategic-plan'",
        "  };",
        "  var userCfg = (typeof window !== 'undefined' && window.SP_CONFIG) || {};",
        "  var SP_CONFIG = {",
        "    basePath: userCfg.basePath != null ? userCfg.basePath : SP_CONFIG_DEFAULTS.basePath,",
        "    pillarPageUrl: userCfg.pillarPageUrl != null ? userCfg.pillarPageUrl : SP_CONFIG_DEFAULTS.pillarPageUrl,",
        "    landingPageUrl: userCfg.landingPageUrl != null ? userCfg.landingPageUrl : SP_CONFIG_DEFAULTS.landingPageUrl",
        "  };",
        "  /* Ensure basePath ends with '/' so string concatenation builds clean URLs. */",
        "  if (SP_CONFIG.basePath && SP_CONFIG.basePath.slice(-1) !== '/') {",
        "    SP_CONFIG.basePath += '/';",
        "  }",
        "",
        "  /* Resolve the wrapper element once. All DOM work is scoped to it. */",
        "  var SP_ROOT = document.querySelector('.sp-dashboard');",
        "  if (!SP_ROOT) {",
        "    console.warn('[sp-dashboard] .sp-dashboard wrapper not found; script will not initialize.');",
        "    return;",
        "  }",
        "",
        "  /* Page-local state that used to live on window.* */",
        "  var allMeasures = null;          /* landing */",
        "  var currentMeasureIndex = 0;     /* landing */",
        "  var pillarData = null;           /* pillar */",
        "",
        "  /* Rewrite hardcoded pillar.html / index.html links AND bare `images/`",
        "     src paths inside the wrapper so they resolve to the configured",
        "     SP_CONFIG values. Drupal serves our page at an arbitrary alias,",
        "     so the static HTML fragment's relative paths must be rewritten at",
        "     mount time and after every dynamic render. A data-sp-rewritten",
        "     flag guards against the MutationObserver re-processing nodes. */",
        "  function rewriteLocalLinks(root) {",
        "    if (!root || root.nodeType !== 1) root = SP_ROOT;",
        "    /* Handle the root node itself if it's an <a> or <img> — our",
        "       MutationObserver hands us individual added nodes, and those",
        "       may BE anchors or images rather than containers. */",
        "    if (root.tagName === 'A') _fixBareHref(root);",
        "    if (root.tagName === 'IMG') {",
        "      var rs = root.getAttribute('data-sp-src');",
        "      if (rs && !root.getAttribute('data-sp-rewritten')) {",
        "        root.setAttribute('src', SP_CONFIG.basePath + rs);",
        "        root.setAttribute('data-sp-rewritten', '1');",
        "      } else if (!root.getAttribute('data-sp-rewritten')) {",
        "        var rs2 = root.getAttribute('src');",
        "        if (rs2 && rs2.indexOf('images/') === 0) {",
        "          root.setAttribute('src', SP_CONFIG.basePath + rs2);",
        "        }",
        "        root.setAttribute('data-sp-rewritten', '1');",
        "      }",
        "    }",
        "    var anchors = root.querySelectorAll",
        "      ? root.querySelectorAll('a[href]:not([data-sp-rewritten])')",
        "      : [];",
        "    for (var i = 0; i < anchors.length; i++) {",
        "      var a = anchors[i];",
        "      var href = a.getAttribute('href');",
        "      if (href) {",
        "        var nextHref = null;",
        "        if (href.indexOf('pillar.html') === 0) {",
        "          nextHref = href.replace('pillar.html', SP_CONFIG.pillarPageUrl);",
        "        } else if (href === 'index.html') {",
        "          nextHref = SP_CONFIG.landingPageUrl;",
        "        }",
        "        if (nextHref != null && nextHref !== href) a.setAttribute('href', nextHref);",
        "      }",
        "      a.setAttribute('data-sp-rewritten', '1');",
        "    }",
        "    /* Static images use data-sp-src so the browser doesn't fire a",
        "       404 against the page's own URL before JS runs. We copy the",
        "       real path into src prefixed with SP_CONFIG.basePath. */",
        "    var imgs = root.querySelectorAll",
        "      ? root.querySelectorAll('img[data-sp-src]:not([data-sp-rewritten])')",
        "      : [];",
        "    for (var j = 0; j < imgs.length; j++) {",
        "      var im = imgs[j];",
        "      var dp = im.getAttribute('data-sp-src');",
        "      if (dp) im.setAttribute('src', SP_CONFIG.basePath + dp);",
        "      im.setAttribute('data-sp-rewritten', '1');",
        "    }",
        "    /* Also catch any img[src] that JS might have built with a raw",
        "       `images/...` path. (Shouldn't happen — our transforms prefix",
        "       with SP_CONFIG.basePath — but this is a safety net.) */",
        "    var stragglers = root.querySelectorAll",
        "      ? root.querySelectorAll('img[src]:not([data-sp-rewritten])')",
        "      : [];",
        "    for (var s = 0; s < stragglers.length; s++) {",
        "      var im2 = stragglers[s];",
        "      var src2 = im2.getAttribute('src');",
        "      if (src2 && src2.indexOf('images/') === 0) {",
        "        im2.setAttribute('src', SP_CONFIG.basePath + src2);",
        "      }",
        "      im2.setAttribute('data-sp-rewritten', '1');",
        "    }",
        "  }",
        "  rewriteLocalLinks(SP_ROOT);",
        "  /* Catch anchors/images added by JS renders (switchMeasure, switchPillar",
        "     build action cards, motion cards, etc.) AND bare `images/` src",
        "     assignments that existing code does like `headerIcon.src = m.iconUrl`.",
        "     The data-sp-rewritten flag prevents re-processing; we also clear",
        "     the flag off an <img> when its src is REassigned by our own code,",
        "     so consecutive renders with new paths still get prefixed. */",
        "  function _fixBareImg(el) {",
        "    if (!el || el.tagName !== 'IMG') return;",
        "    var s = el.getAttribute('src');",
        "    if (!s || s.indexOf('images/') !== 0) return;",
        "    var next = SP_CONFIG.basePath + s;",
        "    if (next !== s) el.setAttribute('src', next);",
        "  }",
        "  function _fixBareHref(a) {",
        "    if (!a || a.tagName !== 'A') return;",
        "    var h = a.getAttribute('href');",
        "    if (!h) return;",
        "    var next = null;",
        "    if (h.indexOf('pillar.html') === 0) {",
        "      next = h.replace('pillar.html', SP_CONFIG.pillarPageUrl);",
        "    } else if (h === 'index.html') {",
        "      next = SP_CONFIG.landingPageUrl;",
        "    }",
        "    /* Only rewrite if the new value actually differs — prevents an",
        "       infinite loop when SP_CONFIG.pillarPageUrl happens to equal",
        "       the string 'pillar.html' (e.g. during local testing where the",
        "       webmaster hasn't configured a real Drupal alias yet). */",
        "    if (next != null && next !== h) a.setAttribute('href', next);",
        "  }",
        "  var _mo = new MutationObserver(function (mutations) {",
        "    for (var m = 0; m < mutations.length; m++) {",
        "      var mut = mutations[m];",
        "      if (mut.type === 'childList') {",
        "        for (var k = 0; k < mut.addedNodes.length; k++) {",
        "          if (mut.addedNodes[k].nodeType === 1) rewriteLocalLinks(mut.addedNodes[k]);",
        "        }",
        "      } else if (mut.type === 'attributes' && mut.attributeName === 'src') {",
        "        _fixBareImg(mut.target);",
        "      } else if (mut.type === 'attributes' && mut.attributeName === 'href') {",
        "        _fixBareHref(mut.target);",
        "      }",
        "    }",
        "  });",
        "  _mo.observe(SP_ROOT, {",
        "    childList: true,",
        "    subtree: true,",
        "    attributes: true,",
        "    attributeFilter: ['src', 'href']",
        "  });",
        "",
    ]
    footer = "\n})();\n"

    # Drop `var` redeclarations of the locals so our IIFE-top declarations win.
    src = re.sub(r"^\s*var\s+currentPillarIndex\s*=\s*0;\s*$", "", src, flags=re.MULTILINE)

    return "\n".join(header_lines) + src + footer


# ---------------------------------------------------------------------------
# Parse source HTML: return (css, body_fragment, js)
# ---------------------------------------------------------------------------


def parse_source(path: Path) -> tuple[str, str, str]:
    html = path.read_text(encoding="utf-8")

    # CSS
    m_style = re.search(r"<style>(.*?)</style>", html, flags=re.DOTALL)
    if not m_style:
        raise RuntimeError(f"No <style> block found in {path.name}")
    css = m_style.group(1)

    # <body>...</body>
    m_body = re.search(r"<body>(.*?)</body>", html, flags=re.DOTALL)
    if not m_body:
        raise RuntimeError(f"No <body> found in {path.name}")
    body_html = m_body.group(1).strip()

    # The last <script>...</script> (page-specific JS, not Chart.js CDN)
    script_blocks = list(re.finditer(r"<script>(.*?)</script>", html, flags=re.DOTALL))
    if not script_blocks:
        raise RuntimeError(f"No inline <script> block found in {path.name}")
    js = script_blocks[-1].group(1)

    return css, body_html, js


# ---------------------------------------------------------------------------
# Build a content-only HTML fragment from the source <body>.
# Strip the <script>/<noscript> chrome and wrap everything in
# <div class="sp-dashboard">...</div>.
# ---------------------------------------------------------------------------


# 1x1 transparent GIF — used as a src placeholder so the browser doesn't
# fire a 404 for the original `images/...` path before JS rewrites it.
_BLANK_PIXEL = "data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="


def build_fragment(body_html: str, page: str) -> str:
    # Remove the Chart.js CDN <script> tags and the page <script>; these get
    # attached separately via the CDN/includes step.
    cleaned = re.sub(r"<script[^>]*></script>", "", body_html, flags=re.DOTALL)
    cleaned = re.sub(r"<script>.*?</script>", "", cleaned, flags=re.DOTALL)
    cleaned = rewrite_image_paths(cleaned)

    # Replace static <img src="images/..."> with a data-src pattern. We
    # cannot leave the bare relative path in the markup because:
    #   - At parse time, the browser immediately fires a GET against the
    #     page's own URL + 'images/...', producing 404s.
    #   - The image's final URL depends on SP_CONFIG.basePath which is
    #     only known at runtime.
    # By swapping the real path into `data-sp-src` and using a 1x1
    # transparent GIF as src, we defer the load to JS rewriteLocalLinks().
    def _swap_src(m):
        full = m.group(0)
        path = m.group(1)
        # Only swap bare images/... paths; leave absolute URLs and data: URIs.
        if path.startswith("images/"):
            return full.replace(f'src="{path}"', f'src="{_BLANK_PIXEL}" data-sp-src="{path}"')
        return full

    cleaned = re.sub(r'<img\b[^>]*\bsrc="([^"]+)"[^>]*>', _swap_src, cleaned)

    # Wrap in .sp-dashboard. Drop any stray leading/trailing whitespace.
    wrapped = f'<div class="sp-dashboard">\n{cleaned.strip()}\n</div>\n'
    return wrapped


# ---------------------------------------------------------------------------
# Main build
# ---------------------------------------------------------------------------


def build():
    pages = [
        ("landing", ROOT / "index.html", CSS_DIR / "sp-landing.css", JS_DIR / "sp-landing.js"),
        ("pillar", ROOT / "pillar.html", CSS_DIR / "sp-pillar.css", JS_DIR / "sp-pillar.js"),
    ]

    fragments = {}
    for page, src, css_out, js_out in pages:
        css, body_html, js = parse_source(src)

        # CSS pipeline: rewrite image paths, prefix url() targets with ../
        # (CSS lives at assets/css/, images at assets/images/), then scope
        # under .sp-dashboard.
        css_pipeline = rewrite_image_paths(css)
        # url("images/...") and url('images/...') and url(images/...) all
        # need the `../` prefix since they resolve relative to the CSS file.
        css_pipeline = re.sub(
            r"url\(\s*(['\"]?)(images/)",
            r"url(\1../\2",
            css_pipeline,
        )
        css_pipeline = scope_css(css_pipeline)
        css_out.write_text(css_pipeline, encoding="utf-8")

        # JS pipeline.
        js_pipeline = transform_js(js, page)
        js_out.write_text(js_pipeline, encoding="utf-8")

        # HTML fragment.
        fragments[page] = build_fragment(body_html, page)

    # Write fragments into option-b-library.
    (OPT_B / "fragment-landing.html").write_text(fragments["landing"], encoding="utf-8")
    (OPT_B / "fragment-pillar.html").write_text(fragments["pillar"], encoding="utf-8")

    # Build Option A (self-contained) — asset paths are relative to the page;
    # webmaster will paste the entire block into a Full HTML body. We use
    # /sites/default/files/strategic-plan/ as the default base.
    build_option_a(fragments)

    # Build Drupal libraries.yml for Option B
    build_libraries_yml()

    # Data files (JSON)
    build_data_files()

    # README
    build_readme()

    # Questions for webmaster
    build_questions()

    print("Build complete.")


# ---------------------------------------------------------------------------


def build_option_a(fragments: dict):
    """Produce a single pasteable HTML block per page.

    Contents:
      <link> + <script src=CDN> + inline <script> SP_CONFIG + <link> our CSS
      + wrapper fragment + <script src> our JS.
    """
    common_head = dedent(
        """\
        <!--
          =================================================================
          NCDPI Strategic Plan Dashboard — OPTION A (paste into Full HTML).

          Paste this entire block into a Drupal page with the Full HTML text
          format. Before pasting, update SP_CONFIG below so basePath points
          to the folder where you uploaded the /assets/ tree.

          All CSS and JS are scoped under .sp-dashboard so they will not
          collide with the theme. No page-level <html>, <head>, or <body>
          tags are emitted — Drupal provides those.
          =================================================================
        -->
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700&display=swap">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
        <script>
          /* Configure paths before the dashboard scripts load. */
          window.SP_CONFIG = {
            basePath:       '/sites/default/files/strategic-plan/',
            pillarPageUrl:  '/strategic-plan/pillar',
            landingPageUrl: '/strategic-plan'
          };
        </script>
        """
    )

    # Landing page: needs Chart.js + annotation plugin CDN before sp-landing.js.
    landing_head = common_head + dedent(
        """\
        <link rel="stylesheet" href="/sites/default/files/strategic-plan/css/sp-landing.css">
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.1.0/dist/chartjs-plugin-annotation.min.js"></script>
        """
    )
    landing_tail = dedent(
        """\
        <script src="/sites/default/files/strategic-plan/js/sp-landing.js" defer></script>
        """
    )

    # Pillar page: no Chart.js needed (pillar page has no bar chart).
    pillar_head = common_head + dedent(
        """\
        <link rel="stylesheet" href="/sites/default/files/strategic-plan/css/sp-pillar.css">
        """
    )
    pillar_tail = dedent(
        """\
        <script src="/sites/default/files/strategic-plan/js/sp-pillar.js" defer></script>
        """
    )

    (OPT_A / "landing-page.html").write_text(
        landing_head + fragments["landing"] + landing_tail, encoding="utf-8"
    )
    (OPT_A / "pillar-page.html").write_text(
        pillar_head + fragments["pillar"] + pillar_tail, encoding="utf-8"
    )


# ---------------------------------------------------------------------------


def build_libraries_yml():
    """Drupal 9/10 library definition for Option B."""
    yml = dedent(
        """\
        # =============================================================
        # Drupal library definitions for the NCDPI Strategic Plan
        # dashboard. Add this file to your custom theme (or a custom
        # module) as strategic_plan.libraries.yml, and reference the
        # libraries from your page templates:
        #
        #   {{ attach_library('strategic_plan/landing') }}
        #   {{ attach_library('strategic_plan/pillar') }}
        #
        # Adjust the asset paths below if you upload to a location
        # other than /sites/default/files/strategic-plan/.
        # =============================================================

        landing:
          version: 1.0
          css:
            theme:
              https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700&display=swap: { type: external, minified: true }
              https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css: { type: external, minified: true }
              /sites/default/files/strategic-plan/css/sp-landing.css: {}
          js:
            https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js: { type: external, minified: true }
            https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.1.0/dist/chartjs-plugin-annotation.min.js: { type: external, minified: true }
            /sites/default/files/strategic-plan/js/sp-landing.js: { defer: true }

        pillar:
          version: 1.0
          css:
            theme:
              https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700&display=swap: { type: external, minified: true }
              https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css: { type: external, minified: true }
              /sites/default/files/strategic-plan/css/sp-pillar.css: {}
          js:
            /sites/default/files/strategic-plan/js/sp-pillar.js: { defer: true }
        """
    )
    (OPT_B / "strategic_plan.libraries.yml").write_text(yml, encoding="utf-8")


# ---------------------------------------------------------------------------


def build_data_files():
    """Copy + rewrite paths in JSON data files."""
    for name in ("measures.json", "pillar-data.json"):
        src = ROOT / "data" / name
        if not src.exists():
            continue
        data = json.loads(src.read_text(encoding="utf-8"))

        # Recursive walk; rewrite strings that start with 'images/'.
        def walk(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    obj[k] = walk(v)
                return obj
            if isinstance(obj, list):
                return [walk(v) for v in obj]
            if isinstance(obj, str):
                return rewrite_image_paths(obj)
            return obj

        data = walk(data)
        (DATA_DIR / name).write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )


# ---------------------------------------------------------------------------


def build_readme():
    readme = dedent(
        """\
        # NCDPI Strategic Plan Dashboard — Drupal Delivery Package

        Drop-in integration for the "Best in the Nation 2030" dashboard.
        This package contains everything needed to render the landing page
        (all measures) and the pillar page inside a Drupal 9/10 site
        without collisions with the active theme.

        Two integration options are included. Pick whichever fits your
        access level and CSP policy.

        ---

        ## Package contents

            drupal-delivery/
              README.md                              (this file)
              QUESTIONS-FOR-WEBMASTER.md             (decisions we need from you)

              option-a-embed/                        Copy-paste approach
                landing-page.html                    Full pasteable block
                pillar-page.html                     Full pasteable block

              option-b-library/                      Drupal theme/library approach
                strategic_plan.libraries.yml         Library definitions
                fragment-landing.html                Body markup only
                fragment-pillar.html                 Body markup only

              assets/                                Shared by both options
                css/sp-landing.css
                css/sp-pillar.css
                js/sp-landing.js
                js/sp-pillar.js
                data/measures.json
                data/pillar-data.json
                images/
                  background-patterns/
                  badges/
                  logos/
                  measure-graphics/
                  pillar-icons/

        ---

        ## Step 1: Upload the /assets/ tree

        Copy the entire `assets/` folder (and its subfolders) to a public
        location on your server. The conventional spot is:

            /sites/default/files/strategic-plan/

        After upload, verify the following URL resolves to an image in a
        browser:

            https://www.dpi.nc.gov/sites/default/files/strategic-plan/
                images/pillar-icons/Pillar-1-Icon-Students.png

        If your path is different, you'll set it in `SP_CONFIG.basePath`
        in step 3 below.

        ---

        ## Step 2: Create the two Drupal nodes / pages

        Create two new pages in Drupal:

            URL alias          Title                                   Body format
            /strategic-plan    Strategic Plan — Best in the Nation     Full HTML (Option A)
                                                                       or Basic HTML (Option B)
            /strategic-plan/pillar   (title updated per pillar via JS) Full HTML / Basic HTML

        If you use different URL aliases, update `SP_CONFIG.pillarPageUrl`
        and `SP_CONFIG.landingPageUrl` in step 3.

        ---

        ## Step 3a: Option A — paste into Full HTML

        Use this option if the "Full HTML" text format allows `<script>`
        and `<link>` tags. If it does not, use Option B instead.

        1. Open `option-a-embed/landing-page.html` in a text editor.
        2. Update the `window.SP_CONFIG` block at the top to match your
           actual upload path and URL aliases:
               window.SP_CONFIG = {
                 basePath:       '/sites/default/files/strategic-plan/',
                 pillarPageUrl:  '/strategic-plan/pillar',
                 landingPageUrl: '/strategic-plan'
               };
        3. Update the two `<link href=...sp-landing.css>` and
           `<script src=...sp-landing.js>` absolute URLs to match your
           upload location (same base).
        4. Copy the entire file contents.
        5. Paste into the body of the `/strategic-plan` node with the
           Full HTML text format selected.
        6. Repeat for `pillar-page.html` on the `/strategic-plan/pillar`
           node.

        ---

        ## Step 3b: Option B — attach via Drupal library

        Use this option if you can't paste `<script>` tags, or if you
        prefer the cleaner library-managed approach.

        1. Copy `option-b-library/strategic_plan.libraries.yml` into
           your custom theme (or a custom module) as
           `<theme>/strategic_plan.libraries.yml`.
        2. Update the paths inside the YAML to match your upload
           location if it's not the default
           `/sites/default/files/strategic-plan/`.
        3. Paste the contents of `fragment-landing.html` into the body
           of the `/strategic-plan` node (Basic HTML is fine — no
           script tags in the fragment).
        4. Paste the contents of `fragment-pillar.html` into the body
           of the `/strategic-plan/pillar` node.
        5. Attach the libraries to each page. In a page template
           (e.g. `page--strategic-plan.html.twig`):

               {# Landing page #}
               {{ attach_library('strategic_plan/landing') }}

               {# Pillar page #}
               {{ attach_library('strategic_plan/pillar') }}

        6. Add a small inline snippet to each page to set SP_CONFIG
           before the library loads (via a preprocess hook, a block,
           or a header field):

               <script>
                 window.SP_CONFIG = {
                   basePath:       '/sites/default/files/strategic-plan/',
                   pillarPageUrl:  '/strategic-plan/pillar',
                   landingPageUrl: '/strategic-plan'
                 };
               </script>

        ---

        ## External dependencies

        Both pages load the following CDN resources. If your Content
        Security Policy blocks any of these, you will need to allowlist
        them or self-host equivalents:

            fonts.googleapis.com                   (Source Sans Pro webfont)
            cdn.jsdelivr.net                       (Bootstrap Icons + Chart.js)

        Chart.js and its annotation plugin are required on the LANDING
        page only. The pillar page does not use Chart.js.

        ---

        ## Data updates

        Changing which measures or pillars appear is a JSON edit, not a
        code edit. Replace:

            assets/data/measures.json      (landing page measure cards)
            assets/data/pillar-data.json   (pillar page focus areas + actions)

        The page reloads the JSON on every page load — no Drupal cache
        rebuild is required, but Varnish/CDN caches may need to be
        cleared if the JSON file URL is cached.

        ---

        ## CSS / JS isolation

        All CSS rules are scoped under the `.sp-dashboard` wrapper so
        they cannot collide with your theme. The JavaScript is wrapped
        in an IIFE — no globals are exported. The only global write the
        script makes is to `window.SP_CONFIG` (and it only READS that —
        you set it before the script loads).

        **Protections against theme leakage:**
        1. Every selector in our CSS is prefixed with `.sp-dashboard `.
        2. A universal inheritance rule forces `color: inherit` and
           `font-family: inherit` on every descendant of the wrapper,
           so theme rules like `h1 { color: red }` or
           `a { font-family: Georgia }` do not affect the dashboard.
           Our own class rules (higher specificity) still set the
           specific colors we want.
        3. Static images use a `data-sp-src` attribute with a 1x1
           transparent GIF placeholder. A JavaScript MutationObserver
           copies `data-sp-src` into `src` with `SP_CONFIG.basePath`
           prefixed, so there are no 404 flashes on page load and the
           real URL is always built from the configured basePath.

        While the mobile drawer is open, the dashboard sets
        `document.body.style.overflow = 'hidden'` to lock page scroll.
        It clears that style when the drawer closes. If your theme
        also sets `overflow` on body in a modal pattern, this may
        conflict — let us know and we'll work around it.

        ---

        ## Troubleshooting

        **The dashboard loads but no measures / pillars appear.**
        Check the browser devtools Network tab. If the request to
        `measures.json` or `pillar-data.json` is 404, your `basePath`
        setting does not match where you uploaded the files. Adjust
        and reload.

        **Images are broken.**
        Same cause — `basePath` mismatch. Open one broken image in a
        new tab; the URL shown is what the script is requesting.

        **Chart doesn't render on the landing page.**
        Your CSP is likely blocking `cdn.jsdelivr.net`. Either
        allowlist it or self-host chart.js and chartjs-plugin-annotation
        in `/sites/default/files/strategic-plan/js/vendor/` and update
        the <script src> URLs.

        **Clicking a pillar goes to a 404.**
        `SP_CONFIG.pillarPageUrl` does not match the real Drupal alias
        of the pillar page. Adjust the config.

        **CSS is broken — fonts or colors wrong.**
        The `.sp-dashboard` wrapper is missing from the HTML you pasted.
        Verify the pasted markup starts with `<div class="sp-dashboard">`.

        ---

        ## Contact

        Andy Baxter, NCDPI (OneDrive project:
        Projects/NCDPI-strategic-plan-site) can regenerate this package
        with different config defaults on request.
        """
    )
    (DELIVERY / "README.md").write_text(readme, encoding="utf-8")


# ---------------------------------------------------------------------------


def build_questions():
    q = dedent(
        """\
        # Questions for the NCDPI Webmaster — Wednesday Meeting

        These are the decisions we need from you to finalize the
        integration. Most can be answered live in the meeting; a few
        may need a quick lookup.

        ## Critical (determines which integration option we use)

        1. **Full HTML text format policy** — Does the Full HTML text
           format allow `<script>` and `<link>` tags to pass through
           unsanitized? (Determines whether Option A can be used, or
           whether we must go with Option B.)
        2. **Filesystem / public-files access** — Can you place files in
           `/sites/default/files/` (or an equivalent public path)?
           If not, where can the CSS/JS/JSON/images live?
        3. **Theme modification access** — Can you add a
           `strategic_plan.libraries.yml` file to the active theme (or a
           custom module)? Needed for Option B.

        ## Path / URL setup

        4. **URL aliases** — We propose `/strategic-plan` for the
           landing page and `/strategic-plan/pillar` for the pillar
           detail page. Is that OK, or do you need different paths
           under an existing parent?
        5. **Breadcrumbs** — Will Drupal's breadcrumb trail show on
           these pages? If yes, under what parent node?

        ## Compatibility

        6. **Fonts** — Is Source Sans Pro (or Source Sans 3) already
           loaded by the theme? If yes, we'll drop our Google Fonts
           `<link>` to avoid the double-load.
        7. **Content Security Policy** — Does the site have CSP headers
           that block `cdn.jsdelivr.net` or `fonts.googleapis.com`?
           (Chart.js is served from jsDelivr; if CSP blocks it, the
           landing-page chart will not render.)
        8. **CSS framework** — Does the active theme use Bootstrap,
           Foundation, or any other CSS framework that may collide with
           our utility classes? (Ours are all scoped under
           `.sp-dashboard` but heads-up helps.)
        9. **Edge caching** — Is there Varnish / a CDN in front of
           Drupal that caches JSON responses? Our pages fetch
           `measures.json` and `pillar-data.json` on every page load;
           stale cached JSON would mean users see stale data after an
           update.

        ## Scope

        10. **Responsive** — Our dashboard is already mobile-friendly
            (drawer nav, accordion panels, responsive chart). Is that
            a requirement for launch, or nice-to-have?
        11. **Header / footer inheritance** — The dashboard has its own
            hero banner (navy + orange strip) below where the Drupal
            masthead will sit. Confirm that's acceptable, or flag if
            we need to strip ours.
        12. **Ongoing data updates** — Who will handle the quarterly
            refresh of `measures.json` and `pillar-data.json`? (Andy
            can, but we should decide the handoff cadence.)

        ## Additional items we'll demo in the meeting

        - Both integration options working side-by-side in a local
          Drupal-like scaffold.
        - The configurable SP_CONFIG paths and how to adjust them.
        - How pillar switching updates the URL (`?p=1` through `?p=8`)
          without a page reload.
        """
    )
    (DELIVERY / "QUESTIONS-FOR-WEBMASTER.md").write_text(q, encoding="utf-8")


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    build()
