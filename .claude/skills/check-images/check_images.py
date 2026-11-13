"""
check_images.py — dashboard image-reference audit

Walks the HTML/JSON that feeds the strategic plan dashboard and the files
actually sitting in /images/, then flags drift between the two:

  A. Broken references (error)  — HTML/JSON points at a missing file.
     When possible, surfaces a candidate replacement (e.g., a "-v2"
     version sitting in the same folder) so Claude can offer to patch.
  B. Suspicious "newer version" files (warn)  — a file in /images/ looks
     like a graphics-team update (`-v2`, `-new`, `-final`, ...) but the
     HTML still references the base-name version.
  C. Duplicate basenames across subfolders (warn)  — same filename lives
     in multiple parent folders (e.g., `Icons Only/` and `Icons Numbered/`).
     Often intentional, but worth eyeballing.
  D. Orphaned files (info)  — present in /images/ but not referenced
     anywhere. Many are intentional (Tableau screenshots, style guides).

Exit code:
  0  — no errors (warnings and info do not change this)
  1  — at least one broken reference or error-level issue
  2  — fatal problem (file read error, malformed JSON)

Usage:
  python .claude/skills/check-images/check_images.py

Runs from any CWD — all paths resolve relative to this script's location.

Author: Andy Baxter / Claude  |  2026-04-14
"""

import difflib
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import unquote

# Ensure UTF-8 output on Windows — em-dashes otherwise appear as � in
# cp1252 terminals. Safe no-op elsewhere.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, Exception):
    pass

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------
# Script lives at .claude/skills/check-images/check_images.py
# Project root is 3 parents up.
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
IMAGES_DIR = PROJECT_ROOT / "images"

# The three sources of image references in the dashboard.
INDEX_HTML = PROJECT_ROOT / "index.html"
PILLAR_HTML = PROJECT_ROOT / "pillar.html"
MEASURES_JSON = PROJECT_ROOT / "data" / "measures.json"
PILLAR_DATA_JSON = PROJECT_ROOT / "data" / "pillar-data.json"

# File extensions we treat as "images" worth auditing.
IMAGE_EXTS = {".png", ".svg", ".jpg", ".jpeg", ".webp", ".gif", ".ico"}

TODAY = date.today()

# Regex patterns for the "this looks like a newer delivery" heuristic.
# Applied to the file stem (no extension), case-insensitive.
# If the stem ends with one of these, we consider the file "suffixed".
#   -v2, -v10         → version number
#   -new, -final, -updated, -latest, -revised
#   (1), (2)          → Windows "copy of" suffix
#   _2026-04-14       → date stamp
#   -FINAL_v3 etc.    → multiple suffixes stack, we strip greedily
VERSION_SUFFIX_RE = re.compile(
    r"("
    r"[-_ ]?[Vv]\d+"
    r"|[-_ ]?(new|final|updated|latest|revised|draft|old|orig|original|copy)"
    r"|[-_ ]?\(\d+\)"
    r"|[-_ ]?\d{4}-\d{2}-\d{2}"
    r")+$",
    re.IGNORECASE,
)

# Regex patterns to pull image references out of HTML.
#   <img src="..."> or <img src='...'>
IMG_SRC_RE = re.compile(r"""<img\b[^>]*\bsrc\s*=\s*["']([^"']+)["']""", re.IGNORECASE)
#   CSS url(...) — handles quoted and unquoted variants.
CSS_URL_RE = re.compile(r"""url\(\s*["']?([^"')]+)["']?\s*\)""", re.IGNORECASE)
#   <a href="..."> / <link href="..."> to images (occasionally used for downloads).
LINK_HREF_RE = re.compile(r"""<(?:a|link)\b[^>]*\bhref\s*=\s*["']([^"']+)["']""", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Finding record + helpers
# ---------------------------------------------------------------------------
@dataclass
class Finding:
    """One image-audit issue. Severity drives sort order and exit code."""
    severity: str           # 'error' | 'warn' | 'info'
    category: str           # short label (e.g., 'Broken reference')
    location: str           # "file:line" or similar
    message: str
    fix: str = ""           # optional concrete remediation suggestion


findings: list[Finding] = []


def add(severity: str, category: str, location: str, message: str, fix: str = "") -> None:
    """Append a Finding to the global list. Thin wrapper for readability."""
    findings.append(Finding(severity, category, location, message, fix))


# ---------------------------------------------------------------------------
# Reference extraction
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ImageRef:
    """A single place in the source where an image path appears."""
    source: str     # e.g., "index.html", "data/measures.json"
    line: int       # 1-based line number (best-effort; 0 if unknown)
    raw: str        # the path as it appears in the file
    norm: str       # URL-decoded, forward-slashed, leading-/-stripped


def _normalize_path(raw: str) -> str:
    """
    Turn a raw image path into something we can match against pathlib paths.
    - URL-decode `%20` → space
    - Forward slashes only
    - Strip leading `./` and `/`
    - Ignore data: URIs and absolute URLs
    """
    s = unquote(raw).replace("\\", "/")
    if s.startswith("data:") or s.startswith("http://") or s.startswith("https://"):
        return ""
    # Strip query strings and fragments (e.g., ?v=2, #icon)
    s = s.split("?", 1)[0].split("#", 1)[0]
    if s.startswith("./"):
        s = s[2:]
    if s.startswith("/"):
        s = s[1:]
    return s


def _ref_is_image(norm: str) -> bool:
    """Only track references that point into /images/ with a known extension."""
    if not norm:
        return False
    if not norm.lower().startswith("images/"):
        return False
    return Path(norm).suffix.lower() in IMAGE_EXTS


def extract_refs_from_html(path: Path) -> list[ImageRef]:
    """Pull img/src, CSS url(...), and href image paths from an HTML file."""
    if not path.exists():
        add("error", "Setup", str(path.relative_to(PROJECT_ROOT)),
            "File not found.",
            fix="Check the file path in check_images.py.")
        return []
    refs: list[ImageRef] = []
    try:
        with path.open(encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        add("error", "Setup", str(path.relative_to(PROJECT_ROOT)),
            f"Could not read file: {e}")
        return []

    rel = path.relative_to(PROJECT_ROOT).as_posix()
    for lineno, line in enumerate(lines, start=1):
        for regex in (IMG_SRC_RE, CSS_URL_RE, LINK_HREF_RE):
            for m in regex.finditer(line):
                raw = m.group(1).strip()
                norm = _normalize_path(raw)
                if _ref_is_image(norm):
                    refs.append(ImageRef(source=rel, line=lineno, raw=raw, norm=norm))
    return refs


def extract_refs_from_json(path: Path) -> list[ImageRef]:
    """
    Walk a JSON file and collect every string value that looks like a
    path into /images/. Line numbers aren't available cheaply, so we
    record 0 and include the JSON-pointer-ish trail in the location.
    """
    if not path.exists():
        add("error", "Setup", str(path.relative_to(PROJECT_ROOT)),
            "File not found.")
        return []
    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        add("error", "Setup", str(path.relative_to(PROJECT_ROOT)),
            f"Could not read file: {e}")
        return []
    except json.JSONDecodeError as e:
        add("error", "Setup", str(path.relative_to(PROJECT_ROOT)),
            f"JSON parse failed: {e}")
        return []

    rel = path.relative_to(PROJECT_ROOT).as_posix()
    refs: list[ImageRef] = []

    # Build a readable path like "[0]/badgeImageUrl" or "[2]/whatsInMotion[1]/iconUrl"
    # so Andy can find the row quickly. For measures.json this is especially helpful.
    def walk(node: Any, trail: str) -> None:
        if isinstance(node, dict):
            # Prefer an ID-bearing key when we're inside a measure dict
            id_val = node.get("measureId") or node.get("id")
            if id_val and trail.endswith("]"):
                trail = re.sub(r"\[\d+\]$", f"/{id_val}", trail)
            for k, v in node.items():
                walk(v, f"{trail}/{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{trail}[{i}]")
        elif isinstance(node, str):
            norm = _normalize_path(node)
            if _ref_is_image(norm):
                # Encode the JSON trail in the "line" field as zero + location detail.
                refs.append(ImageRef(
                    source=f"{rel}{trail}",
                    line=0,
                    raw=node,
                    norm=norm,
                ))

    walk(data, "")
    return refs


# ---------------------------------------------------------------------------
# File inventory
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ImageFile:
    """One file on disk under /images/."""
    path: Path          # absolute
    rel: str            # posix path from project root, e.g. "images/Badges/Badges-AP.svg"
    basename: str       # "Badges-AP.svg"
    stem: str           # "Badges-AP"
    suffix: str         # ".svg"
    parent: str         # posix path of parent folder, e.g. "images/Badges"


def inventory_images() -> list[ImageFile]:
    """Walk /images/ and return every image file as an ImageFile record."""
    if not IMAGES_DIR.exists():
        add("error", "Setup", "images/",
            "Images directory not found.",
            fix="Check that /images/ exists at the project root.")
        return []
    files: list[ImageFile] = []
    for p in IMAGES_DIR.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in IMAGE_EXTS:
            continue
        rel_path = p.relative_to(PROJECT_ROOT).as_posix()
        files.append(ImageFile(
            path=p,
            rel=rel_path,
            basename=p.name,
            stem=p.stem,
            suffix=p.suffix.lower(),
            parent=p.parent.relative_to(PROJECT_ROOT).as_posix(),
        ))
    return files


# ---------------------------------------------------------------------------
# A. Broken references  (error)
# ---------------------------------------------------------------------------
def _base_stem(stem: str) -> str:
    """Strip recognized version suffixes from a stem, recursively."""
    prev = None
    s = stem
    # Loop in case a stem has stacked suffixes (`Foo-FINAL-v3`).
    while prev != s:
        prev = s
        s = VERSION_SUFFIX_RE.sub("", s)
    return s.strip("-_ ")


def _find_candidate(missing: str, by_rel: dict[str, ImageFile],
                    files: list[ImageFile]) -> ImageFile | None:
    """
    Given a reference that doesn't resolve, try to find a plausible
    replacement on disk. Strategy (in order):
      1. Same folder, stem with version suffix stripped/added.
      2. Same folder, fuzzy match on basename (difflib).
      3. Anywhere, same basename (case-insensitive fallback — flags
         case-sensitivity bugs that will break GitHub Pages).
    """
    missing_path = Path(missing)
    missing_parent = missing_path.parent.as_posix()
    missing_stem = missing_path.stem
    missing_ext = missing_path.suffix.lower()
    missing_base_stem = _base_stem(missing_stem)

    # Pass 1: same folder, strip-or-add version suffix.
    same_folder = [f for f in files if f.parent == missing_parent and f.suffix == missing_ext]
    for f in same_folder:
        if _base_stem(f.stem).lower() == missing_base_stem.lower() and f.stem != missing_stem:
            return f

    # Pass 2: same folder, fuzzy basename match.
    if same_folder:
        names = [f.basename for f in same_folder]
        match = difflib.get_close_matches(missing_path.name, names, n=1, cutoff=0.8)
        if match:
            return next(f for f in same_folder if f.basename == match[0])

    # Pass 3: any folder, case-insensitive basename match.
    for f in files:
        if f.basename.lower() == missing_path.name.lower() and f.rel != missing:
            return f

    return None


def check_broken_references(refs: list[ImageRef], files: list[ImageFile]) -> None:
    """For each referenced path, check the file exists; if not, propose a candidate."""
    by_rel = {f.rel: f for f in files}

    for ref in refs:
        if ref.norm in by_rel:
            # Exact hit — good.
            continue

        # Check for a case-sensitivity mismatch specifically (will break on
        # GitHub Pages / Linux, silently succeed on Windows).
        ci_match = next((f for f in files if f.rel.lower() == ref.norm.lower()), None)
        if ci_match:
            loc = ref.source if ref.line == 0 else f"{ref.source}:{ref.line}"
            add("error", "Broken reference (case)", loc,
                f"References `{ref.norm}` but the file on disk is `{ci_match.rel}`. "
                "Windows is case-insensitive, but GitHub Pages is not.",
                fix=f"Update the reference to match the real casing: `{ci_match.rel}`.")
            continue

        # Genuine miss — look for a candidate replacement.
        candidate = _find_candidate(ref.norm, by_rel, files)
        loc = ref.source if ref.line == 0 else f"{ref.source}:{ref.line}"
        if candidate:
            add("error", "Broken reference", loc,
                f"References `{ref.norm}` which does not exist. "
                f"Candidate on disk: `{candidate.rel}`.",
                fix=f"Update reference to `{candidate.rel}` (after confirming it's correct).")
        else:
            add("error", "Broken reference", loc,
                f"References `{ref.norm}` which does not exist on disk.",
                fix="Confirm the file was delivered into /images/; "
                    "or update the reference to the correct path.")


# ---------------------------------------------------------------------------
# B. Suspicious "newer version" files  (warn)
# ---------------------------------------------------------------------------
def check_suspicious_versions(refs: list[ImageRef], files: list[ImageFile]) -> None:
    """
    Flag files in /images/ whose name looks like a newer delivery
    (`-v2`, `-final`, ...) when a base-name version of the file is
    referenced in the HTML/JSON but this suffixed version is not.
    Strong signal that a replacement landed but never got wired up.
    """
    # Group all files by (parent, base_stem, suffix) so siblings that differ
    # only in version suffix end up in the same bucket.
    buckets: dict[tuple[str, str, str], list[ImageFile]] = {}
    for f in files:
        key = (f.parent, _base_stem(f.stem).lower(), f.suffix)
        buckets.setdefault(key, []).append(f)

    # Set of normalized reference paths for fast lookup.
    referenced = {r.norm for r in refs}

    for (parent, base, ext), group in buckets.items():
        if len(group) < 2:
            continue  # No siblings → nothing to suspect.

        suffixed = [f for f in group if VERSION_SUFFIX_RE.search(f.stem)]
        unsuffixed = [f for f in group if not VERSION_SUFFIX_RE.search(f.stem)]
        if not suffixed or not unsuffixed:
            continue  # All or none suffixed → not the pattern we care about.

        # Is the HTML referencing the UN-suffixed (older-looking) file
        # while a suffixed (newer-looking) sibling exists unused?
        for old in unsuffixed:
            if old.rel not in referenced:
                continue
            unused_newer = [f for f in suffixed if f.rel not in referenced]
            if unused_newer:
                names = ", ".join(f"`{f.basename}`" for f in unused_newer)
                add("warn", "Suspicious newer version", old.rel,
                    f"HTML/JSON references `{old.rel}`, but sibling file(s) "
                    f"that look like newer deliveries exist unused: {names}.",
                    fix="If the suffixed file is the current version, update the "
                        "reference to use it. If it's an old backup, remove or archive it.")


# ---------------------------------------------------------------------------
# C. Duplicate basenames across subfolders  (warn)
# ---------------------------------------------------------------------------
def check_duplicate_basenames(refs: list[ImageRef], files: list[ImageFile]) -> None:
    """
    Group files by exact basename. Any basename that appears in 2+
    different parent folders is flagged so Andy can check whether a
    graphics-team update could have landed in the wrong sibling folder.
    """
    by_basename: dict[str, list[ImageFile]] = {}
    for f in files:
        by_basename.setdefault(f.basename, []).append(f)

    referenced = {r.norm for r in refs}

    for basename, group in sorted(by_basename.items()):
        if len(group) < 2:
            continue
        # Which copy (if any) does the HTML actually reference?
        used = [f for f in group if f.rel in referenced]
        unused = [f for f in group if f.rel not in referenced]

        locations = "\n    " + "\n    ".join(
            f"- {f.rel}" + ("  ← referenced" if f.rel in referenced else "")
            for f in group
        )
        if used and unused:
            # Mixed — at least one used, one not. Most interesting case.
            add("warn", "Duplicate basename", basename,
                f"`{basename}` exists in {len(group)} folders. HTML/JSON references "
                f"only some copies — make sure new graphics land in the right folder.{locations}",
                fix="If the un-referenced copies are reference material, that's fine. "
                    "If they're leftover, consider archiving to avoid future confusion.")
        elif not used:
            # None used — less likely to be a problem.
            add("info", "Duplicate basename (unused)", basename,
                f"`{basename}` exists in {len(group)} folders; none are referenced.{locations}")
        else:
            # All copies referenced — probably intentional parallel variants.
            add("info", "Duplicate basename (all used)", basename,
                f"`{basename}` exists in {len(group)} folders, all referenced. "
                f"Likely intentional parallel variants (e.g., icon sets).{locations}")


# ---------------------------------------------------------------------------
# D. Orphaned files  (info)
# ---------------------------------------------------------------------------
def check_orphans(refs: list[ImageRef], files: list[ImageFile]) -> None:
    """Files in /images/ that aren't referenced by any HTML/JSON source."""
    referenced = {r.norm for r in refs}
    orphans = [f for f in files if f.rel not in referenced]
    if not orphans:
        return
    # Group by parent folder for scannable output.
    by_parent: dict[str, list[ImageFile]] = {}
    for f in orphans:
        by_parent.setdefault(f.parent, []).append(f)
    for parent, group in sorted(by_parent.items()):
        names = ", ".join(f"`{f.basename}`" for f in sorted(group, key=lambda x: x.basename))
        add("info", "Orphan files", parent,
            f"{len(group)} file(s) not referenced by HTML/JSON: {names}",
            fix="If these are reference material (style guides, screenshots), "
                "ignore. If they're old versions, consider archiving.")


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
SEV_ORDER = {"error": 0, "warn": 1, "info": 2}
SEV_LABEL = {"error": "Errors", "warn": "Warnings", "info": "Info"}


def print_report(refs: list[ImageRef], files: list[ImageFile]) -> int:
    """Emit a grouped markdown report. Returns exit code (1 if any errors)."""
    errors = [f for f in findings if f.severity == "error"]
    warns = [f for f in findings if f.severity == "warn"]
    infos = [f for f in findings if f.severity == "info"]

    print(f"# Dashboard Image Audit — {TODAY.isoformat()}\n")
    print(f"Scanned {len(refs)} image reference(s) across HTML/JSON "
          f"and {len(files)} file(s) under /images/.\n")

    for sev, group in (("error", errors), ("warn", warns), ("info", infos)):
        label = SEV_LABEL[sev]
        print(f"## {label} ({len(group)})\n")
        if not group:
            print("_None_\n")
            continue
        by_cat: dict[str, list[Finding]] = {}
        for f in group:
            by_cat.setdefault(f.category, []).append(f)
        for cat, items in sorted(by_cat.items()):
            print(f"### {cat} ({len(items)})\n")
            for f in items:
                line = f"- **[{f.location}]** {f.message}"
                if f.fix:
                    line += f" _Fix: {f.fix}_"
                print(line)
            print()

    print("## Summary\n")
    print(f"Errors: {len(errors)}  |  Warnings: {len(warns)}  |  Info: {len(infos)}\n")

    if errors:
        print("## Next step\n")
        print("Claude should propose a fix for each broken reference that has a "
              "candidate file, show the diff, and wait for Andy's confirmation "
              "before editing the HTML or JSON.\n")

    return 1 if errors else 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    try:
        # Collect references from all three sources.
        refs: list[ImageRef] = []
        refs += extract_refs_from_html(INDEX_HTML)
        refs += extract_refs_from_html(PILLAR_HTML)
        refs += extract_refs_from_json(MEASURES_JSON)
        # pillar-data.json doesn't currently contain image paths, but include
        # it anyway so we pick up any future additions (iconUrl, etc.).
        refs += extract_refs_from_json(PILLAR_DATA_JSON)

        files = inventory_images()

        # Even if reference extraction added setup errors, keep going so the
        # report is as complete as possible.
        check_broken_references(refs, files)
        check_suspicious_versions(refs, files)
        check_duplicate_basenames(refs, files)
        check_orphans(refs, files)

        return print_report(refs, files)
    except Exception as e:
        # Fatal problem — exit code 2 distinguishes this from normal error findings.
        print(f"# Fatal error\n\n{type(e).__name__}: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
