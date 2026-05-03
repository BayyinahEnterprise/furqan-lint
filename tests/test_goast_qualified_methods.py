"""Pinning tests for v0.8.2's qualified method-name emission in
goast (locked decision 4).

The v0.8.1 goast collected method names without receiver-type
qualification, causing the method-name conflation false-
negative documented in v0.8.1 commit 4. v0.8.2 adds a
``receiverTypeName`` helper handling four receiver shapes and
emits ``Type.Method`` for each method.

The four shapes pinned here:

  1. Value receiver:        ``func (c T) Foo()``           -> ``T.Foo``
  2. Pointer receiver:      ``func (c *T) Foo()``          -> ``T.Foo``
  3. Value generic:         ``func (c T[U]) Foo()``        -> ``T.Foo``
  4. Pointer generic:       ``func (c *T[U]) Foo()``       -> ``T.Foo``

Tests skipped when [go] extras are absent (matches the
test_go_diff.py shape).
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _go_extras_present() -> bool:
    spec = importlib.util.find_spec("furqan_lint.go_adapter")
    if spec is None or spec.origin is None:
        return False
    pkg_root = Path(spec.origin).parent
    binary = pkg_root / "bin" / "goast"
    return binary.is_file() and os.access(binary, os.X_OK)


pytestmark = [
    pytest.mark.unit,
    pytest.mark.skipif(
        not _go_extras_present(),
        reason="goast binary not built; install [go] extras",
    ),
]


def test_goast_emits_qualified_value_receiver_methods(tmp_path: Path) -> None:
    """``func (c T) Foo()`` emits as ``T.Foo`` in public_names."""
    from furqan_lint.go_adapter import extract_public_names

    src = tmp_path / "m.go"
    src.write_text(
        "package m\n"
        "type Counter struct{}\n"
        "type Logger struct{}\n"
        "func (c Counter) Foo() {}\n"
        "func (l Logger) Foo() {}\n"
    )
    names = extract_public_names(src)
    assert names == frozenset({"Counter", "Logger", "Counter.Foo", "Logger.Foo"})


def test_goast_emits_qualified_pointer_receiver_methods(tmp_path: Path) -> None:
    """``func (c *T) Foo()`` emits as ``T.Foo`` in public_names.
    The pointer-vs-value distinction is intentionally erased at
    the diff layer (both forms address the same method on the
    same type from the API consumer's perspective).
    """
    from furqan_lint.go_adapter import extract_public_names

    src = tmp_path / "m.go"
    src.write_text(
        "package m\n"
        "type Counter struct{}\n"
        "type Logger struct{}\n"
        "func (c *Counter) Foo() {}\n"
        "func (l *Logger) Foo() {}\n"
    )
    names = extract_public_names(src)
    assert names == frozenset({"Counter", "Logger", "Counter.Foo", "Logger.Foo"})


def test_goast_emits_qualified_generic_receiver_methods(tmp_path: Path) -> None:
    """Both value-generic and pointer-generic receivers
    (``func (c T[U]) Foo()`` and ``func (c *T[U]) Foo()``) emit
    as ``T.Foo``. The type-parameter list is stripped at the
    diff layer; type parameters are not part of the public
    name.
    """
    from furqan_lint.go_adapter import extract_public_names

    src = tmp_path / "m.go"
    src.write_text(
        "package m\n"
        "type Container[T any] struct { v T }\n"
        "func (c Container[T]) Peek() T { var z T; return z }\n"
        "func (c *Container[T]) Get() T { var z T; return z }\n"
    )
    names = extract_public_names(src)
    assert names == frozenset({"Container", "Container.Peek", "Container.Get"})
