"""Per-version snapshot of furqan_lint.go_adapter.__all__ (v0.8.0).

Establishes the additive-only discipline for the go_adapter
subpackage, parallel to the v0.7.0 rust_adapter snapshot. Per
Bayyinah Engineering Discipline Framework v2.0 §7.6 per-version
cadence: every shipped minor and patch version gets a named
frozenset constant.

The v0.8.0 baseline is the package's first shipped surface:
{parse_file, GoExtrasNotInstalled, GoParseError}. Future versions
must remain a superset; removals require a major-version bump.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


# v0.8.0 ships the Go adapter Phase 1 as a new subpackage. The
# initial public surface is exactly the parse_file entry point
# plus the two typed exceptions the CLI catches.
_GO_ADAPTER_PUBLIC_SURFACE_v0_8_0: frozenset[str] = frozenset(
    {
        "parse_file",
        "GoExtrasNotInstalled",
        "GoParseError",
    }
)


# v0.8.1 adds the additive-only Go diff path. The new public
# name is ``extract_public_names`` (called by cli._check_go_additive
# alongside furqan_lint.additive.compare_name_sets). Per the
# per-version cadence, V0_8_1 grows by exactly one name; the
# union form (vs. an explicit literal set) makes the delta
# textually visible in the source.
_GO_ADAPTER_PUBLIC_SURFACE_v0_8_1: frozenset[str] = _GO_ADAPTER_PUBLIC_SURFACE_v0_8_0 | {
    "extract_public_names"
}


def test_go_adapter_public_surface_is_superset_of_v0_8_0_baseline() -> None:
    """The v0.8.0 baseline must remain a subset of the current
    surface. If a future release removes any v0.8.0 baseline
    name, this test fails and the change requires a major-version
    bump per the additive-only discipline."""
    from furqan_lint import go_adapter

    current = frozenset(go_adapter.__all__)
    missing = _GO_ADAPTER_PUBLIC_SURFACE_v0_8_0 - current
    assert not missing, (
        f"go_adapter.__all__ removed names from the v0.8.0 baseline: "
        f"{sorted(missing)}. Removals require a major-version bump."
    )


def test_go_adapter_baseline_names_are_callable_or_class() -> None:
    """Each baseline name must resolve to a callable (function)
    or a class (the typed exceptions). Catches accidental removal
    or rename via a re-export change."""
    from furqan_lint import go_adapter

    for name in _GO_ADAPTER_PUBLIC_SURFACE_v0_8_0:
        obj = getattr(go_adapter, name)
        assert callable(obj) or isinstance(
            obj, type
        ), f"go_adapter.{name} is not callable or a class: {obj!r}"


def test_go_adapter_public_surface_is_superset_of_v0_8_1_baseline() -> None:
    """The v0.8.1 baseline (v0.8.0 plus extract_public_names)
    must remain a subset of the current surface. Catches any
    future removal of the Go diff path's public entry point.
    """
    from furqan_lint import go_adapter

    current = frozenset(go_adapter.__all__)
    missing = _GO_ADAPTER_PUBLIC_SURFACE_v0_8_1 - current
    assert not missing, (
        f"go_adapter.__all__ removed names from the v0.8.1 baseline: "
        f"{sorted(missing)}. Removals require a major-version bump."
    )
