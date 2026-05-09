"""Pinning test for F24 closure: step4 TrustedRoot import resolves.

Per Phase G11.0.4 al-Bayyina (Round 31 audit F24): the
``step4_load_trust_root`` method must successfully import
``TrustedRoot`` from sigstore-python regardless of whether
the public path (``sigstore.trust``) or the private path
(``sigstore._internal.trust``) is the current canonical site.

This test catches future API drifts at PR CI rather than
only on push-to-main where the gate11-rust-smoke-test runs.
Per the audit's reasoning: smoke-tests run only on main-push
events (per the
``if: github.event_name == 'push' && github.ref ==
'refs/heads/main'`` gating); a unit-level test here ensures
the import path is exercised on every PR.

Pre-v0.11.5 this raised
``CasmVerificationError("CASM-V-021")`` on sigstore-python
3.6.x because only the public path was attempted; v0.11.5+
uses Option A (public-first then private-fallback).
"""

# ruff: noqa: E402

from __future__ import annotations

import pytest

# Per project convention (5 registered markers in
# pyproject.toml: network, slow, unit, integration, mock).
pytestmark = pytest.mark.unit

# Skip if sigstore-python is genuinely not installed; the test
# pins the API-path drift, not sigstore-installed-ness.
pytest.importorskip("sigstore")

from furqan_lint.gate11 import verification


def test_step4_trust_root_import_resolves() -> None:
    """F24 closure: TrustedRoot must be importable.

    Asserts that ``step4_load_trust_root``'s import block
    successfully resolves ``TrustedRoot`` from sigstore-python,
    regardless of which submodule path (public or private) is
    canonical at the installed version. The load-bearing
    assertion is that no ``CasmVerificationError`` with code
    ``CASM-V-021`` is raised; downstream errors (e.g., TUF
    refresh failure due to no network) are NOT F24 and are
    acceptable here.
    """
    verifier = verification.Verifier()
    try:
        # Bare-statement form: the call's return value is
        # intentionally unused; the load-bearing assertion is
        # that no CASM-V-021 exception is raised. Reaching the
        # next line is the proof that the import block
        # resolved.
        verifier.step4_load_trust_root(force_refresh=False)
    except verification.CasmVerificationError as e:
        if e.code == "CASM-V-021":
            pytest.fail(
                "F24 regression: CASM-V-021 raised on "
                "TrustedRoot import. Per Phase G11.0.4 "
                "al-Bayyina, the import path must resolve via "
                "either sigstore.trust (public, sigstore 4.x+) "
                "or sigstore._internal.trust (private, "
                "sigstore 3.x). Original message: "
                f"{e}"
            )
        # Other CASM-V error codes (e.g., TUF refresh failure
        # due to no network in CI) are NOT F24 and are
        # acceptable here; the test is narrowly scoped to the
        # import path.
