"""Tests for the Phase 2 ``return_none_mismatch`` checker.

Closes Phase 1 Gap 1: a function declaring a non-Optional return type
that returns ``None`` on some path is a type mismatch. D24 still
treats the bare ``return None`` as a satisfied path; this checker
fires alongside.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from furqan.errors.marad import Marad

from furqan_lint.adapter import translate_file, translate_source
from furqan_lint.return_none import check_return_none

pytestmark = pytest.mark.unit
# ---------------------------------------------------------------------------
# Mismatch cases (should fire)
# ---------------------------------------------------------------------------


def test_return_none_in_non_optional_fires(failing_dir: Path) -> None:
    module = translate_file(failing_dir / "return_none_mismatch.py")
    diags = check_return_none(module)
    assert len(diags) == 1
    assert isinstance(diags[0], Marad)
    assert "get_name" in diags[0].diagnosis


def test_bare_return_in_non_optional_fires(failing_dir: Path) -> None:
    """Bare ``return`` (no value) is equivalent to ``return None``."""
    module = translate_file(failing_dir / "bare_return_mismatch.py")
    diags = check_return_none(module)
    assert len(diags) == 1
    assert "fetch" in diags[0].diagnosis


def test_nested_none_return_in_if_fires() -> None:
    """``return None`` inside a nested ``if`` body is found by the
    recursive walker."""
    src = (
        "def f(x: int) -> int:\n"
        "    if x:\n"
        "        if x > 1:\n"
        "            return None\n"
        "        return 0\n"
        "    return 1\n"
    )
    module = translate_source(src, "<test>")
    diags = check_return_none(module)
    assert len(diags) == 1


def test_multiple_functions_independent() -> None:
    """Two mismatches in the same module produce two diagnostics."""
    src = "def a() -> int:\n    return None\ndef b() -> str:\n    return None\n"
    module = translate_source(src, "<test>")
    diags = check_return_none(module)
    assert len(diags) == 2
    names = sorted(d.diagnosis.split("'")[1] for d in diags)
    assert names == ["a", "b"]


# ---------------------------------------------------------------------------
# Clean cases (should not fire)
# ---------------------------------------------------------------------------


def test_return_none_in_optional_passes(clean_dir: Path) -> None:
    module = translate_file(clean_dir / "optional_return_none.py")
    assert check_return_none(module) == []


def test_return_none_in_none_type_passes(clean_dir: Path) -> None:
    module = translate_file(clean_dir / "none_return_type.py")
    assert check_return_none(module) == []


def test_no_return_annotation_skipped() -> None:
    """A function without a return annotation is not subject to the
    check (the user has not promised any specific type)."""
    src = "def f(x):\n    if x:\n        return None\n    return 1\n"
    module = translate_source(src, "<test>")
    assert check_return_none(module) == []


def test_pipe_union_with_none_passes() -> None:
    """``X | None`` is equivalent to ``Optional[X]`` and permits
    ``return None``."""
    src = "def f(x: int) -> str | None:\n    if x:\n        return 'yes'\n    return None\n"
    module = translate_source(src, "<test>")
    assert check_return_none(module) == []


def test_return_value_not_none_passes() -> None:
    """A function whose returns never produce ``None`` does not fire."""
    src = "def f(x: int) -> int:\n    if x:\n        return 1\n    return 2\n"
    module = translate_source(src, "<test>")
    assert check_return_none(module) == []
