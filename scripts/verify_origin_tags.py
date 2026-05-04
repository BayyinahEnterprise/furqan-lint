#!/usr/bin/env python3
"""Verify that every CHANGELOG-listed version has a tag pushed to origin.

v0.8.4 §7.12 origin-tag-presence gate. Round-22 patch audit found
that v0.7.3 and v0.8.3 had been released (commits merged, CHANGELOG
populated, version bumped) but the corresponding ``vX.Y.Z`` tags
had never been pushed to origin. The release workflow added in
v0.8.4 commit 8 listens for ``v*`` tag pushes; without the tags,
PyPI never receives a publish event. This gate catches the same
shape going forward.

Usage
=====

In CI (the default mode):

    python scripts/verify_origin_tags.py

Parses ``CHANGELOG.md`` for ``## [X.Y.Z] - <date>`` headers,
excludes any header annotated as ``(absorbed into vA.B.C)``, and
queries ``git ls-remote --tags origin vX.Y.Z`` for each remaining
version. Exits 0 if every version has a corresponding origin tag;
exits 1 with a list of missing tags otherwise.

Smoke-test mode (``--dry-run``):

    python scripts/verify_origin_tags.py --dry-run

Parses ``CHANGELOG.md`` and prints the list of expected tag names
(one per line) to stdout WITHOUT making any network call. Used by
the hermetic pytest smoke-test to verify that the parser handles
the absorbed-into exclusion and version sort order correctly.

This script is run from the CI workflow's ``lint`` job, NOT from
the pytest suite (the pytest suite must remain hermetic; it has no
network access in sandbox runs).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import tomllib

REPO_ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
PYPROJECT = REPO_ROOT / "pyproject.toml"

# Historical-gap allowlist. These versions appear in CHANGELOG.md
# but were never tagged on origin (the tag-push step was skipped at
# the original release moment, predating this gate). The gate
# acknowledges the gap explicitly rather than silently masking it or
# rewriting history with synthetic tags from arbitrary commits.
#
# Adding entries here requires an audit note in CHANGELOG.md. New
# (post-v0.8.4) versions are NOT eligible for this allowlist; the
# gate must catch them at PR time.
_HISTORICAL_UNTAGGED_VERSIONS: frozenset[str] = frozenset(
    {
        "v0.2.0",  # Pre-tag-discipline; the v0.2.0 line was rolled
        # forward into v0.3.0 without a separate origin tag.
        "v0.7.0",  # Superseded by v0.7.0.1 (the four-component
        # corrective) before the v0.7.0 tag was pushed.
    }
)


def _current_pyproject_version() -> str:
    """Return the current ``pyproject.toml`` version string
    prefixed with ``v`` (e.g. ``v0.8.4``). The current version is
    expected to be absent from origin tags during a release-prep
    PR; the tag push happens post-merge by design (the release.yml
    workflow keys on the tag-push event).
    """
    data = tomllib.loads(PYPROJECT.read_text())
    version = data["project"]["version"]
    return f"v{version}"


# Header pattern: "## [X.Y.Z] - YYYY-MM-DD" or
# "## [X.Y.Z.W] - YYYY-MM-DD" (the v0.7.0.1 four-component case).
# An optional "(absorbed into vA.B.C)" suffix is captured separately
# so we can exclude that version from the gate.
_HEADER_PATTERN = re.compile(
    r"^##\s+\[(\d+\.\d+\.\d+(?:\.\d+)?)\]\s+-\s+\S+(?:\s+\((?P<note>[^)]*)\))?\s*$",
    re.MULTILINE,
)

_ABSORBED_PATTERN = re.compile(r"absorbed into", re.IGNORECASE)


def parse_changelog_versions(changelog_text: str) -> list[str]:
    """Return the list of ``vX.Y.Z`` tags expected on origin.

    Excludes:

    * Versions whose header line carries an ``(absorbed into ...)``
      annotation (e.g. v0.7.4 absorbed into v0.8.0 in the v0.8.0
      release).
    * Versions whose header is followed within 5 lines by a body
      line matching ``absorbed into`` (defensive against future
      annotations placed in the body rather than the header).
    """
    expected: list[str] = []
    lines = changelog_text.splitlines()
    for idx, line in enumerate(lines):
        match = _HEADER_PATTERN.match(line)
        if match is None:
            continue
        version = match.group(1)
        note = match.group("note") or ""
        if _ABSORBED_PATTERN.search(note):
            continue
        # Defensive: also check the next 5 lines for absorbed-into prose.
        body_window = "\n".join(lines[idx + 1 : idx + 6])
        if _ABSORBED_PATTERN.search(body_window):
            continue
        expected.append(f"v{version}")
    return expected


def query_origin_tags() -> set[str]:
    """Run ``git ls-remote --tags origin`` and return the set of
    short tag names (e.g. ``{'v0.8.3', 'v0.7.3', ...}``)."""
    result = subprocess.run(
        ["git", "ls-remote", "--tags", "origin"],
        capture_output=True,
        text=True,
        check=True,
        cwd=REPO_ROOT,
    )
    tags: set[str] = set()
    for line in result.stdout.splitlines():
        # Format: "<sha>\trefs/tags/<tag>" (sometimes "<sha>\trefs/tags/<tag>^{}")
        parts = line.split("\trefs/tags/")
        if len(parts) != 2:
            continue
        tag = parts[1].rstrip("^{}")
        tags.add(tag)
    return tags


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print expected tag names without querying origin (for the smoke-test).",
    )
    args = parser.parse_args()

    if not CHANGELOG.is_file():
        print(f"CHANGELOG.md not found at {CHANGELOG}", file=sys.stderr)
        return 1

    expected = parse_changelog_versions(CHANGELOG.read_text())

    if args.dry_run:
        for tag in expected:
            print(tag)
        return 0

    current_version_tag = _current_pyproject_version()
    origin_tags = query_origin_tags()
    missing = [
        tag
        for tag in expected
        if tag not in origin_tags
        and tag != current_version_tag
        and tag not in _HISTORICAL_UNTAGGED_VERSIONS
    ]
    if missing:
        print(
            "CHANGELOG-listed versions without a corresponding origin tag:",
            file=sys.stderr,
        )
        for tag in missing:
            print(f"  {tag}", file=sys.stderr)
        print(
            "\nFix: push the missing tag(s) with `git push origin refs/tags/<tag>`.",
            file=sys.stderr,
        )
        return 1
    print(f"All {len(expected)} CHANGELOG-listed versions have origin tags.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
