"""Phase G11.0.6 (as-Saff / v0.11.8) module-level verify() + dispatch tests.

Pin the contract for the new module-level
``furqan_lint.gate11.verification.verify(manifest, args)``
function and the private ``_LANGUAGE_DISPATCH`` table built
inside it.

This is the Route B procedural facade introduced at v0.11.8 to
unblock Phase G11.2 (al-Mursalat / Go) and Phase G11.3
(an-Naziat / ONNX), both of which T00-halted at v0.12.0 and
v0.13.0 respectively because their prompts assumed Route A
(per-language modules already extracted) but substrate-truth at
v0.11.7 was a monolithic Verifier class with no module-level
dispatch surface.

These tests focus narrowly on the dispatch-introduction
contract; the substantive 9-step verification flow remains
tested by test_gate11_verification.py.
"""

# ruff: noqa: E402

from __future__ import annotations

import argparse

import pytest

pytest.importorskip("rfc8785")

from furqan_lint.gate11 import verification as v_mod
from furqan_lint.gate11.manifest_schema import Manifest
from furqan_lint.gate11.verification import (
    CasmVerificationError,
    Verifier,
    verify,
)


def _baseline_manifest_dict(language: str) -> dict:
    """Build a minimal Manifest dict in the requested language.

    Mirrors test_gate11_dispatch_f22_corrective._baseline_manifest_dict
    so the dispatch tests use the same shape as the F22 pinning
    tests. Kept inline to avoid cross-test fixture coupling.
    """
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
            "linter_version": "0.11.8",
            "checker_set_hash": "sha256:" + "1" * 64,
        },
        "trust_root": {"trust_root_id": "public-sigstore"},
        "issued_at": "2026-05-09T00:00:00Z",
    }


# ---------------------------------------------------------------
# T03.a: verify is exported and callable
# ---------------------------------------------------------------


def test_module_level_verify_is_exported() -> None:
    """``verify`` is exposed in verification.__all__ at v0.11.8.

    Pre-v0.11.8 the module's __all__ tuple did not include
    ``verify``. Post-v0.11.8 the symbol is part of the public
    re-export contract. Existing entries (CasmIndeterminateError,
    CasmVerificationError, TrustConfig, VerificationResult,
    Verifier) remain for byte-stable discipline.
    """
    assert "verify" in v_mod.__all__
    # Existing entries remain -- byte-stable discipline.
    for name in (
        "CasmIndeterminateError",
        "CasmVerificationError",
        "TrustConfig",
        "VerificationResult",
        "Verifier",
    ):
        assert name in v_mod.__all__, (
            f"v0.11.7 export {name!r} missing from v0.11.8 __all__ "
            f"-- byte-stable discipline regression"
        )
    # The exported symbol is callable.
    assert callable(verify)


# ---------------------------------------------------------------
# T03.b: dispatch raises CASM-V-001 for unknown languages
# ---------------------------------------------------------------


def test_module_level_verify_raises_casm_v_001_on_unknown_language() -> None:
    """``verify`` raises CasmVerificationError(CASM-V-001) for go.

    Future Phase G11.2 (Go) and G11.3 (ONNX) will extend the
    dispatch table; until then, ``language=go`` falls through
    to the dispatch-miss branch and raises CASM-V-001 with a
    message naming the future phase.

    Per F-XR-5 audit absorption: the CasmVerificationError is
    constructed with positional args (``CasmVerificationError(
    "CASM-V-001", msg)``), not keyword, to match the rest of
    the verification module's exception-construction style.
    """
    valid = Manifest.from_dict(_baseline_manifest_dict("python"))
    # Forge the language past the schema (which would reject
    # 'haskell') to exercise the verifier-side dispatch defense.
    # Post-al-Mursalat (v0.12.0): 'go' is now substrate-LIVE so
    # the unknown-language fixture uses 'haskell' instead.
    valid.module_identity["language"] = "haskell"

    args = argparse.Namespace(
        bundle_path="/nonexistent/bundle.tar",
        module_path="/nonexistent/module.hs",
    )
    with pytest.raises(CasmVerificationError) as exc:
        verify(valid, args)
    assert exc.value.code == "CASM-V-001"
    msg = str(exc.value)
    # Post-v0.12.0: G11.3 (ONNX) is the next-phase target, not
    # G11.2 (Go, now substrate).
    assert "G11.3" in msg
    assert "python" in msg.lower()
    assert "rust" in msg.lower()
    assert "go" in msg.lower()


# ---------------------------------------------------------------
# T03.c: dispatch hit reaches the per-language facade
# ---------------------------------------------------------------


def test_module_level_verify_dispatches_python_to_facade() -> None:
    """Python manifests dispatch to python_verification._verify_python.

    The facade composes a Verifier internally; with nonexistent
    paths the Verifier's step1_parse_bundle raises
    CasmVerificationError. We assert the propagated exception is
    *not* the dispatch-miss CASM-V-001, confirming that the
    dispatch table routed to the correct facade rather than
    falling through to the unknown-language branch.
    """
    valid = Manifest.from_dict(_baseline_manifest_dict("python"))
    args = argparse.Namespace(
        bundle_path="/nonexistent/bundle.tar",
        module_path="/nonexistent/module.py",
    )
    with pytest.raises(CasmVerificationError) as exc:
        verify(valid, args)
    # CASM-V-010 is the bundle-parse failure code (step 1).
    # CASM-V-001 would mean the dispatch table missed -- which
    # would be a regression.
    assert exc.value.code == "CASM-V-010", (
        f"dispatch routed wrongly: expected CASM-V-010 (bundle "
        f"parse failure from python facade), got {exc.value.code}"
    )


def test_module_level_verify_dispatches_rust_to_facade() -> None:
    """Rust manifests dispatch to rust_verification._verify_rust.

    Mirror of the python dispatch test; same reasoning.
    """
    valid = Manifest.from_dict(_baseline_manifest_dict("rust"))
    args = argparse.Namespace(
        bundle_path="/nonexistent/bundle.tar",
        module_path="/nonexistent/module.rs",
    )
    with pytest.raises(CasmVerificationError) as exc:
        verify(valid, args)
    assert exc.value.code == "CASM-V-010", (
        f"dispatch routed wrongly: expected CASM-V-010 (bundle "
        f"parse failure from rust facade), got {exc.value.code}"
    )


# ---------------------------------------------------------------
# T03.d: byte-stable Verifier class API + verify_bundle signature
# ---------------------------------------------------------------


def test_verifier_class_api_byte_stable_at_v0_11_8() -> None:
    """The Verifier class API has not regressed across v0.11.7 → v0.11.8.

    The new module-level verify() facade is purely additive; this
    test pins the byte-stable contract for callers that continue
    to use the class API directly (gate11/cli.py and all tests
    pre-v0.11.8).

    Pinned surface:
      * Verifier() default-constructible
      * Verifier(trust_config=...) keyword-constructible
      * verify_bundle keyword-only tail (expected_identity,
        expected_issuer, allow_any_identity) per Phase G11.1 H-5
        audit corrective
    """
    import inspect

    v = Verifier()
    assert callable(v.verify_bundle)

    sig = inspect.signature(Verifier.verify_bundle)
    params = sig.parameters
    # The bundle_path / module_path / force_refresh trio retains
    # positional-or-keyword semantics; the trio after the bare *
    # is keyword-only.
    assert params["bundle_path"].kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert params["module_path"].kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert params["expected_identity"].kind == inspect.Parameter.KEYWORD_ONLY
    assert params["expected_issuer"].kind == inspect.Parameter.KEYWORD_ONLY
    assert params["allow_any_identity"].kind == inspect.Parameter.KEYWORD_ONLY


# ---------------------------------------------------------------
# Phase G11.2 al-Mursalat (v0.12.0) extension tests
# ---------------------------------------------------------------


def test_module_level_verify_dispatches_go_to_facade() -> None:
    """Go manifests dispatch to go_verification._verify_go (al-Mursalat).

    Mirror of the python / rust dispatch tests; same reasoning.
    Per F-PA-3 / F-PF-1 / F-PF-3 v1.8 substrate-of-record: Go is
    substrate-LIVE at v0.12.0; the function-local
    _LANGUAGE_DISPATCH dict inside verification.verify is
    extended via a third lazy-import line; the dispatch routes
    cleanly to _verify_go which propagates the substrate
    CASM-V-010 (bundle parse failure) for nonexistent paths.
    """
    valid = Manifest.from_dict(_baseline_manifest_dict("go"))
    args = argparse.Namespace(
        bundle_path="/nonexistent/bundle.tar",
        module_path="/nonexistent/module.go",
    )
    with pytest.raises(CasmVerificationError) as exc:
        verify(valid, args)
    assert exc.value.code == "CASM-V-010", (
        f"dispatch routed wrongly: expected CASM-V-010 (bundle "
        f"parse failure from go facade), got {exc.value.code}"
    )


def test_module_level_verify_unknown_language_message_names_onnx() -> None:
    """Post-v0.12.0, the unknown-language error message names
    ONNX (Phase G11.3) as the next-phase extension target.

    Closes F-AL-6 / F-AL-7 narrative continuity: Go is no longer
    a future-phase target (it ships at v0.12.0); ONNX is the
    next-phase target awaiting v0.13.0 an-Naziat.
    """
    valid = Manifest.from_dict(_baseline_manifest_dict("python"))
    # Forge past schema:
    valid.module_identity["language"] = "haskell"
    args = argparse.Namespace(
        bundle_path="/nonexistent/bundle.tar",
        module_path="/nonexistent/module.hs",
    )
    with pytest.raises(CasmVerificationError) as exc:
        verify(valid, args)
    assert exc.value.code == "CASM-V-001"
    msg = str(exc.value).lower()
    # Supported set now lists go alongside python/rust:
    assert "python" in msg
    assert "rust" in msg
    assert "go" in msg
    # Future-phase callout names ONNX / G11.3, not G11.2 / go:
    assert "g11.3" in msg
    assert "g11.2" not in msg, (
        "G11.2 still cited as future-phase target; al-Mursalat "
        "(v0.12.0) is substrate-LIVE -- update the dispatch's "
        "CasmVerificationError message"
    )


def test_module_level_verify_threads_trust_config_to_go_handler() -> None:
    """Per F-RN-1 v1.5 absorption + T02 Edit 2: trust_config
    flows through args.trust_config Namespace attribute to
    _verify_go via the substrate-true
    ``getattr(args, "trust_config", None) or TrustConfig()``
    pattern.

    Structural-honesty test: read the _verify_go source bytes
    and confirm the getattr pattern is present (mirrors the
    test_go_verification_facade_honors_args_trust_config
    structural pin in test_gate11_go_verification.py).
    """
    import inspect as _inspect

    from furqan_lint.gate11 import go_verification

    source = _inspect.getsource(go_verification._verify_go)
    assert 'getattr(args, "trust_config", None)' in source, (
        "_verify_go missing args.trust_config getattr pattern; " "F-RN-1 v1.5 absorption regression"
    )
    assert "or TrustConfig()" in source, (
        "_verify_go missing 'or TrustConfig()' default; " "F-RN-1 v1.5 absorption regression"
    )


def test_module_level_verify_function_local_dispatch_isolation_at_v0_12_0() -> None:
    """The function-local _LANGUAGE_DISPATCH dict is constructed
    inside verify() at call time (NOT module-level).

    Closes failure mode #2 of §5.1 step 4 ranked list (CLI
    dispatch by _VERIFIER_DISPATCH accidentally becomes Python-
    only when imports are lazy). The dispatch dict is built
    via three lazy-import lines (python / rust / go) and
    constructed fresh on each verify() call -- a stale
    module-level binding cannot drift.

    Structural-honesty test: read the verify source and confirm
    all three lazy-imports + the three dict entries are present.
    """
    import inspect as _inspect

    from furqan_lint.gate11 import verification

    source = _inspect.getsource(verification.verify)
    assert "from furqan_lint.gate11.python_verification import _verify_python" in source
    assert "from furqan_lint.gate11.rust_verification import _verify_rust" in source
    assert "from furqan_lint.gate11.go_verification import _verify_go" in source
    # Dispatch dict entries:
    assert '"python": _verify_python' in source
    assert '"rust": _verify_rust' in source
    assert '"go": _verify_go' in source
