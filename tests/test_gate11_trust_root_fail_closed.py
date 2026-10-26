"""Regression tests for Gate 11's explicit Sigstore trust-root contract."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

sigstore = pytest.importorskip("sigstore")

from furqan_lint.gate11.verification import (  # noqa: E402
    CasmVerificationError,
    TrustConfig,
    Verifier,
)


def test_unknown_trust_root_is_rejected_without_loading_staging(monkeypatch: pytest.MonkeyPatch) -> None:
    from sigstore._internal import trust

    calls: list[str] = []

    def production() -> object:
        calls.append("production")
        return object()

    def staging() -> object:
        calls.append("staging")
        return object()

    monkeypatch.setattr(trust.TrustedRoot, "production", staticmethod(production))
    monkeypatch.setattr(trust.TrustedRoot, "staging", staticmethod(staging))
    verifier = Verifier(TrustConfig(trust_root_id="unexpected-private-root"))
    with pytest.raises(CasmVerificationError) as error:
        verifier.step4_load_trust_root()
    assert error.value.code == "CASM-V-021"
    assert calls == []


@pytest.mark.parametrize(
    ("root_id", "expected"),
    [("public-sigstore", "production"), ("staging-sigstore", "staging")],
)
def test_explicit_trust_root_selection(
    monkeypatch: pytest.MonkeyPatch, root_id: str, expected: str
) -> None:
    from sigstore._internal import trust

    monkeypatch.setattr(
        trust.TrustedRoot, "production", staticmethod(lambda: "production")
    )
    monkeypatch.setattr(trust.TrustedRoot, "staging", staticmethod(lambda: "staging"))
    assert Verifier(TrustConfig(trust_root_id=root_id)).step4_load_trust_root() == expected


def test_sigstore_constructor_failure_never_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    from sigstore import models, verify

    calls: list[str] = []

    class BrokenVerifier:
        def __init__(self, *, _inner: object) -> None:
            calls.append("constructor")
            raise TypeError("invalid trusted root")

        @staticmethod
        def production() -> object:
            calls.append("production")
            return object()

        @staticmethod
        def staging() -> object:
            calls.append("staging")
            return object()

    monkeypatch.setattr(verify, "Verifier", BrokenVerifier)
    monkeypatch.setattr(
        models.Bundle,
        "from_json",
        staticmethod(lambda _payload: SimpleNamespace()),
    )
    bundle = SimpleNamespace(sigstore_bundle={})
    with pytest.raises(CasmVerificationError) as error:
        Verifier().step6_verify_sigstore(
            bundle, b"manifest", object(), expected_identity="expected", expected_issuer="issuer"
        )
    assert error.value.code == "CASM-V-021"
    assert calls == ["constructor"]
