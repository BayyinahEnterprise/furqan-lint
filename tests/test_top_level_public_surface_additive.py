"""Per-version snapshots of the top-level ``furqan_lint.__all__``
public surface (v0.7.1).

Establishes the additive-only discipline for the top-level
package, parallel to the v0.7.0
``test_rust_public_surface_additive.py`` for the rust subpackage.
Per Bayyinah Engineering Discipline Framework section 7.6
(per-version cadence), every shipped minor and patch version gets
a named frozenset constant. Versions where the surface is
unchanged are explicit aliases of the prior version's snapshot,
with comments naming what changed (or didn't), so that future
drift surfaces in the diff at the named version, not in an
aggregate "everything since vX" snapshot.

Round-11's MEDIUM 3 finding on Bayyinah was exactly the failure
mode that pinning only the latest version creates; v0.7.1
establishes the pattern correctly from the start.

Each baseline asserts SUBSET-of-current. Future versions may
extend the surface; they may not remove from it without a major
version bump.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


# v0.7.0 shipped without an explicit ``__all__`` declaration; the
# implicit surface (after excluding dunders) was {"__version__"}.
# The dunders ``__version__``, ``__name__``, ``__doc__``, etc.
# excluded the latter three by convention. v0.7.1 adds the
# explicit declaration that pins the surface to {"__version__"}.
# Recording the v0.7.0 snapshot here is honest accounting, not
# retroactive claiming: we observed the surface empirically before
# the explicit declaration was added.
V0_7_0_SURFACE: frozenset[str] = frozenset({"__version__"})

# v0.7.0.1 was a corrective release; no surface change.
V0_7_0_1_SURFACE: frozenset[str] = V0_7_0_SURFACE

# v0.7.1 adds Phase 2 R3 wiring and retires two documented
# limits, but does not change the top-level public surface. The
# additive-only test infrastructure itself lands in this release.
# Any future v0.7.x or v0.8 may extend the surface; this snapshot
# pins the v0.7.1 baseline as a subset for those extensions to
# remain consistent with.
V0_7_1_SURFACE: frozenset[str] = V0_7_0_SURFACE

# v0.7.2 adds Result-aware D11 plus the dead-code regression test
# but does not change the top-level public surface. Aliases
# V0_7_0_SURFACE per the per-version cadence (every shipped
# version gets a named constant, even when the surface is
# unchanged).
V0_7_2_SURFACE: frozenset[str] = V0_7_0_SURFACE

# v0.7.3 was a documentation-sweep + release-sweep-gate corrective;
# no top-level public surface change. Aliases V0_7_0_SURFACE per
# the per-version cadence.
V0_7_3_SURFACE: frozenset[str] = V0_7_0_SURFACE

# v0.8.0 lands the Go adapter Phase 1 but does not change the
# top-level public surface (the new go_adapter package is its
# own subpackage with its own snapshot test). Aliases V0_7_0_SURFACE.
V0_8_0_SURFACE: frozenset[str] = V0_7_0_SURFACE
# v0.8.1 adds the Go additive-only diff path. The new public
# entry point is in the go_adapter subpackage
# (extract_public_names); the top-level furqan_lint surface
# is unchanged. Aliases V0_7_0_SURFACE per the per-version
# cadence.
V0_8_1_SURFACE: frozenset[str] = V0_7_0_SURFACE
# v0.8.2 adds the Rust additive-only diff and goast qualified
# method names. Both changes live in subpackage / binary
# layers; the top-level furqan_lint surface is unchanged.
# Aliases V0_7_0_SURFACE per the per-version cadence.
V0_8_2_SURFACE: frozenset[str] = V0_7_0_SURFACE
# v0.8.3 corrective release: Rust diff parse-error gate, goast
# IndexListExpr, impl-methods documented limit, two automated
# gates, two backfilled Rust pins. None of these touch the
# top-level furqan_lint surface (all changes live in
# subpackage / binary / test layers). Aliases V0_7_0_SURFACE.
V0_8_3_SURFACE: frozenset[str] = V0_7_0_SURFACE


def _current_surface() -> frozenset[str]:
    """Return the current ``furqan_lint.__all__`` as a frozenset.

    Reads ``__all__`` directly rather than ``dir(furqan_lint)`` so
    accidental module-level bindings do not silently extend the
    advertised surface; only the explicit declaration counts.
    """
    import furqan_lint

    return frozenset(furqan_lint.__all__)


def test_v0_7_0_surface_is_subset_of_current() -> None:
    """The v0.7.0 baseline must remain a subset of the current
    surface. If a future release removes ``__version__`` (or any
    other v0.7.0 baseline name), this test fails and the change
    requires a major-version bump per the additive-only
    discipline."""
    current = _current_surface()
    missing = V0_7_0_SURFACE - current
    assert not missing, (
        f"furqan_lint.__all__ removed names from the v0.7.0 baseline: "
        f"{sorted(missing)}. Removals require a major-version bump."
    )


def test_v0_7_0_1_surface_is_subset_of_current() -> None:
    """The v0.7.0.1 baseline (alias of v0.7.0; no surface change in
    the corrective release) must remain a subset of the current
    surface."""
    current = _current_surface()
    missing = V0_7_0_1_SURFACE - current
    assert not missing, (
        f"furqan_lint.__all__ removed names from the v0.7.0.1 baseline: "
        f"{sorted(missing)}. Removals require a major-version bump."
    )


def test_v0_7_1_surface_is_subset_of_current() -> None:
    """The v0.7.1 baseline (alias of v0.7.0; no surface change in
    this release) must remain a subset of the current surface."""
    current = _current_surface()
    missing = V0_7_1_SURFACE - current
    assert not missing, (
        f"furqan_lint.__all__ removed names from the v0.7.1 baseline: "
        f"{sorted(missing)}. Removals require a major-version bump."
    )


def test_current_surface_is_not_empty() -> None:
    """The current surface must declare at least one name. An
    empty ``__all__`` would silently make the package
    non-importable-by-name (``from furqan_lint import *`` would
    bind nothing) and is almost always a mistake."""
    current = _current_surface()
    assert current, "furqan_lint.__all__ is empty"


def test_v0_7_2_surface_is_subset_of_current() -> None:
    """The v0.7.2 baseline (alias of v0.7.0; no surface change in
    this release) must remain a subset of the current surface."""
    current = _current_surface()
    missing = V0_7_2_SURFACE - current
    assert not missing, (
        f"furqan_lint.__all__ removed names from the v0.7.2 baseline: "
        f"{sorted(missing)}. Removals require a major-version bump."
    )


def test_v0_7_3_surface_is_subset_of_current() -> None:
    """The v0.7.3 baseline (alias of v0.7.0; documentation-sweep
    corrective; no surface change) must remain a subset of the
    current surface. Round-18 audit caught that v0.7.3's release
    commit body claimed this snapshot existed; v0.7.4 corrective
    backfills the omission."""
    current = _current_surface()
    missing = V0_7_3_SURFACE - current
    assert not missing, (
        f"furqan_lint.__all__ removed names from the v0.7.3 baseline: "
        f"{sorted(missing)}. Removals require a major-version bump."
    )


def test_v0_8_0_surface_is_subset_of_current() -> None:
    """The v0.8.0 baseline (alias of V0_7_0_SURFACE; Go adapter
    Phase 1 lands as a new subpackage with its own snapshot, no
    top-level public surface change) must remain a subset of the
    current surface."""
    current = _current_surface()
    missing = V0_8_0_SURFACE - current
    assert not missing, (
        f"furqan_lint.__all__ removed names from the v0.8.0 baseline: "
        f"{sorted(missing)}. Removals require a major-version bump."
    )


def test_v0_8_1_surface_is_subset_of_current() -> None:
    """The v0.8.1 baseline (alias of V0_7_0_SURFACE; the Go diff
    path's public entry lives in furqan_lint.go_adapter, not at
    the top level) must remain a subset of the current
    furqan_lint.__all__. Catches accidental top-level surface
    removal.
    """
    import furqan_lint

    current = frozenset(furqan_lint.__all__)
    missing = V0_8_1_SURFACE - current
    assert not missing, (
        f"furqan_lint.__all__ removed names from V0_8_1_SURFACE: "
        f"{sorted(missing)}. Removals require a major-version bump."
    )


def test_v0_8_2_surface_is_subset_of_current() -> None:
    """The v0.8.2 baseline (alias of V0_7_0_SURFACE; the Rust
    diff path's public entry lives in furqan_lint.rust_adapter,
    not at the top level; the goast method-name change is in
    the bundled binary's emit format, not Python __all__) must
    remain a subset of the current furqan_lint.__all__.
    """
    import furqan_lint

    current = frozenset(furqan_lint.__all__)
    missing = V0_8_2_SURFACE - current
    assert not missing, (
        f"furqan_lint.__all__ removed names from V0_8_2_SURFACE: "
        f"{sorted(missing)}. Removals require a major-version bump."
    )


def test_v0_8_3_surface_is_subset_of_current() -> None:
    """The v0.8.3 baseline (alias of V0_7_0_SURFACE; the v0.8.3
    changes are corrective + gates, none touching the top-level
    surface) must remain a subset of the current
    furqan_lint.__all__.
    """
    import furqan_lint

    current = frozenset(furqan_lint.__all__)
    missing = V0_8_3_SURFACE - current
    assert not missing, (
        f"furqan_lint.__all__ removed names from V0_8_3_SURFACE: "
        f"{sorted(missing)}. Removals require a major-version bump."
    )
