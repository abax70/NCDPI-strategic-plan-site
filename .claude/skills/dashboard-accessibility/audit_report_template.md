# Audit Report Template

Every review agent MUST return a report in this exact format. The main skill agent parses these to dedupe findings, so consistency matters.

---

## Report skeleton

```markdown
# A11y Review — Agent {N}: {Focus area}
Round: {N}
Files reviewed: index.html, pillar.html
Reviewer focus: {e.g., "Contrast & Color"}
Reviewer WCAG criteria: {e.g., "1.4.1, 1.4.3, 1.4.11"}

---

## index.html

### Findings

- **Finding ID:** `a1-c1` (agent-number + category + counter; e.g., `a1-c1` = agent 1, contrast, violation 1)
- **WCAG criterion:** `1.4.3 Contrast (Minimum)` (Level AA)
- **Severity:** `error` | `warn` | `info`
- **Location:** `index.html:342` (line number) or CSS selector (`.sidebar-link.active`)
- **Element snippet:**
  ```html
  <a class="sidebar-link" href="...">Pillar 1</a>
  ```
- **Description:** One-sentence statement of what's wrong.
- **Measured values:** (when applicable) e.g., "contrast 3.8:1, required 4.5:1"
- **Suggested fix:** Concrete change to make, referencing `common-remediations.md` pattern if one applies.
- **Pause-gate:** `none` | `andy` | `graphics-team` | `design`

---

- **Finding ID:** `a1-c2`
- ... (repeat for each unique violation)

### Unverified items (optional)

List anything that warrants human review but can't be scored mechanically (e.g., "aria-label wording on canvas chart for measure X" — these do NOT count toward the violation total).

### Score

- Unique violations in index.html: **3**
- Score: **100 − (5 × 3) = 85**

---

## pillar.html

### Findings

(same structure as above — each finding gets a unique ID, e.g., `a1-c3`, `a1-c4`)

### Score

- Unique violations in pillar.html: **{N}**
- Score: **{100 − 5×N}**

---

## Agent summary

- Total unique violations reported by this agent: **{sum across both files}**
- Pause-gated items: **{count, or 0}**
- Notes on confidence / unverified items: **{short prose, optional}**
```

---

## Finding ID conventions

Format: `a{agent}-{category}{counter}`

| Agent | Category prefix | Example |
|---|---|---|
| 1 — Contrast & Color | `c` | `a1-c1`, `a1-c2` |
| 2 — Keyboard & Focus | `k` | `a2-k1`, `a2-k2` |
| 3 — Structure & ARIA | `s` | `a3-s1`, `a3-s2` |
| 4 — Non-text Content | `n` | `a4-n1`, `a4-n2` |
| 5 — Forms & Responsive | `f` | `a5-f1`, `a5-f2` |

After dedupe (Phase 2), the consolidated `findings.json` reassigns unified IDs like `v001`, `v002` but retains the original reporter IDs as `reported_by`.

---

## Severity definitions

- **error** — A true WCAG 2.1 AA violation that will fail external validation. Counts toward the score.
- **warn** — A borderline case or a violation that's debatable (e.g., alt text present but possibly not meaningful). Counts toward the score unless marked "unverified" with a pause-gate.
- **info** — A best-practice suggestion, not a WCAG violation. Does NOT count toward the score.

---

## Pause-gate values

- **`none`** — Safe for a remediator to fix mechanically.
- **`andy`** — Requires Andy's judgment (copy, wording, content).
- **`graphics-team`** — Would require changing pillar color definitions. Do not touch.
- **`design`** — Requires design-team input (e.g., mobile layout aesthetic).

Findings with any pause-gate other than `none` still count in the score but remediators will skip them and flag them for the pause gate workflow.

---

## JSON equivalent (for scripted consumption)

If the main skill agent needs to parse findings programmatically, expect this shape per finding:

```json
{
  "id": "a1-c1",
  "file": "index.html",
  "criterion": "1.4.3",
  "criterion_name": "Contrast (Minimum)",
  "level": "AA",
  "severity": "error",
  "location": "index.html:342",
  "selector": ".sidebar-link.active",
  "element_snippet": "<a class=\"sidebar-link\" href=\"...\">Pillar 1</a>",
  "description": "Active sidebar link text contrast is 3.8:1 on white background; required 4.5:1 for normal text.",
  "measured_values": {"contrast": 3.8, "required": 4.5},
  "suggested_fix": "Change .sidebar-link.active color from #888 to #595959 (matches 4.52:1). See common-remediations.md 'Low text contrast'.",
  "pause_gate": "none",
  "reported_by": ["agent-1"]
}
```

The main skill agent converts markdown findings to this JSON shape after deduping.
