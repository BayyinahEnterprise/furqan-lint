"""Phase G11.3 (an-Naziat / v0.13.0) T04 tests for ONNX language facade.

Exercises gate11/onnx_verification.py's private _verify_onnx
procedural facade. The facade mirrors as-Saff (v0.11.8)
_verify_python and al-Mursalat (v0.12.0) _verify_go: thin
delegation to ``Verifier(...).verify_bundle(...)`` with the
six-kwarg signature per F-PB-NZ-2 v1.6 absorption.

These tests are at the unit-test layer: they assert call-
signature substrate-conformance, kwarg-propagation, and
trust_config-discipline. End-to-end sigstore verification
fixtures live in tests/test_gate11_onnx_smoke_test.py (T10)
and tests/test_gate11_verify_dispatch.py (T09).

Per F-NA-4 v1.4 absorption + F-PB-NZ-1 v1.6 absorption:
delta-against-substrate convention treats this NEW file as
contributing +5 fixtures (T00 step 4.1 pinning table T04 row).
"""

# ruff: noqa: E402

from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch

import pytest

pytest.importorskip("rfc8785")

import furqan_lint.gate11.onnx_verification as onnx_verification_module
from furqan_lint.gate11.onnx_verification import _verify_onnx
from furqan_lint.gate11.verification import TrustConfig, Verifier


def _make_args(**overrides: object) -> argparse.Namespace:
    """Build an argparse.Namespace matching the gate11 CLI surface."""
    defaults = {
        "bundle_path": Path("/tmp/fake_bundle.json"),
        "module_path": Path("/tmp/fake_module.onnx"),
        "force_refresh": False,
        "expected_identity": "fixture@example.com",
        "expected_issuer": "https://issuer.example.com",
        "allow_any_identity": False,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def test_verify_onnx_module_exports_only_private_handler() -> None:
    """T04 substrate convention: gate11/onnx_verification.py
    exposes ``__all__ = ("_verify_onnx",)`` only; no public
    ``verify`` alias. Mirrors as-Saff _verify_python and
    al-Mursalat _verify_go convention."""
    assert onnx_verification_module.__all__ == ("_verify_onnx",), (
        "T04 substrate-of-record divergence: __all__ should be "
        "('_verify_onnx',); got " + repr(onnx_verification_module.__all__)
    )
    assert callable(_verify_onnx)
    # The handler signature must accept (manifest, args) positional.
    import inspect

    sig = inspect.signature(_verify_onnx)
    params = list(sig.parameters)
    assert params == ["manifest", "args"], (
        f"_verify_onnx signature must be (manifest, args); got {params!r}"
    )


def test_verify_onnx_delegates_to_verifier_with_six_kwarg_pattern() -> None:
    """T04 + F-PB-NZ-2 v1.6 closure: _verify_onnx invokes
    ``Verifier.verify_bundle`` with the canonical six-kwarg
    pattern (bundle_path, module_path, force_refresh,
    expected_identity, expected_issuer, allow_any_identity).

    This is the substrate-truth fixture for F-PB-NZ-2 v1.6
    absorption: post-as-Saff-T04 sigstore-rebase the
    verify_bundle API is six-kwarg-shaped (not the v1.5-era
    single-arg form)."""
    args = _make_args()
    fake_manifest = object()  # informational at this layer

    with patch.object(Verifier, "verify_bundle") as mock_verify:
        mock_verify.return_value = object()
        _verify_onnx(fake_manifest, args)  # type: ignore[arg-type]

    assert mock_verify.call_count == 1
    call_kwargs = mock_verify.call_args.kwargs
    assert set(call_kwargs.keys()) == {
        "bundle_path",
        "module_path",
        "force_refresh",
        "expected_identity",
        "expected_issuer",
        "allow_any_identity",
    }, f"six-kwarg pattern violated; got {set(call_kwargs.keys())!r}"
    assert call_kwargs["bundle_path"] == args.bundle_path
    assert call_kwargs["module_path"] == args.module_path
    assert call_kwargs["force_refresh"] == args.force_refresh
    assert call_kwargs["expected_identity"] == args.expected_identity
    assert call_kwargs["expected_issuer"] == args.expected_issuer
    assert call_kwargs["allow_any_identity"] == args.allow_any_identity


def test_verify_onnx_honors_args_trust_config() -> None:
    """F-RN-1 v1.5 absorption: when args carries a
    trust_config attribute, the Verifier is constructed with
    that trust_config (not a default TrustConfig())."""
    custom_trust = TrustConfig()
    args = _make_args(trust_config=custom_trust)
    fake_manifest = object()

    with patch.object(Verifier, "__init__", return_value=None) as mock_init, patch.object(
        Verifier, "verify_bundle"
    ) as mock_verify:
        mock_verify.return_value = object()
        _verify_onnx(fake_manifest, args)  # type: ignore[arg-type]

    assert mock_init.call_count == 1
    init_kwargs = mock_init.call_args.kwargs
    assert init_kwargs.get("trust_config") is custom_trust, (
        "F-RN-1 violation: _verify_onnx did not propagate "
        "args.trust_config to Verifier constructor"
    )


def test_verify_onnx_defaults_trust_config_when_args_lacks_attribute() -> None:
    """F-RN-1 v1.5 absorption + v0.11.8 programmatic-RP
    backward compat: when args has no trust_config attribute,
    the Verifier is constructed with a default TrustConfig().
    Preserves caller-side simplicity for callers that do not
    set the attribute."""
    args = _make_args()  # no trust_config attribute
    fake_manifest = object()

    with patch.object(Verifier, "__init__", return_value=None) as mock_init, patch.object(
        Verifier, "verify_bundle"
    ) as mock_verify:
        mock_verify.return_value = object()
        _verify_onnx(fake_manifest, args)  # type: ignore[arg-type]

    init_kwargs = mock_init.call_args.kwargs
    trust_config = init_kwargs.get("trust_config")
    assert isinstance(trust_config, TrustConfig), (
        "F-RN-1 default-fallback violation: expected default "
        "TrustConfig() instance; got " + repr(trust_config)
    )


def test_verify_onnx_optional_kwargs_use_getattr_default() -> None:
    """F-RN-1 / F-PB-NZ-2 v1.6 + optional-kwarg discipline:
    when args lacks force_refresh / expected_identity /
    expected_issuer / allow_any_identity, _verify_onnx still
    invokes verify_bundle with those kwargs set to the
    documented defaults (False / None / None / False).
    Preserves backward-compat for programmatic Relying
    Parties that don't set these flags."""
    args = argparse.Namespace(
        bundle_path=Path("/tmp/a.json"),
        module_path=Path("/tmp/b.onnx"),
        # No force_refresh, expected_identity, expected_issuer,
        # allow_any_identity attributes.
    )
    fake_manifest = object()

    with patch.object(Verifier, "verify_bundle") as mock_verify:
        mock_verify.return_value = object()
        _verify_onnx(fake_manifest, args)  # type: ignore[arg-type]

    call_kwargs = mock_verify.call_args.kwargs
    assert call_kwargs["force_refresh"] is False
    assert call_kwargs["expected_identity"] is None
    assert call_kwargs["expected_issuer"] is None
    assert call_kwargs["allow_any_identity"] is False
