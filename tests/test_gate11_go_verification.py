"""Phase G11.2 (al-Mursalat / v0.12.0) go_verification facade tests.

Mirror of as-Saff (v0.11.8) test_gate11_python_verification.py
and test_gate11_rust_verification.py contract pinning. See those
files' module docstrings for the contract being preserved.

Specifically pins:

1. The facade is importable from the new module location.
2. The facade signature is ``_verify_go(manifest, args)`` with
   ``VerificationResult`` return.
3. The byte-stable Verifier class API is not regressed.
4. Per F-RN-1 v1.5 absorption + F-PF-1 v1.7 absorption: the
   facade body honors caller-passed ``args.trust_config`` via
   ``getattr(args, "trust_config", None) or TrustConfig()``
   pattern.
5. The facade reads optional argparse attributes via getattr
   with safe defaults so partial Namespaces are accepted.
"""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import inspect

import pytest

pytest.importorskip("rfc8785")

from furqan_lint.gate11.go_verification import _verify_go
from furqan_lint.gate11.verification import (
    TrustConfig,
    VerificationResult,
    Verifier,
)

# ---------------------------------------------------------------
# T04.a: facade is importable from the new module location
# ---------------------------------------------------------------


def test_go_verification_facade_is_importable() -> None:
    """The new go_verification module exposes _verify_go.

    Pre-v0.12.0 this module did not exist; the import would
    fail with ModuleNotFoundError. Post-v0.12.0 the import
    resolves and the facade is callable.
    """
    assert callable(_verify_go)


# ---------------------------------------------------------------
# T04.b: facade signature matches the documented contract
# ---------------------------------------------------------------


def test_go_verification_facade_signature() -> None:
    """The facade signature is ``_verify_go(manifest, args)``.

    This is the dispatch shape consumed by
    ``verification._LANGUAGE_DISPATCH``. Any change is a
    refactor-breaking change and must be paired with a
    CHANGELOG entry per the Naskh Discipline.
    """
    sig = inspect.signature(_verify_go)
    params = list(sig.parameters.keys())
    assert params == [
        "manifest",
        "args",
    ], f"facade signature drifted: expected ['manifest', 'args'], got {params}"
    # Read raw return annotation directly via signature (the
    # ``from __future__ import annotations`` future flag stores
    # the annotation as a string forward-reference; resolving
    # via get_annotations(eval_str=True) would attempt to
    # resolve ALL parameter annotations including TYPE_CHECKING-
    # only forward refs, which raises NameError at runtime).
    raw = sig.return_annotation
    assert raw == "VerificationResult" or raw is VerificationResult, (
        f"facade return annotation drifted: expected " f"'VerificationResult', got {raw!r}"
    )


# ---------------------------------------------------------------
# T04.c: byte-stable Verifier class API not regressed
# ---------------------------------------------------------------


def test_go_verification_facade_does_not_regress_verifier_class() -> None:
    """The Verifier class API remains byte-stable across v0.12.0.

    Existing Go callers (gate11/cli.py go path post-T02) use
    ``Verifier(trust_config=...).verify_bundle(...)`` internally
    via the _verify_go facade. The new procedural facade is
    purely additive; this test pins that the class is still
    constructible and has the expected method.
    """
    v = Verifier(trust_config=TrustConfig())
    assert hasattr(v, "verify_bundle")
    assert callable(v.verify_bundle)


# ---------------------------------------------------------------
# T04.d: facade honors caller-passed args.trust_config
# (per F-RN-1 v1.5 absorption + T00 step 4b Row (ii) FAIL
# remediation)
# ---------------------------------------------------------------


def test_go_verification_facade_honors_args_trust_config() -> None:
    """The Go facade reads ``args.trust_config`` if attached.

    Closes the F-RN-1 substrate-flow gap that v1.4 missed:
    private handlers MUST honor caller-passed trust_config via
    ``getattr(args, "trust_config", None) or TrustConfig()``
    rather than constructing default unconditionally. This
    contract preserves the ``--trust-config PATH`` CLI flag
    flow under Route (a1-via-args).

    Without the substrate edit at v0.12.0, T02 Edit 3a/3b
    would silently drop the CLI flag value.

    We can't easily test the full flow without a real bundle,
    so we read the source bytes and confirm the getattr pattern
    appears. This is structural-honesty assertion rather than
    behavioral integration.
    """
    import inspect as _inspect

    from furqan_lint.gate11 import go_verification

    source = _inspect.getsource(go_verification._verify_go)
    assert 'getattr(args, "trust_config", None)' in source, (
        "Go facade missing getattr(args, 'trust_config', None) "
        "pattern; F-RN-1 / F-PF-1 absorption regression"
    )
    assert "or TrustConfig()" in source, (
        "Go facade missing 'or TrustConfig()' default fallback; "
        "F-RN-1 / F-PF-1 absorption regression"
    )


# ---------------------------------------------------------------
# T04.e: facade handles missing-attribute defaults via getattr
# ---------------------------------------------------------------


def test_go_verification_facade_uses_getattr_defaults() -> None:
    """The Go facade reads optional args via getattr with safe defaults.

    See test_python_verification_facade_uses_getattr_defaults
    for the contract rationale; this test is the Go mirror.
    A minimal argparse.Namespace carrying only bundle_path and
    module_path must be acceptable to the facade.
    """
    minimal_args = argparse.Namespace(
        bundle_path="/nonexistent/bundle.tar",
        module_path="/nonexistent/module.go",
    )
    with pytest.raises(Exception) as exc:
        _verify_go(manifest=None, args=minimal_args)
    # The exception (when it eventually comes) came from the
    # substrate Verifier call, NOT from the facade's getattr-
    # based attribute lookup. The getattr defaults
    # (force_refresh=False; expected_identity=None;
    # expected_issuer=None; allow_any_identity=False;
    # trust_config=None->TrustConfig()) prevent AttributeError
    # for partial Namespaces.
    assert not isinstance(exc.value, AttributeError) or (
        "force_refresh" not in str(exc.value)
        and "expected_identity" not in str(exc.value)
        and "expected_issuer" not in str(exc.value)
        and "allow_any_identity" not in str(exc.value)
        and "trust_config" not in str(exc.value)
    )
