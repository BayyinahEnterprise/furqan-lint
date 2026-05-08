#!/usr/bin/env python3
"""Phase G10.5 (al-Mubin) T04d: pre-release sweep gate.

Audits the repository for release-tooling drift before a
``vX.Y.Z`` tag is pushed. Closes finding F9 (no automated
sweep of README install pins, GitHub Action use pins,
pre-commit rev pins, and SAFETY_INVARIANTS.md presence).

Sweep patterns:

  1. README install-pin pattern:
     ``pip install "git+...@vX.Y.Z"`` -- if the captured
     version is older than ``pyproject.toml`` version, fail.

  2. GitHub Action use pattern:
     ``uses: BayyinahEnterprise/furqan-lint@vX.Y.Z`` -- same
     staleness check.

  3. Pre-commit rev pattern:
     ``rev: vX.Y.Z`` (followed by a furqan-lint id block) --
     same staleness check.

Presence check: ``SAFETY_INVARIANTS.md`` MUST exist at the
repository root (substrate is post-Phase-G11.A; absence is a
regression of the al-Fatiha PR).

Exit codes: 0 (clean) / 1 (one or more sweep findings).

Usage::

    python scripts/release_sweep.py
    # In CI: invoked as a release-time gate before tag push.
"""

from __future__ import annotations

import re
import sys

try:
    import tomllib
except ModuleNotFoundError:  # Python <3.11 fallback
    import tomli as tomllib  # type: ignore[no-redef]
from pathlib import Path

# Sweep patterns. Each entry is (name, regex, label-for-error).
# ``regex`` MUST capture the version string (e.g., "0.11.0")
# in group 1 (without the leading ``v``).
_README_INSTALL_PIN = re.compile(
    r"pip install \"git\+https://github\.com/[^\"@]+/furqan-lint" r"\.git@v([\d.]+)\""
)
_README_GITHUB_ACTION = re.compile(r"uses: BayyinahEnterprise/furqan-lint@v([\d.]+)")
_README_PRECOMMIT_REV = re.compile(r"rev:\s*v([\d.]+)\s*\n\s*hooks:\s*\n\s*- id:\s*furqan-lint")


def _current_version(repo_root: Path) -> tuple[int, ...]:
    text = (repo_root / "pyproject.toml").read_text(encoding="utf-8")
    data = tomllib.loads(text)
    v = data["project"]["version"]
    return tuple(int(p) for p in v.split("."))


def _version_tuple(v: str) -> tuple[int, ...]:
    return tuple(int(p) for p in v.split("."))


def _sweep_pattern(
    text: str,
    pattern: re.Pattern[str],
    label: str,
    current: tuple[int, ...],
) -> list[str]:
    findings: list[str] = []
    for m in pattern.finditer(text):
        captured = m.group(1)
        if _version_tuple(captured) < current:
            current_str = ".".join(str(p) for p in current)
            findings.append(f"{label}: stale pin v{captured} (current is " f"v{current_str})")
    return findings


def sweep(repo_root: Path) -> list[str]:
    """Run all sweep patterns + presence checks; return list of findings."""
    findings: list[str] = []

    # SAFETY_INVARIANTS.md presence check.
    if not (repo_root / "SAFETY_INVARIANTS.md").is_file():
        findings.append(
            "SAFETY_INVARIANTS.md absent at repository root; "
            "Phase G11.A (al-Fatiha) substrate must be present "
            "before any release-tooling gate runs."
        )

    readme_path = repo_root / "README.md"
    if not readme_path.is_file():
        findings.append("README.md absent at repository root")
        return findings

    text = readme_path.read_text(encoding="utf-8")
    current = _current_version(repo_root)

    findings.extend(_sweep_pattern(text, _README_INSTALL_PIN, "README install pin", current))
    findings.extend(
        _sweep_pattern(
            text,
            _README_GITHUB_ACTION,
            "README GitHub Action pin",
            current,
        )
    )
    findings.extend(
        _sweep_pattern(
            text,
            _README_PRECOMMIT_REV,
            "README pre-commit rev pin",
            current,
        )
    )

    return findings


def main() -> int:
    repo_root = Path(__file__).parent.parent
    findings = sweep(repo_root)
    if not findings:
        print("release_sweep: clean")
        return 0
    print("release_sweep: stale-pin findings detected:")
    for f in findings:
        print(f"  - {f}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
