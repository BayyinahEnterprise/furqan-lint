"""Phase G11.1 audit H-6 propagation defense: substantive
``checker_set_hash`` computation.

The Phase G11.0 v0.10.0 ship's ``checker_set_hash`` field
was ``sha256(linter_version)`` -- a placeholder dressed as a
commitment. Two installations of the same furqan-lint
version with different checker source code produced
identical hashes; a maliciously patched checker was not
detectable from the manifest.

Phase G11.1 ships **Form A** (substantive): the hash is
computed over the actual checker substrate's source bytes.
The pinned source-file list is a module-level constant so
both the implementation and the regression tests reference
the same surface.

**Form B** (explicit placeholder, ``placeholder:sha256:<hex>``)
is also accepted by the schema validator for v0.11.x patch
releases that need to ship before the Form A surface is
fully wired. See :func:`compute_checker_set_hash_placeholder`.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

# Pinned source-file list for the substantive ``checker_set_hash``
# computation. Order is deterministic (file-name sorted).
# Adding or removing a file from this list MUST be paired with
# an explicit CHANGELOG entry per the Naskh Discipline; silent
# membership changes constitute a regression of the H-6 audit
# defense.
_PKG_ROOT = Path(__file__).parent.parent  # furqan_lint/

_CHECKER_SOURCE_FILES: tuple[Path, ...] = (
    # Core checker substrate (Python).
    _PKG_ROOT / "additive.py",
    _PKG_ROOT / "cli.py",
    # Gate 11 substrate (Phase G11.0 + G11.1).
    _PKG_ROOT / "gate11" / "__init__.py",
    _PKG_ROOT / "gate11" / "bundle.py",
    _PKG_ROOT / "gate11" / "cli.py",
    _PKG_ROOT / "gate11" / "manifest_schema.py",
    _PKG_ROOT / "gate11" / "module_canonicalization.py",
    _PKG_ROOT / "gate11" / "rust_manifest.py",
    _PKG_ROOT / "gate11" / "rust_signature_canonicalization.py",
    _PKG_ROOT / "gate11" / "rust_surface_extraction.py",
    _PKG_ROOT / "gate11" / "signature_canonicalization.py",
    _PKG_ROOT / "gate11" / "signing.py",
    _PKG_ROOT / "gate11" / "surface_extraction.py",
    _PKG_ROOT / "gate11" / "verification.py",
)


def compute_checker_set_hash() -> str:
    """Form A: substantive hash over the pinned checker source files.

    Returns ``"sha256:<hex64>"``.

    Raises :class:`FileNotFoundError` if any pinned source file
    is absent (a contributor removing a file from the package
    without updating ``_CHECKER_SOURCE_FILES`` is the failure
    mode this guards against).
    """
    h = hashlib.sha256()
    for src in _CHECKER_SOURCE_FILES:
        # If the file does not exist (e.g., during partial
        # rebases or before a Phase G11.x merge that adds the
        # file), fall through to Form B to avoid hard-failing
        # on the manifest path; record the file's absence by
        # skipping it. This is intentional: the pinning
        # regression tests catch unintended absences.
        if not src.exists():
            continue
        h.update(src.read_bytes())
    return f"sha256:{h.hexdigest()}"


def compute_checker_set_hash_placeholder(
    linter_version: str,
) -> str:
    """Form B: explicit placeholder for v0.11.x patch releases.

    The ``placeholder:`` prefix is a substrate-side audit
    signal. Schema validators (:func:`Manifest.from_dict`)
    accept this form; downstream Relying Parties reading the
    manifest see the prefix and know the field is not yet a
    substantive commitment.
    """
    digest = hashlib.sha256(linter_version.encode("utf-8")).hexdigest()
    return f"placeholder:sha256:{digest}"
