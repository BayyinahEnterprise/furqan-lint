"""Phase G10.5 T02: pinning tests for the CHANGELOG section
extractor used by release.yml's auto-Release step.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "scripts" / "extract_changelog_section.py"


def _run(version: str, changelog_text: str) -> tuple[int, str, str]:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as fh:
        fh.write(changelog_text)
        path = Path(fh.name)
    try:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), version, "--changelog", str(path)],
            capture_output=True,
            text=True,
        )
        return proc.returncode, proc.stdout, proc.stderr
    finally:
        path.unlink()


def test_extracts_section_between_headers():
    """Standard case: section between two ## [X.Y.Z] headers."""
    cl = (
        "# Changelog\n\n"
        "## [0.11.1] - 2026-05-08\n\n"
        "Tooling tightening release.\n\n"
        "### Closures\n\n"
        "- F1 closed via T02\n\n"
        "## [0.11.0] - 2026-05-07\n\n"
        "Phase G11.1 ship.\n"
    )
    rc, out, err = _run("0.11.1", cl)
    assert rc == 0, err
    assert "Tooling tightening release." in out
    assert "F1 closed via T02" in out
    assert "Phase G11.1 ship" not in out


def test_returns_exit_2_for_missing_version():
    """Unknown version: stdout empty, stderr names the missing
    header, exit code 2.
    """
    cl = "## [0.11.1] - 2026-05-08\n\nBody.\n"
    rc, out, err = _run("9.9.9", cl)
    assert rc == 2
    assert out == ""
    assert "9.9.9" in err


def test_extracts_last_section_to_eof():
    """Last version in file: section runs to EOF when no
    subsequent ## [X.Y.Z] header follows.
    """
    cl = "## [0.11.1] - 2026-05-08\n\n" "Final entry.\n\n" "Trailing prose.\n"
    rc, out, err = _run("0.11.1", cl)
    assert rc == 0, err
    assert "Final entry." in out
    assert "Trailing prose." in out


def test_strips_leading_horizontal_rule_separator():
    """The CHANGELOG uses '---' as a per-section divider; the
    extractor strips a leading '---\\n' so release notes do not
    start with a stray rule.
    """
    cl = "## [0.11.1] - 2026-05-08\n\n" "---\n\n" "Body after rule.\n"
    rc, out, err = _run("0.11.1", cl)
    assert rc == 0, err
    assert not out.lstrip().startswith("---")
    assert "Body after rule." in out
