"""Regression tests for the v0.3.4 round-7 review fixes.

Three quality-tier observations from Fraz's round-7 review of
v0.3.3, none blocking, all asymmetries between code paths that
currently produce correct answers but for incidental reasons:

* Observation 1 (Optional[None] symmetry): the Optional path
  produced ``UnionType(left=TypePath("None"), right=TypePath("None"))``
  on ``Optional[None]``, while the v0.3.3 Union path produced a
  bare ``TypePath(base="None")`` on ``Union[None]``. Both arrived
  at correct answers; only the Union path was structurally
  defended. v0.3.4 mirrors the discipline.

* Observation 3 (bare Optional/Union diagnostic): a function
  declaring ``-> Optional`` (no subscript) returning ``None``
  produced a ``return_none_mismatch`` whose ``minimal_fix``
  suggested ``Optional[Optional]``, which is invalid typing
  syntax. v0.3.4 detects the bare-name case and suggests the
  real fix (add a type argument).

* Observation 2 (PEP 604 redundant None) is documented as a
  limitation in ``tests/fixtures/documented_limits/`` and pinned
  by tests in ``test_documented_limits.py``; the round-7 file
  here is for the two structural fixes only.
"""

from __future__ import annotations

import pytest
from furqan.parser.ast_nodes import TypePath, UnionType

from furqan_lint.adapter import translate_source
from furqan_lint.return_none import _suggested_fix, check_return_none

pytestmark = pytest.mark.unit
# ---------------------------------------------------------------------------
# Observation 1: Optional[None] symmetry with v0.3.3 Union[None]
# ---------------------------------------------------------------------------


def test_round7_optional_none_translates_to_bare_none_typepath() -> None:
    """``Optional[None]`` must translate to a bare
    ``TypePath(base="None")``, mirroring the v0.3.3 Union[None]
    discipline. Failure shape this catches: a regression that
    re-introduces the binary ``UnionType(None, None)`` shape that
    the pre-v0.3.4 Optional path produced. Such a shape is not
    semantically meaningful (a binary union of identical types is
    not a union) and would break any future refactor that requires
    distinct arms.
    """
    src = "from typing import Optional\ndef f() -> Optional[None]:\n    return None\n"
    module = translate_source(src, "<test>")
    fn = next(f for f in module.functions if f.name == "f")
    assert isinstance(fn.return_type, TypePath), (
        f"Optional[None] translated to {type(fn.return_type).__name__}; "
        f"v0.3.4 requires bare TypePath('None') to mirror "
        f"v0.3.3 Union[None] discipline."
    )
    assert fn.return_type.base == "None"


def test_round7_optional_none_does_not_produce_binary_union() -> None:
    """Negative-test the v0.3.4 fix: the pre-v0.3.4 binary
    ``UnionType(None, None)`` shape must not return through any
    refactor. Pin the absence so a future change has a
    self-explaining failure.
    """
    src = "from typing import Optional\ndef f() -> Optional[None]:\n    return None\n"
    module = translate_source(src, "<test>")
    fn = next(f for f in module.functions if f.name == "f")
    assert not isinstance(fn.return_type, UnionType), (
        "Optional[None] translated to a binary UnionType; v0.3.4 "
        "requires the short-circuit to bare TypePath('None') so "
        "the intermediate AST shape matches the runtime semantics "
        "(typing.Optional[None] == type(None))."
    )


def test_round7_optional_none_return_none_passes() -> None:
    """End-to-end: a function annotated ``-> Optional[None]`` with
    a ``return None`` body must produce zero diagnostics. The
    annotation declares NoneType; the body returns None; they
    agree.
    """
    src = "from typing import Optional\ndef f() -> Optional[None]:\n    return None\n"
    module = translate_source(src, "<test>")
    diagnostics = check_return_none(module)
    assert diagnostics == [], (
        f"Optional[None] with return None unexpectedly produced "
        f"diagnostics: {diagnostics}. The annotation and body "
        f"agree (both NoneType); a clean PASS is required."
    )


def test_round7_optional_str_still_translates_to_union_type() -> None:
    """Negative test against an over-correction: the v0.3.4 fix
    only short-circuits ``Optional[None]``; ``Optional[str]`` and
    every other ``Optional[X]`` shape must continue to translate to
    the binary ``UnionType(X, None)`` shape that v0.3.0 introduced
    and the v0.3.x line depends on.
    """
    src = "from typing import Optional\ndef f() -> Optional[str]:\n    return None\n"
    module = translate_source(src, "<test>")
    fn = next(f for f in module.functions if f.name == "f")
    assert isinstance(fn.return_type, UnionType), (
        f"Optional[str] translated to {type(fn.return_type).__name__}; "
        f"the v0.3.4 short-circuit must apply only to Optional[None] "
        f"(where inner is the None literal), not to general Optional[X]."
    )
    assert fn.return_type.left.base == "str"
    assert fn.return_type.right.base == "None"


# ---------------------------------------------------------------------------
# Observation 3: bare Optional/Union diagnostic prose
# ---------------------------------------------------------------------------


def _make_type_path(base: str) -> TypePath:
    """Build a minimal TypePath for unit-testing _suggested_fix.

    The diagnostic helper only reads the ``base`` attribute, so a
    fresh TypePath constructed inline is sufficient. Layer fields
    are left None; span is left None (the helper does not consult
    spans).
    """
    return TypePath(base=base, layer=None, span=None, layer_alias_used=None)


def test_round7_bare_optional_produces_helpful_fix_suggestion() -> None:
    """A function declared ``-> Optional`` (no subscript) is a
    syntax error mypy rejects with 'Bare Optional is not allowed.'
    furqan-lint translates the bare name as
    ``TypePath(base='Optional')``; the pre-v0.3.4 ``minimal_fix``
    was an inline f-string that suggested ``Optional[Optional]``,
    which is incoherent. The v0.3.4 ``_suggested_fix`` helper
    detects the bare-name case and suggests adding a type
    argument.
    """
    fix = _suggested_fix(_make_type_path("Optional"))
    assert "Optional[Optional]" not in fix, (
        f"_suggested_fix returned {fix!r}, which contains the "
        f"incoherent Optional[Optional] suggestion. v0.3.4 must "
        f"detect the bare-name case and suggest adding a type "
        f"argument instead."
    )
    assert "not valid typing syntax" in fix or "Optional[X]" in fix, (
        f"_suggested_fix returned {fix!r} but does not name the "
        f"real bug (bare Optional is a missing type argument). "
        f"Helpful prose should point the user at Optional[X] or "
        f"X | None."
    )


def test_round7_bare_union_produces_helpful_fix_suggestion() -> None:
    """Symmetric form for ``Union``. mypy rejects bare ``Union``
    too. The v0.3.4 helper handles both names.
    """
    fix = _suggested_fix(_make_type_path("Union"))
    assert "Optional[Union]" not in fix, (
        f"_suggested_fix returned {fix!r}, which contains the "
        f"incoherent Optional[Union] suggestion. v0.3.4 must "
        f"detect the bare-name case for Union as well."
    )
    assert "not valid typing syntax" in fix or "Union[X]" in fix, (
        f"_suggested_fix returned {fix!r} but does not name the real bug for bare Union."
    )


def test_round7_normal_type_path_still_uses_optional_suggestion() -> None:
    """Negative test against an over-correction: the v0.3.4 helper
    only special-cases the literal names ``Optional`` and ``Union``;
    every other ``TypePath`` (``str``, ``int``, ``MyClass``, etc.)
    must continue to suggest ``Optional[<name>]`` as the minimal
    fix.
    """
    fix = _suggested_fix(_make_type_path("str"))
    assert "Optional[str]" in fix, (
        f"_suggested_fix on TypePath('str') returned {fix!r}, "
        f"which does not include the canonical Optional[str] fix "
        f"suggestion. The v0.3.4 special-case must not regress on "
        f"the canonical happy path."
    )


def test_bare_union_suggests_union_x_none_not_union_x() -> None:
    """v0.4.1 refinement of the bare-Union prose. The v0.3.4
    helper merged Optional and Union into one branch and could
    end up recommending ``Union[X]`` (well-formed but degenerate -
    typing folds it to ``X``). The user is returning ``None``,
    so the actionable suggestion is a Union that includes None:
    ``Union[X, None]``, or equivalently ``Optional[X]`` or
    ``X | None``.
    """
    from furqan.parser.ast_nodes import SourceSpan, TypePath

    from furqan_lint.return_none import _suggested_fix

    rt = TypePath(
        base="Union",
        layer=None,
        span=SourceSpan(file="<t>", line=1, column=0),
        layer_alias_used=None,
    )
    fix = _suggested_fix(rt)
    assert "Union[X, None]" in fix, (
        f"v0.4.1: bare-Union fix must include 'Union[X, None]', got {fix!r}"
    )
    # Must NOT recommend the degenerate one-arm Union[X] form
    # standalone. We allow the substring 'Union[X' as part of
    # 'Union[X, None]' but disallow the closed form 'Union[X]'.
    assert "Union[X]" not in fix, (
        f"v0.4.1: bare-Union fix should NOT suggest the degenerate Union[X] form, got {fix!r}"
    )
