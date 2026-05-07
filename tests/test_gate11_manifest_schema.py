"""Tests for Phase G11.0 T02: CASM v1.0 manifest schema.

Pin the parse-and-canonical-bytes contract against:

* deterministic canonical bytes for the same input
* key-order independence (canonical bytes invariant)
* rejection of wrong casm_version (CASM-V-001)
* rejection of unsupported language (CASM-V-001)
* rejection of reserved kinds (CASM-V-001)
* rejection of out-of-order public_surface.names (CASM-V-001)
"""

from __future__ import annotations

import pytest

rfc8785 = pytest.importorskip("rfc8785")

from furqan_lint.gate11.manifest_schema import (  # noqa: E402
    CasmSchemaError,
    Manifest,
    PublicName,
)


def _baseline_manifest_dict() -> dict:
    return {
        "casm_version": "1.0",
        "module_identity": {
            "language": "python",
            "module_path": "src/foo/bar.py",
            "module_root_hash": "sha256:" + "a" * 64,
        },
        "public_surface": {
            "names": [
                {
                    "name": "Aardvark",
                    "kind": "class",
                    "signature_fingerprint": "sha256:" + "b" * 64,
                },
                {
                    "name": "do_thing",
                    "kind": "function",
                    "signature_fingerprint": "sha256:" + "c" * 64,
                },
            ],
            "extraction_method": "ast.module-public-surface@v1.0",
            "extraction_substrate": "furqan-lint v0.10.0",
        },
        "chain": {
            "previous_manifest_hash": None,
            "chain_position": 1,
        },
        "linter_substrate_attestation": {
            "linter_name": "furqan-lint",
            "linter_version": "0.10.0",
            "checker_set_hash": "sha256:" + "d" * 64,
        },
        "trust_root": {
            "trust_root_id": "public-sigstore",
            "fulcio_url": "https://fulcio.sigstore.dev",
            "rekor_url": "https://rekor.sigstore.dev",
        },
        "issued_at": "2026-05-07T14:32:11Z",
    }


def test_canonical_bytes_are_deterministic() -> None:
    m1 = Manifest.from_dict(_baseline_manifest_dict())
    m2 = Manifest.from_dict(_baseline_manifest_dict())
    assert m1.to_canonical_bytes() == m2.to_canonical_bytes()
    assert m1 == m2


def test_canonical_bytes_invariant_under_inner_key_order() -> None:
    """Reordering keys inside inner dicts must not change canonical
    bytes (RFC 8785 sorts object keys lexicographically)."""
    a = _baseline_manifest_dict()
    b = _baseline_manifest_dict()
    # Reorder keys inside trust_root via dict reconstruction.
    b["trust_root"] = {
        "rekor_url": "https://rekor.sigstore.dev",
        "fulcio_url": "https://fulcio.sigstore.dev",
        "trust_root_id": "public-sigstore",
    }
    bytes_a = Manifest.from_dict(a).to_canonical_bytes()
    bytes_b = Manifest.from_dict(b).to_canonical_bytes()
    assert bytes_a == bytes_b


def test_rejects_wrong_casm_version() -> None:
    bad = _baseline_manifest_dict()
    bad["casm_version"] = "2.0"
    with pytest.raises(CasmSchemaError) as exc:
        Manifest.from_dict(bad)
    assert exc.value.code == "CASM-V-001"


def test_rejects_unsupported_language() -> None:
    bad = _baseline_manifest_dict()
    bad["module_identity"]["language"] = "rust"
    with pytest.raises(CasmSchemaError) as exc:
        Manifest.from_dict(bad)
    assert exc.value.code == "CASM-V-001"
    assert "rust" in str(exc.value).lower() or "python" in str(exc.value).lower()


def test_rejects_reserved_kind_alias() -> None:
    bad = _baseline_manifest_dict()
    bad["public_surface"]["names"].insert(
        0,
        {
            "name": "AAA_alias",
            "kind": "alias",
            "signature_fingerprint": "sha256:" + "e" * 64,
        },
    )
    # Re-sort to satisfy ASCII-sort precondition; the kind check
    # still fires.
    bad["public_surface"]["names"].sort(key=lambda d: d["name"])
    with pytest.raises(CasmSchemaError) as exc:
        Manifest.from_dict(bad)
    assert exc.value.code == "CASM-V-001"


def test_rejects_reserved_kind_module() -> None:
    bad = _baseline_manifest_dict()
    bad["public_surface"]["names"][0]["kind"] = "module"
    with pytest.raises(CasmSchemaError) as exc:
        Manifest.from_dict(bad)
    assert exc.value.code == "CASM-V-001"


def test_rejects_out_of_order_names() -> None:
    bad = _baseline_manifest_dict()
    bad["public_surface"]["names"] = list(reversed(bad["public_surface"]["names"]))
    with pytest.raises(CasmSchemaError) as exc:
        Manifest.from_dict(bad)
    assert exc.value.code == "CASM-V-001"
    assert "ASCII-sorted" in str(exc.value)


def test_rejects_missing_top_level_field() -> None:
    for key in (
        "casm_version",
        "module_identity",
        "public_surface",
        "chain",
        "linter_substrate_attestation",
        "trust_root",
        "issued_at",
    ):
        bad = _baseline_manifest_dict()
        del bad[key]
        with pytest.raises(CasmSchemaError) as exc:
            Manifest.from_dict(bad)
        assert exc.value.code == "CASM-V-001", f"missing {key!r} should raise CASM-V-001"


def test_rejects_invalid_module_root_hash() -> None:
    bad = _baseline_manifest_dict()
    bad["module_identity"]["module_root_hash"] = "md5:abcd"
    with pytest.raises(CasmSchemaError) as exc:
        Manifest.from_dict(bad)
    assert exc.value.code == "CASM-V-001"


def test_rejects_invalid_chain_position() -> None:
    bad = _baseline_manifest_dict()
    bad["chain"]["chain_position"] = 0
    with pytest.raises(CasmSchemaError) as exc:
        Manifest.from_dict(bad)
    assert exc.value.code == "CASM-V-001"


def test_round_trip_to_dict_and_back() -> None:
    m = Manifest.from_dict(_baseline_manifest_dict())
    d = m.to_dict()
    m2 = Manifest.from_dict(d)
    assert m == m2
    assert m.to_canonical_bytes() == m2.to_canonical_bytes()


def test_public_name_dataclass_is_frozen() -> None:
    pn = PublicName(name="x", kind="function", signature_fingerprint="sha256:f")
    with pytest.raises(Exception):  # noqa: B017
        pn.name = "y"  # type: ignore[misc]
