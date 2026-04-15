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
