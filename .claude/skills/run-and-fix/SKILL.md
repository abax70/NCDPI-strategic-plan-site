---
description: Run a script, diagnose errors from the output, fix them, and retry automatically until it executes cleanly. Works with Python, Stata, and other CLI tools.
user_invocable: true
---

# Run and Fix

Autonomously run a script, catch errors, fix them, and retry — without asking the user to intervene at each failure. Only present the final working result.

## Before Running

1. Detect the environment: check what shell is active (PowerShell vs bash) and confirm the required runtime is available (python, stata, node, etc.).
2. Read the script to understand what it does before executing.
3. If the script references input files or data, confirm those files exist.

## Run Loop

4. Run the script via Bash.
5. Capture the full output (stdout and stderr).
6. If the script succeeds (exit code 0 and no error patterns in output): proceed to Report.
7. If the script fails:
   a. Read the error output carefully. Identify the root cause — don't guess.
   b. Read the relevant lines of the script to understand the context around the failure.
   c. Fix the issue in the source file.
   d. Re-run the script.
   e. Repeat up to 5 attempts. If still failing after 5, stop and report the unresolved error to the user.

## Language-Specific Error Patterns

### Stata
- `r(###)` return codes — read the preceding error message for context.
- `_merge` conflicts — drop or rename `_merge` before subsequent merges.
- Type mismatches — string variables need quoted literals, not numeric codes.
- `variable ___ not found` — check variable names against the dataset.
- Nested `preserve`/`restore` — restructure with `tempfile` instead.

### Python
- `json.JSONDecodeError` — check for trailing commas, encoding issues.
- `KeyError` — verify dict keys exist before accessing.
- `FileNotFoundError` — check paths use Windows backslashes or raw strings.
- `UnicodeDecodeError` — try `encoding="utf-8"` or `encoding="latin-1"`.

### General
- Missing dependencies — install with pip if appropriate, otherwise flag to user.
- Permission errors — flag to user, don't attempt workarounds.

## Report

8. Use TodoWrite to track each attempt (Attempt 1: error X, fixed by Y; Attempt 2: clean).
9. Present the final working version to the user with:
   - Confirmation it ran cleanly.
   - Summary of what was fixed (if anything).
   - Key output or results from the successful run.
