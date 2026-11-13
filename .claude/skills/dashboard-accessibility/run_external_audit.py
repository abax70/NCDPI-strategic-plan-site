"""
External accessibility audit runner for the strategic plan dashboard.

Runs @axe-core/cli and pa11y against index.html and pillar.html, writes raw
per-tool JSON, and emits a unified findings.json with violations deduped
across tools by {criterion, selector}.

Invocation:
    python run_external_audit.py \
        --url-base http://localhost:3000 \
        --output-dir .claude/accessibility-audits/{timestamp}/external

Exit codes:
    0 — zero unique violations across both files and both tools (PASS)
    1 — at least one violation (go to Phase 5)
    2 — tool invocation error (axe/pa11y crashed, server unreachable, etc.)

The script:
  - Checks axe and pa11y are on PATH
  - Pings the URL base to confirm preview server is up
  - Runs each tool against each file, captures stdout
  - Writes:  axe-{file}.json, pa11y-{file}.json  (raw tool output)
  - Writes:  findings.json                        (unified, deduped)
  - Writes:  summary.md                           (human-readable summary)
  - Prints a one-line per-file summary to stdout
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

# TARGETS: (label, path) tuples. `label` is used in output filenames and
# per-target summary keys; `path` is the URL suffix appended to --url-base.
#
# S.025 update: pillar.html now runs once per pillar (?p=1..8) because the
# hero's pillar-specific background colour isn't exercised at the default
# URL. Prior to this change, pillar.html defaulted to Pillar 1 (navy) and
# the audit never saw the failing P3-P6 hero contrast. Iterating all 8 is
# a tiny cost (axe+pa11y on a static page is ~3s each) and closes the gap.
TARGETS: list[tuple[str, str]] = [
    ("index", "index.html"),
] + [
    (f"pillar-p{n}", f"pillar.html?p={n}") for n in range(1, 9)
]

AXE_TAGS = "wcag2a,wcag2aa,wcag21a,wcag21aa"
PA11Y_STANDARD = "WCAG2AA"


def which_or_die(cmd: str) -> str:
    """Resolve a CLI command on PATH; exit code 2 if missing."""
    path = shutil.which(cmd)
    if not path:
        print(f"ERROR: '{cmd}' not found on PATH. Install with: npm install -g @axe-core/cli pa11y",
              file=sys.stderr)
        sys.exit(2)
    return path


def ping_server(url_base: str) -> None:
    """Exit code 2 if the preview server isn't answering."""
    try:
        with urllib.request.urlopen(url_base, timeout=5) as r:
            if r.status >= 400:
                print(f"ERROR: preview server at {url_base} returned HTTP {r.status}", file=sys.stderr)
                sys.exit(2)
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"ERROR: cannot reach preview server at {url_base}: {e}", file=sys.stderr)
        print("Start the server first (e.g., preview_start with name 'static-preview').", file=sys.stderr)
        sys.exit(2)


def run_axe(url: str, out_path: Path) -> list[dict[str, Any]]:
    """Run axe-cli, write raw JSON, return list of violations."""
    # axe supports --save <path> to write raw JSON results.
    cmd = ["axe", url, "--tags", AXE_TAGS, "--save", str(out_path), "--exit"]
    # --exit makes axe return a non-zero exit code when violations exist;
    # we accept that and still parse the output.
    try:
        # On Windows, axe is a .cmd shim; use shell=True to resolve it.
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180,
                              shell=(os.name == "nt"))
    except subprocess.TimeoutExpired:
        print(f"ERROR: axe timed out on {url}", file=sys.stderr)
        sys.exit(2)

    # axe writes an array when --save is given (one entry per URL).
    if not out_path.exists():
        # axe sometimes writes to stdout instead; try parsing stdout as fallback
        try:
            data = json.loads(proc.stdout)
            out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except (json.JSONDecodeError, ValueError):
            print("ERROR: axe produced no output file and no parseable stdout.", file=sys.stderr)
            print(f"  stderr: {proc.stderr[:500]}", file=sys.stderr)
            sys.exit(2)

    data = json.loads(out_path.read_text(encoding="utf-8"))
    # axe --save writes an array of one result object per URL audited
    if isinstance(data, list) and data:
        data = data[0]
    return data.get("violations", [])


def run_pa11y(url: str, out_path: Path) -> list[dict[str, Any]]:
    """Run pa11y with both axe + htmlcs runners, write raw JSON, return issues list."""
    cmd = [
        "pa11y",
        url,
        "--standard", PA11Y_STANDARD,
        "--runner", "axe",
        "--runner", "htmlcs",
        "--reporter", "json",
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180,
                              shell=(os.name == "nt"))
    except subprocess.TimeoutExpired:
        print(f"ERROR: pa11y timed out on {url}", file=sys.stderr)
        sys.exit(2)

    # pa11y exits non-zero when issues are found; parse stdout regardless.
    stdout = proc.stdout.strip()
    if not stdout:
        print("ERROR: pa11y produced no output.", file=sys.stderr)
        print(f"  stderr: {proc.stderr[:500]}", file=sys.stderr)
        sys.exit(2)

    try:
        issues = json.loads(stdout)
    except json.JSONDecodeError as e:
        print(f"ERROR: pa11y output not JSON: {e}", file=sys.stderr)
        print(f"  stdout[:500]: {stdout[:500]}", file=sys.stderr)
        sys.exit(2)

    out_path.write_text(json.dumps(issues, indent=2), encoding="utf-8")
    # pa11y returns only "error" level issues by default for WCAG2AA standard.
    return issues if isinstance(issues, list) else []


def is_needs_review(issue: dict[str, Any]) -> bool:
    """True if this pa11y issue is an axe 'incomplete' (needs manual review) rather
    than a definitive violation. pa11y's axe-runner emits these as type="error" even
    though axe itself classifies them as incomplete — most commonly for colour-contrast
    when an ancestor has a background-image or gradient that axe can't sample.

    These should not count toward WCAG AA failure; they belong in a separate
    "needs manual review" bucket that a human verifies.
    """
    extras = issue.get("runnerExtras") or {}
    return bool(extras.get("needsFurtherReview"))


def normalize_axe_violation(v: dict[str, Any], file: str) -> list[dict[str, Any]]:
    """Axe groups violations by rule; explode one-per-node and normalize shape."""
    out = []
    wcag_tags = [t for t in v.get("tags", []) if t.startswith("wcag")]
    # Convert tag to criterion number where possible (e.g., wcag143 -> 1.4.3)
    criterion = _tag_to_criterion(wcag_tags)
    for node in v.get("nodes", []):
        out.append({
            "tool": "axe",
            "file": file,
            "rule_id": v.get("id", ""),
            "criterion": criterion,
            "wcag_tags": wcag_tags,
            "impact": node.get("impact") or v.get("impact", ""),
            "help": v.get("help", ""),
            "help_url": v.get("helpUrl", ""),
            "description": v.get("description", ""),
            "selector": _first_selector(node.get("target", [])),
            "html": node.get("html", ""),
            "failure_summary": node.get("failureSummary", ""),
        })
    return out


def normalize_pa11y_issue(i: dict[str, Any], file: str) -> dict[str, Any]:
    """Normalize a pa11y issue into the same shape as axe."""
    code = i.get("code", "")
    criterion = _pa11y_code_to_criterion(code)
    return {
        "tool": "pa11y",
        "file": file,
        "rule_id": code,
        "criterion": criterion,
        "wcag_tags": [],
        "impact": i.get("type", ""),  # "error", "warning", "notice"
        "help": i.get("message", ""),
        "help_url": "",
        "description": i.get("message", ""),
        "selector": i.get("selector", ""),
        "html": i.get("context", ""),
        "failure_summary": i.get("message", ""),
    }


def _first_selector(target: list[Any]) -> str:
    """Axe target is sometimes nested arrays for iframe contexts."""
    if not target:
        return ""
    first = target[0]
    if isinstance(first, list) and first:
        return str(first[0])
    return str(first)


def _tag_to_criterion(tags: list[str]) -> str:
    """Map axe WCAG tags like 'wcag143' -> '1.4.3'. Best-effort."""
    for t in tags:
        if not t.startswith("wcag"):
            continue
        digits = t.replace("wcag", "")
        # Skip level tags like wcag2a, wcag2aa, wcag21a, wcag21aa
        if digits in ("2a", "2aa", "21a", "21aa", "22a", "22aa"):
            continue
        # digits like "143" -> "1.4.3"; "412" -> "4.1.2"
        if len(digits) == 3 and digits.isdigit():
            return f"{digits[0]}.{digits[1]}.{digits[2]}"
        if len(digits) == 4 and digits.isdigit():
            # 1412 -> 1.4.12
            return f"{digits[0]}.{digits[1]}.{digits[2:]}"
    return ""


def _pa11y_code_to_criterion(code: str) -> str:
    """pa11y codes look like 'WCAG2AA.Principle1.Guideline1_4.1_4_3.G18.Fail' — extract 1.4.3."""
    parts = code.split(".")
    for p in parts:
        if p.startswith("1_") or p.startswith("2_") or p.startswith("3_") or p.startswith("4_"):
            # shape: "1_4_3"
            bits = p.split("_")
            if len(bits) == 3:
                return ".".join(bits)
    return ""


def dedupe(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Dedupe by (file, criterion, selector). Merge tool names that reported the same issue."""
    seen: dict[tuple[str, str, str], dict[str, Any]] = {}
    for f in findings:
        key = (f["file"], f["criterion"] or f["rule_id"], f["selector"])
        if key in seen:
            existing_tools = set(seen[key].get("reported_by", []))
            existing_tools.add(f["tool"])
            seen[key]["reported_by"] = sorted(existing_tools)
        else:
            seen[key] = {**f, "reported_by": [f["tool"]]}
            seen[key].pop("tool", None)  # replaced by reported_by
    return list(seen.values())


def write_summary(output_dir: Path, results: dict[str, Any]) -> None:
    """Human-readable summary at summary.md."""
    lines = [
        "# External Accessibility Audit — Summary",
        "",
        f"Timestamp: {datetime.now().isoformat(timespec='seconds')}",
        f"URL base:  {results['url_base']}",
        "",
        "## Per-file results",
        "",
    ]
    total_needs_review = 0
    for label, _path in TARGETS:
        per = results["per_file"].get(label)
        if per is None:
            continue  # target skipped or errored mid-run
        axe_count = per["axe_violations"]
        pa11y_count = per["pa11y_issues"]
        unique = per["unique_after_dedupe"]
        needs_review = per.get("pa11y_needs_review", 0)
        total_needs_review += needs_review
        suffix = f" · pa11y needs-review: {needs_review}" if needs_review else ""
        lines.append(f"- **{label}** — axe: {axe_count}, pa11y: {pa11y_count}, unique: {unique}{suffix}")
    lines += [
        "",
        f"## Total unique violations: {results['total_unique']}",
    ]
    if total_needs_review:
        lines += [
            "",
            f"## Total pa11y needs-review items: {total_needs_review}",
            "",
            "pa11y's axe-runner flags these with `runnerExtras.needsFurtherReview: true` —",
            "most often because an ancestor has a background-image or gradient that axe",
            "can't sample. They are NOT definitive WCAG failures. Confirm manually by",
            "computing contrast against the true rendered background; re-audit only if a",
            "real contrast issue is found.",
        ]
    lines += [
        "",
        f"Exit code: {results['exit_code']}",
        "",
        "See `findings.json` for the full deduped findings list, and `axe-*.json` / `pa11y-*.json` for raw tool output.",
    ]
    (output_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url-base", required=True,
                    help="Base URL of the preview server (e.g., http://localhost:3000)")
    ap.add_argument("--output-dir", required=True,
                    help="Directory to write raw + unified audit artifacts")
    args = ap.parse_args()

    url_base = args.url_base.rstrip("/")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Pre-flight
    which_or_die("axe")
    which_or_die("pa11y")
    ping_server(url_base)

    # Static pillar-contrast guard (S.025). Runs in milliseconds and fails fast
    # if any --pillarN x hero-text pairing regresses below WCAG AA, before we
    # spend ~30s in axe/pa11y. Exit 1 from this subprocess means the hero
    # contrast matrix is broken — fix the token usage in pillar.html and re-run.
    verify_script = Path(__file__).resolve().parent / "verify_pillar_contrast.py"
    if verify_script.is_file():
        print("-> Pre-flight: verifying pillar-hero contrast matrix")
        verify_proc = subprocess.run(
            [sys.executable, str(verify_script)],
            capture_output=True,
            text=True,
        )
        # Pass through both stdout (the pass/fail table) and stderr (remediation
        # hint on failure) so the audit log is self-contained.
        if verify_proc.stdout:
            print(verify_proc.stdout, end="")
        if verify_proc.stderr:
            print(verify_proc.stderr, end="", file=sys.stderr)
        if verify_proc.returncode != 0:
            print("ERROR: pillar-contrast pre-flight failed; aborting external audit.",
                  file=sys.stderr)
            return verify_proc.returncode
    else:
        print(f"WARN: verify_pillar_contrast.py not found at {verify_script}; "
              f"skipping static contrast pre-flight.", file=sys.stderr)

    all_findings: list[dict[str, Any]] = []
    per_file: dict[str, dict[str, int]] = {}

    for label, path in TARGETS:
        url = f"{url_base}/{path}"
        # ASCII arrow so stdout prints fine on Windows cp1252 consoles.
        print(f"-> Auditing {url}")

        # Use `label` for output filenames so pillar variants get unique
        # files (axe-pillar-p3.json etc.) rather than overwriting each other.
        axe_out = output_dir / f"axe-{label}.json"
        pa11y_out = output_dir / f"pa11y-{label}.json"

        axe_viols = run_axe(url, axe_out)
        pa11y_issues = run_pa11y(url, pa11y_out)

        # Normalize. Split pa11y errors into definitive violations vs.
        # "needs manual review" (axe incompletes surfaced by pa11y's axe-runner).
        # Tag findings with `label` so a P3-only regression doesn't dedupe
        # away against an otherwise-identical finding from a different pillar.
        norm = []
        for v in axe_viols:
            norm.extend(normalize_axe_violation(v, label))
        pa11y_needs_review_count = 0
        for i in pa11y_issues:
            if i.get("type") != "error":
                continue  # keep only errors; skip warnings/notices
            if is_needs_review(i):
                pa11y_needs_review_count += 1
                continue  # surfaced separately, not a WCAG failure
            norm.append(normalize_pa11y_issue(i, label))

        # Dedupe within this target (label)
        unique_for_file = dedupe(norm)
        per_file[label] = {
            "axe_violations": sum(len(v.get("nodes", [])) for v in axe_viols),
            "pa11y_issues": sum(
                1 for i in pa11y_issues
                if i.get("type") == "error" and not is_needs_review(i)
            ),
            "pa11y_needs_review": pa11y_needs_review_count,
            "unique_after_dedupe": len(unique_for_file),
        }
        suffix = ""
        if pa11y_needs_review_count:
            suffix = f"  (+{pa11y_needs_review_count} pa11y needs-review)"
        print(f"  axe: {per_file[label]['axe_violations']}  "
              f"pa11y: {per_file[label]['pa11y_issues']}  "
              f"unique: {per_file[label]['unique_after_dedupe']}{suffix}")
        all_findings.extend(unique_for_file)

    # Write unified findings
    (output_dir / "findings.json").write_text(
        json.dumps(all_findings, indent=2), encoding="utf-8"
    )

    total_unique = len(all_findings)
    exit_code = 0 if total_unique == 0 else 1

    write_summary(output_dir, {
        "url_base": url_base,
        "per_file": per_file,
        "total_unique": total_unique,
        "exit_code": exit_code,
    })

    print()
    print(f"Total unique violations: {total_unique}")
    print(f"Artifacts: {output_dir}")
    print(f"Exit: {exit_code}  ({'PASS' if exit_code == 0 else 'VIOLATIONS REMAIN'})")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
