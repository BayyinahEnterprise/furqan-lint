"""Phase G11.0.1 (at-Tawbah) T03: pin Python signature canonicalizer
H-4 nested-generic recursion defense.

Mirror of the G11.1 amended_4 H-4 propagation defense: a
multi-argument generic's slice is an ast.Tuple whose elements
MUST recurse element-wise. The pre-v0.11.2 implementation fell
through to ast.unparse(node.slice) for tuple slices, producing
"Dict[(str, int)]" instead of "Dict[str, int]". v0.11.2
restores cross-language symmetry with the Rust verifier.

Five pinning cases per the prompt's T03 specification (plus
an extra Optional[List[Result]] anchor to round out the test).
"""

# ruff: noqa: E402

from __future__ import annotations

import ast

import pytest

pytest.importorskip("rfc8785")

from furqan_lint.gate11.signature_canonicalization import (
    _canonical_type_string,
)


def _canon(source: str) -> str:
    """Parse ``source`` as a single annotation expression and
    return the canonical type string.
    """
    return _canonical_type_string(ast.parse(source, mode="eval").body)


def test_h4_dict_two_arg_recurses_element_wise():
    """Dict[str, int] -- the canonical H-4 audit case.

    Pre-v0.11.2 produced "Dict[(str, int)]" (tuple
    stringification fallthrough). v0.11.2 produces
    "Dict[str, int]".
    """
    assert _canon("Dict[str, int]") == "Dict[str, int]"


def test_h4_dict_str_optional_tuple():
    """Dict[str, Optional[Tuple[int, str]]] --
    multi-arg generic with nested Optional.
    """
    assert _canon("Dict[str, Optional[Tuple[int, str]]]") == "Dict[str, Tuple[int, str] | None]"


def test_h4_list_dict_kv_typevars():
    """List[Dict[K, V]] -- nested with type-variable parameters."""
    assert _canon("List[Dict[K, V]]") == "List[Dict[K, V]]"


def test_h4_union_optional_t_list_u():
    """Union[Optional[T], List[U]] -- Union containing nested
    generics with inner Union flattening.
    """
    assert _canon("Union[Optional[T], List[U]]") == "List[U] | T | None"


def test_h4_callable_with_nested_generics():
    """Callable[[Dict[str, T]], Optional[List[U]]] -- callable
    with nested generics in arg + return position.
    """
    assert (
        _canon("Callable[[Dict[str, T]], Optional[List[U]]]")
        == "Callable[[Dict[str, T]], List[U] | None]"
    )


def test_h4_optional_list_result_te():
    """Optional[List[Result[T, E]]] -- triple-nested with
    Optional outer (the audit-prompt's first listed fixture).
    """
    assert _canon("Optional[List[Result[T, E]]]") == "List[Result[T, E]] | None"


def test_h4_inner_difference_detected():
    """The H-4 audit's central assertion: two structurally
    distinct nested generics MUST produce different canonical
    strings. Pre-v0.11.2 the tuple-stringification fallthrough
    could erase the difference.
    """
    assert _canon("Dict[str, Optional[V]]") != _canon("Dict[str, Result[V, Exception]]")


def test_h4_dict_tuple_value_preserved():
    """Dict[str, Tuple[int, str]] -- inner Tuple is itself a
    multi-arg generic; recursion must reach the inner Tuple's
    elements.
    """
    assert _canon("Dict[str, Tuple[int, str]]") == "Dict[str, Tuple[int, str]]"
