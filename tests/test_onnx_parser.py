"""Tests for the ONNX parser entry point.

Covers the three commit-2 tests:

* ``test_onnx_parser_loads_valid_model``
* ``test_onnx_parser_raises_on_invalid_protobuf``
* ``test_onnx_parser_raises_on_missing_extras``

The third test exercises the ``OnnxExtrasNotInstalled`` typed
exception by patching ``sys.modules`` so the lazy ``import onnx``
inside ``parse_model`` raises ``ImportError``.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

onnx = pytest.importorskip("onnx")

from tests.fixtures.onnx.builders import make_relu_model, write_model  # noqa: E402


def test_onnx_parser_loads_valid_model(tmp_path: Path) -> None:
    """A well-formed ONNX model loads and parse_model returns a
    ModelProto-shaped object with the expected graph identity."""
    from furqan_lint.onnx_adapter import parse_model

    path = write_model(tmp_path / "relu.onnx", make_relu_model())
    model = parse_model(path)
    assert model.graph.name == "test_relu"
    assert len(model.graph.input) == 1
    assert len(model.graph.output) == 1
    assert model.graph.input[0].name == "x"
    assert model.graph.output[0].name == "y"


def test_onnx_parser_raises_on_invalid_protobuf(tmp_path: Path) -> None:
    """A file whose bytes are not a valid ONNX protobuf raises
    OnnxParseError carrying the failing path."""
    from furqan_lint.onnx_adapter import OnnxParseError, parse_model

    bad = tmp_path / "garbage.onnx"
    bad.write_bytes(b"this is not a protobuf at all")
    with pytest.raises(OnnxParseError) as exc_info:
        parse_model(bad)
    assert str(bad) in str(exc_info.value)


def test_onnx_parser_raises_on_missing_extras(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When ``onnx`` is not importable, parse_model raises
    OnnxExtrasNotInstalled (subclass of ImportError) with the
    install hint as its message.
    """
    from furqan_lint.onnx_adapter import OnnxExtrasNotInstalled

    # Force the ``import onnx`` inside parse_model to fail by
    # removing it from sys.modules and blocking re-import.
    monkeypatch.setitem(sys.modules, "onnx", None)
    # Re-import parser to re-trigger the lazy import path.
    import importlib

    import furqan_lint.onnx_adapter.parser as parser_mod

    importlib.reload(parser_mod)
    with pytest.raises(OnnxExtrasNotInstalled) as exc_info:
        parser_mod.parse_model(tmp_path / "ignored.onnx")
    assert "pip install furqan-lint[onnx]" in str(exc_info.value)
    # Subclass relationship for callers catching ImportError.
    assert isinstance(exc_info.value, ImportError)
    # Restore the module for downstream tests in the same session.
    monkeypatch.setitem(sys.modules, "onnx", onnx)
    importlib.reload(parser_mod)
