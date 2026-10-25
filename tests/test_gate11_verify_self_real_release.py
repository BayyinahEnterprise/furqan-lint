"""v1.0.2: ``manifest verify-self`` against a real release's assets.

Up to v1.0.1, ``verify-self`` routed the downloaded assets through the
nine-step CASM verifier, which expects a ``{manifest, sigstore_bundle}``
wrapper and runs steps 7-8 (source hash, Python surface) against a
source file. The release workflow publishes something else: it runs
``python -m sigstore sign --bundle self_manifest.bundle
self_manifest.json``, so the signed artifact is the raw JSON bytes and
the bundle is a bare Sigstore bundle. Every real release therefore
failed with "bundle missing 'manifest' field" (first observed on
v1.0.1, the first release whose workflow reached the signing step).

``tests/fixtures/gate11/release_v1_0_1/`` holds the exact assets
published on the v1.0.1 GitHub Release:

* ``self_manifest.json``   sha256 639d00ae...e08b5
* ``self_manifest.bundle`` sha256 81342542...951bc

The offline tests replace Sigstore verification with a recorder and
pin what is verified and how; the network test runs real Sigstore
verification of those bytes against the release workflow identity.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import shutil
import urllib.request
from pathlib import Path

import pytest

from furqan_lint.gate11 import cli as gate11_cli
from furqan_lint.gate11.verification import CasmVerificationError, Verifier

RELEASE = Path(__file__).parent / "fixtures" / "gate11" / "release_v1_0_1"
MANIFEST = RELEASE / "self_manifest.json"
BUNDLE = RELEASE / "self_manifest.bundle"
IDENTITY = (
    "https://github.com/BayyinahEnterprise/furqan-lint/"
    ".github/workflows/release.yml@refs/tags/v1.0.1"
)
ISSUER = "https://token.actions.githubusercontent.com"


def _serve_fixtures(monkeypatch: pytest.MonkeyPatch, bundle: Path = BUNDLE) -> None:
    def fake_retrieve(url: str, dest: Path) -> None:
        src = MANIFEST if url.endswith("self_manifest.json") else bundle
        shutil.copyfile(src, dest)

    monkeypatch.setattr(urllib.request, "urlretrieve", fake_retrieve)


def _record_step6(monkeypatch: pytest.MonkeyPatch) -> dict:
    seen: dict = {}
    monkeypatch.setattr(Verifier, "step4_load_trust_root", lambda self, force_refresh=False: "root")

    def fake_step6(self, bundle, data, trusted_root, **kw):  # type: ignore[no-untyped-def]
        seen.update(bundle=bundle, data=data, trusted_root=trusted_root, **kw)
        return kw["expected_identity"]

    monkeypatch.setattr(Verifier, "step6_verify_sigstore", fake_step6)
    # Isolate from whatever furqan-lint is installed in the test env: the
    # drift check (sub-condition b) is pinned separately below.
    import furqan_lint.gate11.self_manifest as sm

    attested = json.loads(MANIFEST.read_text())["linter_substrate_attestation"]
    monkeypatch.setattr(sm, "compute_self_checker_set_hash", lambda: attested["checker_set_hash"])
    return seen


@pytest.mark.unit
def test_fixtures_are_the_published_v1_0_1_assets() -> None:
    assert (
        hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
        == "639d00ae64eafcb27d0653cc15d07f160e3824ac163ebb2ef199d39b642e08b5"
    )
    assert (
        hashlib.sha256(BUNDLE.read_bytes()).hexdigest()
        == "8134254256cfb10e99998e1c5404dfd4dfc79a5243f02ad977302d5e8e0951bc"
    )
    raw = json.loads(BUNDLE.read_text())
    assert "messageSignature" in raw and "manifest" not in raw  # bare Sigstore bundle


@pytest.mark.unit
def test_verify_self_signs_exact_bytes_with_release_identity(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The fix: the signature is checked over the published JSON bytes,
    with the release workflow at this tag as the required identity."""
    _serve_fixtures(monkeypatch)
    seen = _record_step6(monkeypatch)
    rc = gate11_cli.cmd_manifest_verify_self(["--version", "1.0.1"])
    out = capsys.readouterr()
    assert rc == 0, out.err
    assert seen["data"] == MANIFEST.read_bytes()
    assert seen["expected_identity"] == IDENTITY
    assert seen["expected_issuer"] == ISSUER
    assert seen["allow_any_identity"] is False
    assert "messageSignature" in seen["bundle"].sigstore_bundle
    assert "CASM-OK  furqan-lint@1.0.1" in out.out


@pytest.mark.unit
def test_verify_self_identity_override_is_honoured(monkeypatch: pytest.MonkeyPatch) -> None:
    _serve_fixtures(monkeypatch)
    seen = _record_step6(monkeypatch)
    rc = gate11_cli.cmd_manifest_verify_self(
        ["--version", "1.0.1", "--expected-identity", "https://example.invalid/x"]
    )
    assert rc == 0
    assert seen["expected_identity"] == "https://example.invalid/x"


@pytest.mark.unit
@pytest.mark.parametrize(
    ("code", "expected"),
    [("CASM-V-032", "CASM-V-032:"), ("CASM-V-030", "CASM-V-030:"), ("CASM-V-021", "(c)")],
)
def test_verify_self_signature_failures_are_reported(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    code: str,
    expected: str,
) -> None:
    _serve_fixtures(monkeypatch)
    monkeypatch.setattr(Verifier, "step4_load_trust_root", lambda self, force_refresh=False: "root")

    def failing_step6(self, *a, **kw):  # type: ignore[no-untyped-def]
        raise CasmVerificationError(code, "simulated")

    monkeypatch.setattr(Verifier, "step6_verify_sigstore", failing_step6)
    rc = gate11_cli.cmd_manifest_verify_self(["--version", "1.0.1"])
    assert rc == 1
    assert expected in capsys.readouterr().err


@pytest.mark.unit
def test_verify_self_rejects_a_bundle_that_is_not_sigstore(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    wrapper = tmp_path / "wrapper.bundle"
    wrapper.write_text(json.dumps({"manifest": {}, "sigstore_bundle": {}}))
    _serve_fixtures(monkeypatch, bundle=wrapper)
    _record_step6(monkeypatch)
    rc = gate11_cli.cmd_manifest_verify_self(["--version", "1.0.1"])
    assert rc == 1
    assert "CASM-V-010" in capsys.readouterr().err


@pytest.mark.unit
def test_verify_self_reports_drift_after_a_valid_signature(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Sub-condition (b) still fires when the installed package is the
    requested version but its pinned sources hash differently, and only
    after the signature has been verified."""
    import importlib.metadata as md

    import furqan_lint.gate11.self_manifest as sm

    _serve_fixtures(monkeypatch)
    seen = _record_step6(monkeypatch)
    monkeypatch.setattr(sm, "compute_self_checker_set_hash", lambda: "sha256:" + "0" * 64)
    real_version = md.version
    monkeypatch.setattr(
        md, "version", lambda name: "1.0.1" if name == "furqan-lint" else real_version(name)
    )
    rc = gate11_cli.cmd_manifest_verify_self(["--version", "1.0.1"])
    assert rc == 1
    assert seen["data"] == MANIFEST.read_bytes()  # signature checked first
    assert "(b) checker-set-hash-drift" in capsys.readouterr().err


@pytest.mark.unit
def test_verify_self_no_longer_routes_through_source_verifier() -> None:
    """Naskh of the v1.0.0 T05 pin
    (``test_verify_self_handler_routes_through_verify_bundle_dispatch``):
    that route ran steps 7-8 against the manifest file and could not
    accept the published bundle format."""
    source = inspect.getsource(gate11_cli.cmd_manifest_verify_self)
    assert "_verify_self_signature(" in source
    assert "_verification.verify(" not in source


@pytest.mark.network
@pytest.mark.slow
def test_real_sigstore_verification_of_published_v1_0_1_assets() -> None:
    """End to end with real Sigstore: the published bytes verify against
    the release workflow identity, and altered bytes or a different
    identity do not. Needs network for the TUF trust root."""
    pytest.importorskip("sigstore")
    from furqan_lint.gate11.manifest_schema import Manifest
    from furqan_lint.gate11.verification import TrustConfig

    manifest = Manifest.from_dict(json.loads(MANIFEST.read_text()))

    def verify(data: bytes, identity: str) -> str:
        return gate11_cli._verify_self_signature(
            manifest=manifest,
            manifest_bytes=data,
            bundle_path=BUNDLE,
            trust_config=TrustConfig(),
            expected_identity=identity,
            expected_issuer=ISSUER,
            allow_any_identity=False,
            force_refresh=False,
        )

    try:
        signer = verify(MANIFEST.read_bytes(), IDENTITY)
    except CasmVerificationError as e:
        if e.code == "CASM-V-021":
            pytest.skip(f"Sigstore trust root unavailable: {e}")
        raise
    assert signer
    with pytest.raises(CasmVerificationError):
        verify(MANIFEST.read_bytes().replace(b"1.0.1", b"1.0.9"), IDENTITY)
    with pytest.raises(CasmVerificationError):
        verify(
            MANIFEST.read_bytes(),
            IDENTITY.replace("release.yml@refs/tags/v1.0.1", "ci.yml@refs/heads/main"),
        )
