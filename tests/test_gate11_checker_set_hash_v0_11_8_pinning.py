"""Phase G11.0.6 (as-Saff / v0.11.8) checker_set_hash extension pinning.

Pin the v0.11.8 substrate decision: the Phase G11.0.6 facade
modules ``python_verification.py`` and ``rust_verification.py``
are part of the pinned checker source-file list. Their bytes
participate in the substantive Form A
``checker_set_hash`` so a Relying Party can detect substrate
divergence between furqan-lint installations whose facade modules
disagree.

This test fires at v0.11.8 onwards. Removing either facade module
from ``_CHECKER_SOURCE_FILES`` (without an explicit CHANGELOG
entry per the Naskh Discipline) is a regression of the H-6 audit
defense.
"""

# ruff: noqa: E402

from __future__ import annotations

from furqan_lint.gate11.checker_set_hash import _CHECKER_SOURCE_FILES


def test_v0_11_8_facade_modules_in_checker_source_files() -> None:
    """python_verification.py + rust_verification.py are pinned.

    v0.11.8 introduces two new Route B facade modules in
    ``furqan_lint/gate11/``. Both must appear in the pinned
    ``_CHECKER_SOURCE_FILES`` tuple so:

    1. The substantive checker_set_hash includes their bytes,
       making substrate divergence detectable from manifest
       comparison alone (defense against the H-6 propagation
       failure mode that the Form A hash defends against).
    2. Future deletions of either facade module trip the H-6
       regression guard rather than silently weakening the
       commitment.

    Removing either entry must be paired with an explicit
    CHANGELOG entry per the Naskh Discipline.
    """
    file_names = {p.name for p in _CHECKER_SOURCE_FILES}
    assert "python_verification.py" in file_names, (
        "Phase G11.0.6 / as-Saff (v0.11.8) introduced "
        "python_verification.py as a Route B facade module. It "
        "must be pinned in _CHECKER_SOURCE_FILES; absence is a "
        "regression of the H-6 propagation-defense audit."
    )
    assert "rust_verification.py" in file_names, (
        "Phase G11.0.6 / as-Saff (v0.11.8) introduced "
        "rust_verification.py as a Route B facade module. It "
        "must be pinned in _CHECKER_SOURCE_FILES; absence is a "
        "regression of the H-6 propagation-defense audit."
    )
    # Pre-v0.11.8 pinning still in place — byte-stable discipline.
    for v0_11_7_pinned in (
        "additive.py",
        "cli.py",
        "__init__.py",
        "bundle.py",
        "manifest_schema.py",
        "module_canonicalization.py",
        "rust_manifest.py",
        "rust_signature_canonicalization.py",
        "rust_surface_extraction.py",
        "signature_canonicalization.py",
        "signing.py",
        "surface_extraction.py",
        "verification.py",
    ):
        assert v0_11_7_pinned in file_names, (
            f"v0.11.7 pinned file {v0_11_7_pinned!r} dropped from "
            f"_CHECKER_SOURCE_FILES; this would silently weaken "
            f"the Form A commitment and is a regression of the "
            f"H-6 audit defense."
        )
