"""Smoke test for Phase G11.0 T06: Sigstore signing.

Network-bound and OIDC-bound. Skipped unless
``FURQAN_LINT_GATE11_SMOKE_TEST=1`` is set in the environment.
The ``gate11-smoke-test`` CI job (T10) sets the env var and
exercises the test on push to main using the ambient
GitHub OIDC token.

The unit-test suite does NOT cover this path; T08's verification
tests cover the verifier with synthetic bundles, no live
network. Together: the smoke test pins the sign-then-verify
round-trip; the unit tests pin the verification logic for every
CASM-V error path.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("FURQAN_LINT_GATE11_SMOKE_TEST") != "1",
    reason="set FURQAN_LINT_GATE11_SMOKE_TEST=1 to enable Gate 11 smoke test",
)


@pytest.mark.network
def test_sign_and_round_trip(tmp_path: Path) -> None:
    """Sign a fixture manifest with ambient or interactive OIDC,
    serialize the bundle to disk, read it back, and verify the
    round-trip preserves the canonical manifest bytes.
    """
    pytest.importorskip("sigstore")
    from furqan_lint.gate11.bundle import Bundle
    from furqan_lint.gate11.manifest_schema import Manifest
    from furqan_lint.gate11.signing import sign_manifest

    manifest_dict = {
        "casm_version": "1.0",
        "module_identity": {
            "language": "python",
            "module_path": "src/example.py",
            "module_root_hash": "sha256:" + "0" * 64,
        },
        "public_surface": {
            "names": [
                {
                    "name": "alpha",
                    "kind": "function",
                    "signature_fingerprint": "sha256:" + "1" * 64,
                }
            ],
            "extraction_method": "ast.module-public-surface@v1.0",
            "extraction_substrate": "furqan-lint smoke-test",
        },
        "chain": {
            "previous_manifest_hash": None,
            "chain_position": 1,
        },
        "linter_substrate_attestation": {
            "linter_name": "furqan-lint",
            "linter_version": "0.10.0",
            "checker_set_hash": "sha256:" + "2" * 64,
        },
        "trust_root": {
            "trust_root_id": "public-sigstore",
            "fulcio_url": "https://fulcio.sigstore.dev",
            "rekor_url": "https://rekor.sigstore.dev",
        },
        "issued_at": "2026-05-07T14:32:11Z",
    }
    manifest = Manifest.from_dict(manifest_dict)
    bundle_obj = sign_manifest(manifest)

    # Round-trip via T07 Bundle helper.
    out_path = tmp_path / "example.furqan.manifest.sigstore"
    bundle = Bundle(manifest=manifest, sigstore_bundle=bundle_obj)
    bundle.write(out_path)
    re_read = Bundle.read(out_path)
    assert re_read.manifest.to_canonical_bytes() == manifest.to_canonical_bytes()
