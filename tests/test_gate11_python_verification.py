"""Phase G11.0.6 (as-Saff / v0.11.8) python_verification facade tests.

These tests pin the contract for the new procedural facade
``furqan_lint.gate11.python_verification._verify_python``:

1. The facade is importable from the new module location.
2. The facade accepts an argparse-shaped namespace and composes
   a Verifier internally (verified by signature-shape probe; the
   actual end-to-end verification path is tested by
   test_gate11_verification.py against the byte-stable
   Verifier class API).
3. The facade does not regress the byte-stable Verifier class
   API: callers using ``Verifier(...).verify_bundle(...)``
   continue to work unchanged.

The facade's substantive verification logic is the
``Verifier.verify_bundle`` 9-step flow tested elsewhere; these
tests focus narrowly on the facade-introduction contract.
"""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import inspect

import pytest

pytest.importorskip("rfc8785")

from furqan_lint.gate11.python_verification import _verify_python
from furqan_lint.gate11.verification import (
    TrustConfig,
    VerificationResult,
    Verifier,
)

# ---------------------------------------------------------------
# T01.a: facade is importable from the new module location
# ---------------------------------------------------------------


def test_python_verification_facade_is_importable() -> None:
    """The new python_verification module exposes _verify_python.

    Pre-v0.11.8 this module did not exist; the import would
    fail with ModuleNotFoundError. Post-v0.11.8 the import
    resolves and the facade is callable.
    """
    assert callable(_verify_python)


# ---------------------------------------------------------------
# T01.b: facade signature matches the documented contract
# ---------------------------------------------------------------


def test_python_verification_facade_signature() -> None:
    """The facade signature is ``_verify_python(manifest, args)``.

    This is the dispatch shape consumed by
    ``verification._LANGUAGE_DISPATCH``. Any change to the
    signature is a refactor-breaking change and must be paired
    with a CHANGELOG entry per the Naskh Discipline.
    """
    sig = inspect.signature(_verify_python)
    params = list(sig.parameters.keys())
    assert params == ["manifest", "args"], (
        f"facade signature drifted: expected ['manifest', 'args'], " f"got {params}"
    )
    # The return annotation is VerificationResult (the same type
    # the underlying Verifier.verify_bundle returns). Because
    # ``from __future__ import annotations`` is in force, the
    # annotation is stored as a string forward-reference; with
    # ``eval_str=True`` get_annotations would attempt to resolve
    # ALL parameter annotations including the TYPE_CHECKING-only
    # Manifest/argparse forward refs, which raises NameError at
    # runtime. Read the raw return annotation string directly via
    # __annotations__ and check it equals "VerificationResult"
    # (the imported name). The fact that VerificationResult IS
    # importable from this test is the runtime-availability
    # check; the string match is the contract pin.
    raw = sig.return_annotation
    assert raw == "VerificationResult" or raw is VerificationResult, (
        f"facade return annotation drifted: expected " f"'VerificationResult', got {raw!r}"
    )


# ---------------------------------------------------------------
# T01.c: byte-stable Verifier class API is not regressed
# ---------------------------------------------------------------


def test_python_verification_facade_does_not_regress_verifier_class() -> None:
    """The Verifier class API remains byte-stable across v0.11.8.

    Existing callers (gate11/cli.py, all tests pre-v0.11.8) use
    ``Verifier(trust_config=...).verify_bundle(...)``. The new
    procedural facade is purely additive; this test pins that
    the class is still constructible and has the expected
    method.
    """
    # Construction path 1: default trust config
    v1 = Verifier()
    assert hasattr(v1, "verify_bundle")
    assert callable(v1.verify_bundle)

    # Construction path 2: explicit TrustConfig (the gate11/cli.py
    # path)
    v2 = Verifier(trust_config=TrustConfig())
    assert hasattr(v2, "verify_bundle")
    assert callable(v2.verify_bundle)

    # The verify_bundle signature must retain its keyword-only
    # tail (Phase G11.1 audit corrective) so callers passing
    # expected_identity / expected_issuer / allow_any_identity
    # by keyword continue to work.
    sig = inspect.signature(Verifier.verify_bundle)
    params = sig.parameters
    assert params["expected_identity"].kind == inspect.Parameter.KEYWORD_ONLY
    assert params["expected_issuer"].kind == inspect.Parameter.KEYWORD_ONLY
    assert params["allow_any_identity"].kind == inspect.Parameter.KEYWORD_ONLY


# ---------------------------------------------------------------
# T01.d: facade handles missing-attribute defaults via getattr
# ---------------------------------------------------------------


def test_python_verification_facade_uses_getattr_defaults() -> None:
    """The facade reads optional args via getattr with safe defaults.

    A minimal argparse.Namespace carrying only bundle_path and
    module_path must be acceptable to the facade (the missing
    attributes default to False/None). This contract supports
    both the gate11/cli.py production path (which sets all
    attributes) and downstream programmatic callers (e.g.,
    integration tests) that may construct a partial namespace.

    This test does NOT execute the verification flow; it
    verifies that attribute lookup against a minimal namespace
    does not raise AttributeError before reaching the substrate
    Verifier call. The substrate call itself will fail on
    nonexistent paths -- but that failure must come from
    Verifier.verify_bundle, not from the facade's own attribute
    lookup.
    """
    minimal_args = argparse.Namespace(
        bundle_path="/nonexistent/bundle.tar",
        module_path="/nonexistent/module.py",
    )
    # The facade should call getattr(args, "force_refresh", False)
    # rather than args.force_refresh -- the latter would raise
    # AttributeError before we reach the substrate call.
    # We confirm by asserting the failure (when it eventually
    # comes) is from the substrate, not from the facade.
    with pytest.raises(Exception) as exc:
        _verify_python(manifest=None, args=minimal_args)
    # The facade's getattr-based attribute lookup did not raise
    # AttributeError for force_refresh / expected_identity /
    # expected_issuer / allow_any_identity. The exception that
    # propagated up came from Verifier.verify_bundle's own
    # path-resolution failure, which is the expected behavior.
    assert not isinstance(exc.value, AttributeError) or (
        "force_refresh" not in str(exc.value)
        and "expected_identity" not in str(exc.value)
        and "expected_issuer" not in str(exc.value)
        and "allow_any_identity" not in str(exc.value)
    )
