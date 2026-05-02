"""Regression tests for the v0.3.3 round-6 review fixes.

One blocking finding from Fraz's round-6 review of v0.3.2,
empirically reproduced before fixing:

* Boundary crash on degenerate ``Union[None, ...]`` shapes.
  ``Union[None]``, ``Union[None, None]``, and
  ``Union[None, None, None]`` all sent v0.3.2's
  ``_extract_union_with_none_inner`` into ``IndexError: list index
  out of range`` on the line that picks ``non_none[0]``. The function
  handled ``len(non_none) == 1`` explicitly and assumed
  ``len(non_none) >= 2`` for the fall-through; the
  ``len(non_none) == 0`` case was never considered. All three input
  shapes are legal Python that mypy accepts (``Union[None]``
  evaluates to ``type(None)`` at runtime).

The fix is structural: ``_is_union_with_none`` is the truthful
predicate of what ``_extract_union_with_none_inner`` can satisfy.
v0.3.3 tightens ``_is_union_with_none`` to require *both* a None
arm AND a non-None arm, so degenerate ``Union[None, ...]`` shapes
fall through to the ordinary type-translation path instead of
through a specialised helper that cannot represent them.

Same shape of failure as the original Furqan parser RecursionError
bug (round-3, May 2026): an unstructured Python exception on a
shape of legal input the matcher did not anticipate. Per
``errors/marad.py``: \"An error in Furqan is not a thrown exception
with a free-form string. It is a structured diagnosis with four
required fields.\" The v0.3.2 code path violated that contract on
three concrete inputs; v0.3.3 closes it.
"""

from __future__ import annotations

from furqan_lint.adapter import (
    _extract_union_with_none_inner,
    _is_union_with_none,
    translate_source,
)
from furqan_lint.runner import check_python_module
import ast


# ---------------------------------------------------------------------------
# Boundary: degenerate Union[None, ...] shapes must not crash translation
# ---------------------------------------------------------------------------

def test_round6_degenerate_union_single_none_does_not_crash() -> None:
    """``Union[None]`` is legal Python that ``typing.Union``
    evaluates to ``type(None)`` at runtime. v0.3.2 raised
    ``IndexError`` on this input. v0.3.3 must translate without
    raising; the exact diagnostic shape is open (the input is
    degenerate) but a hard crash is not the right answer.
    """
    src = (
        "from typing import Union\n"
        "def f() -> Union[None]:\n"
        "    return None\n"
    )
    module = translate_source(src, "<test>")
    # Smoke: the module translates and the function is collected.
    assert module is not None
    assert any(fn.name == "f" for fn in module.functions)


def test_round6_degenerate_union_two_nones_does_not_crash() -> None:
    """``Union[None, None]`` is legal Python (degenerate but no
    syntax error; ``typing.Union`` collapses it to ``type(None)``
    at runtime). v0.3.2 crashed here. v0.3.3 must not.
    """
    src = (
        "from typing import Union\n"
        "def f() -> Union[None, None]:\n"
        "    return None\n"
    )
    module = translate_source(src, "<test>")
    assert module is not None
    assert any(fn.name == "f" for fn in module.functions)


def test_round6_degenerate_union_three_nones_does_not_crash() -> None:
    """The 3+ arm fall-through path was the line that crashed in
    v0.3.2 (``folded = non_none[0]`` with ``non_none == []``). Pin
    a 3-arm all-None Union explicitly so the regression cannot
    return through the variadic case.
    """
    src = (
        "from typing import Union\n"
        "def f() -> Union[None, None, None]:\n"
        "    return None\n"
    )
    module = translate_source(src, "<test>")
    assert module is not None
    assert any(fn.name == "f" for fn in module.functions)


# ---------------------------------------------------------------------------
# Predicate truthfulness: _is_union_with_none must reject what
# _extract_union_with_none_inner cannot satisfy
# ---------------------------------------------------------------------------

def test_round6_is_union_with_none_rejects_all_none_arms() -> None:
    """``_is_union_with_none`` must return False on
    ``Union[None]``, ``Union[None, None]``, and
    ``Union[None, None, None]``. The predicate is the truthful
    contract that ``_extract_union_with_none_inner`` can satisfy:
    if every arm is None, there is no non-None inner type to
    extract.

    Failure shape this catches: a future refactor that re-broadens
    the predicate to accept all-None Unions would re-introduce the
    v0.3.2 IndexError. The error message names what would break if
    that happened, so a regression has a self-explaining failure.
    """
    for src_arms in ("None", "None, None", "None, None, None"):
        annotation_src = f"Union[{src_arms}]"
        node = ast.parse(annotation_src, mode="eval").body
        assert not _is_union_with_none(node), (
            f"_is_union_with_none accepted a degenerate "
            f"{annotation_src} as Optional. The predicate must require "
            f"BOTH a None arm AND a non-None arm; otherwise the "
            f"downstream _extract_union_with_none_inner crashes with "
            f"IndexError on the empty non_none list."
        )


def test_round6_is_union_with_none_still_accepts_real_optional_unions() -> None:
    """Negative test: the tightened predicate must NOT regress on
    the real ``Union[X, None]`` shape that v0.3.2 Finding 1
    introduced support for. Pin the happy path so the v0.3.3 fix
    cannot accidentally undo the v0.3.2 fix.
    """
    for src_arms in ("int, None", "None, int", "int, str, None"):
        annotation_src = f"Union[{src_arms}]"
        node = ast.parse(annotation_src, mode="eval").body
        assert _is_union_with_none(node), (
            f"_is_union_with_none rejected {annotation_src}, which "
            f"is the canonical Optional-via-Union shape that v0.3.2 "
            f"Finding 1 added support for. The v0.3.3 boundary fix "
            f"must not regress on the v0.3.2 happy path."
        )


def test_round6_extract_inner_assertion_fires_on_contract_violation() -> None:
    """Defense in depth: if a future caller bypasses
    ``_is_union_with_none`` and calls
    ``_extract_union_with_none_inner`` directly on a Union with no
    non-None arms, the assertion must fire with a contract-naming
    message instead of the cryptic ``IndexError: list index out of
    range``.
    """
    node = ast.parse("Union[None, None]", mode="eval").body
    try:
        _extract_union_with_none_inner(node)
    except AssertionError as exc:
        assert "non-None" in str(exc) or "_is_union_with_none" in str(exc)
    else:
        raise AssertionError(
            "_extract_union_with_none_inner accepted a Union with no "
            "non-None arms without asserting. The defense-in-depth "
            "assertion is the second line of defense after "
            "_is_union_with_none; both must hold."
        )


# ---------------------------------------------------------------------------
# End-to-end: degenerate Unions produce no MARAD, no crash
# ---------------------------------------------------------------------------

def test_round6_degenerate_union_runs_full_pipeline_clean() -> None:
    """End-to-end: a function with ``Union[None]`` return and an
    actual ``return None`` body must complete the full check
    pipeline without raising. The expected outcome under v0.3.3 is
    a clean PASS (zero diagnostics): the return statement returns
    ``None``, the annotation resolves to ``type(None)``, the two
    are compatible.
    """
    src = (
        "from typing import Union\n"
        "def f() -> Union[None]:\n"
        "    return None\n"
    )
    module = translate_source(src, "<test>")
    diagnostics = check_python_module(module)
    # Zero diagnostics: degenerate Union[None] declares NoneType,
    # the body returns None, the two agree. The important property
    # is the absence of an unhandled exception; the absence of a
    # false-positive Marad is a bonus.
    assert diagnostics == [], (
        f"v0.3.3 unexpectedly produced diagnostics on a degenerate "
        f"Union[None] with a matching return None body. The full "
        f"pipeline must complete without crashing AND without "
        f"firing a false-positive Marad. Got: {diagnostics}"
    )
