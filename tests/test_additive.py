"""Tests for the Phase 2 additive-only API checker.

The checker is Python-native and compares two source strings (or two
files) on their public surface. ``__all__`` takes precedence; without
it, the public surface is every top-level name not starting with an
underscore. Removed names fire; added names are silent; unchanged
names produce nothing.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from furqan.errors.marad import Marad

from furqan_lint.additive import check_additive_api

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def additive_dir() -> Path:
    return Path(__file__).parent / "fixtures" / "additive"


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Marad construction and cleanliness
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_additive_clean_no_removals_passes(additive_dir: Path) -> None:
    diags = check_additive_api(
        _read(additive_dir / "v2_api_clean.py"),
        _read(additive_dir / "v1_api.py"),
    )
    assert diags == []


@pytest.mark.unit
def test_additive_removed_name_fires_marad(additive_dir: Path) -> None:
    diags = check_additive_api(
        _read(additive_dir / "v2_api_breaking.py"),
        _read(additive_dir / "v1_api.py"),
    )
    assert len(diags) == 1
    assert isinstance(diags[0], Marad)
    assert "farewell" in diags[0].diagnosis


@pytest.mark.unit
def test_additive_multiple_removals_fire_each() -> None:
    old = "__all__ = ['a', 'b', 'c']\ndef a(): pass\ndef b(): pass\ndef c(): pass\n"
    new = "__all__ = ['a']\ndef a(): pass\n"
    diags = check_additive_api(new, old)
    assert len(diags) == 2
    removed_names = sorted(d.diagnosis.split("'")[1] for d in diags)
    assert removed_names == ["b", "c"]


@pytest.mark.unit
def test_additive_added_name_does_not_fire() -> None:
    old = "__all__ = ['a']\ndef a(): pass\n"
    new = "__all__ = ['a', 'b']\ndef a(): pass\ndef b(): pass\n"
    assert check_additive_api(new, old) == []


# ---------------------------------------------------------------------------
# Public-surface extraction
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_additive_no_all_uses_top_level_names(additive_dir: Path) -> None:
    """No ``__all__`` -> every non-underscore top-level name is public.
    The fixture removes ``Formatter`` but keeps ``VERSION``, so only
    ``Formatter`` should fire."""
    diags = check_additive_api(
        _read(additive_dir / "no_all_v2_breaking.py"),
        _read(additive_dir / "no_all_v1.py"),
    )
    removed = sorted(d.diagnosis.split("'")[1] for d in diags)
    assert removed == ["Formatter"]


@pytest.mark.unit
def test_additive_no_all_private_not_tracked() -> None:
    """Names starting with ``_`` are excluded from the public surface."""
    old = "def public(): pass\ndef _private(): pass\n"
    new = "def public(): pass\n"
    assert check_additive_api(new, old) == []


@pytest.mark.unit
def test_additive_with_all_uses_all_list() -> None:
    """``__all__`` takes precedence: a name not in ``__all__`` is
    private, even if it would be public without the declaration."""
    old = "__all__ = ['exposed']\ndef exposed(): pass\ndef hidden(): pass\n"
    new = "__all__ = ['exposed']\ndef exposed(): pass\n"
    assert check_additive_api(new, old) == []


@pytest.mark.unit
def test_additive_all_as_tuple_works() -> None:
    """``__all__ = (...)`` should parse the same as a list."""
    old = "__all__ = ('a', 'b')\ndef a(): pass\ndef b(): pass\n"
    new = "__all__ = ('a',)\ndef a(): pass\n"
    diags = check_additive_api(new, old)
    assert len(diags) == 1
    assert "'b'" in diags[0].diagnosis


@pytest.mark.unit
def test_additive_empty_old_trivially_passes() -> None:
    """An empty previous version cannot have anything removed."""
    old = ""
    new = "def a(): pass\n"
    assert check_additive_api(new, old) == []


@pytest.mark.unit
def test_additive_class_removal_fires() -> None:
    """Top-level class removal fires the same as function removal."""
    old = "class A: pass\nclass B: pass\n"
    new = "class A: pass\n"
    diags = check_additive_api(new, old)
    assert len(diags) == 1
    assert "'B'" in diags[0].diagnosis


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "furqan_lint.cli", *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


@pytest.mark.integration
def test_cli_diff_command_works(additive_dir: Path) -> None:
    """``furqan-lint diff`` prints a MARAD line and exits 1 on
    breaking changes; exits 0 on clean ones."""
    breaking = _run_cli(
        "diff",
        str(additive_dir / "v1_api.py"),
        str(additive_dir / "v2_api_breaking.py"),
    )
    assert breaking.returncode == 1
    assert "MARAD" in breaking.stdout
    assert "farewell" in breaking.stdout

    clean = _run_cli(
        "diff",
        str(additive_dir / "v1_api.py"),
        str(additive_dir / "v2_api_clean.py"),
    )
    assert clean.returncode == 0
    assert "PASS" in clean.stdout
