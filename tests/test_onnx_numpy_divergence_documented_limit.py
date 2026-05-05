"""Four-place pinning test for the v0.9.3 documented limit
``numpy_divergence_neurogolf_convention``.

The check is opt-in by NeuroGolf-convention reference and
probe-grid presence (Decision 9 of v0.9.3 prompt). When neither
sidecar is present, the divergence checker silent-passes with no
diagnostic emitted. Generic ONNX users who lack the NeuroGolf
shape see this behavior; the four-place pattern surfaces it so
they understand why.
"""

from __future__ import annotations

from pathlib import Path

import pytest

onnx = pytest.importorskip("onnx")

from tests.fixtures.onnx.builders import make_relu_model  # noqa: E402


def test_numpy_divergence_silent_pass_when_neurogolf_convention_absent(
    tmp_path: Path,
) -> None:
    """No ``_build.py`` and no ``.json`` task file in the same
    directory as the model: the divergence checker silent-passes
    per Decision 6 conditions (b)/(c) of the v0.9.3 prompt.

    This is the four-place pinning test for the
    ``numpy_divergence_neurogolf_convention`` documented limit.
    A future change in convention semantics (e.g., adding
    decorator-based discovery) would shift this behavior; the
    pin catches that drift.
    """
    from furqan_lint.onnx_adapter.numpy_divergence import (
        check_numpy_divergence,
    )

    onnx_path = tmp_path / "lonely.onnx"
    onnx.save(make_relu_model(), str(onnx_path))
    findings = list(check_numpy_divergence(onnx.load(str(onnx_path)), onnx_path))
    assert findings == [], (
        "v0.9.3 divergence checker should silent-pass when no "
        "NeuroGolf convention sidecars are present; got "
        f"{findings}"
    )
