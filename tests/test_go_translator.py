"""Go adapter translator tests (v0.8.0 Phase 1).

6 unit tests covering the JSON-to-Furqan-IR contract:

- function translates to FunctionDef with correct fields.
- (T, error) return becomes UnionType with error in right arm
  (pinning the translator's ordering convention).
- nil expressions translate to opaque markers, NOT __none__
  markers (locked decision 5: avoid accidental cross-language
  firing of Python's check_return_none on idiomatic Go returns).
- Two-element non-error tuples treated as opaque TypePath.
- 3+-element returns are documented limit.

The convention pin (test_go_translator_emits_error_in_right_arm)
is load-bearing: D11's _is_error_return predicate is symmetric
across union arms, but the translator's emission contract is
asymmetric (error always in right per Go convention). The pin
ensures a future translator change that reorders fires the test,
not silently breaks the predicate.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def _go_extras_present() -> bool:
    spec = importlib.util.find_spec("furqan_lint.go_adapter")
    if spec is None or spec.origin is None:
        return False
    pkg_root = Path(spec.origin).parent
    binary = pkg_root / "bin" / "goast"
    return binary.is_file() and os.access(binary, os.X_OK)


_REASON = "goast binary not built; install [go] extras"
pytestmark_go = pytest.mark.skipif(not _go_extras_present(), reason=_REASON)


@pytestmark_go
def test_go_function_translates_to_function_def(tmp_path: Path) -> None:
    """A simple Go function becomes a FunctionDef with name,
    return_type, statements, and calls."""
    from furqan.parser.ast_nodes import FunctionDef

    from furqan_lint.go_adapter import parse_file
    from furqan_lint.go_adapter.translator import translate

    source = tmp_path / "simple.go"
    source.write_text(
        "package simple\n\n" "func Add(a int, b int) int {\n" "    return a + b\n" "}\n"
    )
    module = translate(parse_file(source), filename=str(source))
    assert len(module.functions) == 1
    fn = module.functions[0]
    assert isinstance(fn, FunctionDef)
    assert fn.name == "Add"


@pytestmark_go
def test_go_error_return_translates_to_union_type(tmp_path: Path) -> None:
    """``(T, error)`` returns translate to UnionType with concrete
    type names. The structural shape that ``_is_error_return``
    fires on."""
    from furqan.parser.ast_nodes import UnionType

    from furqan_lint.go_adapter import parse_file
    from furqan_lint.go_adapter.translator import translate

    source = tmp_path / "error_ret.go"
    source.write_text(
        "package errret\n\n"
        "func Load(path string) (string, error) {\n"
        "    return path, nil\n"
        "}\n"
    )
    module = translate(parse_file(source), filename=str(source))
    fn = module.functions[0]
    assert isinstance(fn.return_type, UnionType)


@pytestmark_go
def test_go_translator_emits_error_in_right_arm(tmp_path: Path) -> None:
    """Pinning test for the translator's ordering convention.

    The Go translator places error in the RIGHT arm of UnionType
    by Go convention (error is conventionally the last return
    value). The D11 predicate _is_error_return is symmetric, so
    a future translator change that reorders does not silently
    break D11; this test fires first and forces the change to
    be deliberate.
    """
    from furqan.parser.ast_nodes import UnionType

    from furqan_lint.go_adapter import parse_file
    from furqan_lint.go_adapter.translator import translate

    source = tmp_path / "right_arm.go"
    source.write_text("package rightarm\n\n" 'func Load() (string, error) { return "", nil }\n')
    module = translate(parse_file(source), filename=str(source))
    rt = module.functions[0].return_type
    assert isinstance(rt, UnionType)
    assert rt.left.base == "string", f"expected string in left arm, got {rt.left.base!r}"
    assert rt.right.base == "error", f"expected error in right arm, got {rt.right.base!r}"


@pytestmark_go
def test_go_nil_translates_to_opaque(tmp_path: Path) -> None:
    """nil in return position translates to IdentExpr(__opaque__),
    NOT IdentExpr(__none__).

    Locked decision 5: the __none__ marker stays Python-specific.
    Cross-language reuse would accidentally fire the Python-only
    check_return_none on idiomatic Go (T, error) returns.
    """
    from furqan.parser.ast_nodes import ReturnStmt

    from furqan_lint.go_adapter import parse_file
    from furqan_lint.go_adapter.translator import translate

    source = tmp_path / "nil_ret.go"
    source.write_text("package nilret\n\n" "func Load() (*int, error) { return nil, nil }\n")
    module = translate(parse_file(source), filename=str(source))
    fn = module.functions[0]
    return_stmts = [s for s in fn.statements if isinstance(s, ReturnStmt)]
    assert len(return_stmts) == 1
    # The marker text must be __opaque__, not __none__.
    assert return_stmts[0].value.name == "__opaque__"


@pytestmark_go
def test_go_two_element_non_error_tuple_treated_as_opaque(
    tmp_path: Path,
) -> None:
    """Two-element returns where the LAST arm is not error become
    an opaque TypePath, not a UnionType.

    A ``(T, U)`` return where neither is error is not a may-fail
    producer; D11 should not fire on callers. The translator's
    rule (last must be ``error`` for UnionType emission) prevents
    accidental D11 firing on these shapes.
    """
    from furqan.parser.ast_nodes import TypePath

    from furqan_lint.go_adapter import parse_file
    from furqan_lint.go_adapter.translator import translate

    source = tmp_path / "tuple.go"
    source.write_text("package tup\n\n" 'func Pair() (int, string) { return 1, "x" }\n')
    module = translate(parse_file(source), filename=str(source))
    rt = module.functions[0].return_type
    assert isinstance(rt, TypePath)
    assert "int" in rt.base and "string" in rt.base


@pytestmark_go
def test_go_three_or_more_element_return_documented_limit(
    tmp_path: Path,
) -> None:
    """Three-or-more-element returns are out of scope for Phase 1.

    The translator emits an opaque ``TypePath("<multi-return>")``
    rather than attempting an n-ary encoding. Documented limit
    per locked decision 4 (UnionType IR is binary).
    """
    from furqan.parser.ast_nodes import TypePath

    from furqan_lint.go_adapter import parse_file
    from furqan_lint.go_adapter.translator import translate

    source = tmp_path / "triple.go"
    source.write_text(
        "package triple\n\n" 'func Triple() (int, string, error) { return 1, "x", nil }\n'
    )
    module = translate(parse_file(source), filename=str(source))
    rt = module.functions[0].return_type
    assert isinstance(rt, TypePath)
    assert rt.base == "<multi-return>"
