"""Tests for numpy reference discovery (v0.9.3 commit 2 part).

Covers 5 reference-discovery tests:

* finds existing _build.py
* returns None when _build.py absent
* returns None when numpy_reference not callable
* returns None on _build.py syntax error
* does not pollute sys.modules

The convention is NeuroGolf-specific (Decision 9 / four-place
documented limit ``numpy_divergence_neurogolf_convention``);
these tests pin the discovery behavior. The downstream divergence
checker (commit 3) consumes the discovered reference.
"""

from __future__ import annotations

import sys
from pathlib import Path


def _write_build_script(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")


def test_discover_numpy_reference_finds_existing_build_py(tmp_path: Path) -> None:
    """For ``<dir>/foo.onnx``, ``<dir>/foo_build.py`` containing a
    top-level ``numpy_reference`` callable is discovered and
    returned."""
    from furqan_lint.onnx_adapter.numpy_reference import (
        discover_numpy_reference,
    )

    onnx_path = tmp_path / "foo.onnx"
    onnx_path.write_bytes(b"")  # presence only; the loader looks at the sibling
    _write_build_script(
        tmp_path / "foo_build.py",
        "def numpy_reference(grid):\n" "    import numpy as np\n" "    return np.array(grid) * 2\n",
    )
    ref = discover_numpy_reference(onnx_path)
    assert callable(ref)
    # Sanity: exercise the callable.
    out = ref([[1, 2], [3, 4]])
    assert out.tolist() == [[2, 4], [6, 8]]


def test_discover_numpy_reference_returns_none_when_build_py_absent(
    tmp_path: Path,
) -> None:
    """No sibling ``_build.py`` file means silent-pass per
    Decision 6 condition (b)."""
    from furqan_lint.onnx_adapter.numpy_reference import (
        discover_numpy_reference,
    )

    onnx_path = tmp_path / "lonely.onnx"
    onnx_path.write_bytes(b"")
    assert discover_numpy_reference(onnx_path) is None


def test_discover_numpy_reference_returns_none_when_not_callable(
    tmp_path: Path,
) -> None:
    """If ``numpy_reference`` exists but is not callable, the
    discovery returns ``None`` rather than the non-callable
    object."""
    from furqan_lint.onnx_adapter.numpy_reference import (
        discover_numpy_reference,
    )

    onnx_path = tmp_path / "foo.onnx"
    onnx_path.write_bytes(b"")
    _write_build_script(
        tmp_path / "foo_build.py",
        "numpy_reference = 'not callable, just a string'\n",
    )
    assert discover_numpy_reference(onnx_path) is None


def test_discover_numpy_reference_returns_none_on_syntax_error(
    tmp_path: Path,
) -> None:
    """A ``_build.py`` that fails to load (syntax error, import
    error, etc.) returns ``None`` rather than propagating the
    exception. The lint must not blow up because a sidecar is
    malformed."""
    from furqan_lint.onnx_adapter.numpy_reference import (
        discover_numpy_reference,
    )

    onnx_path = tmp_path / "foo.onnx"
    onnx_path.write_bytes(b"")
    _write_build_script(
        tmp_path / "foo_build.py",
        "this is not valid python @@@\n",
    )
    assert discover_numpy_reference(onnx_path) is None


def test_discover_numpy_reference_does_not_pollute_sys_modules(
    tmp_path: Path,
) -> None:
    """Round-33 robustness pin: the loader must not register the
    loaded module in ``sys.modules``. Subsequent invocations on
    different files must not collide; the unique-per-invocation
    module name is the implementation contract."""
    from furqan_lint.onnx_adapter.numpy_reference import (
        discover_numpy_reference,
    )

    onnx_path = tmp_path / "foo.onnx"
    onnx_path.write_bytes(b"")
    _write_build_script(
        tmp_path / "foo_build.py",
        "def numpy_reference(grid):\n    return grid\n",
    )
    keys_before = set(sys.modules.keys())
    ref = discover_numpy_reference(onnx_path)
    assert callable(ref)
    new_keys = set(sys.modules.keys()) - keys_before
    polluted = [k for k in new_keys if k.startswith("_furqan_build_")]
    assert polluted == [], f"loader polluted sys.modules with: {polluted}"
