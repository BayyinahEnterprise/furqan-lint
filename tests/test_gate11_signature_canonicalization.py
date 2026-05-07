"""Tests for Phase G11.0 T04: signature canonicalization.

Pin:

* Optional[User] / User | None / Union[User, None] / Union[None, User]
  produce the same fingerprint.
* PEP 604 unions reorder consistently (int|str = str|int).
* Class includes public method names; excludes underscore-prefixed.
* Constant value changes do not change fingerprint; annotation
  changes do.
* Forward-reference strings unwrap (Optional["User"] = Optional[User]).
"""

from __future__ import annotations

import ast

import pytest

rfc8785 = pytest.importorskip("rfc8785")

from furqan_lint.gate11.signature_canonicalization import (  # noqa: E402
    class_signature_dict,
    constant_signature_dict,
    function_signature_dict,
    signature_fingerprint,
)


def _func(src: str) -> ast.FunctionDef:
    tree = ast.parse(src)
    fn = tree.body[0]
    assert isinstance(fn, ast.FunctionDef | ast.AsyncFunctionDef)
    return fn


def _cls(src: str) -> ast.ClassDef:
    tree = ast.parse(src)
    c = tree.body[0]
    assert isinstance(c, ast.ClassDef)
    return c


def _const(src: str):
    tree = ast.parse(src)
    a = tree.body[0]
    assert isinstance(a, ast.AnnAssign)
    name = a.target.id  # type: ignore[union-attr]
    return name, a.annotation


def test_optional_forms_are_equivalent() -> None:
    f1 = _func("def f(x: Optional[User]) -> None: ...")
    f2 = _func("def f(x: User | None) -> None: ...")
    f3 = _func("def f(x: Union[User, None]) -> None: ...")
    f4 = _func("def f(x: Union[None, User]) -> None: ...")
    fps = {signature_fingerprint(function_signature_dict(fn)) for fn in (f1, f2, f3, f4)}
    assert len(fps) == 1, f"all four Optional forms should match; got {fps}"


def test_pep604_union_order_invariant() -> None:
    f1 = _func("def f(x: int | str) -> None: ...")
    f2 = _func("def f(x: str | int) -> None: ...")
    a = signature_fingerprint(function_signature_dict(f1))
    b = signature_fingerprint(function_signature_dict(f2))
    assert a == b


def test_class_includes_public_methods_excludes_private() -> None:
    c = _cls(
        "class C:\n"
        "    def public(self): ...\n"
        "    def _private(self): ...\n"
        "    def __dunder__(self): ...\n"
    )
    sig = class_signature_dict(c)
    assert sig["method_names"] == ["public"]


def test_class_method_names_are_ascii_sorted() -> None:
    c = _cls(
        "class C:\n"
        "    def zeta(self): ...\n"
        "    def alpha(self): ...\n"
        "    def mu(self): ...\n"
    )
    sig = class_signature_dict(c)
    assert sig["method_names"] == ["alpha", "mu", "zeta"]


def test_constant_value_change_does_not_change_fingerprint() -> None:
    n1, a1 = _const("X: int = 1")
    n2, a2 = _const("X: int = 2")
    fp1 = signature_fingerprint(constant_signature_dict(n1, a1))
    fp2 = signature_fingerprint(constant_signature_dict(n2, a2))
    assert fp1 == fp2


def test_constant_annotation_change_changes_fingerprint() -> None:
    n1, a1 = _const("X: int = 1")
    n2, a2 = _const("X: str = '1'")
    fp1 = signature_fingerprint(constant_signature_dict(n1, a1))
    fp2 = signature_fingerprint(constant_signature_dict(n2, a2))
    assert fp1 != fp2


def test_forward_reference_unwrap() -> None:
    f1 = _func("def f(x: Optional['User']) -> None: ...")
    f2 = _func("def f(x: Optional[User]) -> None: ...")
    a = signature_fingerprint(function_signature_dict(f1))
    b = signature_fingerprint(function_signature_dict(f2))
    assert a == b


def test_async_flag_distinguishes_signature() -> None:
    f1 = _func("def f() -> int: ...")
    f2 = _func("async def f() -> int: ...")
    a = signature_fingerprint(function_signature_dict(f1))
    b = signature_fingerprint(function_signature_dict(f2))
    assert a != b


def test_default_present_distinguishes_signature() -> None:
    f1 = _func("def f(x: int) -> int: return x")
    f2 = _func("def f(x: int = 0) -> int: return x")
    sig1 = function_signature_dict(f1)
    sig2 = function_signature_dict(f2)
    assert sig1["parameters"][0]["default_present"] is False
    assert sig2["parameters"][0]["default_present"] is True
    assert signature_fingerprint(sig1) != signature_fingerprint(sig2)


def test_kwonly_and_vararg_handled() -> None:
    f = _func("def f(a: int, *args: str, b: int = 0, **kwargs: float) -> None: ...")
    sig = function_signature_dict(f)
    names = [p["name"] for p in sig["parameters"]]
    assert names == ["a", "*args", "b", "**kwargs"]
    annotations = [p["annotation"] for p in sig["parameters"]]
    assert annotations == ["int", "str", "int", "float"]
    defaults = [p["default_present"] for p in sig["parameters"]]
    # a no default; *args no default; b has default; **kwargs no default.
    assert defaults == [False, False, True, False]


def test_class_bases_canonical() -> None:
    c1 = _cls("class C(int, str): ...")
    c2 = _cls("class C(int, str): ...")
    assert class_signature_dict(c1) == class_signature_dict(c2)
    # base list is in source order, not sorted; canonical_type_string
    # normalizes each entry but order-of-bases is semantically
    # significant in Python (MRO).
    assert class_signature_dict(c1)["bases"] == ["int", "str"]


def test_no_annotation_returns_canonical_none() -> None:
    f = _func("def f(x): return x")
    sig = function_signature_dict(f)
    assert sig["parameters"][0]["annotation"] == "None"
    assert sig["return_annotation"] == "None"


def test_three_member_union_orders_alphabetically() -> None:
    f1 = _func("def f(x: int | str | float) -> None: ...")
    f2 = _func("def f(x: float | str | int) -> None: ...")
    a = signature_fingerprint(function_signature_dict(f1))
    b = signature_fingerprint(function_signature_dict(f2))
    assert a == b
    sig = function_signature_dict(f1)
    # alphabetical: float, int, str (no None present)
    assert sig["parameters"][0]["annotation"] == "float | int | str"
