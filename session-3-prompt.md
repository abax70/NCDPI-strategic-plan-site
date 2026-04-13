# Session 3 Prompt — paste this to start your next session

---

Session 3 - Strat Plan. Review the memory files (especially project_status.md and feedback_design_round2.md) to get up to speed. Last session we confirmed Mockup C as the direction and iterated on the hero, left sidebar, and center content. Two things to do this session:

1. **Review the right sidebar** — I'm going to open mockup-c-hybrid.html and give you feedback on the record badge, "What's in Motion" cards, "Why It Counts", and "More Data" sections.

2. **Build the Chart.js integration** — We decided to drop Tableau and use Chart.js for all bar charts. We need to:
   - Create `data/measures.json` with the structure for all 14 measures (I'll provide the data)
   - Replace the static HTML bars in the mockup with a Chart.js rendered chart
   - Support: baseline bars (navy), future target bars (light/outline), and eventually actual-vs-target bars with conditional coloring (green/amber) and dashed horizontal target lines

Let's start with the right sidebar review — I'll pull up the mockup now.
