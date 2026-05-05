"""ONNX-specific verification gates (post-v0.9.4 inventory):

* ``test_gate_8c_onnx_containment``: static AST scan of
  ``src/furqan_lint/`` confirms ``import onnx`` and
  ``from onnx ...`` appear only in files under
  ``src/furqan_lint/onnx_adapter/``. Round-24 finding m5
  closure: the assertion is exact-AST, not a naive grep, so
  comments and docstring mentions of "onnx" do not false-fire.
* ``test_gate_9c_onnx_missing_extras``: simulates the
  ``[onnx]`` extra missing from the install. The CLI raises
  ``OnnxExtrasNotInstalled`` (subclass of ``ImportError``)
  with the install hint as its message.

The v0.9.0-pinned ``test_gate_changelog_math_v0_9_0`` scaffold
was retired in v0.9.4 (Part 1 / round-30 META closure). The
canonical ``test_changelog_math_matches_pytest_collect`` in
``tests/test_changelog_math_gate.py`` covers the same
arithmetic check version-agnostically.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = REPO_ROOT / "src" / "furqan_lint"


def _walks_python_source_files(root: Path):
    """Yield every ``.py`` file under ``root`` (excluding caches)."""
    for p in root.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        yield p


def test_gate_8c_onnx_containment() -> None:
    """``import onnx`` / ``from onnx ...`` appear only in files
    under ``src/furqan_lint/onnx_adapter/``.

    Implementation: AST-walk every ``.py`` file under
    ``src/furqan_lint/``; flag ``Import``/``ImportFrom`` nodes
    whose module is ``onnx`` (or a submodule) AND whose source
    file is NOT under ``src/furqan_lint/onnx_adapter/``.

    Round-24 finding m5 closure: the assertion uses ``ast``,
    not a naive grep, so prose mentions of ``onnx`` in
    comments or docstrings do not false-fire.
    """
    onnx_adapter_dir = SRC_ROOT / "onnx_adapter"
    violations: list[tuple[Path, int, str]] = []

    for source_file in _walks_python_source_files(SRC_ROOT):
        if onnx_adapter_dir in source_file.parents:
            continue  # the adapter is the one place onnx may be imported.
        try:
            tree = ast.parse(source_file.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "onnx" or alias.name.startswith("onnx."):
                        violations.append((source_file, node.lineno, f"import {alias.name}"))
            elif isinstance(node, ast.ImportFrom):
                if node.module is not None and (
                    node.module == "onnx" or node.module.startswith("onnx.")
                ):
                    violations.append((source_file, node.lineno, f"from {node.module} import ..."))

    assert not violations, (
        f"onnx imports leaked outside src/furqan_lint/onnx_adapter/: "
        f"{[(str(p.relative_to(REPO_ROOT)), ln, kind) for p, ln, kind in violations]}"
    )


def test_gate_9c_onnx_missing_extras(monkeypatch: pytest.MonkeyPatch) -> None:
    """When the [onnx] extra is missing, parse_model raises
    ``OnnxExtrasNotInstalled`` (subclass of ``ImportError``)
    with the canonical install hint."""
    from furqan_lint.onnx_adapter import OnnxExtrasNotInstalled

    # Force the lazy ``import onnx`` inside parser to fail.
    monkeypatch.setitem(sys.modules, "onnx", None)
    import importlib

    import furqan_lint.onnx_adapter.parser as parser_mod

    importlib.reload(parser_mod)
    try:
        with pytest.raises(OnnxExtrasNotInstalled) as exc:
            parser_mod.parse_model("ignored.onnx")
        assert "pip install furqan-lint[onnx]" in str(exc.value)
        assert isinstance(exc.value, ImportError)
    finally:
        # Restore the real onnx for downstream tests in the same session.
        try:
            import onnx as _real_onnx

            monkeypatch.setitem(sys.modules, "onnx", _real_onnx)
        except ImportError:
            monkeypatch.delitem(sys.modules, "onnx", raising=False)
        importlib.reload(parser_mod)
