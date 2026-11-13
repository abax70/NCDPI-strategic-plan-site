---
description: Run a standard review checklist on the strategic plan dashboard before presenting results to the user.
user_invocable: true
---

# Dashboard Review Skill

Before reporting that dashboard work is done, run through this checklist:

## Serving
1. Serve the page via the localhost preview server (never open from filesystem paths).
2. If the preview server is already running, reload the page to pick up changes.

## Viewport & Layout
3. Set the preview viewport to at least 1200px width.
4. Confirm the page renders without horizontal overflow or layout collapse.
5. Check that all grid/flex containers have visible content (no zero-height or zero-width sections).

## Charts & Data
6. Verify all Chart.js canvases render with non-zero dimensions.
7. Confirm sequential color palettes follow the dark-is-more convention (darker = higher value).
8. Check that chart axis labels, legends, and data labels are present and correctly formatted.

## Data Files
9. Validate all JSON data files parse cleanly using Python (`import json; json.load(...)`).
10. Confirm the loaded data matches expectations (correct pillar count, measure count, etc.).

## Visual Consistency
11. Check that pillar pages use the correct pillar color theme (header, badges, accents).
12. Verify focus area ID pills (e.g., P1.F1) appear on both Actions and Stories tabs.
13. Confirm status indicator colors: blue for In Progress, gray for Not Started, green for Completed.

## Console & Errors
14. Check the browser console for JavaScript errors or warnings.
15. Check the server logs for request errors.

## Report
16. Summarize any issues found with specific locations and suggested fixes.
17. If all checks pass, report clean and take a screenshot as proof.
