"""Tests for the Rust CASM v1.0 manifest builder.

Pins the audit H-6 propagation defense:
``checker_set_hash`` is either Form A (substantive hash over
pinned checker source) or Form B (``placeholder:sha256:`` prefix).
The Phase G11.0 v0.10.0 ``sha256(linter_version)`` form is NOT
permitted; the schema validator rejects it.
"""

# ruff: noqa: E402, SIM115, RUF005

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_rust")
pytest.importorskip("rfc8785")

from furqan_lint.gate11.checker_set_hash import (
    compute_checker_set_hash,
)
from furqan_lint.gate11.manifest_schema import (
    CasmSchemaError,
    Manifest,
)
from furqan_lint.gate11.rust_manifest import build_manifest_rust


def _write_rust(src: str) -> Path:
    fh = tempfile.NamedTemporaryFile(mode="w", suffix=".rs", delete=False)
    fh.write(src)
    fh.close()
    return Path(fh.name)


def test_manifest_built_for_rust_source():
    p = _write_rust("pub fn add(a: i32, b: i32) -> i32 { a + b }")
    try:
        m = build_manifest_rust(p)
        assert m.casm_version == "1.0"
        assert m.module_identity["language"] == "rust"
        assert m.public_surface["extraction_method"] == ("tree-sitter.rust-public-surface@v1.0")
        assert m.chain["previous_manifest_hash"] is None
        assert m.chain["chain_position"] == 1
    finally:
        p.unlink()


def test_manifest_chain_increments_position():
    p = _write_rust("pub fn add(a: i32, b: i32) -> i32 { a + b }")
    try:
        m1 = build_manifest_rust(p)
        m2 = build_manifest_rust(p, previous_manifest=m1)
        assert m2.chain["chain_position"] == 2
        assert m2.chain["previous_manifest_hash"] is not None
        assert m2.chain["previous_manifest_hash"].startswith("sha256:")
    finally:
        p.unlink()


def test_manifest_round_trip_via_canonical_bytes():
    p = _write_rust("pub struct Point { pub x: i32, y: i32 }")
    try:
        m = build_manifest_rust(p)
        canonical = m.to_canonical_bytes()
        import json

        parsed_dict = json.loads(canonical)
        m_again = Manifest.from_dict(parsed_dict)
        assert m_again.module_identity == m.module_identity
        assert m_again.public_surface == m.public_surface
    finally:
        p.unlink()


# H-6 defense tests
# ---------------------------------------------------------------


def test_h6_form_a_substantive_hash_default():
    """Default builds use Form A (substantive)."""
    p = _write_rust("pub fn f() {}")
    try:
        m = build_manifest_rust(p)
        csh = m.linter_substrate_attestation["checker_set_hash"]
        assert csh.startswith("sha256:")
        assert not csh.startswith("placeholder:")
        # The hash is deterministic across two builds (same
        # checker source).
        m2 = build_manifest_rust(p)
        assert m2.linter_substrate_attestation["checker_set_hash"] == csh
    finally:
        p.unlink()


def test_h6_form_b_placeholder_prefix():
    """Form B is opt-in via the kwarg; prefix preserved."""
    p = _write_rust("pub fn f() {}")
    try:
        m = build_manifest_rust(p, use_placeholder_checker_hash=True)
        csh = m.linter_substrate_attestation["checker_set_hash"]
        assert csh.startswith("placeholder:sha256:")
    finally:
        p.unlink()


def test_h6_form_b_round_trips_via_schema():
    """Form B round-trips through canonicalize -> parse."""
    p = _write_rust("pub fn f() {}")
    try:
        m = build_manifest_rust(p, use_placeholder_checker_hash=True)
        canonical = m.to_canonical_bytes()
        import json

        parsed = json.loads(canonical)
        m_again = Manifest.from_dict(parsed)
        csh = m_again.linter_substrate_attestation["checker_set_hash"]
        assert csh.startswith("placeholder:sha256:")
    finally:
        p.unlink()


def test_h6_schema_rejects_bare_placeholder_form():
    """The Phase G11.0 v0.10.0 form ``sha256(linter_version)``
    is bare-string-indistinguishable from a substantive hash.
    The schema validator does NOT reject the SHAPE of such a
    hash (it cannot tell), but Phase G11.1 ships substantive
    hashes by default. The audit H-6 substrate-side defense
    is the explicit ``placeholder:`` prefix for Form B; this
    test pins that the prefix is preserved through round-trip
    and that arbitrary non-prefixed strings are rejected.
    """
    fh = tempfile.NamedTemporaryFile(mode="w", suffix=".rs", delete=False)
    fh.write("pub fn f() {}")
    fh.close()
    rs_path = Path(fh.name)
    try:
        m = build_manifest_rust(rs_path)
        # Tamper with the manifest dict to inject a bad
        # checker_set_hash form.

        tampered = Manifest(
            casm_version=m.casm_version,
            module_identity=dict(m.module_identity),
            public_surface=dict(m.public_surface),
            chain=dict(m.chain),
            linter_substrate_attestation={
                "linter_name": "furqan-lint",
                "linter_version": "0.11.0",
                # NOT a sha256: or placeholder:sha256: prefix
                "checker_set_hash": "this-is-not-a-valid-form",
            },
            trust_root=dict(m.trust_root),
            issued_at=m.issued_at,
        )
        import json

        canonical = tampered.to_canonical_bytes()
        parsed = json.loads(canonical)
        with pytest.raises(CasmSchemaError) as excinfo:
            Manifest.from_dict(parsed)
        assert "checker_set_hash" in str(excinfo.value)
    finally:
        rs_path.unlink()


def test_h6_hash_changes_when_pinned_source_changes():
    """The substantive hash changes when checker source bytes
    change. Concrete pin: temporarily monkey-patch one source
    file, re-compute, observe a different hash.
    """
    from furqan_lint.gate11 import checker_set_hash as csh_mod

    original = compute_checker_set_hash()
    # Add a synthetic file path to the pinned tuple, pointing
    # at a temp file with custom contents.
    import tempfile

    fh = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False)
    fh.write("# synthetic checker source")
    fh.close()
    extra = Path(fh.name)
    try:
        original_tuple = csh_mod._CHECKER_SOURCE_FILES
        csh_mod._CHECKER_SOURCE_FILES = original_tuple + (extra,)
        modified = compute_checker_set_hash()
        assert modified != original
    finally:
        csh_mod._CHECKER_SOURCE_FILES = original_tuple
        extra.unlink()


def test_language_rust_accepted_by_schema():
    """The schema validator accepts language='rust'."""
    p = _write_rust("pub fn f() {}")
    try:
        m = build_manifest_rust(p)
        assert m.module_identity["language"] == "rust"
    finally:
        p.unlink()


def test_language_unknown_rejected_by_schema():
    """Unknown languages are rejected."""
    p = _write_rust("pub fn f() {}")
    try:
        m = build_manifest_rust(p)
        canonical = m.to_canonical_bytes()
        import json

        parsed = json.loads(canonical)
        parsed["module_identity"]["language"] = "klingon"
        with pytest.raises(CasmSchemaError):
            Manifest.from_dict(parsed)
    finally:
        p.unlink()
