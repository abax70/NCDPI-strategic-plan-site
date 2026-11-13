---
description: Audit and remediate the strategic plan dashboard (index.html, pillar.html) to WCAG 2.1 Level AA. Runs parallel review agents to score 0–100, remediates until score = 100, then validates with axe-core + pa11y until both return zero violations. Iterative, pause-for-Andy-on-judgment-calls.
user_invocable: true
---

# Dashboard Accessibility Skill

Drive `index.html` and `pillar.html` to **WCAG 2.1 Level AA** conformance through an internal multi-agent audit loop followed by an external validator gate (`@axe-core/cli` + `pa11y`). Public-agency delivery requirement.

**Philosophy:** Automated tooling catches ~50–60% of WCAG issues; the parallel review-agent phase fills the rest (keyboard nav, heading logic, alt-text quality). The external validator is the acceptance gate, not the audit.

**Scope:** Only `index.html` and `pillar.html`. Mockups (`mockup-a-redesign.html`, `mockup-b-three-column.html`) are out of scope.

---

## Prerequisites

```bash
npm install -g @axe-core/cli pa11y
```

Verify before running: `axe --version && pa11y --version`. If either is missing, print the install command and stop — do not proceed.

Node.js must be on PATH. Python 3 must be available for `run_external_audit.py`.

**Windows note:** `run_external_audit.py` prints plain ASCII, so the default `cp1252` console works out of the box. If you later modify the script to print Unicode (e.g. `→`, `✓`), prefix invocations with `PYTHONIOENCODING=utf-8` or set `sys.stdout.reconfigure(encoding="utf-8")` inside the script.

---

## Quick start

When the user says something like:
> "Run the a11y audit on the dashboard" / "Check WCAG compliance" / "Make the dashboards accessible"

Follow the phases below in order. Do not skip phases. Do not declare success before Phase 4 passes.

---

## Phase 0 — Setup

1. **Verify tooling:** `axe --version` and `pa11y --version` both succeed. If not, print install command and stop.
2. **Start preview server:** Use `preview_start` with name `static-preview` (from `.claude/launch.json`, serves on `http://localhost:3000`). If the server is already running, reuse it.
3. **Create audit directory:** `.claude/accessibility-audits/YYYY-MM-DD-HHMM/` — this holds every artifact for this run (agent reports, external-tool JSON, diffs). Never overwrite a prior audit directory; each run gets its own timestamped folder.
4. **Snapshot starting state:** `git status --short` to the audit directory as `starting-state.txt`. Stops mid-audit uncommitted changes from being misattributed.

---

## Phase 1 — Internal audit (parallel review agents)

Launch **5 Explore agents in parallel** (single message, 5 tool calls). Each has a narrow WCAG focus and returns a JSON-shaped findings report.

| # | Agent focus | Primary WCAG criteria |
|---|---|---|
| 1 | Contrast & color | 1.4.1, 1.4.3, 1.4.11 |
| 2 | Keyboard & focus | 2.1.1, 2.1.2, 2.4.1, 2.4.3, 2.4.7 |
| 3 | Structure & ARIA | 1.3.1, 2.4.6, 4.1.2, 4.1.3 |
| 4 | Non-text content | 1.1.1, 1.2.x |
| 5 | Forms, input & responsive | 1.4.4, 1.4.10, 3.3.1, 3.3.2 |

Use the canonical prompts in `references/review-agent-prompts.md` — do not paraphrase, they're tuned to produce consistent structured output.

Each agent audits **both files** (`index.html` and `pillar.html`) and returns findings in the format specified by `audit_report_template.md`.

Save each agent's raw report to the audit directory as `round-N/agent-{1-5}-report.md`.

---

## Phase 2 — Consolidate & score

1. Read all 5 reports.
2. **Dedupe** violations — same WCAG criterion + same element selector/line = one violation, regardless of which agent reported it.
3. Compute per-file score: `score = max(0, 100 − 5 × unique_violations)`.
4. Write a consolidated `round-N/findings.json` with unique violations, each tagged with file, criterion, severity, location, description, suggested fix, and which reporter(s) found it.
5. Print the round summary:
   ```
   Round N internal audit:
     index.html:  score = 85 (3 unique violations)
     pillar.html: score = 75 (5 unique violations)
   ```
6. If **both** scores = 100 → Phase 4. Else → Phase 3.

---

## Phase 3 — Internal remediation

1. **Group** unique violations by category (contrast, ARIA, structure, non-text, keyboard, responsive).
2. **Launch remediation agents in parallel, grouped by category.** Each remediator:
   - Reads `references/common-remediations.md` for patterns
   - Edits the target file(s) surgically (only the flagged elements — no drive-by changes)
   - Returns a diff summary citing which finding IDs they addressed
3. After all remediators finish, run the **self-verify checklist:**
   - Reload preview (`preview_eval: window.location.reload()`)
   - Check `preview_console_logs` — zero JS errors
   - Check `preview_network` — zero failed requests
   - Confirm charts render (Chart.js canvases have non-zero dimensions)
   - Confirm measure carousel + tab pattern still keyboard-operable (preview_eval to tab through)
4. **Return to Phase 1** with fresh review-agent instances (new agent IDs — never reuse; prevents confirmation bias).
5. **Cap: 5 rounds.** On round 5 still <100, stop and summarize blocking items for Andy. Flag any that hit a pause gate (see below).

### Pause gates — stop and ask Andy when

- A fix would change **pillar color definitions** (graphics team approved — locked).
- A fix requires changing measure/pillar **content copy** (Andy owns copy).
- **Canvas chart alt-text** wording for a specific measure (judgment call — Andy writes the wording).
- Two consecutive rounds show no score improvement (loop detection).
- Round 5 of Phase 3 or Phase 5 fails.

---

## Phase 4 — External validation

1. Run the external audit:
   ```bash
   python .claude/skills/dashboard-accessibility/run_external_audit.py \
     --url-base http://localhost:3000 \
     --output-dir .claude/accessibility-audits/{timestamp}/external
   ```
   The script runs **axe + pa11y against `index.html` once and `pillar.html` once per pillar (?p=1..8)** — 9 target URLs total. Prior to S.025 it only hit `pillar.html` with no query string, which always renders Pillar 1 (navy); P3–P6 hero contrast failures were never exercised. Iterating all 8 pillars is cheap (axe+pa11y are ~3s each on a static page) and closes that gap.
2. The script's pre-flight runs [`verify_pillar_contrast.py`](verify_pillar_contrast.py), a static regression check that parses the `--pillarN` and `--pillarN-text` tokens out of `pillar.html`'s `:root` block and computes WCAG contrast against the hero text colours used by the hybrid hero design (white on dark-family pillars, navy on light-family pillars). If any pairing regresses below WCAG AA (≥3.0 for ≥14pt bold hero text), the pre-flight fails with a remediation hint and the audit aborts before any axe/pa11y runs.
3. Exit code:
   - `0` — pre-flight passed AND zero unique violations across all 9 targets × both tools → **PASS**.
   - `1` — at least one failure (either pre-flight or tool-reported) → Phase 5.
4. Artifacts: `axe-index.json`, `pa11y-index.json`, and `axe-pillar-pN.json` / `pa11y-pillar-pN.json` for N ∈ 1..8. `findings.json` is labelled per target so a P3-only regression doesn't dedupe away against an otherwise-identical finding from a different pillar.
5. Print summary from the script's stdout: per-tool + per-target violation counts. Any **pa11y needs-review** count (axe's "incomplete" results surfaced via pa11y) prints on the same line with a `+N pa11y needs-review` suffix — these are **not** WCAG failures and do not block the exit code; treat them as a manual-verification checklist.

---

## Phase 5 — External remediation loop

1. Launch remediation agents with the external findings (tool-reported violations are concrete: selector + criterion + message).
2. Run the self-verify checklist from Phase 3 step 3.
3. Re-run Phase 4.
4. **Cap: 5 rounds.** On round 5 failure, pause and summarize blocking items for Andy. Pause gates from Phase 3 apply here too.

---

## Final step — keyboard walkthrough (human)

Tools catch ~50–60% of WCAG. Before declaring done, prompt Andy to do a 2-minute keyboard walkthrough:

1. Load `http://localhost:3000/index.html`, Tab from the top.
2. Confirm every interactive control is reachable, the focus indicator is visible, and Tab order is logical.
3. Repeat on `pillar.html` — also arrow-key through the tab pattern (Actions / Stories / Results).
4. Record result in audit directory as `keyboard-walkthrough.md` (pass / issues found).

Skill cannot automate this — document it in the final report as a required human step, not something we silently skipped.

---

## Final report

When all phases pass, write `.claude/accessibility-audits/{timestamp}/FINAL-REPORT.md` containing:

- Rounds needed (internal + external)
- Unique violations fixed (categorized)
- External tool versions + timestamps
- Keyboard walkthrough result
- Any remaining caveats (e.g., Drupal environment will re-need audit post-migration)

---

## What this skill does NOT do

- **Does not audit mockups.** Only `index.html` and `pillar.html`.
- **Does not assess cognitive/reading-level WCAG** (3.1.x) — plain-language review is separate.
- **Does not run screen readers** (NVDA/JAWS require manual testing).
- **Does not test the Drupal-rendered output** — re-run post-Drupal handoff (different DOM, different CSS scoping).
- **Does not change pillar colors or copy** without Andy's explicit approval.

---

## Reference files

| File | Purpose |
|---|---|
| `references/wcag-2.1-aa-checklist.md` | Success-criteria cheat sheet for review agents |
| `references/common-remediations.md` | Violation → recommended fix mapping |
| `references/review-agent-prompts.md` | Canonical prompts for the 5 review-agent roles |
| `audit_report_template.md` | Structured format for agent findings reports |
| `run_external_audit.py` | Runs axe + pa11y against index.html + pillar.html×8 pillars, normalizes output, exits 0 on pass |
| `verify_pillar_contrast.py` | Static WCAG regression check on the pillar-hero contrast matrix; called as pre-flight by `run_external_audit.py` and runnable standalone |

---

## Exit codes (for `run_external_audit.py`)

- `0` — pre-flight passed AND zero violations across all 9 targets × both tools
- `1` — pre-flight detected a pillar-hero contrast regression, OR at least one axe/pa11y violation remaining
- `2` — tool invocation error (axe or pa11y crashed, server unreachable, pillar.html missing/malformed, etc.)
