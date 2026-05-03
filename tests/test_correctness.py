"""Tests for the Phase 2 ``_extract_calls`` scoping fix.

Phase 1 used ``ast.walk`` which descended into nested function
definitions and decorator lists. Phase 2 walks only the function's
direct body via ``ast.iter_child_nodes`` with a depth guard.

Lambdas and comprehensions are deliberately NOT excluded: their
calls execute when the enclosing function runs and so are correctly
attributed to it.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from furqan_lint.adapter import translate_file, translate_source
from furqan_lint.runner import check_python_module

pytestmark = pytest.mark.unit


def _calls_of(module, name: str) -> tuple:
    fn = next(f for f in module.functions if f.name == name)
    return tuple(c.path[0] for c in fn.calls)


# ---------------------------------------------------------------------------
# Nested-definition scoping
# ---------------------------------------------------------------------------


def test_closure_call_not_attributed_to_outer(clean_dir: Path) -> None:
    """The fixture ``closure_no_false_positive.py`` has ``find_item``
    called inside a closure inside ``outer``. The Phase 2 fix must
    not attribute that call to ``outer``."""
    module = translate_file(clean_dir / "closure_no_false_positive.py")
    assert "find_item" not in _calls_of(module, "outer")
    # And the whole-module check should be clean.
    diags = check_python_module(module)
    assert diags == []


def test_inner_function_call_not_attributed() -> None:
    src = (
        "def outer() -> int:\n"
        "    def inner():\n"
        "        helper()\n"
        "    return 1\n"
        "def helper() -> int:\n"
        "    return 1\n"
    )
    module = translate_source(src, "<test>")
    assert "helper" not in _calls_of(module, "outer")


def test_direct_call_still_extracted() -> None:
    """The scoping fix must not regress the basic case: a call in the
    function's direct body is still collected."""
    src = "def f() -> int:\n    return helper()\ndef helper() -> int:\n    return 1\n"
    module = translate_source(src, "<test>")
    assert "helper" in _calls_of(module, "f")


def test_nested_class_method_not_attributed() -> None:
    """A method on a class defined inside a function should not have
    its calls attributed to the enclosing function."""
    src = (
        "def outer() -> int:\n"
        "    class C:\n"
        "        def method(self):\n"
        "            helper()\n"
        "    return 1\n"
        "def helper() -> int:\n"
        "    return 1\n"
    )
    module = translate_source(src, "<test>")
    assert "helper" not in _calls_of(module, "outer")


# ---------------------------------------------------------------------------
# Decorator scoping
# ---------------------------------------------------------------------------


def test_decorator_call_not_attributed_to_function(clean_dir: Path) -> None:
    """The decorator ``@retry`` on ``outer`` should not register as a
    call inside ``outer``'s body."""
    module = translate_file(clean_dir / "decorator_no_false_positive.py")
    assert "retry" not in _calls_of(module, "outer")


def test_multiple_decorators_not_attributed() -> None:
    """A function carrying multiple decorators should have none of
    them appear in its call list."""
    src = (
        "def deco_a(f): return f\n"
        "def deco_b(f): return f\n"
        "def deco_c(f): return f\n"
        "@deco_a\n"
        "@deco_b\n"
        "@deco_c\n"
        "def target() -> int:\n"
        "    return 1\n"
    )
    module = translate_source(src, "<test>")
    calls = _calls_of(module, "target")
    assert "deco_a" not in calls
    assert "deco_b" not in calls
    assert "deco_c" not in calls


# ---------------------------------------------------------------------------
# Lambdas and comprehensions are inline expressions: still count
# ---------------------------------------------------------------------------


def test_lambda_call_still_extracted() -> None:
    """A lambda is an inline expression, not a separate scope the
    user reasons about. Calls inside it count for the enclosing
    function."""
    src = (
        "def f() -> int:\n"
        "    g = lambda: helper()\n"
        "    return g()\n"
        "def helper() -> int:\n"
        "    return 1\n"
    )
    module = translate_source(src, "<test>")
    assert "helper" in _calls_of(module, "f")


def test_comprehension_call_still_extracted() -> None:
    """List/dict comprehensions execute in the enclosing function;
    calls inside the comprehension count for the outer function."""
    src = (
        "def f() -> list:\n"
        "    return [helper(x) for x in range(3)]\n"
        "def helper(x) -> int:\n"
        "    return x\n"
    )
    module = translate_source(src, "<test>")
    assert "helper" in _calls_of(module, "f")
