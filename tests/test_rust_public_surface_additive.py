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
