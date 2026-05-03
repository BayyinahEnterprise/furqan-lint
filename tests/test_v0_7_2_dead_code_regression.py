"""Forward-compat regression test (v0.7.2).

Pins the absence of ``_d24_diagnostic_in_r3_set``. The function
was a defensive D24-suppression helper added in v0.6.0 that turned
out to be dead code (D24 only fires on partial-path coverage,
R3 only on zero-return shapes; the two are non-overlapping in
practice). It was removed in the v0.6.1 corrective (commit
b0a4b18). The round-13 audit note flagging the dead code was
already resolved at that point; the v0.7.2 prompt's §3.4 direction
to "delete the function" was based on a stale audit note.

This test pins the absence so a future re-introduction (e.g., a
contributor copying old runner.py for inspiration) trips a
deliberate test failure rather than silently re-adding the dead
code. Cheap insurance.

The cost-of-removal-from-this-test is one line (delete the
assertion) once the function is genuinely unwanted; the cost of
re-introducing it without noticing is a future audit round.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_d24_diagnostic_in_r3_set_does_not_exist() -> None:
    """``_d24_diagnostic_in_r3_set`` was dead code introduced in
    v0.6.0 and removed in v0.6.1. Re-introducing it would mean
    re-introducing dead code; this test asserts via grep that no
    file under ``src/`` references the name.

    Uses subprocess + grep rather than an import-based check
    because the function lived inside ``runner.py`` at module
    scope; a re-introduction could be at any nested function
    definition or even in a docstring (which we explicitly want
    to flag).
    """
    result = subprocess.run(
        [
            "grep",
            "-rn",
            "_d24_diagnostic_in_r3_set",
            str(REPO_ROOT / "src"),
        ],
        capture_output=True,
        text=True,
    )
    # grep exits 1 when no matches found (the desired state).
    assert result.returncode == 1, (
        "_d24_diagnostic_in_r3_set was re-introduced under src/.\n"
        "It was removed in v0.6.1 (commit b0a4b18) as dead code; D24 "
        "and R3 are non-overlapping in practice (D24 needs >=1 return "
        "present, R3 needs zero), so the suppression branch had no "
        "reachable effect.\n"
        f"Matches found:\n{result.stdout}"
    )
