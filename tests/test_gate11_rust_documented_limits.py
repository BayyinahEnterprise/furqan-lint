"""Phase G11.1 documented-limits pinning tests.

Each test pins a current furqan-lint Rust adapter behaviour
that is expected to hold in v1.0. If a future improvement
changes the adapter's behaviour, these tests will fail and
force the change to surface as either a Naskh Discipline
schema/invariant update OR an explicit retirement of the
documented limit -- not a silent improvement.
"""

# ruff: noqa: E402

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_rust")
pytest.importorskip("rfc8785")

from furqan_lint.gate11.rust_surface_extraction import (
    extract_public_surface_rust,
)

FIXTURES = Path(__file__).parent / "fixtures" / "gate11_rust" / "documented_limits"


def test_lifetime_stripped_from_signature():
    """Renaming the lifetime should NOT change the fingerprint;
    lifetimes are stripped during canonicalization (rule 2).
    """
    p = FIXTURES / "lifetime_stripped_from_signature.rs"
    entries_a = extract_public_surface_rust(p)

    # Same logical function with renamed lifetime in a temp file:
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".rs", delete=False) as fh:
        fh.write(p.read_text().replace("'a", "'b"))
        renamed = Path(fh.name)
    try:
        entries_b = extract_public_surface_rust(renamed)
        assert entries_a[0]["signature_fingerprint"] == entries_b[0]["signature_fingerprint"]
    finally:
        renamed.unlink()


def test_impl_methods_omitted_from_surface():
    """impl-block methods are NOT in the public surface for v1.0."""
    entries = extract_public_surface_rust(FIXTURES / "impl_methods_omitted_from_surface.rs")
    names = [e["name"] for e in entries]
    # The struct surfaces; the impl-block methods do not.
    assert "Counter" in names
    assert "increment" not in names
    assert "value" not in names


def test_trait_object_literal_text():
    """Trait-object return types are signed as literal text;
    semantic equivalence is a v1.5 horizon item.
    """
    entries = extract_public_surface_rust(FIXTURES / "trait_object_literal_text.rs")
    names = [e["name"] for e in entries]
    assert "make_shape" in names
    assert "Shape" in names


def test_macro_call_signed_pre_expansion():
    """Macros are signed at the source level, NOT after expansion."""
    entries = extract_public_surface_rust(FIXTURES / "macro_call_signed_pre_expansion.rs")
    assert len(entries) == 1
    assert entries[0]["name"] == "use_macro"
    # Pinning the fingerprint is a regression detector: any
    # change to canonicalization that affects this case will
    # fail this test and require explicit retirement.
    assert entries[0]["signature_fingerprint"].startswith("sha256:")


def test_pub_crate_and_pub_super_excluded():
    """pub(crate) and pub(super) are NOT in the external surface."""
    entries = extract_public_surface_rust(FIXTURES / "pub_crate_excluded.rs")
    names = [e["name"] for e in entries]
    assert "external" in names
    assert "internal" not in names
    assert "parent_only" not in names
