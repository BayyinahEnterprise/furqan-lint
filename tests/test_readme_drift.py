"""README drift detection (v0.6.1).

Round-11 / v3.0-prep regression test. Parses the project README's
``Remaining limitations`` section, extracts every fixture path
mentioned in the prose, and asserts each path exists on disk.

This would have caught the v0.3.5-era ``redundant_pipe_none.py``
bullet that lingered in README.md across rounds 6-11 even though
the fixture file was deleted when the limit was retired. Same
discipline as `test_documented_limits.py`: documentation cannot
silently drift away from code.

Scope: only the ``Remaining limitations`` section. The rest of the
README may legitimately reference historical fixtures (in CHANGELOG
quotes, in retired-section bullets) and those should not be
required to exist.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"

# Match `tests/fixtures/<dir>/<file>.py` in inline code spans (the only
# shape the README uses for fixture references). The trailing `\.py`
# anchor avoids matching directory paths.
_FIXTURE_PATH_RE = re.compile(r"`(tests/fixtures/[^`\s]+\.py)`")


def _extract_remaining_limitations_section() -> str:
    """Return the README text from the ``## Remaining limitations``
    heading up to (but excluding) the next top-level heading."""
    text = README.read_text(encoding="utf-8")
    start_marker = "## Remaining limitations"
    start = text.find(start_marker)
    assert start != -1, "Remaining limitations section not found in README.md"
    rest = text[start + len(start_marker) :]
    next_heading = re.search(r"\n## ", rest)
    end = next_heading.start() if next_heading else len(rest)
    return rest[:end]


def test_readme_remaining_limitations_section_exists() -> None:
    """The README must have a ``## Remaining limitations`` section
    for this drift check to be meaningful. If it is renamed or
    removed, this test surfaces the rename so the regex anchor can
    be updated deliberately."""
    section = _extract_remaining_limitations_section()
    assert section.strip(), "Remaining limitations section is empty"


def test_every_fixture_path_in_remaining_limitations_exists() -> None:
    """Every ``tests/fixtures/.../<file>.py`` path mentioned in the
    README's Remaining limitations section must exist on disk.

    This catches the failure mode where a documented limit is
    closed (fixture deleted) but the README bullet pointing at the
    fixture is left behind. The redundant_pipe_none.py case
    persisted across rounds 6-11 because no test asserted this
    invariant."""
    section = _extract_remaining_limitations_section()
    paths = _FIXTURE_PATH_RE.findall(section)
    missing = [p for p in paths if not (REPO_ROOT / p).exists()]
    assert not missing, (
        "Remaining limitations references fixture paths that do not "
        f"exist on disk: {missing}. Either restore the fixture or "
        "remove the bullet from the README."
    )
