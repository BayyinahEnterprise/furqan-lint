"""Frozen snapshot of furqan_lint.rust_adapter.__all__ (v0.7.0).

Establishes the additive-only discipline for the rust subpackage:
every release MUST be a superset of the prior release's public
surface. The Python adapter does not yet have an equivalent
snapshot; v0.7.x or v0.8 may add one without urgency.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

# The v0.7.0 baseline. Future releases may EXTEND this set; they
# may not REMOVE from it without a major-version bump.
_RUST_ADAPTER_PUBLIC_SURFACE_v0_7_0: frozenset[str] = frozenset(
    {
        "parse_file",
        "RustParseError",
    }
)

# v0.7.0.1 added RustExtrasNotInstalled (typed exception for the
# missing-[rust]-extra case). Snapshot grows additively.
_RUST_ADAPTER_PUBLIC_SURFACE_v0_7_0_1: frozenset[str] = frozenset(
    {
        "parse_file",
        "RustParseError",
        "RustExtrasNotInstalled",
    }
)

# v0.7.1 added Phase 2 R3 wiring + Result-aware D11 (in v0.7.2,
# part of commit 1) but did not change the rust_adapter public
# surface; v0.7.2 also leaves the surface unchanged. Both versions
# alias the v0.7.0.1 baseline.
_RUST_ADAPTER_PUBLIC_SURFACE_v0_7_1: frozenset[str] = _RUST_ADAPTER_PUBLIC_SURFACE_v0_7_0_1
_RUST_ADAPTER_PUBLIC_SURFACE_v0_7_2: frozenset[str] = _RUST_ADAPTER_PUBLIC_SURFACE_v0_7_0_1

# v0.7.3 is a documentation-sweep + gate-addition corrective; no
# rust_adapter public surface change. Aliases v0.7.0.1.
_RUST_ADAPTER_PUBLIC_SURFACE_v0_7_3: frozenset[str] = _RUST_ADAPTER_PUBLIC_SURFACE_v0_7_0_1


def test_rust_adapter_public_surface_is_superset_of_v0_7_0_baseline() -> None:
    """``furqan_lint.rust_adapter.__all__`` must include every name
    from the v0.7.0 baseline. If a future version drops a name
    listed here, this test fails and the version requires a major
    bump."""
    from furqan_lint import rust_adapter

    current = frozenset(rust_adapter.__all__)
    missing = _RUST_ADAPTER_PUBLIC_SURFACE_v0_7_0 - current
    assert not missing, (
        f"rust_adapter.__all__ removed names from the v0.7.0 baseline: "
        f"{sorted(missing)}. Removals require a major-version bump per "
        f"the additive-only discipline."
    )


def test_rust_adapter_baseline_names_are_callable_or_class() -> None:
    """Each baseline name must resolve to a callable (function) or
    a class (RustParseError). This catches accidental removal or
    rename via a re-export change."""
    from furqan_lint import rust_adapter

    for name in _RUST_ADAPTER_PUBLIC_SURFACE_v0_7_0:
        obj = getattr(rust_adapter, name)
        assert callable(obj) or isinstance(
            obj, type
        ), f"rust_adapter.{name} is not callable or a class: {obj!r}"


def test_rust_adapter_public_surface_is_superset_of_v0_7_0_1_baseline() -> None:
    """v0.7.0.1 added ``RustExtrasNotInstalled`` to the surface;
    every later release must remain a superset of the v0.7.0.1
    baseline as well as the v0.7.0 baseline."""
    from furqan_lint import rust_adapter

    current = frozenset(rust_adapter.__all__)
    missing = _RUST_ADAPTER_PUBLIC_SURFACE_v0_7_0_1 - current
    assert not missing, (
        f"rust_adapter.__all__ removed names from the v0.7.0.1 baseline: "
        f"{sorted(missing)}. Removals require a major-version bump."
    )


def test_rust_adapter_public_surface_is_superset_of_v0_7_1_baseline() -> None:
    """v0.7.1 added Phase 2 R3 wiring without changing the
    rust_adapter public surface. This baseline aliases v0.7.0.1
    and must remain a subset of the current surface."""
    from furqan_lint import rust_adapter

    current = frozenset(rust_adapter.__all__)
    missing = _RUST_ADAPTER_PUBLIC_SURFACE_v0_7_1 - current
    assert not missing, (
        f"rust_adapter.__all__ removed names from the v0.7.1 baseline: "
        f"{sorted(missing)}. Removals require a major-version bump."
    )


def test_rust_adapter_public_surface_is_superset_of_v0_7_2_baseline() -> None:
    """v0.7.2 added Result-aware D11 + a dead-code regression test
    without changing the rust_adapter public surface. This baseline
    aliases v0.7.0.1 and must remain a subset of the current
    surface."""
    from furqan_lint import rust_adapter

    current = frozenset(rust_adapter.__all__)
    missing = _RUST_ADAPTER_PUBLIC_SURFACE_v0_7_2 - current
    assert not missing, (
        f"rust_adapter.__all__ removed names from the v0.7.2 baseline: "
        f"{sorted(missing)}. Removals require a major-version bump."
    )


def test_rust_adapter_public_surface_is_superset_of_v0_7_3_baseline() -> None:
    """v0.7.3 is a documentation-sweep + gate-addition corrective.
    No rust_adapter public surface change."""
    from furqan_lint import rust_adapter

    current = frozenset(rust_adapter.__all__)
    missing = _RUST_ADAPTER_PUBLIC_SURFACE_v0_7_3 - current
    assert not missing, (
        f"rust_adapter.__all__ removed names from the v0.7.3 baseline: "
        f"{sorted(missing)}. Removals require a major-version bump."
    )
