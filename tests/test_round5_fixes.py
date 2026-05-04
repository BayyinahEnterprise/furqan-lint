"""Regression tests for the v0.3.2 round-5 review fixes.

Three findings from the round-5 review of v0.3.1, all empirically
reproduced before fixing:

* Finding 1 (Union[X, None]) - the matcher now recognises
  ``Union[X, None]``, ``Union[None, X]``, ``Union[X, Y, None]``,
  and the ``typing.Union`` / ``t.Union`` aliased forms as Optional.
* Finding 2 (string forward refs) - PEP 484 string annotations like
  ``-> "Optional[User]"`` are parsed and recursed into so the
  matcher sees the real shape.
* Finding 3 (nested class methods) - methods of inner classes
  (``Outer.Inner.method``, etc.) are now collected via recursive
  descent through nested ``ClassDef`` bodies.
"""

from __future__ import annotations

import pytest

from furqan_lint.adapter import translate_source
from furqan_lint.return_none import check_return_none
from furqan_lint.runner import check_python_module

pytestmark = pytest.mark.unit
# ---------------------------------------------------------------------------
# Finding 1 - Union[X, None]
# ---------------------------------------------------------------------------


def test_finding1_union_x_none_no_false_positive() -> None:
    """``Union[int, None]`` with ``return None`` is correct typing
    and must NOT fire return_none_mismatch."""
    src = (
        "from typing import Union\n"
        "def f(x: int) -> Union[int, None]:\n"
        "    if x > 0:\n"
        "        return x\n"
        "    return None\n"
    )
    module = translate_source(src, "<t>")
    assert check_return_none(module) == []


def test_finding1_typing_union_qualified_no_false_positive() -> None:
    src = "import typing\ndef g() -> typing.Union[int, None]:\n    return None\n"
    module = translate_source(src, "<t>")
    assert check_return_none(module) == []


def test_finding1_t_union_alias_no_false_positive() -> None:
    src = "import typing as t\ndef g() -> t.Union[int, None]:\n    return None\n"
    module = translate_source(src, "<t>")
    assert check_return_none(module) == []


def test_finding1_none_first_arm_recognised() -> None:
    """``Union[None, X]`` (None as first arm) must be recognised
    just like ``Union[X, None]``."""
    src = "from typing import Union\ndef g() -> Union[None, str]:\n    return None\n"
    module = translate_source(src, "<t>")
    assert check_return_none(module) == []


def test_finding1_three_arm_union_with_none_recognised() -> None:
    """``Union[X, Y, None]`` is semantically Optional[X | Y]."""
    src = "from typing import Union\ndef g() -> Union[int, str, None]:\n    return None\n"
    module = translate_source(src, "<t>")
    assert check_return_none(module) == []


def test_finding1_union_without_none_still_fires() -> None:
    """``Union[int, str]`` (no None arm) returning None is still a
    real mismatch and must fire."""
    src = "from typing import Union\ndef g() -> Union[int, str]:\n    return None\n"
    module = translate_source(src, "<t>")
    diags = check_return_none(module)
    assert len(diags) == 1


# ---------------------------------------------------------------------------
# Finding 2 - string forward references
# ---------------------------------------------------------------------------


def test_finding2_string_optional_forward_ref_recognised() -> None:
    """The TYPE_CHECKING forward-reference idiom must not produce
    false positives."""
    src = 'def find_user(id: int) -> "Optional[User]":\n    return None\n'
    module = translate_source(src, "<t>")
    assert check_return_none(module) == []


def test_finding2_string_pipe_union_forward_ref_recognised() -> None:
    src = 'def f() -> "User | None":\n    return None\n'
    module = translate_source(src, "<t>")
    assert check_return_none(module) == []


def test_finding2_string_bare_type_still_fires_on_none() -> None:
    """A string forward ref to a non-Optional type returning None
    is still a real mismatch."""
    src = 'def f() -> "User":\n    return None\n'
    module = translate_source(src, "<t>")
    assert len(check_return_none(module)) == 1


def test_finding2_unparseable_string_does_not_crash() -> None:
    """A malformed string annotation (not valid Python expression)
    must fall through gracefully, not raise."""
    src = 'def f() -> "not :: valid":\n    return None\n'
    # The translation must complete without raising.
    module = translate_source(src, "<t>")
    # And the check must not crash either.
    diags = check_python_module(module)
    # Best-effort: bare TypePath, fires return_none_mismatch.
    assert any(n == "return_none_mismatch" for n, _ in diags)


# ---------------------------------------------------------------------------
# Finding 3 - nested class methods
# ---------------------------------------------------------------------------


def test_finding3_nested_class_method_d24_fires() -> None:
    """A method on ``Outer.Inner`` with a missing return path must
    now be visible to D24."""
    src = (
        "class Outer:\n"
        "    class Inner:\n"
        "        def method(self) -> int:\n"
        "            if True:\n"
        "                return 1\n"
    )
    module = translate_source(src, "<t>")
    diags = check_python_module(module)
    d24 = [d for n, d in diags if n == "all_paths_return"]
    assert len(d24) == 1


def test_finding3_doubly_nested_class_method_collected() -> None:
    """Methods of ``Outer.Mid.Inner`` are also collected."""
    src = (
        "class Outer:\n"
        "    class Mid:\n"
        "        class Inner:\n"
        "            def m(self) -> int:\n"
        "                return None\n"
    )
    module = translate_source(src, "<t>")
    method_names = [fn.name for fn in module.functions]
    assert "m" in method_names


def test_finding3_nested_class_method_return_none_fires() -> None:
    """``return_none_mismatch`` runs on nested-class methods just
    like any other function."""
    src = "class Outer:\n    class Inner:\n        def get(self) -> str:\n            return None\n"
    module = translate_source(src, "<t>")
    diags = check_return_none(module)
    assert len(diags) == 1


def test_finding3_clean_nested_class_passes() -> None:
    """Negative case: a clean nested class produces no diagnostics."""
    src = "class Outer:\n    class Inner:\n        def good(self) -> int:\n            return 1\n"
    module = translate_source(src, "<t>")
    assert check_python_module(module) == []
