"""Tests for Phase G11.0 T07: bundle read/write.

Pin:

* Round-trip equivalence (write then read recovers the manifest
  bytes-equal to the original).
* Malformed JSON raises BundleParseError(CASM-V-010).
* Missing 'manifest' field raises CASM-V-010.
* Missing 'sigstore_bundle' field raises CASM-V-010.
* Manifest-schema violation inside the bundle propagates as
  CASM-V-010 (with the underlying CasmSchemaError chained).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

rfc8785 = pytest.importorskip("rfc8785")

from furqan_lint.gate11.bundle import (  # noqa: E402
    Bundle,
    BundleParseError,
)
from furqan_lint.gate11.manifest_schema import Manifest  # noqa: E402


def _baseline_manifest_dict() -> dict:
    return {
        "casm_version": "1.0",
        "module_identity": {
            "language": "python",
            "module_path": "src/foo.py",
            "module_root_hash": "sha256:" + "a" * 64,
        },
        "public_surface": {
            "names": [
                {
                    "name": "alpha",
                    "kind": "function",
                    "signature_fingerprint": "sha256:" + "b" * 64,
                }
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
            "checker_set_hash": "sha256:" + "c" * 64,
        },
        "trust_root": {
            "trust_root_id": "public-sigstore",
            "fulcio_url": "https://fulcio.sigstore.dev",
            "rekor_url": "https://rekor.sigstore.dev",
        },
        "issued_at": "2026-05-07T14:32:11Z",
    }


def test_round_trip_equivalence(tmp_path: Path) -> None:
    manifest = Manifest.from_dict(_baseline_manifest_dict())
    bundle = Bundle(
        manifest=manifest,
        sigstore_bundle={"signature": "fake", "certificate": "fake"},
    )
    out = tmp_path / "foo.furqan.manifest.sigstore"
    bundle.write(out)
    re_read = Bundle.read(out)
    assert re_read.manifest.to_canonical_bytes() == manifest.to_canonical_bytes()
    assert re_read.sigstore_bundle == {"signature": "fake", "certificate": "fake"}


def test_malformed_json_raises_casm_v_010(tmp_path: Path) -> None:
    p = tmp_path / "bad.furqan.manifest.sigstore"
    p.write_text("{ not valid json", encoding="utf-8")
    with pytest.raises(BundleParseError) as exc:
        Bundle.read(p)
    assert exc.value.code == "CASM-V-010"


def test_missing_manifest_field_raises_casm_v_010(tmp_path: Path) -> None:
    p = tmp_path / "x.furqan.manifest.sigstore"
    p.write_text(json.dumps({"sigstore_bundle": {}}), encoding="utf-8")
    with pytest.raises(BundleParseError) as exc:
        Bundle.read(p)
    assert exc.value.code == "CASM-V-010"
    assert "manifest" in str(exc.value)


def test_missing_sigstore_bundle_field_raises_casm_v_010(tmp_path: Path) -> None:
    p = tmp_path / "x.furqan.manifest.sigstore"
    p.write_text(
        json.dumps({"manifest": _baseline_manifest_dict()}),
        encoding="utf-8",
    )
    with pytest.raises(BundleParseError) as exc:
        Bundle.read(p)
    assert exc.value.code == "CASM-V-010"
    assert "sigstore_bundle" in str(exc.value)


def test_manifest_schema_violation_chains_as_casm_v_010(
    tmp_path: Path,
) -> None:
    bad = _baseline_manifest_dict()
    bad["casm_version"] = "2.0"  # CASM-V-001 from manifest_schema
    p = tmp_path / "x.furqan.manifest.sigstore"
    p.write_text(
        json.dumps({"manifest": bad, "sigstore_bundle": {}}),
        encoding="utf-8",
    )
    with pytest.raises(BundleParseError) as exc:
        Bundle.read(p)
    # Bundle parse-error code is CASM-V-010; the underlying
    # manifest schema error (CASM-V-001) is in the chain.
    assert exc.value.code == "CASM-V-010"
    assert "CASM-V-001" in str(exc.value)


def test_top_level_not_an_object_raises_casm_v_010(tmp_path: Path) -> None:
    p = tmp_path / "x.furqan.manifest.sigstore"
    p.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    with pytest.raises(BundleParseError) as exc:
        Bundle.read(p)
    assert exc.value.code == "CASM-V-010"


def test_bundle_extension_canonical(tmp_path: Path) -> None:
    """The bundle suffix is .furqan.manifest.sigstore per the
    deliverable scope. Test that we can write to that path and
    that the .sigstore tail is preserved verbatim."""
    from furqan_lint.gate11 import GATE11_BUNDLE_SUFFIX

    assert GATE11_BUNDLE_SUFFIX == ".furqan.manifest.sigstore"
    manifest = Manifest.from_dict(_baseline_manifest_dict())
    bundle = Bundle(manifest=manifest, sigstore_bundle={})
    p = tmp_path / f"foo{GATE11_BUNDLE_SUFFIX}"
    bundle.write(p)
    assert p.exists()
    assert p.name.endswith(".sigstore")
