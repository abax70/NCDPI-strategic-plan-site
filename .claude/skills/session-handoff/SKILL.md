---
description: Write a structured session handoff note so the next conversation starts with full context.
user_invocable: true
---

# Session Handoff

Write a handoff note to `session-handoff.md` in the project root. This file is overwritten each time so the next session always has a current snapshot.

## Gather Context
1. Review what was accomplished in this session (check TodoWrite history, recent file edits, git status if available).
2. Identify any unfinished work, known issues, or blockers.
3. Note the current state of key files (which HTML pages were edited, data files regenerated, etc.).

## Write the Handoff Note

Use this structure:

```markdown
# Session Handoff — [DATE]

## Completed This Session
- [Bullet list of what was done, with specific file names]

## Still Pending
- [Bullet list of unfinished work or next steps]

## Current State
- **Key files modified:** [list]
- **Data last regenerated:** [date or "not regenerated this session"]
- **Preview server:** [running/not running, port if relevant]

## Known Issues / Gotchas
- [Anything the next session should watch out for]

## Suggested Next Steps
- [Prioritized list of what to tackle next]
```

## Rules
- Be specific — name files, line numbers, pillar IDs, measure IDs.
- Convert any relative references ("today", "this morning") to absolute dates.
- Keep it concise — this is a reference doc, not a narrative.
- If there's an existing session prompt file (e.g., `session-13-prompt.md`), mention it if still relevant, but don't duplicate its content.
