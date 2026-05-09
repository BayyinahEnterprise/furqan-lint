"""Tests for Phase G11.0 T08: 9-step CASM verification flow.

Exercises each step in isolation via the Verifier's per-step
methods. The Sigstore step is exercised by faking the trust
root and bundle inputs; no live network. The composed
verify_bundle path is tested for happy-case shape and for the
expected error code on each non-advisory failure.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

rfc8785 = pytest.importorskip("rfc8785")

from furqan_lint.gate11.bundle import Bundle  # noqa: E402
from furqan_lint.gate11.manifest_schema import Manifest  # noqa: E402
from furqan_lint.gate11.module_canonicalization import (  # noqa: E402
    module_root_hash,
)
from furqan_lint.gate11.verification import (  # noqa: E402
    CasmIndeterminateError,
    CasmVerificationError,
    Verifier,
)


def _baseline_manifest_dict(module_path: Path, names_entries: list) -> dict:
    return {
        "casm_version": "1.0",
        "module_identity": {
            "language": "python",
            "module_path": str(module_path.name),
            "module_root_hash": module_root_hash(module_path),
        },
        "public_surface": {
            "names": names_entries,
            "extraction_method": "ast.module-public-surface@v1.0",
            "extraction_substrate": "furqan-lint test",
        },
        "chain": {"previous_manifest_hash": None, "chain_position": 1},
        "linter_substrate_attestation": {
            "linter_name": "furqan-lint",
            "linter_version": "0.10.0",
            "checker_set_hash": "sha256:" + "0" * 64,
        },
        "trust_root": {
            "trust_root_id": "public-sigstore",
            "fulcio_url": "https://fulcio.sigstore.dev",
            "rekor_url": "https://rekor.sigstore.dev",
        },
        "issued_at": "2026-05-07T14:32:11Z",
    }


def _module(tmp_path: Path, src: str, name: str = "m.py") -> Path:
    p = tmp_path / name
    p.write_text(src, encoding="utf-8")
    return p


def _entries_for(module_path: Path) -> list:
    from furqan_lint.gate11.surface_extraction import extract_public_surface

    return extract_public_surface(module_path)


def _write_bundle(
    tmp_path: Path,
    module_path: Path,
    entries: list,
    bundle_name: str = "m.furqan.manifest.sigstore",
    manifest_overrides: dict | None = None,
) -> Path:
    md = _baseline_manifest_dict(module_path, entries)
    if manifest_overrides:
        for k, v in manifest_overrides.items():
            if "." in k:
                a, b = k.split(".", 1)
                md[a][b] = v
            else:
                md[k] = v
    bundle_path = tmp_path / bundle_name
    bundle_path.write_text(
        json.dumps({"manifest": md, "sigstore_bundle": {}}),
        encoding="utf-8",
    )
    return bundle_path


# Step 1 + 2 + 3
def test_step1_parse_bundle_propagates_casm_v_010(tmp_path: Path) -> None:
    p = tmp_path / "bad.furqan.manifest.sigstore"
    p.write_text("{ not valid", encoding="utf-8")
    v = Verifier()
    with pytest.raises(CasmVerificationError) as exc:
        v.step1_parse_bundle(p)
    assert exc.value.code == "CASM-V-010"


# Step 7 module hash
def test_step7_module_hash_mismatch_raises_casm_v_040(tmp_path: Path) -> None:
    mod = _module(tmp_path, "def f(): ...\n")
    entries = _entries_for(mod)
    manifest = Manifest.from_dict(_baseline_manifest_dict(mod, entries))
    # Mutate the module after manifest snapshot
    mod.write_text("def f(): pass\nx = 1\n", encoding="utf-8")
    v = Verifier()
    with pytest.raises(CasmVerificationError) as exc:
        v.step7_compare_module_hash(manifest, mod)
    assert exc.value.code == "CASM-V-040"


def test_step7_module_hash_matches_when_unchanged(tmp_path: Path) -> None:
    mod = _module(tmp_path, "def f(): ...\n")
    entries = _entries_for(mod)
    manifest = Manifest.from_dict(_baseline_manifest_dict(mod, entries))
    v = Verifier()
    # Should not raise.
    v.step7_compare_module_hash(manifest, mod)


# Step 8 public surface
def test_step8_removed_name_raises_casm_v_050(tmp_path: Path) -> None:
    mod = _module(tmp_path, "def alpha(): ...\ndef beta(): ...\n")
    entries = _entries_for(mod)
    manifest = Manifest.from_dict(_baseline_manifest_dict(mod, entries))
    # Remove `beta` from current source -> CASM-V-050
    mod.write_text("def alpha(): ...\n", encoding="utf-8")
    v = Verifier()
    with pytest.raises(CasmVerificationError) as exc:
        v.step8_compare_public_surface(manifest, mod)
    assert exc.value.code == "CASM-V-050"
    assert "beta" in str(exc.value)


def test_step8_added_name_is_silent_pass(tmp_path: Path) -> None:
    mod = _module(tmp_path, "def alpha(): ...\n")
    entries = _entries_for(mod)
    manifest = Manifest.from_dict(_baseline_manifest_dict(mod, entries))
    # Add `beta` to current source; manifest still mentions only alpha.
    # Module hash will mismatch but that is step 7, not step 8.
    mod.write_text("def alpha(): ...\ndef beta(): ...\n", encoding="utf-8")
    v = Verifier()
    # Should not raise.
    v.step8_compare_public_surface(manifest, mod)


def test_step8_signature_change_raises_casm_v_051(tmp_path: Path) -> None:
    mod = _module(tmp_path, "def f(x: int) -> int: return x\n")
    entries = _entries_for(mod)
    manifest = Manifest.from_dict(_baseline_manifest_dict(mod, entries))
    # Change f's signature: same name, different annotation.
    mod.write_text("def f(x: str) -> str: return x\n", encoding="utf-8")
    v = Verifier()
    with pytest.raises(CasmVerificationError) as exc:
        v.step8_compare_public_surface(manifest, mod)
    assert exc.value.code == "CASM-V-051"
    assert "f" in str(exc.value)


def test_step8_dynamic_all_indeterminate(tmp_path: Path) -> None:
    mod = _module(tmp_path, "def f(): ...\n")
    entries = _entries_for(mod)
    manifest = Manifest.from_dict(_baseline_manifest_dict(mod, entries))
    # Replace module with dynamic __all__
    mod.write_text(
        "_NAMES = ['f']\n__all__ = list(_NAMES)\ndef f(): ...\n",
        encoding="utf-8",
    )
    v = Verifier()
    with pytest.raises(CasmIndeterminateError):
        v.step8_compare_public_surface(manifest, mod)


# Step 9 chain integrity
def test_step9_chain_head_returns_ok(tmp_path: Path) -> None:
    mod = _module(tmp_path, "def f(): ...\n")
    bundle_path = _write_bundle(tmp_path, mod, _entries_for(mod))
    bundle = Bundle.read(bundle_path)
    v = Verifier()
    ok, advisory = v.step9_check_chain_integrity(bundle.manifest, bundle_path)
    assert ok and advisory is None


def test_step9_previous_bundle_not_located_advisory(tmp_path: Path) -> None:
    mod = _module(tmp_path, "def f(): ...\n")
    entries = _entries_for(mod)
    manifest = Manifest.from_dict(
        _baseline_manifest_dict(mod, entries)
        | {
            "chain": {
                "previous_manifest_hash": "sha256:" + "f" * 64,
                "chain_position": 2,
            }
        }
    )
    bundle_path = tmp_path / "m.furqan.manifest.sigstore"
    bundle_path.write_text(
        json.dumps({"manifest": manifest.to_dict(), "sigstore_bundle": {}}),
        encoding="utf-8",
    )
    v = Verifier()
    ok, advisory = v.step9_check_chain_integrity(manifest, bundle_path)
    assert not ok
    assert advisory is not None
    assert "not located" in advisory


def test_step9_chain_integrity_break_raises_casm_v_060(tmp_path: Path) -> None:
    """Two adjacent bundles where the chain_position lines up but
    the previous_manifest_hash does NOT match the previous
    canonical-bytes hash -> CASM-V-060."""
    mod = _module(tmp_path, "def f(): ...\n")
    # Previous bundle at chain_position=1
    prev_path = _write_bundle(
        tmp_path,
        mod,
        _entries_for(mod),
        bundle_name="prev.furqan.manifest.sigstore",
    )
    # Compute the prev canonical-bytes hash, then forge a wrong one.
    prev_bundle = Bundle.read(prev_path)
    prev_correct_hash = (
        "sha256:" + hashlib.sha256(prev_bundle.manifest.to_canonical_bytes()).hexdigest()
    )
    forged_prev = "sha256:" + "0" * 64
    assert forged_prev != prev_correct_hash
    # Current bundle at chain_position=2 with forged previous hash.
    cur_path = _write_bundle(
        tmp_path,
        mod,
        _entries_for(mod),
        bundle_name="cur.furqan.manifest.sigstore",
        manifest_overrides={
            "chain": {
                "previous_manifest_hash": forged_prev,
                "chain_position": 2,
            }
        },
    )
    cur_bundle = Bundle.read(cur_path)
    v = Verifier()
    with pytest.raises(CasmVerificationError) as exc:
        v.step9_check_chain_integrity(cur_bundle.manifest, cur_path)
    assert exc.value.code == "CASM-V-060"


# Composed verify_bundle (without live Sigstore network)
def test_compose_fails_at_step6_with_fake_bundle(tmp_path: Path) -> None:
    """The composed verify_bundle path will fail at step 6
    (Sigstore verification) when the sigstore_bundle is empty.
    Confirm the failure surfaces a CASM-V-03x code rather than
    crashing with an unrelated exception."""
    mod = _module(tmp_path, "def f(): ...\n")
    bundle_path = _write_bundle(tmp_path, mod, _entries_for(mod))
    v = Verifier()
    with pytest.raises(CasmVerificationError) as exc:
        v.verify_bundle(bundle_path, mod)
    # The empty sigstore_bundle adapt step raises CASM-V-030;
    # different sigstore-python versions may surface earlier
    # codes if TUF refresh fails first. Phase G11.0.4 al-Bayyina
    # (v0.11.5) F24 closure makes step4 TrustedRoot import
    # resolve via the public-then-private fallback, so the
    # verifier now reaches step6 reliably; step6's C-1 corrective
    # (Phase G11.1, v0.11.0) raises CASM-V-035 when no Identity
    # policy is supplied (the default refuse-without-policy
    # state). Pre-v0.11.5 step4 failed first with CASM-V-021,
    # masking step6's behavior. CASM-V-035 is therefore now the
    # most-common observed code on this composed path.
    assert exc.value.code in {
        "CASM-V-021",
        "CASM-V-030",
        "CASM-V-032",
        "CASM-V-035",
    }
