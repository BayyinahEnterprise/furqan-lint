"""Phase G10.5 (al-Mubin) T04d: pin release_sweep.py extension.

Positive case: current README + SAFETY_INVARIANTS.md present
sweeps clean.

Negative cases: synthetic stale-pin fixtures fire; absent
SAFETY_INVARIANTS.md fires.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from scripts.release_sweep import sweep

REPO_ROOT = Path(__file__).parent.parent


def _build_repo_clone(tmp_path: Path) -> Path:
    """Copy the minimal subset of repo files needed for the
    sweep into a tmp path so the test can mutate them.
    """
    target = tmp_path / "repo"
    target.mkdir()
    for fname in ("README.md", "SAFETY_INVARIANTS.md", "pyproject.toml"):
        src = REPO_ROOT / fname
        if src.is_file():
            shutil.copy(src, target / fname)
    return target


def test_positive_current_repo_sweeps_clean(tmp_path: Path) -> None:
    """The repo at v0.11.x with SAFETY_INVARIANTS.md present
    and all README pins refreshed must sweep clean.
    """
    findings = sweep(REPO_ROOT)
    # The repo is at v0.11.0 with the T04a sweep applied; no
    # stale pins should remain.
    assert findings == [], f"current repo expected to sweep clean but got: {findings}"


def test_negative_stale_install_pin_fires(tmp_path: Path) -> None:
    repo = _build_repo_clone(tmp_path)
    readme = repo / "README.md"
    text = readme.read_text(encoding="utf-8")
    text = text.replace(
        'pip install "git+https://github.com/BayyinahEnterprise/' 'furqan-lint.git@v0.11.0"',
        'pip install "git+https://github.com/BayyinahEnterprise/' 'furqan-lint.git@v0.4.0"',
    )
    readme.write_text(text, encoding="utf-8")
    findings = sweep(repo)
    assert any("stale pin v0.4.0" in f for f in findings), findings


def test_negative_stale_github_action_fires(tmp_path: Path) -> None:
    repo = _build_repo_clone(tmp_path)
    readme = repo / "README.md"
    text = readme.read_text(encoding="utf-8")
    text = text.replace(
        "uses: BayyinahEnterprise/furqan-lint@v0.11.0",
        "uses: BayyinahEnterprise/furqan-lint@v0.4.0",
    )
    readme.write_text(text, encoding="utf-8")
    findings = sweep(repo)
    assert any("GitHub Action" in f and "v0.4.0" in f for f in findings), findings


def test_negative_stale_precommit_rev_fires(tmp_path: Path) -> None:
    repo = _build_repo_clone(tmp_path)
    readme = repo / "README.md"
    text = readme.read_text(encoding="utf-8")
    # First refresh case: substitute one of the v0.11.0 rev examples
    # back to a stale v0.5.0 to exercise the regex.
    text = text.replace(
        "    rev: v0.11.0\n    hooks:\n      - id: furqan-lint",
        "    rev: v0.5.0\n    hooks:\n      - id: furqan-lint",
        1,
    )
    readme.write_text(text, encoding="utf-8")
    findings = sweep(repo)
    assert any("pre-commit rev" in f and "v0.5.0" in f for f in findings), findings


def test_negative_safety_invariants_absent_fires(tmp_path: Path) -> None:
    """If SAFETY_INVARIANTS.md is absent at root, sweep fires
    the al-Fatiha presence check.
    """
    repo = _build_repo_clone(tmp_path)
    (repo / "SAFETY_INVARIANTS.md").unlink()
    findings = sweep(repo)
    assert any("SAFETY_INVARIANTS.md absent" in f for f in findings), findings
