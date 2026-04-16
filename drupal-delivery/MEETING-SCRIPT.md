# Webmaster Meeting Script — Wednesday, April 15

A talking guide for handing off the Strategic Plan dashboard to the
NCDPI webmaster. Read the "say this" blocks out loud; the "if they
ask" notes are translations for when jargon comes back at you. Skip
anything that doesn't apply.

---

## Part 1: Opening (90 seconds)

> "Thanks for making time. Quick context so we're on the same page:
> the Strategic Plan dashboard is a standalone HTML page today —
> works great, but it needs to live inside dpi.nc.gov. I've prepped
> it two different ways so you can pick whichever fits how you
> normally add pages. I don't know which one will work until you
> tell me what access you have, so I want to walk through a few
> questions first, then we'll decide together."

**Goal of Part 1:** Set the tone that you've done the work and
they pick the path. Don't pitch — let them choose.

---

## Part 2: The three critical questions (drive the decision)

Ask these FIRST. The answers determine everything else.

### Question 1 — Full HTML vs. Basic HTML

> "When you create a page in Drupal, do you ever use the 'Full HTML'
> text format — the one that lets you paste `<script>` and `<style>`
> tags into the body? Or is everything locked to 'Basic HTML'?"

**If they say "Full HTML is fine":** Option A is on the table.
Simplest path, one file to paste per page.

**If they say "Basic HTML only" / "we don't allow script tags in
content":** Option B is the path. You'll need them to add a library
file to the theme.

**If they look confused:** Ask it differently — "When someone wants
to embed a Google Form or an iframe, who does that and how?" Their
answer tells you their stance on embedded code.

### Question 2 — Where assets live

> "I've got about 2.5 megabytes of assets — CSS, JavaScript, images,
> two JSON data files. Where on the server would those typically go?
> Is `/sites/default/files/` the right home, or do you use a
> different folder for shared assets?"

**Their answer is literally just a file path** — something like
`/sites/default/files/strategic-plan/` or
`/themes/custom/dpi/dashboards/`. Write it down. This becomes
`SP_CONFIG.basePath` in the configuration.

**If they ask why you're asking:** "Because the CSS references
background images by path, and the JavaScript fetches two JSON
files by path. Both need to know where you put everything."

### Question 3 — Theme access

> "For Option B, I'd need you to add a tiny YAML file to the active
> theme — a `libraries.yml` entry that tells Drupal when to load
> our CSS and JS. Can you do that, or is the theme locked down?"

**If yes:** Option B works.
**If no:** You're on Option A (assuming they answered yes to Q1).
**If both are no:** Flag it — you can't integrate until one of
those opens up.

---

## Part 3: Show, don't tell (open the demo)

Open `drupal-delivery/_test/landing.html` in a browser on your
laptop. It's a simulated Drupal page — the black bar at the top is
pretending to be their site chrome.

> "This is what the dashboard looks like when it's dropped into a
> Drupal-like page. The header at the top is a fake NCDPI theme —
> Georgia font, aggressive red colors — and you can see it's not
> bleeding into the dashboard below. The dashboard is using our
> Source Sans Pro, our navy, all our styling. That isolation is the
> part that took the longest to get right."

Click through a few measures, switch to the pillar page, switch
tabs. **The point to make:** "None of this is new styling — it's
the existing dashboard, just wrapped in an isolation layer so it
can't collide with whatever's in the theme."

---

## Part 4: Walk the package

Open the delivery folder. Go slow — let them read the structure.

> "Everything lives in a folder called `drupal-delivery`. Let me
> give you the tour.
>
> - **assets/** — this is the one you'd upload to the server. CSS,
>   JavaScript, images, the JSON data files. About 2.5 megabytes.
> - **option-a-embed/** — if we go with Option A, these are the
>   two HTML blocks you paste directly into the Drupal page body.
> - **option-b-library/** — if we go with Option B, there's a
>   `strategic_plan.libraries.yml` you drop into the theme, and
>   two fragment files that become the page body.
> - **README.md** — step-by-step install for both options.
> - **QUESTIONS-FOR-WEBMASTER.md** — the list I'm walking you
>   through today, in writing, so you can reference it."

---

## Part 5: The compatibility questions (cover your bases)

These are quick yes/no's. Don't dwell — just get the answers.

> **"Is Source Sans Pro already loaded by the theme? I don't want
> to double-load the webfont."**
>
> (If yes, they save bandwidth. If no, our CDN link handles it.
> Either way, no action needed from them.)

> **"Does the site have a Content Security Policy that might block
> jsdelivr.net or fonts.googleapis.com? The chart library we use is
> served from jsdelivr."**
>
> (If yes: you'll need to either allowlist those domains, or
> self-host Chart.js. Flag it as a follow-up.)

> **"Is there Varnish or a CDN in front of the site? The dashboard
> fetches JSON on every page load, and if that gets aggressively
> cached, users will see stale data after we update it."**
>
> (If yes: make sure the JSON files have cache-busting or short
> TTLs. Not a blocker, just something to configure.)

> **"What URL aliases should the pages live at? I've been
> proposing `/strategic-plan` for the landing page and
> `/strategic-plan/pillar` for the pillar detail page."**
>
> (Their call. Whatever they say, write it down — it goes into
> `SP_CONFIG.pillarPageUrl` and `SP_CONFIG.landingPageUrl`.)

---

## Part 6: What happens next

Close the loop. Concrete asks only.

> "So, based on what you've told me, it sounds like we're going
> with **Option [A/B]**. Here's what I need from you:
>
> 1. Upload `drupal-delivery/assets/` to `[their path]`.
> 2. Create the two pages at `/strategic-plan` and
>    `/strategic-plan/pillar`.
> 3. [If Option A:] Paste in the two files from
>    `option-a-embed/`, updating `SP_CONFIG` at the top of each
>    to match the upload path.
> 4. [If Option B:] Add `strategic_plan.libraries.yml` to the
>    theme, paste the fragment bodies, attach the library.
>
> The README has screenshots and walk-throughs for all of that.
>
> What's your turnaround like on something like this? And is
> there a staging environment where we can preview it before it
> goes live?"

---

## Cheat sheet: translation table

When they say this, they mean this:

| They say | Means |
|---|---|
| "Full HTML" / "filtered HTML" | Text format that allows `<script>`, `<style>`, `<link>` |
| "Basic HTML" | Text format that strips most tags |
| "Theme" | The code that controls how every page on the site looks |
| "Custom module" | A place to put PHP code if they don't want to touch the theme |
| "Library" | A bundle of CSS + JS that Drupal attaches to pages on request |
| "Preprocess hook" | PHP code that runs before a page renders, often used to inject config |
| "Twig template" | The HTML template for a page type |
| "Content type" | The kind of node — Article, Basic Page, etc. |
| "Aliases" | Pretty URLs (`/strategic-plan` instead of `/node/123`) |
| "Paragraphs" / "Layout Builder" | Modular page-building tools — overkill for what we need |
| "Cache rebuild" / "Drush cr" | Clear Drupal's cache (they'll do this after changes) |
| "Varnish" | A caching layer in front of Drupal |

---

## If it goes sideways

- **"That won't work, the JavaScript won't pass our filters":**
  "Okay — can you load it as a theme library instead? I have an
  Option B that keeps all the JavaScript out of the page body."

- **"We can't serve custom assets from /sites/default/files":**
  "Where can you? I just need a public path that'll resolve
  consistently. I can retarget the configuration to any path."

- **"The theme team has a 6-week backlog":**
  "Okay. Option A doesn't touch the theme — it's just a page-body
  paste. Can I work with content folks to get that in while we wait
  on the theme team for Option B?"

- **"Content Security Policy blocks jsdelivr":**
  "Got it — I'll swap in self-hosted copies of Chart.js. Can I
  upload those to the same assets folder, or is there a specific
  vendored-JS path you prefer?"

- **"Source Sans Pro isn't loaded, and we can't add new webfonts":**
  "Okay — what fonts does your theme already load? I can swap our
  CSS to use whichever of those is closest."

- **"Can you just send it over and we'll figure it out?":**
  "Absolutely — the README walks through every step. But if we
  can decide Option A vs. B right now, I can hand you the exact
  two or three files you need instead of the whole folder."

---

## One-sentence elevator pitch

If they only have 30 seconds:

> "It's a self-contained dashboard, scoped under a single CSS
> wrapper class and wrapped in an IIFE so nothing leaks in or out.
> Two integration options depending on your access level — paste
> into Full HTML, or attach via a theme library file. All paths
> and URLs are configurable through one config block you set once.
> About 2.5 megabytes of assets total."

---

## What to bring

- Laptop with `drupal-delivery/_test/landing.html` and `pillar.html`
  pre-opened in a browser.
- The `QUESTIONS-FOR-WEBMASTER.md` file, printed or on screen.
- A notepad for their answers to the three critical questions.
- No slides. This is a working meeting.
