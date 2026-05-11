"""Phase G11.2 (al-Mursalat / v0.12.0) Go language facade.

This module is the procedural facade for ``language=go``
manifests dispatched by
``furqan_lint.gate11.verification.verify``.

Mirror of as-Saff (v0.11.8) ``python_verification.py`` and
``rust_verification.py`` private handlers, adapted for Go
substrate. The substrate convention is preserved verbatim:
private ``_verify_go(manifest, args)`` function only;
``__all__ = ("_verify_go",)``; no public ``verify`` alias.

It is **purely additive** at v0.12.0: the existing
``Verifier(...).verify_bundle(...)`` class API in
``verification.py`` continues to be the byte-stable substrate
that all production callers (``gate11/cli.py``) and all tests
use directly. The module-level ``verify(manifest, args)``
function in verification.py composes a Verifier instance
internally and delegates to ``_verify_go`` (this file) when
``manifest.module_identity['language'] == "go"``.

The facade signature ``_verify_go(manifest, args)`` accepts
the parsed Manifest plus the argparse namespace from
gate11/cli.py (carrying bundle_path, module_path,
trust_config, force_refresh, expected_identity, expected_issuer,
allow_any_identity). The ``manifest`` parameter is informational
only at this layer -- ``verification.Verifier.verify_bundle``
re-parses the bundle from ``args.bundle_path`` to enforce the
byte-stable single-source-of-truth contract; the manifest
argument is kept for future language-specific pre-flight
checks (e.g., Go module-graph validation).

Per F-RN-1 v1.5 absorption: this body honors caller-passed
``args.trust_config`` via ``getattr(args, "trust_config", None)
or TrustConfig()``. The CLI loads trust_config via existing
``_trust_config_from_path`` helper and attaches to the args
Namespace; programmatic Relying Parties not setting
``args.trust_config`` get default behavior matching v0.11.8
backward-compat semantics.

API pattern mirrored from the v0.11.8-LIVE Python and Rust
private handlers per al-Mursalat T00 step 6 pre-flight
verification record (NOT the at-Tawbah-era reference; the
v0.11.5 G11.0.4 al-Bayyina F24 corrective re-routed the
sigstore import paths). The Verifier class internally uses
the ``SgVerifier(_inner=trusted_root)`` construction with
``TrustedRoot.production()/staging()`` fallback per H-5
propagation defense; ``UnsafeNoOp()`` policy under explicit
``--allow-any-identity`` opt-in per C-1 refuse-without-policy
default (CASM-V-035).

D24 discipline: this module's helpers use single-trailing-return
shape (raise on miss, return on hit) so the path-coverage
analysis sees terminal coverage across all branches.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from furqan_lint.gate11.verification import (
    TrustConfig,
    VerificationResult,
    Verifier,
)

if TYPE_CHECKING:
    import argparse

    from furqan_lint.gate11.manifest_schema import Manifest


def _verify_go(
    manifest: Manifest,
    args: argparse.Namespace,
) -> VerificationResult:
    """Procedural facade for ``language=go`` manifest verification.

    Composes a ``Verifier`` instance with the trust config implied
    by ``args`` and delegates to ``verify_bundle``. Existing
    callers using ``Verifier(...).verify_bundle(...)`` directly
    are unaffected (the Verifier class is byte-stable from
    v0.11.7 onward).

    The ``manifest`` parameter is informational at this layer:
    ``Verifier.verify_bundle`` re-parses the bundle from
    ``args.bundle_path`` to enforce the byte-stable
    single-source-of-truth contract. The argument is retained
    for language-specific pre-flight checks added in future
    phases (e.g., Go module-graph dependency validation).

    Per F-RN-1 v1.5 absorption: honors caller-passed
    ``args.trust_config`` if attached to the args Namespace by
    the CLI; falls back to default ``TrustConfig()`` when absent
    (preserves v0.11.8 programmatic-RP backward compat).

    For Go-language manifests, ``Verifier.verify_bundle``'s
    9-step flow operates as for Python and Rust:

    1. Parse bundle (CASM-V-010 on JSON / schema failure)
    2. Check casm_version == "1.0" (CASM-V-001)
    3. Check language == "go" matches this verifier (CASM-V-001;
       generalized at T01 per al-Mursalat to include go in the
       supported set)
    4. Load Sigstore trust root via TUF (CASM-V-020 ADVISORY /
       CASM-V-021)
    5. Re-canonicalize the manifest (RFC 8785; Invariant 3)
    6. Verify Sigstore signature; enforce identity policy
       (CASM-V-030..036; CASM-V-032 on mismatch; CASM-V-035
       refuse-without-policy default; CASM-V-036 on identity
       extraction TypeError)
    7. Compare module_root_hash to the on-disk Go module path
       (CASM-V-040 on mismatch)
    8. Compare public_surface.names to the live extraction
       (Go-side extraction via goast per Invariant 5
       ``goast.go-public-surface@v1.0`` extraction-method
       identifier; canonicalization rules 6-8 per
       go_signature_canonicalization.py for nested generics +
       channel direction)
    9. Check chain_pointer integrity (CASM-V-060 / CASM-V-061)

    Raises ``CasmVerificationError`` with the underlying
    CASM-V-NNN code if any of the nine verification steps fail.
    Returns the populated ``VerificationResult`` on success.
    """
    trust_config = getattr(args, "trust_config", None) or TrustConfig()
    verifier = Verifier(trust_config=trust_config)
    return verifier.verify_bundle(
        bundle_path=args.bundle_path,
        module_path=args.module_path,
        force_refresh=getattr(args, "force_refresh", False),
        expected_identity=getattr(args, "expected_identity", None),
        expected_issuer=getattr(args, "expected_issuer", None),
        allow_any_identity=getattr(args, "allow_any_identity", False),
    )


__all__ = ("_verify_go",)
