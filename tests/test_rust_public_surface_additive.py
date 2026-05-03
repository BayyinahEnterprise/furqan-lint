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

# v0.8.0 lands the Go adapter; the rust_adapter public surface
# is unchanged. Aliases v0.7.0.1.
_RUST_ADAPTER_PUBLIC_SURFACE_v0_8_0: frozenset[str] = _RUST_ADAPTER_PUBLIC_SURFACE_v0_7_0_1
# v0.8.1 ships the Go diff path; the Rust adapter surface is
# unchanged in v0.8.1 (Rust diff deferred to v0.8.2). Aliases
# v0_7_0_1 per the per-version cadence (every shipped minor and
# patch version gets a named frozenset constant, even when the
# surface is unchanged -- the constant's existence is the
# baseline, the name is the audit pin).
_RUST_ADAPTER_PUBLIC_SURFACE_v0_8_1: frozenset[str] = _RUST_ADAPTER_PUBLIC_SURFACE_v0_7_0_1
# v0.8.2 adds the additive-only Rust diff path. The new public
# name is ``extract_public_names`` (called by
# cli._check_rust_additive alongside
# furqan_lint.additive.compare_name_sets). Per the per-version
# cadence, V0_8_2 grows by exactly one name; the union form
# (vs. an explicit literal set) makes the delta textually
# visible in the source.
_RUST_ADAPTER_PUBLIC_SURFACE_v0_8_2: frozenset[str] = _RUST_ADAPTER_PUBLIC_SURFACE_v0_8_1 | {
    "extract_public_names"
}


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


def test_rust_adapter_public_surface_is_superset_of_v0_8_0_baseline() -> None:
    """v0.8.0 lands the Go adapter Phase 1; the rust_adapter
    public surface is unchanged. Baseline aliases v0.7.0.1."""
    from furqan_lint import rust_adapter

    current = frozenset(rust_adapter.__all__)
    missing = _RUST_ADAPTER_PUBLIC_SURFACE_v0_8_0 - current
    assert not missing, (
        f"rust_adapter.__all__ removed names from the v0.8.0 baseline: "
        f"{sorted(missing)}. Removals require a major-version bump."
    )


def test_rust_adapter_public_surface_is_superset_of_v0_8_1_baseline() -> None:
    """The v0.8.1 baseline (alias of v0_7_0_1; Rust diff deferred
    to v0.8.2; no rust_adapter surface change in v0.8.1) must
    remain a subset of the current surface. Removals require a
    major-version bump.
    """
    from furqan_lint import rust_adapter

    current = frozenset(rust_adapter.__all__)
    missing = _RUST_ADAPTER_PUBLIC_SURFACE_v0_8_1 - current
    assert not missing, (
        f"rust_adapter.__all__ removed names from v0.8.1 baseline: "
        f"{sorted(missing)}. Removals require a major-version bump."
    )


def test_rust_adapter_public_surface_is_superset_of_v0_8_2_baseline() -> None:
    """The v0.8.2 baseline (v0.8.1 plus extract_public_names)
    must remain a subset of the current surface. Catches any
    future removal of the Rust diff path's public entry point.
    """
    from furqan_lint import rust_adapter

    current = frozenset(rust_adapter.__all__)
    missing = _RUST_ADAPTER_PUBLIC_SURFACE_v0_8_2 - current
    assert not missing, (
        f"rust_adapter.__all__ removed names from v0.8.2 baseline: "
        f"{sorted(missing)}. Removals require a major-version bump."
    )
