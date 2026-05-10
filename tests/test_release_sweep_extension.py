"""Phase G10.5 (al-Mubin) T04d: pin release_sweep.py extension.

Positive case: current README + SAFETY_INVARIANTS.md present
sweeps clean.

Negative cases: synthetic stale-pin fixtures fire; absent
SAFETY_INVARIANTS.md fires.

v0.11.8 robustness fix: the negative-case tests previously
hardcoded a substitution source of ``v0.11.6``. At v0.11.7
release, the README was bumped to ``v0.11.7`` and the
substitutions silently no-op'd (assertions then failed because
no findings were produced). This pre-existing test brittleness
was exposed at v0.11.8 release. The fix is to read the current
README's pin sites dynamically rather than hardcoding the
expected version. This makes the tests robust against
release-time README bumps so the same drift cannot recur.
"""

from __future__ import annotations

import shutil
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python <3.11 fallback
    import tomli as tomllib  # type: ignore[no-redef]

from scripts.release_sweep import sweep

REPO_ROOT = Path(__file__).parent.parent


def _current_version() -> str:
    """Read the current pyproject.toml version (e.g. ``0.11.8``)."""
    text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    return tomllib.loads(text)["project"]["version"]


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
    assert findings == [], f"current repo expected to sweep clean but got: {findings}"


def test_negative_stale_install_pin_fires(tmp_path: Path) -> None:
    repo = _build_repo_clone(tmp_path)
    readme = repo / "README.md"
    text = readme.read_text(encoding="utf-8")
    current = _current_version()
    n = text.count(
        f'pip install "git+https://github.com/BayyinahEnterprise/' f'furqan-lint.git@v{current}"'
    )
    assert n >= 1, (
        f"expected current README to have at least one install " f"pin at v{current}; got {n}"
    )
    text = text.replace(
        f'pip install "git+https://github.com/BayyinahEnterprise/' f'furqan-lint.git@v{current}"',
        'pip install "git+https://github.com/BayyinahEnterprise/' 'furqan-lint.git@v0.4.0"',
    )
    readme.write_text(text, encoding="utf-8")
    findings = sweep(repo)
    assert any("stale pin v0.4.0" in f for f in findings), findings


def test_negative_stale_github_action_fires(tmp_path: Path) -> None:
    repo = _build_repo_clone(tmp_path)
    readme = repo / "README.md"
    text = readme.read_text(encoding="utf-8")
    current = _current_version()
    n = text.count(f"uses: BayyinahEnterprise/furqan-lint@v{current}")
    assert n >= 1, (
        f"expected current README to have at least one GitHub "
        f"Action use pin at v{current}; got {n}"
    )
    text = text.replace(
        f"uses: BayyinahEnterprise/furqan-lint@v{current}",
        "uses: BayyinahEnterprise/furqan-lint@v0.4.0",
    )
    readme.write_text(text, encoding="utf-8")
    findings = sweep(repo)
    assert any("GitHub Action" in f and "v0.4.0" in f for f in findings), findings


def test_negative_stale_precommit_rev_fires(tmp_path: Path) -> None:
    repo = _build_repo_clone(tmp_path)
    readme = repo / "README.md"
    text = readme.read_text(encoding="utf-8")
    current = _current_version()
    pre_commit_pattern = f"    rev: v{current}\n    hooks:\n      - id: furqan-lint"
    n = text.count(pre_commit_pattern)
    assert n >= 1, (
        f"expected current README to have at least one pre-commit "
        f"rev pin at v{current}; got {n}"
    )
    text = text.replace(
        pre_commit_pattern,
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
