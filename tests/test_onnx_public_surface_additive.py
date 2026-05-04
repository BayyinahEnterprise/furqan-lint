"""ONNX adapter surface snapshots + v0.9.0 cross-cuts.

Establishes the additive-only discipline for the
``furqan_lint.onnx_adapter`` subpackage and pins:

* ``test_v0_9_0_onnx_adapter_surface_snapshot``: the v0.9.0
  baseline of ``onnx_adapter.__all__``.
* ``test_v0_9_0_top_level_surface_snapshot``: the v0.9.0
  baseline of the top-level ``furqan_lint.__all__`` (alias of
  V0_7_0_SURFACE; v0.9.0 ships a new subpackage but does not
  change the top-level surface).
* ``test_v0_9_0_rust_go_baselines_unchanged``: the v0.9.0
  baselines for the Rust and Go subpackages are aliases of
  v0.8.5; v0.9.0 introduces no Rust or Go surface change.

Per Bayyinah Engineering Discipline Framework section 7.6
(per-version cadence), every shipped minor and patch version
gets a named frozenset constant. The constant's existence is
the baseline; the name is the audit pin.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


# v0.9.0 baseline of furqan_lint.onnx_adapter.__all__. Eight
# names ship in v0.9.0:
#   BranchSummary, NodeSummary, OnnxExtrasNotInstalled,
#   OnnxModule, OnnxParseError, ValueInfoSummary,
#   extract_public_names, parse_model
# Future v0.9.x and v0.10.x may EXTEND this set; they may NOT
# remove from it without a major-version bump.
ONNX_ADAPTER_PUBLIC_SURFACE_v0_9_0: frozenset[str] = frozenset(
    {
        "BranchSummary",
        "NodeSummary",
        "OnnxExtrasNotInstalled",
        "OnnxModule",
        "OnnxParseError",
        "ValueInfoSummary",
        "extract_public_names",
        "parse_model",
    }
)


def test_v0_9_0_onnx_adapter_surface_snapshot() -> None:
    """``furqan_lint.onnx_adapter.__all__`` must include every
    name from the v0.9.0 baseline. If a future version drops a
    name listed here, this test fails and the version requires
    a major bump.
    """
    pytest.importorskip("onnx")
    from furqan_lint import onnx_adapter

    current = frozenset(onnx_adapter.__all__)
    missing = ONNX_ADAPTER_PUBLIC_SURFACE_v0_9_0 - current
    assert not missing, (
        f"onnx_adapter.__all__ removed names from the v0.9.0 baseline: "
        f"{sorted(missing)}. Removals require a major-version bump."
    )
    # Belt-and-braces: v0.9.0 ships exactly these 8 names. Any
    # superset is fine; any subset fails above.
    assert ONNX_ADAPTER_PUBLIC_SURFACE_v0_9_0 <= current


def test_v0_9_0_top_level_surface_snapshot() -> None:
    """The v0.9.0 top-level baseline aliases V0_7_0_SURFACE
    (``{"__version__"}``); v0.9.0 ships a new subpackage but
    does not change the top-level ``furqan_lint.__all__``
    surface, mirroring how v0.8.0 (Go adapter) and v0.7.0
    (Rust adapter) shipped without touching the top-level."""
    import furqan_lint
    from tests.test_top_level_public_surface_additive import V0_7_0_SURFACE

    current = frozenset(furqan_lint.__all__)
    v0_9_0_baseline = V0_7_0_SURFACE
    missing = v0_9_0_baseline - current
    assert not missing, (
        f"furqan_lint.__all__ removed names from the v0.9.0 baseline "
        f"(alias of V0_7_0_SURFACE): {sorted(missing)}. Removals "
        f"require a major-version bump."
    )


def test_v0_9_0_rust_go_baselines_unchanged() -> None:
    """v0.9.0 introduces no Rust or Go subpackage surface change.

    The Rust baseline is the v0.8.5 alias (which itself aliases
    v0.8.4 ... v0.8.2's ``extract_public_names`` extension). The
    Go baseline follows the same alias chain.
    """
    from tests.test_rust_public_surface_additive import (
        _RUST_ADAPTER_PUBLIC_SURFACE_v0_8_5,
    )

    pytest.importorskip("tree_sitter_rust")
    from furqan_lint import rust_adapter

    rust_current = frozenset(rust_adapter.__all__)
    rust_v0_9_0_baseline = _RUST_ADAPTER_PUBLIC_SURFACE_v0_8_5
    missing_rust = rust_v0_9_0_baseline - rust_current
    assert not missing_rust, (
        f"rust_adapter.__all__ removed names from v0.9.0 baseline "
        f"(alias of v0.8.5): {sorted(missing_rust)}."
    )

    # Go: the per-version cadence file
    # tests/test_go_public_surface_additive.py defines the v0.8.5
    # alias; reuse it here.
    from furqan_lint import go_adapter
    from tests.test_go_public_surface_additive import (
        _GO_ADAPTER_PUBLIC_SURFACE_v0_8_5,
    )

    go_current = frozenset(go_adapter.__all__)
    go_v0_9_0_baseline = _GO_ADAPTER_PUBLIC_SURFACE_v0_8_5
    missing_go = go_v0_9_0_baseline - go_current
    assert not missing_go, (
        f"go_adapter.__all__ removed names from v0.9.0 baseline "
        f"(alias of v0.8.5): {sorted(missing_go)}."
    )


# -------------------------------------------------------------
# §8 four-place documented-limit pinning tests (2 of 3; the
# registry-pin pin landed in commit 3 alongside the checker
# tests).
# -------------------------------------------------------------


def test_onnx_diff_intermediates_excluded(tmp_path) -> None:
    """The additive-only diff covers ``graph.input`` and
    ``graph.output`` ValueInfo only (Decision 5 / round-24
    finding m2 closure).

    A new model that differs from the old only in intermediate
    value names (``graph.value_info`` / per-edge tensor names)
    must NOT fire a MARAD. Otherwise every model retraining
    that renamed an internal layer would break the additive
    contract.
    """
    pytest.importorskip("onnx")
    from furqan_lint.additive import compare_name_sets
    from furqan_lint.onnx_adapter import extract_public_names
    from tests.fixtures.onnx.builders import (
        make_intermediates_only_diff_model,
        make_relu_model,
        write_model,
    )

    old = write_model(tmp_path / "old.onnx", make_relu_model())
    new = write_model(tmp_path / "new.onnx", make_intermediates_only_diff_model())
    diags = compare_name_sets(
        previous_names=extract_public_names(old),
        current_names=extract_public_names(new),
        filename=str(new),
        language="onnx",
    )
    assert diags == [], (
        f"intermediate-only diff should not fire MARAD per Decision 5; " f"got: {diags}"
    )
