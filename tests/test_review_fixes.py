"""Regression tests for the v0.3.0 review fixes.

Each test pins one finding from the three-round review:

* Bug 1 (compound statements) - return-None and missing-path
  detection through ``for``, ``while``, ``with``, ``try``, ``match``.
* Bug 2 (additive surface) - ``AnnAssign`` and tuple-target
  assignments are now visible to the additive checker.
* Bug 3 (dynamic ``__all__``) - refused with a typed exception and
  CLI exit 2 instead of an empty-set false-positive cascade.
* Bug 4 (thread-safety) - concurrent context-manager entry no longer
  leaks the patched predicate.
* Bug 5 (Optional matcher) - ``X.lib.Optional[Y]`` no longer
  misclassified as ``typing.Optional[Y]``.
* Quality - ``int | str`` annotation renders as ``int | str`` in
  diagnostic prose, not as ``Unknown``.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from furqan.checker import status_coverage
from furqan.errors.marad import Marad

from furqan_lint.additive import (
    DynamicAllError,
    check_additive_api,
)
from furqan_lint.adapter import translate_source
from furqan_lint.return_none import check_return_none
from furqan_lint.runner import check_python_module


REPO_ROOT = Path(__file__).resolve().parents[1]


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "furqan_lint.cli", *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


# ---------------------------------------------------------------------------
# Bug 1 - compound statements
# ---------------------------------------------------------------------------

def test_bug1_for_loop_return_none_fires() -> None:
    src = (
        "def f(xs: list) -> str:\n"
        "    for x in xs:\n"
        "        return None\n"
        "    return 'fallback'\n"
    )
    module = translate_source(src, "<t>")
    diags = check_return_none(module)
    assert len(diags) == 1


def test_bug1_while_loop_return_none_fires() -> None:
    src = (
        "def f(xs: list) -> str:\n"
        "    while xs:\n"
        "        return None\n"
        "    return 'x'\n"
    )
    module = translate_source(src, "<t>")
    assert len(check_return_none(module)) == 1


def test_bug1_with_block_return_none_fires() -> None:
    src = (
        "def f() -> str:\n"
        "    with open('x') as g:\n"
        "        return None\n"
    )
    module = translate_source(src, "<t>")
    assert len(check_return_none(module)) == 1


def test_bug1_try_block_return_none_fires() -> None:
    src = (
        "def f() -> str:\n"
        "    try:\n"
        "        return None\n"
        "    except Exception:\n"
        "        return 'x'\n"
    )
    module = translate_source(src, "<t>")
    assert len(check_return_none(module)) == 1


def test_bug1_match_case_return_none_fires() -> None:
    src = (
        "def f(x: int) -> str:\n"
        "    match x:\n"
        "        case 1:\n"
        "            return None\n"
        "        case _:\n"
        "            return 'y'\n"
    )
    module = translate_source(src, "<t>")
    assert len(check_return_none(module)) == 1


def test_bug1_d24_fires_when_only_return_is_inside_for() -> None:
    """A function whose only return is inside a for-loop body is no
    longer silently certified clean: the for-body wraps as
    ``IfStmt(opaque, ..., ())`` so D24 sees a maybe-not-run path."""
    src = (
        "def f(xs: list) -> int:\n"
        "    for x in xs:\n"
        "        if x > 0:\n"
        "            return 1\n"
    )
    module = translate_source(src, "<t>")
    diags = check_python_module(module)
    d24 = [d for n, d in diags if n == "all_paths_return"]
    assert len(d24) == 1


def test_bug1_with_block_body_treated_as_unconditional() -> None:
    """``with`` blocks unconditionally execute their body, so a
    function whose entire body is ``with: return X`` does
    all-paths-return."""
    src = (
        "def f() -> int:\n"
        "    with open('x') as g:\n"
        "        return 1\n"
    )
    module = translate_source(src, "<t>")
    diags = check_python_module(module)
    d24 = [d for n, d in diags if n == "all_paths_return"]
    assert d24 == []


# ---------------------------------------------------------------------------
# Bug 2 - AnnAssign + tuple-target visibility
# ---------------------------------------------------------------------------

def test_bug2_annassign_removal_fires() -> None:
    old = "MAX_RETRIES: int = 5\ndef foo(): pass\n"
    new = "def foo(): pass\n"
    diags = check_additive_api(new, old)
    assert len(diags) == 1
    assert "MAX_RETRIES" in diags[0].diagnosis


def test_bug2_tuple_target_removal_fires() -> None:
    old = "A, B = 1, 2\ndef foo(): pass\n"
    new = "def foo(): pass\n"
    diags = check_additive_api(new, old)
    names = sorted(d.diagnosis.split("'")[1] for d in diags)
    assert names == ["A", "B"]


def test_bug2_annotated_all_still_recognised() -> None:
    """``__all__: list[str] = ['x']`` should be read the same as a
    plain ``__all__`` assignment."""
    old = "__all__: list[str] = ['x', 'y']\ndef x(): pass\ndef y(): pass\n"
    new = "__all__: list[str] = ['x']\ndef x(): pass\n"
    diags = check_additive_api(new, old)
    assert len(diags) == 1
    assert "'y'" in diags[0].diagnosis


def test_bug2_private_annassign_not_tracked() -> None:
    """An ``AnnAssign`` whose name starts with ``_`` is private."""
    old = "_X: int = 1\ndef foo(): pass\n"
    new = "def foo(): pass\n"
    assert check_additive_api(new, old) == []


# ---------------------------------------------------------------------------
# Bug 3 - refuse on dynamic __all__
# ---------------------------------------------------------------------------

def test_bug3_dynamic_all_raises_on_new_side() -> None:
    old = "__all__ = ['foo']\ndef foo(): pass\n"
    new = "_NAMES = ['foo']\n__all__ = list(_NAMES)\ndef foo(): pass\n"
    with pytest.raises(DynamicAllError) as excinfo:
        check_additive_api(new, old)
    assert excinfo.value.where == "new"


def test_bug3_dynamic_all_raises_on_old_side() -> None:
    old = "_NAMES = ['foo']\n__all__ = list(_NAMES)\ndef foo(): pass\n"
    new = "__all__ = ['foo']\ndef foo(): pass\n"
    with pytest.raises(DynamicAllError) as excinfo:
        check_additive_api(new, old)
    assert excinfo.value.where == "old"


def test_bug3_non_string_element_raises() -> None:
    """``__all__ = ['foo', SOME_NAME]`` cannot be statically read."""
    src = "__all__ = ['foo', SOME_NAME]\ndef foo(): pass\n"
    with pytest.raises(DynamicAllError):
        check_additive_api(src, "def foo(): pass\n")


def test_bug3_cli_diff_returns_2_on_dynamic_all(tmp_path: Path) -> None:
    old_path = tmp_path / "old.py"
    new_path = tmp_path / "new.py"
    old_path.write_text("__all__ = ['x']\ndef x(): pass\n")
    new_path.write_text(
        "_N = ['x']\n__all__ = list(_N)\ndef x(): pass\n",
        encoding="utf-8",
    )
    result = _run_cli("diff", str(old_path), str(new_path))
    assert result.returncode == 2
    assert "INDETERMINATE" in result.stdout


# ---------------------------------------------------------------------------
# Bug 4 - thread-safety
# ---------------------------------------------------------------------------

def test_bug4_d11_uses_producer_predicate_kwarg() -> None:
    """v0.4.1 retired the monkey-patch entirely. D11 status-coverage
    now passes the Python-Optional predicate via the upstream
    ``producer_predicate`` keyword (furqan>=0.11.0). The global
    ``status_coverage._is_integrity_incomplete_union`` attribute
    must never be touched at runtime - if any code path mutates it,
    Furqan's own test suite running in the same process would see
    the wrong predicate.

    The original v0.3.0 thread-safety test was a stopgap pinning the
    lock that protected the monkey-patch. With the patch retired,
    the right invariant to pin is "the global is never touched."
    """
    original = status_coverage._is_integrity_incomplete_union
    original_id = id(original)

    src = (
        "from typing import Optional\n"
        "def validate(data: str) -> Optional[dict]:\n"
        "    if not data:\n"
        "        return None\n"
        "    return {'value': data}\n"
        "def run(data: str) -> dict:\n"
        "    return validate(data)\n"
    )
    module = translate_source(src, "<test>")
    diags = check_python_module(module)

    assert id(status_coverage._is_integrity_incomplete_union) == original_id, (
        "Runner mutated status_coverage._is_integrity_incomplete_union; "
        "v0.4.1 must use producer_predicate= kwarg instead of patching."
    )
    # Sanity: the kwarg path still produces the expected D11 diagnostic
    # on this canonical Optional-collapse fixture.
    s_diags = [d for n, d in diags if n == "status_coverage"]
    assert any(getattr(d, "diagnosis", "").find("validate") != -1 for d in s_diags), (
        "Expected a status_coverage diagnostic naming 'validate'"
    )


# ---------------------------------------------------------------------------
# Bug 5 - Optional matcher tightness
# ---------------------------------------------------------------------------

def test_bug5_fake_optional_attribute_no_longer_matched() -> None:
    """An annotation like ``Some.lib.Optional[str]`` should NOT be
    treated as ``typing.Optional[str]``. After v0.3.0, a function
    with such an annotation that returns None fires
    return_none_mismatch.

    v0.3.1 also asserts the diagnostic prose renders the full dotted
    path (``FakeOptional.Optional``) rather than just the leaf attr.
    Without that, the fix suggestion read ``Optional[Optional]``,
    which is incoherent.
    """
    src = (
        "class FakeOptional:\n"
        "    def __class_getitem__(cls, item): return None\n"
        "def f(x: int) -> FakeOptional.Optional[str]:\n"
        "    return None\n"
    )
    module = translate_source(src, "<t>")
    diags = check_return_none(module)
    assert len(diags) == 1
    diagnosis = diags[0].diagnosis
    assert "FakeOptional.Optional" in diagnosis
    fix = diags[0].minimal_fix
    assert "FakeOptional.Optional" in fix
    assert "Optional[Optional]" not in fix


def test_bug5_typing_optional_still_recognised() -> None:
    """Regression: ``typing.Optional[str]`` must remain recognised."""
    src = (
        "import typing\n"
        "def f(x: int) -> typing.Optional[str]:\n"
        "    return None\n"
    )
    module = translate_source(src, "<t>")
    assert check_return_none(module) == []


def test_bug5_t_optional_alias_recognised() -> None:
    """Regression: ``import typing as t`` followed by
    ``t.Optional[str]`` must remain recognised."""
    src = (
        "import typing as t\n"
        "def f(x: int) -> t.Optional[str]:\n"
        "    return None\n"
    )
    module = translate_source(src, "<t>")
    assert check_return_none(module) == []


# ---------------------------------------------------------------------------
# Quality - BinOp annotation rendering
# ---------------------------------------------------------------------------

def test_quality_binop_union_renders_with_pipe() -> None:
    src = (
        "def f(x: str) -> int | str:\n"
        "    if x == '':\n"
        "        return None\n"
        "    return x\n"
    )
    module = translate_source(src, "<t>")
    diags = check_return_none(module)
    assert len(diags) == 1
    diagnosis = diags[0].diagnosis
    assert "int | str" in diagnosis
    assert "Unknown" not in diagnosis


def test_quality_binop_fix_suggestion_is_actionable() -> None:
    src = (
        "def f() -> int | str:\n"
        "    return None\n"
    )
    module = translate_source(src, "<t>")
    diags = check_return_none(module)
    fix = diags[0].minimal_fix
    assert "Optional[int | str]" in fix
