"""Phase G11.0.6 (as-Saff / v0.11.8) rust_verification facade tests.

Mirror of test_gate11_python_verification.py for the Rust facade.
See that file's module docstring for the contract being pinned.
"""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import inspect

import pytest

pytest.importorskip("rfc8785")

from furqan_lint.gate11.rust_verification import _verify_rust
from furqan_lint.gate11.verification import (
    TrustConfig,
    VerificationResult,
    Verifier,
)

# ---------------------------------------------------------------
# T02.a: facade is importable from the new module location
# ---------------------------------------------------------------


def test_rust_verification_facade_is_importable() -> None:
    """The new rust_verification module exposes _verify_rust.

    Pre-v0.11.8 this module did not exist; the import would
    fail with ModuleNotFoundError. Post-v0.11.8 the import
    resolves and the facade is callable.
    """
    assert callable(_verify_rust)


# ---------------------------------------------------------------
# T02.b: facade signature matches the documented contract
# ---------------------------------------------------------------


def test_rust_verification_facade_signature() -> None:
    """The facade signature is ``_verify_rust(manifest, args)``.

    This is the dispatch shape consumed by
    ``verification._LANGUAGE_DISPATCH``. Any change to the
    signature is a refactor-breaking change and must be paired
    with a CHANGELOG entry per the Naskh Discipline.
    """
    sig = inspect.signature(_verify_rust)
    params = list(sig.parameters.keys())
    assert params == ["manifest", "args"], (
        f"facade signature drifted: expected ['manifest', 'args'], " f"got {params}"
    )
    # The return annotation is VerificationResult. With
    # ``from __future__ import annotations``, get_annotations(
    # eval_str=True) would attempt to resolve ALL parameter
    # annotations including the TYPE_CHECKING-only forward refs,
    # which raises NameError at runtime. Read the raw return
    # annotation string from the signature directly and check it
    # equals "VerificationResult".
    raw = sig.return_annotation
    assert raw == "VerificationResult" or raw is VerificationResult, (
        f"facade return annotation drifted: expected " f"'VerificationResult', got {raw!r}"
    )


# ---------------------------------------------------------------
# T02.c: byte-stable Verifier class API is not regressed for rust
# ---------------------------------------------------------------


def test_rust_verification_facade_does_not_regress_verifier_class() -> None:
    """The Verifier class API remains byte-stable across v0.11.8.

    Existing rust callers (gate11/cli.py rust path, all rust
    tests pre-v0.11.8 in test_gate11_rust_cli.py) use
    ``Verifier(trust_config=...).verify_bundle(...)``. The new
    procedural facade is purely additive; this test pins that
    the class is still constructible and has the expected
    method.
    """
    v = Verifier(trust_config=TrustConfig())
    assert hasattr(v, "verify_bundle")
    assert callable(v.verify_bundle)


# ---------------------------------------------------------------
# T02.d: facade handles missing-attribute defaults via getattr
# ---------------------------------------------------------------


def test_rust_verification_facade_uses_getattr_defaults() -> None:
    """The Rust facade reads optional args via getattr with safe defaults.

    See test_python_verification_facade_uses_getattr_defaults for
    the contract rationale; this test is the rust mirror.
    """
    minimal_args = argparse.Namespace(
        bundle_path="/nonexistent/bundle.tar",
        module_path="/nonexistent/module.rs",
    )
    with pytest.raises(Exception) as exc:
        _verify_rust(manifest=None, args=minimal_args)
    assert not isinstance(exc.value, AttributeError) or (
        "force_refresh" not in str(exc.value)
        and "expected_identity" not in str(exc.value)
        and "expected_issuer" not in str(exc.value)
        and "allow_any_identity" not in str(exc.value)
    )
