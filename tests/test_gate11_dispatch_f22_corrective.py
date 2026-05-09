"""Phase G11.0.2 (v0.11.3) F22 corrective pinning tests.

Pre-v0.11.3 the verifier's dispatch site
(``verification.step2_3_check_version_and_language``) rejected
any manifest whose ``language`` was not exactly ``"python"``,
even though ``Manifest.from_dict`` accepted both
``("python", "rust")`` from v0.11.0 onwards. The result was
that the ``gate11-rust-smoke-test`` CI job had been red since
PR #20 (v0.11.0): a rust manifest passed the schema validator
but was rejected at the dispatch site with CASM-V-001. The
dispatch surface contradicted the documented schema surface.

v0.11.3 aligns the dispatch whitelist with the schema
whitelist. After this corrective, the rust smoke test goes
green for the first time since v0.11.0.

These tests pin the corrective. They are intentionally
narrow: only python and rust are exercised, because those are
the two language substrates that have shipped verifiers as of
v0.11.3. Go (Phase G11.2) and ONNX (Phase G11.3) are out of
scope for this patch.
"""

# ruff: noqa: E402

from __future__ import annotations

import pytest

pytest.importorskip("rfc8785")

from furqan_lint.gate11.manifest_schema import (
    CasmSchemaError,
    Manifest,
)
from furqan_lint.gate11.verification import (
    CasmVerificationError,
    TrustConfig,
    Verifier,
)


def _baseline_manifest_dict(language: str) -> dict:
    """Build a minimal Manifest dict in the requested language."""
    return {
        "casm_version": "1.0",
        "module_identity": {
            "language": language,
            "module_path": "x",
            "module_root_hash": "sha256:" + "0" * 64,
        },
        "public_surface": {
            "names": [],
            "extraction_method": (f"placeholder.{language}-public-surface@v1.0"),
            "extraction_substrate": "test",
        },
        "chain": {
            "previous_manifest_hash": None,
            "chain_position": 1,
        },
        "linter_substrate_attestation": {
            "linter_name": "furqan-lint",
            "linter_version": "0.11.3",
            "checker_set_hash": "sha256:" + "1" * 64,
        },
        "trust_root": {"trust_root_id": "public-sigstore"},
        "issued_at": "2026-05-09T00:00:00Z",
    }


# ---------------------------------------------------------------
# Schema-side: Manifest.from_dict accepts python and rust
# (this was already true from v0.11.0; pin it as regression guard)
# ---------------------------------------------------------------


def test_schema_accepts_language_python() -> None:
    Manifest.from_dict(_baseline_manifest_dict("python"))


def test_schema_accepts_language_rust() -> None:
    Manifest.from_dict(_baseline_manifest_dict("rust"))


def test_schema_rejects_language_go() -> None:
    """Go support ships in Phase G11.2; until then schema rejects it.

    This pin is removed when Phase G11.2 ships (v0.12.0+).
    """
    bad = _baseline_manifest_dict("go")
    with pytest.raises(CasmSchemaError) as exc:
        Manifest.from_dict(bad)
    assert exc.value.code == "CASM-V-001"


# ---------------------------------------------------------------
# Dispatch-site: step2_3 accepts python and rust (THE F22 FIX)
# ---------------------------------------------------------------


def test_step2_3_accepts_python_manifest() -> None:
    verifier = Verifier(trust_config=TrustConfig())
    manifest = Manifest.from_dict(_baseline_manifest_dict("python"))
    # No exception raised -> dispatch accepts.
    verifier.step2_3_check_version_and_language(manifest)


def test_f22_step2_3_accepts_rust_manifest() -> None:
    """F22 CLOSURE: rust manifest no longer rejected at step 2_3.

    Pre-v0.11.3 this raised CasmVerificationError(CASM-V-001,
    'v1.0 supports only language=python; got rust'), causing
    gate11-rust-smoke-test CI to be red since v0.11.0. v0.11.3
    aligns the dispatch whitelist with the schema whitelist
    (both accept python/rust).
    """
    verifier = Verifier(trust_config=TrustConfig())
    manifest = Manifest.from_dict(_baseline_manifest_dict("rust"))
    verifier.step2_3_check_version_and_language(manifest)


def test_step2_3_rejects_unknown_language_with_supported_list() -> None:
    """Unsupported languages still fail-closed at the dispatch site
    with CasmVerificationError(CASM-V-001) and the supported list
    enumerated in the error message. Future Phase G11.2 (Go) and
    G11.3 (ONNX) will extend the whitelist when their verifiers
    ship.
    """
    # We bypass schema (which would reject 'haskell') and forge
    # the language field directly to exercise the verifier-side
    # defense.
    valid = Manifest.from_dict(_baseline_manifest_dict("python"))
    valid.module_identity["language"] = "haskell"

    verifier = Verifier(trust_config=TrustConfig())
    with pytest.raises(CasmVerificationError) as exc:
        verifier.step2_3_check_version_and_language(valid)
    assert exc.value.code == "CASM-V-001"
    # The error message must enumerate the supported list so an
    # operator hitting this knows how to adjust.
    msg = str(exc.value).lower()
    assert "python" in msg
    assert "rust" in msg


def test_step2_3_rejects_go_pre_g11_2() -> None:
    """Go is not yet supported (Phase G11.2 / v0.12.0). The
    dispatch site fails-closed with CASM-V-001 + a clear error
    message naming the future phase.
    """
    valid = Manifest.from_dict(_baseline_manifest_dict("python"))
    valid.module_identity["language"] = "go"

    verifier = Verifier(trust_config=TrustConfig())
    with pytest.raises(CasmVerificationError) as exc:
        verifier.step2_3_check_version_and_language(valid)
    assert exc.value.code == "CASM-V-001"
    # Error message names the phase that will add Go.
    assert "G11.2" in str(exc.value)
