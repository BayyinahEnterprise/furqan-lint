"""Tests for Phase G11.0 T12: F1 closure regenerator.

Pin:

* Generator output matches the README (no drift).
* Editing the README inside the auto block fires the check.
* The prose count line is derived from the table length.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "regenerate_check_table.py"


def _import_script():
    spec = importlib.util.spec_from_file_location("_regenerate_check_table_test", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_generator_no_drift_against_committed_readme() -> None:
    """`scripts/regenerate_check_table.py --check` must exit 0
    against the in-repo README. If it does not, run the
    generator without --check to update the README, then commit
    the result."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        check=False,
    )
    assert result.returncode == 0, (
        f"README check table is out of date with the generator. "
        f"Run 'python scripts/regenerate_check_table.py' and commit "
        f"the result.\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_count_prose_derived_from_table_length() -> None:
    """The generator's count prose ('Four core Python checks ship
    today') is derived from len(PYTHON_CHECKS), not hardcoded."""
    mod = _import_script()
    block = mod.render_block()
    assert f"{mod._number_word(len(mod.PYTHON_CHECKS))} core" in block


def test_handwritten_drift_fires_check(tmp_path: Path) -> None:
    """Edit the README inside the auto block; verify the check
    fires. Use a tmp copy so we do not mutate the in-repo file."""
    mod = _import_script()
    original_readme_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    # Simulate hand-editing inside the auto block.
    drifted = original_readme_text.replace(
        "Four core Python checks ship today",
        "Five core Python checks ship today",
        1,
    )
    target = tmp_path / "README.md"
    target.write_text(drifted, encoding="utf-8")
    # Run the generator's check_no_drift against this synthetic
    # README via monkeypatching the module's REPO_ROOT/README.
    mod.README = target
    rc = mod.check_no_drift()
    assert rc == 1, "expected drift detection"
