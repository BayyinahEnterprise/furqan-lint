#!/usr/bin/env python3
"""Phase G10.5 (al-Mubin) T03 + Phase G11.0.1 (at-Tawbah) T08:
one-time backfill of GitHub Release objects for v0.8.2 through v0.11.0.

Run manually after Phase G10.5 T01 + T02 land. After this script
runs against the upstream repository, finding F1 (12 historical
versions tagged on origin but absent from the GitHub Releases UI)
closes.

Phase G11.0.1 (at-Tawbah) T08 / F18 closure: this script REQUIRES
an explicit ``--dry-run`` (preview only, no API mutation) or
``--apply`` (real ``gh release create`` calls) flag. The default
no-flag invocation now exits 1 with usage text rather than silently
mutating live GitHub state. The Round 28 audit observed the
runbook's ``--dry-run`` invocation creating 12 Release objects
because the pre-v0.11.2 script silently no-op'd ``--dry-run``;
v0.11.2 closes that structural-honesty gap loudly.

Phase G11.0.1 T08 / F19 incidental closure: the version filter
now excludes v0.11.1 and later because release.yml's T02 step
(added in Phase G10.5 al-Mubin) creates Release objects on tag
push. Backfilling them would race the workflow.

The script:

  1. Reads CHANGELOG.md and enumerates every ``## [X.Y.Z]`` header.
  2. Excludes the historical-untagged versions (v0.2.0, v0.7.0
     per ``_HISTORICAL_UNTAGGED_VERSIONS`` allowlist) and the
     pre-CHANGELOG-format versions (v0.7.3, v0.8.0, v0.8.1).
  3. For each remaining version, extracts the CHANGELOG section
     via ``scripts/extract_changelog_section.py`` and invokes
     ``gh release create --verify-tag`` against the existing tag.
  4. If extraction returns literally empty output (NOT for
     skeletal entries; those produce non-empty output), falls
     back to a one-line placeholder per S2 calibration.
  5. Logs each tag as ``created`` / ``already exists, skipping``
     / ``BLOCKED`` and continues. Per the T03-specific skip
     rule, partial backfill is acceptable.

Authentication: uses the maintainer's ``gh auth`` context (NOT
a workflow). Run from a local clone with the maintainer logged
in via ``gh auth login``.

Usage::

    cd /path/to/furqan-lint
    python scripts/backfill_github_releases.py
    # Save the transcript to docs/release-checklist.md Appendix A
    # as evidence of execution.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

_HISTORICAL_UNTAGGED_VERSIONS = frozenset({"0.2.0", "0.7.0"})
_PRE_CHANGELOG_FORMAT_VERSIONS = frozenset({"0.7.3", "0.8.0", "0.8.1"})
# v0.1.0 already has a Release object on the upstream repo and
# is excluded from this backfill so the script does not attempt
# to recreate it.
_ALREADY_HAS_RELEASE_OBJECT = frozenset({"0.1.0"})
# Phase G10.5 T03 backfill scope: v0.8.2 through v0.11.0
# inclusive (12 versions). Versions below v0.8.2 are out of
# scope per the structured-table calibration in the prompt;
# pre-v0.8.2 entries in CHANGELOG.md predate the
# release.yml + Trusted-Publishing era and are not eligible
# for retroactive Release-object backfill via this tool.
_BACKFILL_FLOOR = (0, 8, 2)
# Phase G11.0.1 T08 / F19 incidental closure: workflow-managed
# release boundary. v0.11.1 was the first release whose Release
# object was created by release.yml T02 (Phase G10.5 al-Mubin
# ship); backfilling at v0.11.1+ would race the workflow.
_WORKFLOW_MANAGED_FLOOR = (0, 11, 1)


def _version_tuple(v: str) -> tuple[int, ...]:
    """Normalize ``"0.9.3.1"`` -> ``(0, 9, 3, 1)`` for floor comparison."""
    return tuple(int(part) for part in v.split("."))


def _extract_versions_from_changelog(
    changelog_path: Path = Path("CHANGELOG.md"),
) -> list[str]:
    """Return the versions to backfill, in CHANGELOG order
    (top-down, newest first)."""
    text = changelog_path.read_text(encoding="utf-8")
    versions: list[str] = []
    for m in re.finditer(r"^## \[([0-9.]+)\]", text, re.MULTILINE):
        v = m.group(1)
        if v in _ALREADY_HAS_RELEASE_OBJECT:
            continue
        if v in _HISTORICAL_UNTAGGED_VERSIONS:
            continue
        if v in _PRE_CHANGELOG_FORMAT_VERSIONS:
            continue
        if _version_tuple(v)[:3] < _BACKFILL_FLOOR:
            continue
        # Phase G11.0.1 T08 / F19 incidental closure:
        # workflow-managed releases (v0.11.1+) are intentionally
        # excluded from backfill scope. The release.yml T02 step
        # (added in Phase G10.5 al-Mubin) creates GitHub Release
        # objects on tag push for these versions; backfilling
        # them here would race with the workflow.
        if _version_tuple(v)[:3] >= _WORKFLOW_MANAGED_FLOOR:
            continue
        versions.append(v)
    return versions


def _extract_notes(version: str) -> str:
    """Return the CHANGELOG section for ``version`` via the T02
    helper; fall back to a one-line placeholder if extraction
    returns literally empty output.
    """
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/extract_changelog_section.py",
            version,
        ],
        capture_output=True,
        text=True,
    )
    notes = proc.stdout
    if not notes.strip():
        # Per S2 calibration: empty output (NOT skeletal) -> fallback.
        notes = f"Patch release. See `git log v<previous>..v{version}` " f"for changes."
    return notes


def _create_release(tag: str, notes: str) -> tuple[bool, str, str | None]:
    """Run ``gh release create``; return (created_ok, status, blocked_reason).

    ``status`` is one of ``created`` / ``already_exists`` /
    ``blocked``. ``blocked_reason`` is non-None only when
    ``status == "blocked"``.
    """
    result = subprocess.run(
        [
            "gh",
            "release",
            "create",
            tag,
            "--title",
            tag,
            "--notes",
            notes,
            "--verify-tag",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return True, "created", None
    if "already exists" in result.stderr:
        return True, "already_exists", None
    return False, "blocked", result.stderr.strip()


def _build_arg_parser() -> argparse.ArgumentParser:
    """Phase G11.0.1 T08 / F18 closure: argparse with required
    mutually-exclusive --dry-run / --apply group.

    No-flag invocation exits 1 with usage rather than silently
    no-op'ing the documented --dry-run flag and mutating live
    GitHub state.
    """
    p = argparse.ArgumentParser(
        prog="backfill_github_releases.py",
        description=(
            "One-time backfill of GitHub Release objects for "
            "historical tags. REQUIRES explicit --dry-run or --apply."
        ),
        epilog=(
            "REQUIRED: --dry-run for preview OR --apply to execute. "
            "No silent-execute; the substrate's surface claim must "
            "match its behavior."
        ),
    )
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the backfill scope without API mutation.",
    )
    mode.add_argument(
        "--apply",
        action="store_true",
        help="Execute the backfill (creates real GitHub Release objects).",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    versions = _extract_versions_from_changelog()
    if args.dry_run:
        print(f"DRY-RUN: would backfill {len(versions)} versions:")
        for v in versions:
            print(f"  v{v}")
        print("\nNo API calls executed. Pass --apply to execute.")
        return 0
    # args.apply is True (mutually exclusive with --dry-run guarantees this).
    print(f"APPLYING: backfilling {len(versions)} versions: {versions}")
    blocked: list[tuple[str, str]] = []
    created: list[str] = []
    skipped: list[str] = []
    for v in versions:
        tag = f"v{v}"
        notes = _extract_notes(v)
        ok, status, reason = _create_release(tag, notes)
        if status == "created":
            print(f"{tag}: created")
            created.append(tag)
        elif status == "already_exists":
            print(f"{tag}: already exists, skipping")
            skipped.append(tag)
        else:  # blocked
            assert reason is not None
            print(f"{tag}: BLOCKED -- {reason}", file=sys.stderr)
            blocked.append((tag, reason))
            # Per the T03-specific skip rule: log and proceed.
            continue
    print(
        f"\nSummary: {len(created)} created, "
        f"{len(skipped)} already existed, "
        f"{len(blocked)} blocked."
    )
    if blocked:
        print(
            "\nBLOCKED versions (record in " "docs/release-checklist.md Appendix A):",
            file=sys.stderr,
        )
        for tag, reason in blocked:
            print(f"  {tag}: {reason}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
