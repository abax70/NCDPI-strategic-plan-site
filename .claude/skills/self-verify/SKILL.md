---
description: Self-verify all changes before reporting done. Run scripts, validate data files, and preview pages to catch errors before the user has to.
user_invocable: true
---

# Self-Verify Before Reporting Done

After making changes, run through these verification steps before telling the user you're finished. Do NOT skip steps — the goal is to catch your own mistakes.

## Code & Scripts
1. If you wrote or edited a Python script, run it and confirm zero errors in the output.
2. If you wrote or edited a Stata .do file, run it via Bash and check the log for `r()` errors, type mismatches, and `_merge` conflicts.
3. If you edited any JSON file, validate it parses cleanly: `python -c "import json; json.load(open('path/to/file.json'))"`
4. If you edited a Jupyter notebook, validate the notebook JSON structure and confirm all cells have `cell_type`.

## HTML / Dashboard
5. If you edited HTML, CSS, or JS files, launch the preview server and reload the page.
6. Check the browser console for JavaScript errors.
7. Check the server logs for request errors.
8. Take a screenshot or snapshot to confirm the page renders correctly.

## Data Integrity
9. If you modified data files (JSON, CSV), spot-check that record counts, key fields, and structure match expectations.
10. If you generated data from a build script, compare output to the prior version and flag any unexpected differences.

## Report
- If any check fails: diagnose and fix the issue, then re-run the failed check. Repeat until clean.
- Only report done after ALL relevant checks pass.
- Summarize what you verified: "Ran script — clean. Validated JSON — 14 measures present. Previewed page — no console errors."
