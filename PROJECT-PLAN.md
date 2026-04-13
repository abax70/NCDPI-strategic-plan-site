# NCDPI Strategic Plan Dashboard — Project Plan

**Owner:** Andy Baxter, NCDPI
**Last updated:** 2026-04-06
**Status:** Design & prototyping phase

---

## 1. Project Overview

Build a public-facing website that monitors the implementation and results of NCDPI's "Achieving Educational Excellence" strategic plan. Replaces the current Tableau Public prototype with a hybrid approach: HTML/CSS website for content and navigation, with Tableau embeds or lightweight JS charts for data visualization.

### Content Structure
1. **Landing page** ("Best in the Nation") — 14 overall measures, updated annually
2. **Pillar pages** (×8) — one per strategic plan pillar, each containing:
   - Focus areas (26 total across all pillars)
   - Measures/outcomes per focus area (updated annually) — mostly TBD by leadership
   - Implementation actions (109 total, updated monthly)
   - Stories from the field (published weekly)

### Why We're Moving from Tableau to Web
- The project is overwhelmingly text and navigation, not data exploration
- Tableau is fighting against the requirements: pillar-specific theming, text-heavy layouts, story publishing, hierarchical navigation
- A website handles all of these natively; Tableau can still be used where it shines (charts)
- Responsive/mobile experience will be dramatically better
- Stories from the field can be managed as CMS content rather than workbook edits
- Reference model: [myFutureNC Dashboard](https://dashboard.myfuturenc.org) — similar mission, implemented as a website

### Deployment Path
1. Andy + Claude build HTML/CSS pages locally
2. Handoff to DPI webmaster for integration into Drupal (Digital Commons platform on dpi.nc.gov)
3. Webmaster tweaks and publishes
4. Tableau Public charts can be embedded via iframe where needed

### Timeline
- ~2 weeks total
- Week 1: Build all pages (landing + 8 pillars)
- Week 2: Polish, populate stories, handoff to webmaster

---

## 2. Data Sources

### Primary: `data/DIM_TablesForTableau.xlsx`
| Sheet | Rows | What it contains |
|-------|------|-----------------|
| DIM_Pillars | 8 | Pillar names, descriptions, URLs, IDs |
| DIM_FocusAreas | 26 | Focus area names mapped to pillars |
| DIM_Measures | 49 | Measure names, goals, labels, BIN flag |
| LandingPage_MeasureMenu | 14 | Landing page measure carousel menu (14 BIN measures) |
| DIM_Actions | 109 | Action names, descriptions, launch dates, mapped to focus areas |
| LandingPage_MeasureDetailsText | 14 | "Why it counts", data sources, tooltips, definitions, links |
| LandingPage_MeasureResults | 80 | Actual/target values by year (2024-2030), format specs |
| Sheet3 | 109 | Action ID/name lookup (duplicate of DIM_Actions subset) |

### Data Gaps
- "Why it counts" (CallOutImportance) is lorem ipsum for most measures
- Several measure definitions say "[Need to add note]"
- "Schools of Character" measure has no data yet
- Pillar-level measures (not BIN) are mostly TBD by leadership
- Stories from the field: 30 stories in `data/Strategic Plan Dashboard Communications Assets.xlsx` (Assets sheet) with titles, blog URLs, publish dates, and some county tags. FocusAreaName column is unpopulated — once filled in, stories can be filtered by pillar/focus area. Lookup list of 25 focus areas is in the `_FocusAreas` tab.

---

## 3. Brand Assets Inventory

### Logos (`images/Achieving Academic Excellence Logos/`)
- Logo-AchEdExc-MAIN.png — primary logo (navy text, orange star)
- Logo-AchEdExc-Black.png, White.png, WhiteOrange.png — variants
- Tagline versions in subfolder (include "Best in the Nation—Our 2030 Plan for NC Public Schools")

### Pillar Graphics (`images/Eight Pillars Graphic/`)
- 8-Pillars-TextLogo.png — full graphic with logo, icons, names, gradient bars
- 8-Pillars-TextNoLogo.png — same without logo
- 8-Pillars-NoTextLogo.png — icons and bars only, no names

### Measure Icons (`images/Measure Graphics/`)
- Individual icons for each BIN measure (PNG + SVG)
- SVGs preferred for web (scalable, crisp)
- Examples: StratPlan-BIN-GradRate.svg, StratPlan-BIN-APparticipate.svg, etc.

### Pillar Colors (from Strategic Plan Style Guide, page 8)
| Pillar | Icon Color | Large Text | Small Text | 15% Background |
|--------|-----------|------------|------------|----------------|
| 1 | #003A70 (DPI Blue) | #003A70 | #003A70 | #D9E4F1 |
| 2 | #922880 (Purple) | #801E70 | #6E1360 | #EFDFEC |
| 3 | #29B5D9 (Aqua) | #077890 | #006174 | #DFF4F9 |
| 4 | #FF9015 (Orange) | #C75128 | #943E20 | #FFEEDC |
| 5 | #74C04B (Green) | #3D803F | #2F6230 | #EAF6E4 |
| 6 | #B7B9BB (Gray) | #6B6F70 | #525A60 | #F4F4F5 |
| 7 | #0077BF (Blue*) | #0063A2 | #0063A2 | #D4EFFC |
| 8 | #801323 (Burgundy*) | #801323 | #801323 | #ECDCDE |

*Pillars 7 & 8 colors are exclusive to the strategic plan, not general NCDPI brand colors.

### NCDPI Web Style Guide (`images/NCDPI Web Style Guide/`)
- **Typography:** Source Sans Pro (Google Fonts), weights 400/600/700
- **Primary color:** Dark navy (#003A70 area)
- **Accessibility:** WCAG Section 508, 4.5:1 contrast ratio required
- **Icons:** Open-source (Bootstrap or FontAwesome), on secondary light backgrounds with primary fill
- **Logo:** Upper left, linked to home, 250×75px desktop

---

## 4. Design Decisions & Open Questions

### Feedback from Superintendent
- Dashboard "lacks warmth"
- Needs to feel more celebratory and human, less like a data tool

### Feedback from Graphics Team
1. **More scaffolding at the top** — "How we lead" and "How we are doing" sections need better framing so users understand the left nav = pillars and center = progress measures
2. **Increase whitespace** — rethink the right-hand callout area ("Why it counts" + "What's in motion")
3. **"Why it counts"** — committee thinks it's important but hasn't produced content; current sidebar is too cramped for meaningful narrative; consider inline treatment like myFutureNC

### Record-High Badges
- Leadership wants to celebrate measures at historic highs (see dpi.nc.gov homepage gold shield badges)
- Current Tableau version only has "Goal Status: Baseline Year" — not celebratory
- **Recommendation:** Build a reusable badge component; show it on measures that are at record highs; when a measure is at baseline with no historic high, show a forward-looking treatment instead

### "What's in Motion" Section — Recommendation
The concern: hard to map a BIN measure like graduation rate to a single action.
The counter: it's valuable to show *some* linkage between measures and actions.

**My recommendation: the "Spotlight" approach.**
- Rename to something like "Action Spotlight" or "See It in Action"
- For each measure, curate 1-2 related actions to highlight
- Rotate monthly — this month spotlight one action, next month another
- Each spotlight links to the relevant pillar page for full context
- This is warm (it's about people doing things), connects the abstract metric to concrete work, and is low-maintenance (one update per month per measure)
- If leadership decides against it, the section is easy to remove — it's just a component

### "Why It Counts" — Recommendation
**Go inline, myFutureNC-style.** Instead of cramming it into a sidebar:
- Give each measure a full-width narrative section below the chart
- Headings like "What does this measure?" / "Why does it matter?" / "How is NC performing?"
- This solves the space problem, allows for richer content, and is much more readable
- Bonus: when the committee finally writes the content, there's room for it

### Landing Page Layout — Proposed Redesign
Instead of the current three-column layout (pillars | chart | sidebar), consider:
- **Hero section** with AEE logo, plan title, and the 8 Pillar graphic
- **Measure carousel** (or card grid) as the main content — each measure gets more vertical space
- **Pillar navigation** as a horizontal row of clickable icons (not a sidebar list)
- **Badge/celebration callouts** for record-high measures
- Narrative content flows naturally below the chart
- Clean, spacious, warm

---

## 5. Landing Page Interactivity (from current Tableau version)

### Measure Carousel
- Left/right arrows cycle through all 14 BIN measures one at a time
- Dropdown menu below chart lets user skip to a specific measure
- Each measure shows: icon, name, goal statement, goal status, current value, metric description, bar chart with actuals + targets through 2030

### Pillar Navigation
- 8 pillars listed in left sidebar with icons
- Clicking a pillar navigates to that pillar's dedicated page (separate Tableau workbook)
- URL passes pillar number as parameter

### Other Elements
- "Why it counts" panel (right side) — mostly placeholder text
- "What's in motion" panel (right side) — links to related actions
- Notes section at bottom: measure definition, next update date, data source with URL
- Links to: download strategic plan PDF, email Geoff Coltrane
- Info/context button (small, location unclear)

---

## 6. Pillar Page Structure (from current Tableau version)

### Header
- Pillar icon, number, and name
- AEE logo

### Three Tabs
- **Actions** (built) — focus areas on left, actions on right (click focus area to filter)
- **Stories** (not built) — stories from the field
- **Results** (not built) — pillar-specific measures/outcomes

### Actions Tab Detail
- Left panel: focus area list (e.g., P1.F1 through P1.F5) with status
- Right panel: actions for selected focus area, each with ID, name, launch date, description

---

## 7. File Structure

```
strategic-plan-site/
├── PROJECT-PLAN.md          ← this file
├── index.html               ← landing page (Best in the Nation)
├── pillar-1.html            ← pillar pages (×8)
├── pillar-2.html
├── ...
├── css/
│   └── styles.css           ← main stylesheet (pillar colors as CSS variables)
├── js/
│   └── main.js              ← carousel, navigation, interactivity
├── images/                  ← brand assets (as uploaded)
│   ├── Achieving Academic Excellence Logos/
│   ├── Eight Pillars Graphic/
│   ├── Measure Graphics/
│   ├── NCDPI Web Style Guide/
│   ├── Tableau Dashboard Screenshots/
│   └── Strategic Plan Style Guide.pdf
├── data/
│   └── DIM_TablesForTableau.xlsx
└── reference/               ← (empty, for plan docs if needed)
```

---

## 8. Build Plan

### Phase 1: Prototype (Days 1-3)
- [x] Extract all measure data from DIM_TablesForTableau.xlsx (14 BIN measures with values, goals, targets through 2030, definitions, sources)
- [x] Build two landing page layout mockups for comparison:
  - `mockup-a-redesign.html` — hero + measure card grid + horizontal pillar nav + inline narrative (myFutureNC-style)
  - `mockup-b-three-column.html` — cleaned-up 3-column layout (pillar sidebar | chart | why-it-counts sidebar)
  - Both use real data (graduation rate), actual SVG icons, brand colors, Source Sans Pro
- [ ] **NEXT: Andy picks layout direction (A, B, or hybrid), then build index.html for real**
- [ ] Build one pillar page (pillar-1.html) with actions tab populated
- [ ] Implement measure carousel with all 14 measures (JS-driven, data from Excel)
- [ ] Apply pillar color theming
- [ ] Design badge component for record-high measures
- [ ] Review with Andy, iterate

### Phase 2: Build Out (Days 4-7)
- [ ] Generate all 8 pillar pages from data
- [ ] Build stories tab template (ready for content)
- [ ] Build results tab template (ready for measures when decided)
- [ ] Populate all landing page measure data and narratives
- [ ] Cross-page navigation (landing ↔ pillars)

### Phase 3: Polish & Handoff (Days 8-10)
- [ ] Populate stories (Andy has samples)
- [ ] Responsive design / mobile testing
- [ ] Accessibility review (WCAG compliance, contrast, alt text)
- [ ] Package for webmaster handoff
- [ ] Documentation for webmaster on structure and how to update

### Buffer (Days 11-14)
- Webmaster integration into Drupal
- Final review and launch
