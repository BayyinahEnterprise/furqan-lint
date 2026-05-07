#!/usr/bin/env python3
"""Phase G10.5 (al-Mubin) T02 helper.

Extracts the section of CHANGELOG.md for a single version
between its ``## [X.Y.Z]`` header and the next ``## [`` header.

Used by ``.github/workflows/release.yml`` to derive GitHub
Release notes from the canonical CHANGELOG. Stdlib-only; no
markdown AST parser. Regex-based section-cutting per the
Step 3 calibration (30-50 line implementation; do not over-
specify).

Exit codes:

  0  section emitted (may be empty if the version exists but
     the section between its header and the next header
     contains no body content; an empty section is a valid
     CHANGELOG state for skeletal release entries -- the
     T03 backfill script handles empty stdout via its own
     fallback)
  2  no ``## [X.Y.Z]`` header found for the requested version

Usage:

    python scripts/extract_changelog_section.py 0.11.1
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_HEADER_RE = re.compile(r"^## \[([0-9.]+)\]", re.MULTILINE)


def extract_section(text: str, version: str) -> str | None:
    """Return the body between ``## [version]`` and the next
    ``## [`` header, or ``None`` if the version header is absent.

    Trailing whitespace is stripped from the returned body.
    """
    pattern = re.compile(
        rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## \[|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(text)
    if m is None:
        return None
    body = m.group(1)
    # Strip leading "---" separators carried over from the
    # CHANGELOG's per-section divider convention.
    body = re.sub(r"^\s*---\s*\n", "", body, count=1)
    return body.rstrip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract a single CHANGELOG.md section by version."
    )
    parser.add_argument(
        "version",
        help="Version string without the leading 'v' (e.g., 0.11.1)",
    )
    parser.add_argument(
        "--changelog",
        default="CHANGELOG.md",
        help="Path to CHANGELOG.md (default: CHANGELOG.md in cwd)",
    )
    args = parser.parse_args(argv)

    text = Path(args.changelog).read_text(encoding="utf-8")
    section = extract_section(text, args.version)
    if section is None:
        print(
            f"ERROR: no '## [{args.version}]' header found in " f"{args.changelog}",
            file=sys.stderr,
        )
        return 2
    sys.stdout.write(section + "\n" if section else "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
