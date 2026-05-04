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
# v0.8.2 changes goast's qualified method-name emission and the
# CLI's Rust diff path. The go_adapter Python __all__ surface is
# unchanged in v0.8.2 (the goast emit-format change is a behavior
# refinement, not a public-surface change). Aliases v0_8_1 per
# the per-version cadence.
_GO_ADAPTER_PUBLIC_SURFACE_v0_8_2: frozenset[str] = _GO_ADAPTER_PUBLIC_SURFACE_v0_8_1
# v0.8.3 corrective: goast IndexListExpr added (binary emit-
# format refinement, not a Python __all__ change). Aliases
# v0_8_2 per the per-version cadence.
_GO_ADAPTER_PUBLIC_SURFACE_v0_8_3: frozenset[str] = _GO_ADAPTER_PUBLIC_SURFACE_v0_8_2
# v0.8.4 corrective: round-22 patch sweeps two go_adapter
# docstrings (no surface change), patches PARSE ERROR
# diagnostic filename, lands three CI gates and the release
# workflow. No go_adapter __all__ change. Aliases v0.8.3.
_GO_ADAPTER_PUBLIC_SURFACE_v0_8_4: frozenset[str] = _GO_ADAPTER_PUBLIC_SURFACE_v0_8_3
# v0.8.5 attribution-corrective: documentation-only release.
# No go_adapter __all__ change. Aliases v0.8.4.
_GO_ADAPTER_PUBLIC_SURFACE_v0_8_5: frozenset[str] = _GO_ADAPTER_PUBLIC_SURFACE_v0_8_4


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


def test_go_adapter_public_surface_is_superset_of_v0_8_2_baseline() -> None:
    """The v0.8.2 baseline (alias of v0_8_1; goast emission
    change is internal, no Go __all__ change in v0.8.2) must
    remain a subset of the current surface.
    """
    from furqan_lint import go_adapter

    current = frozenset(go_adapter.__all__)
    missing = _GO_ADAPTER_PUBLIC_SURFACE_v0_8_2 - current
    assert not missing, (
        f"go_adapter.__all__ removed names from v0.8.2 baseline: "
        f"{sorted(missing)}. Removals require a major-version bump."
    )


def test_go_adapter_public_surface_is_superset_of_v0_8_3_baseline() -> None:
    """The v0.8.3 baseline (alias of v0_8_2; goast IndexListExpr
    is a binary emit-format refinement, not a Python public-
    surface change).
    """
    from furqan_lint import go_adapter

    current = frozenset(go_adapter.__all__)
    missing = _GO_ADAPTER_PUBLIC_SURFACE_v0_8_3 - current
    assert not missing, (
        f"go_adapter.__all__ removed names from v0.8.3 baseline: "
        f"{sorted(missing)}. Removals require a major-version bump."
    )


def test_go_adapter_public_surface_is_superset_of_v0_8_4_baseline() -> None:
    """The v0.8.4 baseline (alias of v0_8_3; the round-22
    corrective sweeps two go_adapter docstrings and lands
    PARSE ERROR diagnostic + CI gates + release workflow,
    none of which change the go_adapter __all__ surface).
    """
    from furqan_lint import go_adapter

    current = frozenset(go_adapter.__all__)
    missing = _GO_ADAPTER_PUBLIC_SURFACE_v0_8_4 - current
    assert not missing, (
        f"go_adapter.__all__ removed names from v0.8.4 baseline: "
        f"{sorted(missing)}. Removals require a major-version bump."
    )


def test_go_adapter_public_surface_is_superset_of_v0_8_5_baseline() -> None:
    """The v0.8.5 baseline (alias of v0_8_4; the v0.8.5
    attribution-corrective is a documentation-only release
    that does not change the go_adapter __all__ surface).
    """
    from furqan_lint import go_adapter

    current = frozenset(go_adapter.__all__)
    missing = _GO_ADAPTER_PUBLIC_SURFACE_v0_8_5 - current
    assert not missing, (
        f"go_adapter.__all__ removed names from v0.8.5 baseline: "
        f"{sorted(missing)}. Removals require a major-version bump."
    )
