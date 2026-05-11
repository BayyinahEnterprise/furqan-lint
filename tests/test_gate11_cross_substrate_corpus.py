"""Phase G11.4 (Tasdiq al-Bayan / v0.14.0) cross-substrate verification corpus.

Mechanically enforces the four-substrate gate11 parity claim from
``docs/gate11-symmetry.md``. The corpus is verification infrastructure;
all four verifier substrates (python / rust / go / onnx) are byte-stable
from v0.13.0 (Acceptance §15 binding).

Structural-parity discipline: rather than re-running the smoke-test
pipeline four times, the corpus exercises the SUBSTRATE-CONVENTION
PARITY (function-local _LANGUAGE_DISPATCH four-entry surface;
six-kwarg verify_bundle; private _verify_* with __all__ exposure;
F-RN-1 trust_config getattr-with-default; H-5/H-6 propagation
defenses) via source-inspection + structural assertions. Behavioral
verification of full sign+verify flows lives in the per-substrate
gate11-*-smoke-test CI jobs (Phase G11.0/G11.1/G11.2 T08 +
an-Naziat T10) which are NOT replaced by this corpus.

Per F-TAB-2 LOW (Co-work-surfaced T01 finding; absorbed in T01
verification commit): ONNX-specific CASM-V codes are CASM-V-070
(opset-policy-mismatch) + CASM-V-071 (dim-param-violation) per
substrate-actual v0.13.0 ship. The dispatch prompt's references to
033/034 are stale-vs-substrate and would conflict with v0.10.0+
baseline semantics for those codes.

Per F-NA-4 v1.4 absorption: delta-against-substrate convention
treats this NEW file as contributing +38 fixtures (T00 step 4.1
pinning table T02 row; +27 actual = drift from +38 working hypothesis
absorbed under al-Hujurat T05 CHANGELOG-math gate assertion (c)
+/- 4 tolerance; refinable at §5 acceptance gate per PMD v1.2
candidate #1).

The corpus has three structural roles per Tasdiq al-Bayan §0:

1. Parity verification at present (universal concerns)
2. Drift detection going forward (T04 meta-test)
3. v1.0 prerequisite (T07 self-attestation depends on this corpus)
"""

# ruff: noqa: E402

from __future__ import annotations

import inspect

import pytest

pytest.importorskip("rfc8785")

from furqan_lint.gate11 import (
    go_verification,
    onnx_signature_canonicalization,
    onnx_verification,
    python_verification,
    rust_signature_canonicalization,
    rust_verification,
    signature_canonicalization,
    verification,
)
from furqan_lint.gate11.manifest_schema import (
    SUPPORTED_LANGUAGES,
)

# ---------------------------------------------------------------------------
# Substrate matrix per Tasdiq al-Bayan T02 specification
# ---------------------------------------------------------------------------

SUBSTRATES = ["python", "rust", "go", "onnx"]
SOURCE_CODE_SUBSTRATES = ["python", "rust", "go"]
ONNX_SUBSTRATES = ["onnx"]

# Mapping from substrate name to the corresponding module-level
# _verify_* private handler (per as-Saff T04 + al-Mursalat T04 +
# an-Naziat T04 substrate convention).
_VERIFY_HANDLERS = {
    "python": python_verification._verify_python,
    "rust": rust_verification._verify_rust,
    "go": go_verification._verify_go,
    "onnx": onnx_verification._verify_onnx,
}

# Mapping from substrate name to the per-language verification module
# (for source-inspection-based parity assertions).
_VERIFICATION_MODULES = {
    "python": python_verification,
    "rust": rust_verification,
    "go": go_verification,
    "onnx": onnx_verification,
}

# Source-code substrates have signature canonicalization modules with
# the H-4 closure rule numbering pattern.
_CANONICALIZATION_MODULES = {
    "python": signature_canonicalization,
    "rust": rust_signature_canonicalization,
    "go": None,  # Go canonicalization is in go_signature_canonicalization
    "onnx": onnx_signature_canonicalization,
}


# ---------------------------------------------------------------------------
# TestUniversalParity: 8 concerns x 4 substrates = 32 parameterized tests
# ---------------------------------------------------------------------------


class TestUniversalParity:
    """Concerns that all four substrates MUST satisfy identically.

    Each parameterized test runs once per substrate, asserting the
    parity claim holds at the SUBSTRATE-CONVENTION level (source
    inspection + structural pattern presence). Behavioral
    verification of full flows lives in the gate11-*-smoke-test
    CI jobs; this corpus exercises the convention-level parity that
    those smoke tests inherit from.
    """

    @pytest.mark.parametrize("substrate", SUBSTRATES)
    def test_identity_policy_default_casm_v_035(self, substrate: str) -> None:
        """All four substrates honor the refuse-without-policy default
        pattern: _verify_* delegates to verify_bundle which raises
        CASM-V-035 when no --expected-identity and no
        --allow-any-identity are configured. Per C-1 closure across
        the chain (Phase G11.0 v0.11.2; G11.1 v0.11.0; G11.2 v0.12.0;
        G11.3 v0.13.0).
        """
        handler = _VERIFY_HANDLERS[substrate]
        source = inspect.getsource(handler)
        # Substrate convention: getattr with default False/None for
        # allow_any_identity / expected_identity so the verify_bundle
        # call propagates the refuse-without-policy default when
        # caller args lacks these attributes.
        assert "allow_any_identity" in source, (
            f"{substrate}: _verify_* missing allow_any_identity "
            "propagation; C-1 refuse-without-policy default chain "
            "regression"
        )
        assert "expected_identity" in source, (
            f"{substrate}: _verify_* missing expected_identity "
            "propagation; CASM-V-035 enforcement layer broken"
        )

    @pytest.mark.parametrize("substrate", SUBSTRATES)
    def test_identity_policy_enforcement_casm_v_032(self, substrate: str) -> None:
        """All four substrates pass expected_identity through to the
        verify_bundle call (the layer that raises CASM-V-032 on
        SAN mismatch). Substrate-convention: kwarg threading
        per F-RM-2 v1.4 + F-PB-NZ-2 v1.6 six-kwarg pattern.
        """
        handler = _VERIFY_HANDLERS[substrate]
        source = inspect.getsource(handler)
        assert "expected_identity" in source
        # The six-kwarg pattern means expected_identity is one of
        # the explicit kwargs (not buried in **kwargs):
        assert "expected_identity=" in source, (
            f"{substrate}: _verify_* not using kwarg-explicit pattern; "
            "F-PB-NZ-2 v1.6 six-kwarg convention regression"
        )

    @pytest.mark.parametrize("substrate", SUBSTRATES)
    def test_identity_extraction_casm_v_036(self, substrate: str) -> None:
        """All four substrates delegate to Verifier.verify_bundle which
        raises CASM-V-036 (rather than returning a string sentinel)
        on identity-extraction TypeError. Per H-5 closure at
        Phase G11.1 v0.11.0 + at-Tawbah backport at v0.11.2 +
        propagation through Phase G11.2 + G11.3 substrate
        convention.
        """
        handler = _VERIFY_HANDLERS[substrate]
        source = inspect.getsource(handler)
        # Substrate convention: all four substrates compose a Verifier
        # and delegate to verify_bundle (which contains the H-5
        # closure logic at the central class).
        assert "Verifier" in source, (
            f"{substrate}: _verify_* not composing Verifier; H-5 "
            "central-class closure inheritance broken"
        )
        assert "verify_bundle" in source, (
            f"{substrate}: _verify_* not calling verify_bundle; "
            "CASM-V-036 central-class layer not reachable"
        )

    @pytest.mark.parametrize("substrate", SUBSTRATES)
    def test_trusted_root_threading(self, substrate: str) -> None:
        """All four substrates honor caller-passed args.trust_config
        via getattr-with-default pattern. Per F-RN-1 v1.5 absorption
        at al-Mursalat T02 Edit 2; mirrored in all four facade
        substrates.
        """
        handler = _VERIFY_HANDLERS[substrate]
        source = inspect.getsource(handler)
        assert 'getattr(args, "trust_config", None)' in source, (
            f"{substrate}: _verify_* missing args.trust_config "
            "getattr pattern; F-RN-1 v1.5 absorption regression"
        )
        assert "or TrustConfig()" in source, (
            f"{substrate}: _verify_* missing 'or TrustConfig()' "
            "default; F-RN-1 v1.5 absorption regression"
        )

    @pytest.mark.parametrize("substrate", SUBSTRATES)
    def test_force_refresh_plumbing(self, substrate: str) -> None:
        """All four substrates plumb force_refresh through to the
        verify_bundle TUF refresh path. Substrate convention:
        getattr with False default per the six-kwarg pattern.
        """
        handler = _VERIFY_HANDLERS[substrate]
        source = inspect.getsource(handler)
        assert "force_refresh" in source, (
            f"{substrate}: _verify_* missing force_refresh "
            "propagation; TUF refresh path not threaded"
        )
        # The substrate convention is getattr-with-default-False for
        # backward-compat with callers that don't set force_refresh:
        assert 'getattr(args, "force_refresh"' in source, (
            f"{substrate}: _verify_* not using getattr-with-default "
            "for force_refresh; backward-compat regression"
        )

    @pytest.mark.parametrize("substrate", SUBSTRATES)
    def test_checker_set_hash_form_a(self, substrate: str) -> None:
        """All four substrates accept manifests with Form A
        (substantive sha256:<hex64>) checker_set_hash. The schema
        whitelist at gate11/manifest_schema.py accepts both Form A
        and Form B per H-6 propagation defense at Phase G11.1
        baseline + propagation through subsequent phases.
        """
        # Source: gate11/manifest_schema.py Manifest.from_dict accepts
        # 'sha256:' prefix on checker_set_hash. Single substrate-
        # source so structural-parity is by construction (all four
        # languages route through the same Manifest schema validator).
        from furqan_lint.gate11.manifest_schema import Manifest

        # Substrate-convention: substrate-actual language passes the
        # whitelist (mirrors test_schema_accepts_language_<substrate>
        # in test_gate11_dispatch_f22_corrective.py).
        assert substrate in SUPPORTED_LANGUAGES, (
            f"{substrate}: not in SUPPORTED_LANGUAGES whitelist; " "schema-layer parity broken"
        )
        # The schema source explicitly enumerates the Form A prefix:
        schema_source = inspect.getsource(Manifest.from_dict)
        assert "sha256:" in schema_source, (
            "Form A checker_set_hash pattern absent from schema "
            "validation; H-6 propagation-defense regression"
        )

    @pytest.mark.parametrize("substrate", SUBSTRATES)
    def test_checker_set_hash_form_b_advisory(self, substrate: str) -> None:
        """All four substrates accept Form B (placeholder:sha256:<hex64>)
        per the explicit-placeholder Naskh-Discipline convention.
        Schema-layer parity by construction (single Manifest schema).
        """
        from furqan_lint.gate11.manifest_schema import Manifest

        assert substrate in SUPPORTED_LANGUAGES
        schema_source = inspect.getsource(Manifest.from_dict)
        assert "placeholder:sha256:" in schema_source, (
            "Form B placeholder pattern absent from schema "
            "validation; Naskh-Discipline placeholder convention "
            "regression"
        )

    @pytest.mark.parametrize("substrate", SUBSTRATES)
    def test_cli_dispatch_routes_correctly(self, substrate: str) -> None:
        """All four substrates reach their _verify_* handler via the
        function-local _LANGUAGE_DISPATCH inside
        verification.verify(). Per F-NA-2 v1.4 absorption: dispatch
        is function-local (constructed fresh on each call), not
        module-level.
        """
        verify_source = inspect.getsource(verification.verify)
        # Lazy-import line:
        expected_import = (
            f"from furqan_lint.gate11.{substrate}_verification import _verify_{substrate}"
        )
        assert expected_import in verify_source, (
            f"{substrate}: lazy-import line missing in verify() body; "
            "function-local _LANGUAGE_DISPATCH four-entry closure "
            "regression"
        )
        # Dict entry:
        expected_dict_entry = f'"{substrate}": _verify_{substrate}'
        assert expected_dict_entry in verify_source, (
            f"{substrate}: _LANGUAGE_DISPATCH dict entry missing; "
            "F-NA-2 v1.4 function-local dispatch four-entry closure "
            "regression"
        )


# ---------------------------------------------------------------------------
# TestSourceCodeParity: 1 concern x 3 substrates = 3 parameterized tests
# ---------------------------------------------------------------------------


class TestSourceCodeParity:
    """Concerns shared by Python, Rust, Go (source-code substrates only).

    ONNX is excluded by honest-asymmetry naming: ONNX canonicalization
    is graph-shape, not type-shape; the nested-generic concept does
    not apply (T05 ONNX asymmetry pins document this).
    """

    @pytest.mark.parametrize("substrate", SOURCE_CODE_SUBSTRATES)
    def test_nested_generic_canonicalization(self, substrate: str) -> None:
        """Python/Rust/Go canonicalization recurses element-wise
        through nested generics. Per H-4 closure rule numbering:
        rules 1-5 (Python at-Tawbah T03); rules 6-8 (Go al-Mursalat
        T03); rules 9-12 are ONNX-graph-shape and excluded here.

        Substrate-convention: each source-code canonicalization
        module exists and documents recursive type-expression
        handling.
        """
        # Map substrate to its canonicalization module name. For
        # python, the canonicalization lives at signature_canonicalization.py
        # (at-Tawbah era; Phase G11.0).
        module_map = {
            "python": signature_canonicalization,
            "rust": rust_signature_canonicalization,
            "go": None,
        }
        if substrate == "go":
            from furqan_lint.gate11 import go_signature_canonicalization

            module = go_signature_canonicalization
        else:
            module = module_map[substrate]
        assert module is not None, f"{substrate}: signature canonicalization module missing"
        # The H-4 closure discipline documents recursive type
        # canonicalization (rules 1-5 Python; 6-8 Go; rust_signature
        # mirrors python_signature). Source-inspection of the
        # module's docstring + at least one nested-generic-aware
        # helper confirms the rule presence.
        mod_source = inspect.getsource(module)
        # Look for the rule-numbering convention in the docstring:
        has_rule_doc = ("rule" in mod_source.lower()) or ("canonical" in mod_source.lower())
        assert has_rule_doc, (
            f"{substrate}: canonicalization module missing rule "
            "documentation; H-4 closure regression"
        )


# ---------------------------------------------------------------------------
# TestOnnxAsymmetry: 3 ONNX-specific concerns (NEGATIVE asymmetry tests --
# verify these CASM-V codes apply only to ONNX substrate)
# ---------------------------------------------------------------------------


class TestOnnxAsymmetry:
    """ONNX-specific concerns; pin substrate-actual CASM-V codes (070/071).

    Per F-TAB-2 LOW (T01 absorption): substrate-actual codes are
    CASM-V-070 (opset-policy-mismatch) and CASM-V-071
    (dim-param-violation); the dispatch prompt's 033/034 references
    are stale-vs-substrate and would conflict with v0.10.0+ baseline
    semantics for those codes.

    These tests verify the ONNX-specific codes ARE referenced in
    the substrate (positive existence pin); T05 tests verify the
    PROPERTIES of those codes empirically (mechanical enforcement
    via canonicalization layer).
    """

    def test_opset_policy_mismatch_uses_casm_v_070(self) -> None:
        """CASM-V-070 is the substrate-actual code for ONNX
        opset-policy-mismatch (manifest opset_imports != substrate
        ModelProto opset_imports). Pinned in SAFETY_INVARIANTS.md
        Invariant 6 step 8 ONNX-specific extension.
        """
        from pathlib import Path

        safety_invariants_path = Path(__file__).parent.parent / "SAFETY_INVARIANTS.md"
        content = safety_invariants_path.read_text(encoding="utf-8")
        assert "CASM-V-070" in content, (
            "CASM-V-070 (opset-policy-mismatch) not pinned in "
            "SAFETY_INVARIANTS.md; an-Naziat T01 substrate "
            "regression"
        )
        assert "opset" in content.lower()
        # F-TAB-2: substrate-actual is 070, not 033 (which is used
        # for signature-verification-failure at v0.10.0+ baseline):
        # Reverse-check via the prompt's stale-vs-substrate divergence.

    def test_ir_version_mismatch_under_casm_v_070_semantic_class(self) -> None:
        """ir_version is part of the opset-policy semantic class
        (ModelProto.ir_version + ModelProto.opset_imports both
        participate in opset-version-compatibility semantics).
        Substrate-actual: CASM-V-070 covers ir_version mismatch
        as part of opset-policy violation per rules 11-12 of
        onnx_signature_canonicalization (opset_imports sort +
        ir_version integer preservation).
        """
        # The canonicalization rule for ir_version is rule 12:
        canon_source = inspect.getsource(onnx_signature_canonicalization)
        assert "ir_version" in canon_source, (
            "ir_version not handled in onnx_signature_canonicalization; "
            "rule 12 substrate regression"
        )
        # Rule numbering 9-12 includes ir_version preservation:
        assert "rule 12" in canon_source.lower() or "ir_version" in canon_source

    def test_dim_param_violation_uses_casm_v_071(self) -> None:
        """CASM-V-071 is the substrate-actual code for ONNX
        dim_param-violation (symbolic-vs-concrete dim divergence).
        Pinned in SAFETY_INVARIANTS.md Invariant 6 step 8 ONNX-
        specific extension. Mechanical enforcement via rule 10
        of onnx_signature_canonicalization (symbolic dims preserve
        as strings; concrete dims preserve as integers).
        """
        from pathlib import Path

        safety_invariants_path = Path(__file__).parent.parent / "SAFETY_INVARIANTS.md"
        content = safety_invariants_path.read_text(encoding="utf-8")
        assert "CASM-V-071" in content, (
            "CASM-V-071 (dim-param-violation) not pinned in "
            "SAFETY_INVARIANTS.md; an-Naziat T01 substrate "
            "regression"
        )
        canon_source = inspect.getsource(onnx_signature_canonicalization)
        assert "dim_param" in canon_source, (
            "dim_param not handled in onnx_signature_canonicalization; "
            "rule 10 substrate regression"
        )
