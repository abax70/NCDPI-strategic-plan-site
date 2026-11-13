# CLAUDE.md — NCDPI Strategic Plan Site

## Git state (updated 2026-07-16)

The old "intentionally diverged from origin — do not reconcile" situation is **resolved**: the
divergence healed once the desktop pushed its history, and this laptop fast-forwarded to
`origin/master` on 2026-07-16. Normal git workflow applies here now (still: ask Andy before
committing, per global rules).

One cross-machine quirk to know: files sometimes show as modified with **line-ending-only churn**
(CRLF/LF, Windows host vs container; no `.gitattributes` in the repo). Verify with
`git diff --ignore-cr-at-eol` — if that's empty, the "changes" are noise and safe to
`git restore` with Andy's ok. Don't commit line-ending churn.

This repo is **public** (served via GitHub Pages) — never commit data/check files (e.g.
`checkdata_*.txt`, `data/*.csv`) without checking first, and never commit
`data/.smartsheet-token`.

## Running this project in the container sandbox
The `.devcontainer/` is already here. In VS Code: **Open Folder** → `Ctrl+Shift+P` →
**"Dev Containers: Reopen in Container."** (Requires Podman Desktop running + the VS Code setting
`dev.containers.dockerPath` pointing at the full `podman.exe` path.) See the **Claude-Sandbox** repo
for the image, the autonomous wrapper, and full docs.
