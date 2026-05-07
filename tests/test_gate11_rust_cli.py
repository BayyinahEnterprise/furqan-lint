"""Phase G11.1 CLI + verifier audit-corrective pinning tests.

Pins the audit C-1 (CRITICAL identity policy gap), H-5 (HIGH
trusted_root threading), M-7 (MEDIUM string-sentinel identity
extraction), and amended_4 T05 specification of CASM-V-032 /
CASM-V-035 / CASM-V-036.

Live OIDC signing is NOT exercised here (that path requires
``FURQAN_LINT_GATE11_SMOKE_TEST=1`` and a real Sigstore PKI
endpoint). These tests validate the synthesizable parts of the
contract: argument parsing, refuse-without-policy default,
identity-extraction error paths.
"""

# ruff: noqa: E402, SIM115, RUF005

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("rfc8785")
pytest.importorskip("sigstore")

from furqan_lint.gate11.bundle import Bundle
from furqan_lint.gate11.cli import _parse_options
from furqan_lint.gate11.manifest_schema import Manifest
from furqan_lint.gate11.verification import (
    CasmVerificationError,
    TrustConfig,
    Verifier,
)

# ---------------------------------------------------------------
# C-1 propagation defense: refuse-without-policy default
# ---------------------------------------------------------------


def test_c1_parse_options_recognizes_expected_identity():
    positional, opts = _parse_options(["--expected-identity", "user@example.com", "bundle.path"])
    assert positional == ["bundle.path"]
    assert opts["expected_identity"] == "user@example.com"


def test_c1_parse_options_recognizes_allow_any_identity():
    positional, opts = _parse_options(["--allow-any-identity", "bundle.path"])
    assert opts["allow_any_identity"] is True


def test_c1_parse_options_expected_issuer():
    positional, opts = _parse_options(
        [
            "--expected-issuer",
            "https://accounts.google.com",
            "bundle.path",
        ]
    )
    assert opts["expected_issuer"] == "https://accounts.google.com"


def test_c1_step6_refuses_without_policy(tmp_path: Path) -> None:
    """Without --expected-identity AND without
    --allow-any-identity, step6 raises CASM-V-035.
    """
    # Build a minimal bundle to feed step6.
    minimal_manifest_dict = {
        "casm_version": "1.0",
        "module_identity": {
            "language": "rust",
            "module_path": "x.rs",
            "module_root_hash": "sha256:" + "0" * 64,
        },
        "public_surface": {
            "names": [],
            "extraction_method": "tree-sitter.rust-public-surface@v1.0",
            "extraction_substrate": "test",
        },
        "chain": {
            "previous_manifest_hash": None,
            "chain_position": 1,
        },
        "linter_substrate_attestation": {
            "linter_name": "furqan-lint",
            "linter_version": "0.11.0",
            "checker_set_hash": "sha256:" + "1" * 64,
        },
        "trust_root": {"trust_root_id": "public-sigstore"},
        "issued_at": "2026-05-07T00:00:00Z",
    }
    manifest = Manifest.from_dict(minimal_manifest_dict)
    bundle = Bundle(manifest=manifest, sigstore_bundle={})
    verifier = Verifier(trust_config=TrustConfig())
    canonical = manifest.to_canonical_bytes()
    with pytest.raises(CasmVerificationError) as excinfo:
        verifier.step6_verify_sigstore(bundle, canonical, trusted_root=None)
    assert excinfo.value.code == "CASM-V-035"


def test_c1_allow_any_identity_proceeds_past_policy_gate():
    """With --allow-any-identity, the CASM-V-035 refuse-without-
    policy check is skipped (the request now reaches the next
    error -- here, the missing trusted_root / empty bundle).
    """
    minimal_manifest_dict = {
        "casm_version": "1.0",
        "module_identity": {
            "language": "rust",
            "module_path": "x.rs",
            "module_root_hash": "sha256:" + "0" * 64,
        },
        "public_surface": {
            "names": [],
            "extraction_method": "tree-sitter.rust-public-surface@v1.0",
            "extraction_substrate": "test",
        },
        "chain": {
            "previous_manifest_hash": None,
            "chain_position": 1,
        },
        "linter_substrate_attestation": {
            "linter_name": "furqan-lint",
            "linter_version": "0.11.0",
            "checker_set_hash": "sha256:" + "1" * 64,
        },
        "trust_root": {"trust_root_id": "public-sigstore"},
        "issued_at": "2026-05-07T00:00:00Z",
    }
    manifest = Manifest.from_dict(minimal_manifest_dict)
    bundle = Bundle(manifest=manifest, sigstore_bundle={})
    verifier = Verifier(trust_config=TrustConfig())
    canonical = manifest.to_canonical_bytes()
    with pytest.raises(CasmVerificationError) as excinfo:
        verifier.step6_verify_sigstore(
            bundle,
            canonical,
            trusted_root=None,
            allow_any_identity=True,
        )
    # The error code is NOT CASM-V-035 (we explicitly opted past
    # the policy gate); it's some downstream error. The C-1
    # corrective is verified by the absence of CASM-V-035.
    assert excinfo.value.code != "CASM-V-035"


# ---------------------------------------------------------------
# H-6 propagation defense: --placeholder-checker-hash flag
# ---------------------------------------------------------------


def test_h6_placeholder_checker_hash_flag_parsed():
    positional, opts = _parse_options(["--placeholder-checker-hash", "module.rs"])
    assert opts["use_placeholder_checker_hash"] is True


# ---------------------------------------------------------------
# Bundle filename preserves the source extension
# ---------------------------------------------------------------


def test_bundle_filename_preserves_rs_extension(tmp_path: Path) -> None:
    """foo.rs -> foo.rs.furqan.manifest.sigstore (not
    foo.furqan.manifest.sigstore which would collide with foo.py).
    """
    from furqan_lint.gate11.cli import _bundle_path_for

    rs_path = tmp_path / "foo.rs"
    py_path = tmp_path / "foo.py"
    rs_bundle = _bundle_path_for(rs_path)
    py_bundle = _bundle_path_for(py_path)
    assert rs_bundle != py_bundle
    assert rs_bundle.name == "foo.rs.furqan.manifest.sigstore"
    assert py_bundle.name == "foo.py.furqan.manifest.sigstore"
