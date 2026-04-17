# Option C — Embed via `<iframe>`

Use this option when the host CMS (e.g. a locked-down Drupal)
won't let you paste custom CSS, JS, or library YAML. An iframe
is the path of least resistance: the dashboard lives at its
own URL and the host page just reserves a rectangle for it.

---

## At a glance

- **Pros:** zero CMS modifications. Perfect isolation — nothing
  the dashboard does can touch the host page. Dashboard updates
  are independent of CMS deploys.
- **Cons:** slight whitespace or scrollbar if auto-resize can't
  be wired up. Deep-linking to a specific pillar (`?p=3`) works
  inside the iframe but the parent page's URL doesn't reflect
  it. Slightly worse SEO (content is in an iframe, not the
  parent page).
- **Prerequisites:** the dashboard must be hosted at a stable,
  publicly reachable URL. Currently that's the GitHub Pages
  staging URL; long-term you probably want an NCDPI-controlled
  subdomain (e.g. `strategicplan.ncdpi.gov`).

---

## Step 1 — Decide on auto-resize

The iframe has a fixed height unless the parent page listens
for height messages from the dashboard. Two sub-options:

**Sub-option C1: fixed-height iframe (simplest).**
Set `height="1800"` (or whatever comfortably fits the tallest
pillar) on the iframe tag. Accept a little whitespace on
shorter pages. Works in ANY CMS that allows iframes.

**Sub-option C2: auto-height via postMessage (recommended).**
Paste a small `<script>` on the host page that listens for
height messages from the dashboard and resizes the iframe
to match. Eliminates whitespace and double scrollbars.
Requires that the host CMS allows a `<script>` tag somewhere
on the page — even if it doesn't allow custom inline markup
in the body, many Drupal setups let admins add a "custom JS"
block or header snippet.

Ask the webmaster: "Can I add a small `<script>` to the
header or footer of the pages that host these iframes?" If
yes → C2. If no → C1.

---

## Step 2a — Fixed height (Sub-option C1)

Paste this into the Drupal page where you want the landing
dashboard:

```html
<iframe
  class="sp-dashboard-iframe"
  src="https://abax70.github.io/NCDPI-strategic-plan-site/"
  title="NCDPI Strategic Plan — Best in the Nation Dashboard"
  width="100%"
  height="1400"
  style="border: 0; display: block; width: 100%; max-width: 1400px; margin: 0 auto;"
  loading="lazy"
  referrerpolicy="no-referrer-when-downgrade">
</iframe>
```

For the pillar detail page, use a second iframe with
`src="...#pillar.html"` or link users out to the standalone
dashboard (iframing the pillar page inside another iframed
page is possible but usually isn't necessary — the landing
iframe already has pillar navigation inside it).

**Tune the height:** start at 1400px. If you see whitespace
at the bottom of the iframe, reduce. If content gets clipped
or shows an inner scrollbar, increase. Set it once; you
shouldn't need to revisit.

---

## Step 2b — Auto-resize (Sub-option C2)

### 2b.1. Paste the iframe (same as above, but with `height="600"`)

```html
<iframe
  class="sp-dashboard-iframe"
  src="https://abax70.github.io/NCDPI-strategic-plan-site/"
  title="NCDPI Strategic Plan — Best in the Nation Dashboard"
  width="100%"
  height="600"
  style="border: 0; display: block; width: 100%; margin: 0 auto;"
  loading="lazy"
  referrerpolicy="no-referrer-when-downgrade">
</iframe>
```

The initial `height="600"` is a placeholder. The listener
script below will resize it to the real content height within
a second of page load.

### 2b.2. Paste this listener script somewhere on the SAME page

Anywhere in the page body or header is fine. It has to be on
the page that contains the iframe, not inside the iframe.

```html
<script>
/*
 * NCDPI Strategic Plan — iframe auto-height listener.
 * Listens for { type: 'sp-dashboard-height', height: N }
 * messages posted by the dashboard and resizes any iframe
 * with class 'sp-dashboard-iframe' to match.
 */
(function () {
  window.addEventListener('message', function (e) {
    var d = e.data;
    if (!d || d.type !== 'sp-dashboard-height') return;
    if (typeof d.height !== 'number' || d.height < 200) return;

    var iframes = document.querySelectorAll('iframe.sp-dashboard-iframe');
    for (var i = 0; i < iframes.length; i++) {
      // Only resize the iframe whose contentWindow sent the message —
      // important when multiple Strategic-Plan iframes share a page.
      if (iframes[i].contentWindow === e.source) {
        iframes[i].style.height = d.height + 'px';
        break;
      }
    }
  });
})();
</script>
```

### 2b.3. Standalone JS file (alternative to inline)

If your CMS lets you link to a JS file but not paste inline,
copy `parent-auto-height.js` from this folder to the server
and reference it like:

```html
<script src="/sites/default/files/strategic-plan/parent-auto-height.js"></script>
```

---

## Accessibility notes

The `title` attribute on the iframe is NOT optional. Screen
readers announce iframes as "frame" and use the title to tell
users what's inside. A missing or generic title (e.g.
`title="Frame"`) is a WCAG failure. Our recommended title:

> NCDPI Strategic Plan — Best in the Nation Dashboard

That identifies the content before the user tabs into it.

The dashboard inside the iframe already meets WCAG 2.1 AA:
skip links, focus indicators, proper heading hierarchy,
keyboard navigation, ARIA labels on the carousel and tabs.
Nothing extra is required in the parent page.

---

## Security / CSP notes

If dpi.nc.gov sets Content Security Policy headers, the
relevant ones for iframe embedding are:

- **`frame-src`**: must include the dashboard's host (e.g.
  `abax70.github.io` or `strategicplan.ncdpi.gov`). If CSP
  omits this the iframe won't load and DevTools will show
  "Refused to frame ... because it violates the following
  Content Security Policy directive".
- **`script-src`**: only relevant for sub-option C2. Must
  permit inline `<script>` or whatever path hosts
  `parent-auto-height.js`.
- **`X-Frame-Options`** on the dashboard's server: must be
  `SAMEORIGIN` or unset. If the dashboard is hosted on a
  different domain than dpi.nc.gov, set it to allow framing.
  GitHub Pages does not set X-Frame-Options, so GitHub
  hosting works out of the box.

Ask the webmaster to grep the CSP config for these if anything
doesn't render.

---

## Deep linking

The dashboard supports `?p=N` on the pillar page (where N is
1-8). Inside an iframe, that URL fragment lives in the
iframe's address bar, not the parent page's.

If users need shareable URLs for specific pillars:
- **Option:** provide a separate Drupal page per pillar and
  use a different iframe `src` on each (e.g.
  `src="...#pillar.html?p=3"`).
- **Option:** link out of the iframe to the standalone
  dashboard when a shareable URL is needed. The
  standalone URL DOES reflect `?p=N` updates as users
  navigate.

This is a judgment call — for most users, pillar switching
inside the iframe is enough.

---

## Troubleshooting

**The iframe is blank / shows a connection error.**
Your `frame-src` CSP directive is blocking the dashboard
host. Contact DIT to allowlist it.

**The iframe shows the dashboard but with a double scrollbar
(inner scrollbar AND the page scrollbar).**
You're using Sub-option C1 with a height that's too small,
or Sub-option C2 but the listener script isn't on the host
page. Open DevTools on the host page, check the Console for
any errors, and verify in the Network tab that the
`parent-auto-height.js` file loaded if you went that route.

**The iframe auto-resizes once but doesn't shrink when the
user switches to a shorter pillar.**
This shouldn't happen — ResizeObserver in the child fires
on any height change, and the listener updates iframe
height directly. If you see it, check that `lastPosted` is
being reset. Report to Andy.

**The iframe content looks wrong (cut off at sides, weird
scaling).**
Remove any `max-width`, `transform: scale()`, or `padding`
rules on the iframe's container in your CMS. The iframe
should be allowed to go 100% width. The dashboard inside
has its own responsive breakpoints and handles narrow
widths gracefully.

**"Permission policy" or "cross-origin" errors in the
console.**
Usually safe to ignore if the dashboard still renders.
`referrerpolicy` on the iframe tag prevents some of these.
