---
description: Audit dashboard images — flag broken references, suspicious newer-version files, duplicate basenames across subfolders, and orphaned files. Offers to fix broken references by proposing a replacement, but never edits without approval.
user_invocable: true
---

# Check Dashboard Images

`/images/` is the source of truth for this project and HTML references are live paths — dropping a new file in place instantly swaps it on the site. This skill catches the drift patterns that can still slip past: files the graphics team delivered under a new name, files saved in the wrong subfolder, broken references, and abandoned files no one uses anymore.

Detect-only script, plus a guided fix-offer step run by Claude after the detection script surfaces candidate replacements.

## What it checks

Four categories, each emitting findings at severity **error / warn / info**:

- **A. Broken references (error)** — Every image path referenced by `index.html`, `pillar.html`, or `data/measures.json` must resolve to a real file in `/images/`. Case-sensitive match, because GitHub Pages is case-sensitive even though Windows isn't. For each miss, the script looks for a plausible replacement (e.g., same stem with a `-v2`, `-new`, `-final`, `-updated`, or date suffix) and reports it as a candidate so Claude can offer to patch the reference.
- **B. Suspicious "newer version" files (warn)** — A file in `/images/` whose name looks like a newer delivery (`-v\d+`, `-new`, `-final`, `-updated`, `-latest`, `-revised`, ` (1)`, trailing `_YYYY-MM-DD`) when the base-name version of it is still the one referenced in the HTML/JSON. Strong sign a replacement was dropped but the HTML was never updated to use it.
- **C. Duplicate basenames across subfolders (warn)** — Same filename in multiple parent folders (e.g., `Pillar-1-Icon-Students.png` in both `Pillar Icons/Icons Only/` and `Pillar Icons/Icons Numbered/`). The skill reports which subfolder the HTML actually references so it's obvious whether a graphics-team update could have landed in the wrong sibling folder. Some duplicates are intentional (the three Pillar Icons variants are genuinely different icon sets with matching filenames) — the `warn` severity lets Andy eyeball them.
- **D. Orphaned files (info)** — Files in `/images/` that aren't referenced anywhere. Many are intentional (Tableau screenshots, style guides, unused logo variants kept for reference), so this is `info` and meant for scanning, not action.

## How to run

1. From the project root, run:
   ```
   python .claude/skills/check-images/check_images.py
   ```
   The script resolves all paths from its own location, so it works from any CWD.

2. The script prints a grouped markdown report to stdout and exits with code **1** if any errors were found, **0** otherwise. Code **2** means a fatal problem (file read error, malformed JSON).

## How to present results

1. **Errors first.** Broken references block the UI and should be fixed before anything else. Include the candidate replacement (when the script found one) in the summary so Andy sees the proposed fix at a glance.
2. **Warnings next.** Call out suspicious newer-version files prominently — they're the strongest signal that a graphics delivery didn't land where intended.
3. **Info last.** Orphans can be skimmed; don't nag about them unless Andy asks.
4. Include file path + line number (for HTML refs) or JSON pointer (for `measures.json`) on every finding so Andy can jump straight to the row.

## Remediation (Claude's job, not the script's)

After running the detection script:

- For each **broken reference** where the script identified a candidate replacement, show Andy the diff (`old path → new path`) and **ask for confirmation before applying the Edit**. Never auto-edit. If the candidate is uncertain or multiple candidates exist, present them as options and ask Andy to pick.
- For broken references with **no candidate**, just report — the file is genuinely missing and Andy needs to find it.
- **Warnings and info findings are report-only.** Never delete, rename, or move a file without explicit confirmation, and even then prefer having Andy do it manually (global golden rule: "Never delete files").

## What this skill does NOT do

- **Does not compare pixel content.** It can't tell you if `Pillar-1-Icon.png` visually looks like what graphics delivered — only that a file by that name exists.
- **Does not sync from an external graphics-team inbox.** This project doesn't have a separate source folder; `/images/` is the source. If graphics team delivers via email/Teams, Andy still has to save the file into `/images/` himself.
- **Does not delete files.** Orphan reports are informational only.
- **Does not auto-edit.** Every proposed fix requires Andy's approval.

## Exit codes

- `0` — no errors (warnings and info findings are fine)
- `1` — at least one broken reference or error-level issue
- `2` — fatal (could not read a file, malformed JSON)

## Related skills

- `/check-data` — companion skill for data-file drift. Run both before `/review-dashboard` so image and data issues surface together.
- `/review-dashboard` — standard pre-share review; include image audit findings in the pre-check.
- `/self-verify` — after fixing any broken references, re-run this skill and confirm it reports clean.
