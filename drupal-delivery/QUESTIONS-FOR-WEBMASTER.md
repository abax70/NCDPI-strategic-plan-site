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
