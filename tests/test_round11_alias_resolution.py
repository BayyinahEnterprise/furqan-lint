"""Round-11 alias-resolution tests (v0.6.1).

Pin the symbol-table-backed decorator skip-list. Covers all four
import shapes:

  - ``from X import Y as Z``         -> aliased bare
  - ``from X import Y``              -> direct bare (regression check)
  - ``import X as Y``                -> aliased dotted prefix
  - ``import X``                     -> direct dotted prefix (regression check)

Plus a negative case asserting that a bare-name import from an
unrelated module that happens to collide with a skip-list name
(``from somemodule import abstractmethod``) is still treated as a
match. That false positive predates v0.6.1 and is documented as a
known imprecision; closing it would need full symbol-resolution
across the import graph.
"""

from __future__ import annotations

import ast

import pytest

from furqan_lint.zero_return import (
    _build_decorator_alias_map,
    check_zero_return,
)

pytestmark = pytest.mark.unit


def _diags_for(source: str) -> list[str]:
    """Return the function names R3 fired on for ``source``."""
    tree = ast.parse(source)
    return [d.function_name for d in check_zero_return(tree)]


# ---------------------------------------------------------------------------
# Alias map construction
# ---------------------------------------------------------------------------


def test_alias_map_records_from_import_with_asname() -> None:
    """``from abc import abstractmethod as abstract`` records the
    local name ``abstract`` mapped to the qualified ``abc.abstractmethod``.
    """
    tree = ast.parse("from abc import abstractmethod as abstract\n")
    aliases = _build_decorator_alias_map(tree)
    assert aliases["abstract"] == "abc.abstractmethod"


def test_alias_map_records_from_import_without_asname() -> None:
    """``from abc import abstractmethod`` records ``abstractmethod``
    mapped to the qualified ``abc.abstractmethod``."""
    tree = ast.parse("from abc import abstractmethod\n")
    aliases = _build_decorator_alias_map(tree)
    assert aliases["abstractmethod"] == "abc.abstractmethod"


def test_alias_map_records_module_alias() -> None:
    """``import abc as a`` records ``a -> abc`` so that
    ``@a.abstractmethod`` resolves correctly."""
    tree = ast.parse("import abc as a\n")
    aliases = _build_decorator_alias_map(tree)
    assert aliases["a"] == "abc"


def test_alias_map_records_bare_module_import() -> None:
    """``import abc`` records ``abc -> abc`` (no-op but kept for
    consistency with the dotted-resolution path)."""
    tree = ast.parse("import abc\n")
    aliases = _build_decorator_alias_map(tree)
    assert aliases["abc"] == "abc"


# ---------------------------------------------------------------------------
# Skip-list resolution through the alias map
# ---------------------------------------------------------------------------


def test_aliased_bare_abstractmethod_skipped() -> None:
    """``from abc import abstractmethod as abstract; @abstract`` is
    correctly recognized as ``abc.abstractmethod`` and skipped."""
    src = (
        "from abc import abstractmethod as abstract\n"
        "class C:\n"
        "    @abstract\n"
        "    def required(self) -> int: ...\n"
    )
    assert _diags_for(src) == []


def test_aliased_dotted_abstractmethod_skipped() -> None:
    """``import abc as a; @a.abstractmethod`` resolves the prefix
    ``a`` to ``abc`` and matches ``abc.abstractmethod``."""
    src = (
        "import abc as a\n"
        "class C:\n"
        "    @a.abstractmethod\n"
        "    def required(self) -> int: ...\n"
    )
    assert _diags_for(src) == []


def test_aliased_overload_skipped() -> None:
    """``from typing import overload as ov; @ov`` resolves
    ``ov -> typing.overload`` and is skipped."""
    src = (
        "from typing import overload as ov\n"
        "@ov\n"
        "def parse(x: int) -> int: ...\n"
        "@ov\n"
        "def parse(x: str) -> str: ...\n"
        "def parse(x):\n"
        "    return x\n"
    )
    assert _diags_for(src) == []


def test_dotted_typing_overload_via_alias_skipped() -> None:
    """``import typing as t; @t.overload`` resolves the prefix
    ``t -> typing`` and matches ``typing.overload``."""
    src = (
        "import typing as t\n"
        "@t.overload\n"
        "def parse(x: int) -> int: ...\n"
        "@t.overload\n"
        "def parse(x: str) -> str: ...\n"
        "def parse(x):\n"
        "    return x\n"
    )
    assert _diags_for(src) == []


# ---------------------------------------------------------------------------
# Direct (non-aliased) cases still work after the refactor
# ---------------------------------------------------------------------------


def test_direct_abstractmethod_still_skipped() -> None:
    """Regression check: the existing direct-form recognition was
    not broken by the alias-resolution refactor."""
    src = (
        "from abc import abstractmethod\n"
        "class C:\n"
        "    @abstractmethod\n"
        "    def required(self) -> int: ...\n"
    )
    assert _diags_for(src) == []


def test_direct_dotted_abstractmethod_still_skipped() -> None:
    """Regression check: ``@abc.abstractmethod`` direct form."""
    src = (
        "import abc\n"
        "class C:\n"
        "    @abc.abstractmethod\n"
        "    def required(self) -> int: ...\n"
    )
    assert _diags_for(src) == []


# ---------------------------------------------------------------------------
# Negative cases (R3 still fires)
# ---------------------------------------------------------------------------


def test_unrelated_decorator_still_fires() -> None:
    """An unrelated decorator without alias resolution to anything
    on the skip-list does NOT skip R3."""
    src = (
        "def somedec(f):\n"
        "    return f\n"
        "@somedec\n"
        "def offender(x: int) -> int:\n"
        "    pass\n"
    )
    assert _diags_for(src) == ["offender"]


def test_no_imports_no_match() -> None:
    """Without any imports, a bare ``@abstract`` decorator does NOT
    resolve to ``abc.abstractmethod``."""
    src = "@abstract\n" "def offender(x: int) -> int:\n" "    pass\n"
    # Note: 'abstract' is undefined at runtime but R3 doesn't care;
    # it only checks structural match against the skip-list.
    assert _diags_for(src) == ["offender"]
