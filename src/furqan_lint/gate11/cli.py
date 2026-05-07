"""Gate 11 CLI handlers (T09).

Subcommands implemented in this module:

* ``furqan-lint manifest init <module-path>``: create the first
  manifest in a chain and sign via Sigstore (T06).
* ``furqan-lint manifest verify <bundle-path>``: run the
  9-step verification flow (T08).
* ``furqan-lint manifest update <module-path>``: create a
  successor manifest in the chain; requires an existing
  adjacent bundle.

Flag parsing in this module is intentionally minimal: the
upstream ``furqan_lint.cli.main`` dispatcher only routes here
when ``args[0] == "manifest"``. Parsing of options such as
``--trust-config`` happens here.

CLI exit codes per the deliverable:

* 0: verification PASSED, or ADVISORY-only.
* 1: a non-advisory CASM-V error fired.
* 2: INDETERMINATE (e.g., DynamicAllError on the public surface).
"""

from __future__ import annotations

import datetime
import hashlib

from furqan_lint.gate11.checker_set_hash import (
    compute_checker_set_hash as _compute_checker_set_hash,
)
import json
import sys
from pathlib import Path

from furqan_lint.gate11 import CASM_VERSION, GATE11_BUNDLE_SUFFIX
from furqan_lint.gate11.bundle import Bundle, BundleParseError
from furqan_lint.gate11.manifest_schema import CasmSchemaError, Manifest
from furqan_lint.gate11.module_canonicalization import (
    ModuleCanonicalizationError,
    module_root_hash,
)
from furqan_lint.gate11.surface_extraction import (
    DynamicAllError,
    extract_public_surface,
)
from furqan_lint.gate11.verification import (
    CasmIndeterminateError,
    CasmVerificationError,
    TrustConfig,
    Verifier,
)


def _bundle_path_for(module_path: Path) -> Path:
    """Return the canonical bundle path for ``module_path``.

    For ``foo/bar.py`` the bundle is ``foo/bar.furqan.manifest.sigstore``.
    """
    return module_path.with_suffix(GATE11_BUNDLE_SUFFIX)


def _build_manifest_dict(
    module_path: Path,
    chain_position: int,
    previous_manifest_hash: str | None,
    trust_config: TrustConfig,
    linter_version: str,
) -> dict[str, object]:
    """Build a CASM v1.0 manifest dict for ``module_path``.

    Raises ``DynamicAllError`` if ``__all__`` is dynamic; the
    caller (init / update) maps this to exit code 2.
    """
    names_entries = extract_public_surface(module_path)
    return {
        "casm_version": CASM_VERSION,
        "module_identity": {
            "language": "python",
            "module_path": str(module_path),
            "module_root_hash": module_root_hash(module_path),
        },
        "public_surface": {
            "names": names_entries,
            "extraction_method": "ast.module-public-surface@v1.0",
            "extraction_substrate": f"furqan-lint v{linter_version}",
        },
        "chain": {
            "previous_manifest_hash": previous_manifest_hash,
            "chain_position": chain_position,
        },
        "linter_substrate_attestation": {
            "linter_name": "furqan-lint",
            "linter_version": linter_version,
            # Phase G11.1 audit H-6 propagation defense: the
            # substantive ``checker_set_hash`` is computed over
            # the pinned checker source files via
            # :func:`furqan_lint.gate11.checker_set_hash.compute_checker_set_hash`.
            # The Phase G11.0 v0.10.0 ship used
            # ``sha256(linter_version)`` (a placeholder dressed
            # as a commitment); v0.11.0 corrects this for both
            # Python and Rust pipelines.
            "checker_set_hash": _compute_checker_set_hash(),
        },
        "trust_root": {
            "trust_root_id": trust_config.trust_root_id,
            "fulcio_url": trust_config.fulcio_url,
            "rekor_url": trust_config.rekor_url,
        },
        "issued_at": (
            datetime.datetime.now(datetime.timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        ),
    }


def _parse_options(args: list[str]) -> tuple[list[str], dict[str, object]]:
    """Parse common Gate 11 options out of an argv list.

    Returns ``(positional, opts)`` where ``opts`` may carry
    ``trust_config_path`` (Path or None).
    """
    positional: list[str] = []
    opts: dict[str, object] = {"trust_config_path": None, "force_refresh": False}
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--trust-config":
            if i + 1 >= len(args):
                print("--trust-config requires a path argument", file=sys.stderr)
                raise SystemExit(2)
            opts["trust_config_path"] = Path(args[i + 1])
            i += 2
        elif a == "--force-refresh":
            opts["force_refresh"] = True
            i += 1
        else:
            positional.append(a)
            i += 1
    return positional, opts


def _trust_config_from_path(path: Path | None) -> TrustConfig:
    if path is None:
        return TrustConfig()
    if not path.is_file():
        print(f"trust-config file not found: {path}", file=sys.stderr)
        raise SystemExit(2)
    data = json.loads(path.read_text(encoding="utf-8"))
    return TrustConfig(
        trust_root_id=str(data.get("trust_root_id", "public-sigstore")),
        fulcio_url=str(data.get("fulcio_url", "https://fulcio.sigstore.dev")),
        rekor_url=str(data.get("rekor_url", "https://rekor.sigstore.dev")),
    )


def cmd_manifest_init(args: list[str]) -> int:
    """``furqan-lint manifest init <module-path>``.

    Creates the first manifest in a chain (chain_position=1,
    previous_manifest_hash=None) and signs it via Sigstore.
    """
    positional, opts = _parse_options(args)
    if not positional:
        print(
            "usage: furqan-lint manifest init <module-path> " "[--trust-config PATH]",
            file=sys.stderr,
        )
        return 2
    module_path = Path(positional[0])
    if not module_path.is_file():
        print(f"module not found: {module_path}", file=sys.stderr)
        return 1
    trust_config = _trust_config_from_path(
        opts["trust_config_path"]  # type: ignore[arg-type]
    )

    from furqan_lint import __version__

    try:
        manifest_dict = _build_manifest_dict(
            module_path,
            chain_position=1,
            previous_manifest_hash=None,
            trust_config=trust_config,
            linter_version=__version__,
        )
    except DynamicAllError as e:
        print(f"INDETERMINATE: {e}", file=sys.stderr)
        return 2
    except (ModuleCanonicalizationError, CasmSchemaError) as e:
        print(f"{e.code}: {e}", file=sys.stderr)
        return 1

    manifest = Manifest.from_dict(manifest_dict)

    try:
        from furqan_lint.gate11.signing import sign_manifest
    except ImportError:
        print(
            "Gate 11 signing requires the [gate11] extra: " "pip install furqan-lint[gate11]",
            file=sys.stderr,
        )
        return 1

    try:
        sg_bundle = sign_manifest(manifest)
    except Exception as e:
        print(f"signing failed: {e}", file=sys.stderr)
        return 1

    out_path = _bundle_path_for(module_path)
    Bundle(manifest=manifest, sigstore_bundle=sg_bundle).write(out_path)
    print(f"CASM-INIT  {out_path}")
    return 0


def cmd_manifest_verify(args: list[str]) -> int:
    """``furqan-lint manifest verify <bundle-path>``."""
    positional, opts = _parse_options(args)
    if not positional:
        print(
            "usage: furqan-lint manifest verify <bundle-path> "
            "[--trust-config PATH] [--force-refresh]",
            file=sys.stderr,
        )
        return 2
    bundle_path = Path(positional[0])
    if not bundle_path.is_file():
        print(f"bundle not found: {bundle_path}", file=sys.stderr)
        return 1
    trust_config = _trust_config_from_path(
        opts["trust_config_path"]  # type: ignore[arg-type]
    )

    # Module path: resolved by stripping the GATE11_BUNDLE_SUFFIX
    # and trying both .py and the parent directory.
    if bundle_path.name.endswith(GATE11_BUNDLE_SUFFIX):
        module_stem = bundle_path.name[: -len(GATE11_BUNDLE_SUFFIX)]
        module_path = bundle_path.parent / f"{module_stem}.py"
    else:
        print(
            f"bundle filename does not end with {GATE11_BUNDLE_SUFFIX!r}",
            file=sys.stderr,
        )
        return 1

    if not module_path.is_file():
        # Best-effort: also accept the manifest's recorded module_path.
        try:
            bundle = Bundle.read(bundle_path)
            recorded = Path(bundle.manifest.module_identity["module_path"])
            if recorded.is_file():
                module_path = recorded
        except (BundleParseError, KeyError):
            pass

    if not module_path.is_file():
        print(f"module not found for bundle {bundle_path}", file=sys.stderr)
        return 1

    verifier = Verifier(trust_config=trust_config)
    try:
        result = verifier.verify_bundle(
            bundle_path,
            module_path,
            force_refresh=bool(opts["force_refresh"]),
        )
    except CasmIndeterminateError as e:
        print(f"INDETERMINATE: {e}", file=sys.stderr)
        return 2
    except CasmVerificationError as e:
        if e.code in {"CASM-V-020", "CASM-V-061"}:
            # ADVISORY codes should not raise; defensive map.
            print(f"ADVISORY {e.code}: {e}", file=sys.stderr)
            return 0
        print(f"{e.code}: {e}", file=sys.stderr)
        return 1

    print(f"CASM-OK  {module_path}")
    print(f"  signed_by: {result.signed_by}")
    if result.manifest is not None:
        print(f"  signed_at: {result.manifest.issued_at}")
    print(f"  chain_position: {result.chain_position}")
    for code, msg in result.advisories:
        print(f"  ADVISORY {code}: {msg}")
    return 0


def cmd_manifest_update(args: list[str]) -> int:
    """``furqan-lint manifest update <module-path>``.

    Creates a successor manifest in the chain. Requires an
    adjacent bundle at ``<module_path.with_suffix(GATE11_BUNDLE_SUFFIX)>``;
    the new manifest's ``previous_manifest_hash`` is the
    canonical-bytes hash of the existing bundle's manifest, and
    ``chain_position`` is the previous + 1.
    """
    positional, opts = _parse_options(args)
    if not positional:
        print(
            "usage: furqan-lint manifest update <module-path> " "[--trust-config PATH]",
            file=sys.stderr,
        )
        return 2
    module_path = Path(positional[0])
    if not module_path.is_file():
        print(f"module not found: {module_path}", file=sys.stderr)
        return 1
    bundle_path = _bundle_path_for(module_path)
    if not bundle_path.is_file():
        print(
            f"no existing bundle at {bundle_path}; use 'manifest init' "
            f"to create the first manifest in a chain",
            file=sys.stderr,
        )
        return 1
    try:
        existing = Bundle.read(bundle_path)
    except BundleParseError as e:
        print(f"{e.code}: {e}", file=sys.stderr)
        return 1
    prev_canonical = existing.manifest.to_canonical_bytes()
    prev_hash = "sha256:" + hashlib.sha256(prev_canonical).hexdigest()
    next_position = int(existing.manifest.chain.get("chain_position", 0)) + 1
    trust_config = _trust_config_from_path(
        opts["trust_config_path"]  # type: ignore[arg-type]
    )

    from furqan_lint import __version__

    try:
        manifest_dict = _build_manifest_dict(
            module_path,
            chain_position=next_position,
            previous_manifest_hash=prev_hash,
            trust_config=trust_config,
            linter_version=__version__,
        )
    except DynamicAllError as e:
        print(f"INDETERMINATE: {e}", file=sys.stderr)
        return 2
    except (ModuleCanonicalizationError, CasmSchemaError) as e:
        print(f"{e.code}: {e}", file=sys.stderr)
        return 1

    manifest = Manifest.from_dict(manifest_dict)

    try:
        from furqan_lint.gate11.signing import sign_manifest
    except ImportError:
        print(
            "Gate 11 signing requires the [gate11] extra: " "pip install furqan-lint[gate11]",
            file=sys.stderr,
        )
        return 1

    try:
        sg_bundle = sign_manifest(manifest)
    except Exception as e:
        print(f"signing failed: {e}", file=sys.stderr)
        return 1

    Bundle(manifest=manifest, sigstore_bundle=sg_bundle).write(bundle_path)
    print(f"CASM-UPDATE  {bundle_path}  chain_position={next_position}")
    return 0


def cmd_check_gate11(directory: Path, opts: dict[str, object]) -> int:
    """``furqan-lint check --gate11 <path>``.

    Walks the path for ``*.furqan.manifest.sigstore`` bundles and
    runs ``manifest verify`` on each. Silent no-op when no
    bundles are present.
    """
    bundles = sorted(directory.rglob(f"*{GATE11_BUNDLE_SUFFIX}"))
    if not bundles:
        return 0
    trust_config = _trust_config_from_path(
        opts["trust_config_path"]  # type: ignore[arg-type]
    )
    verifier = Verifier(trust_config=trust_config)
    overall = 0
    for bp in bundles:
        if bp.name.endswith(GATE11_BUNDLE_SUFFIX):
            stem = bp.name[: -len(GATE11_BUNDLE_SUFFIX)]
            module_path = bp.parent / f"{stem}.py"
        else:
            continue
        if not module_path.is_file():
            try:
                bundle = Bundle.read(bp)
                recorded = Path(bundle.manifest.module_identity["module_path"])
                if recorded.is_file():
                    module_path = recorded
            except (BundleParseError, KeyError):
                pass
        if not module_path.is_file():
            print(f"GATE11-SKIP  {bp}  module not found", file=sys.stderr)
            continue
        try:
            result = verifier.verify_bundle(bp, module_path)
        except CasmIndeterminateError as e:
            print(f"INDETERMINATE  {bp}  {e}", file=sys.stderr)
            overall = max(overall, 2)
            continue
        except CasmVerificationError as e:
            print(f"{e.code}  {bp}  {e}", file=sys.stderr)
            overall = max(overall, 1)
            continue
        print(f"CASM-OK  {module_path}  signed_by={result.signed_by}")
        for code, msg in result.advisories:
            print(f"  ADVISORY {code}: {msg}")
    return overall


def dispatch_manifest(args: list[str]) -> int:
    """Top-level dispatcher invoked from furqan_lint.cli.main()
    when args[0] == "manifest"."""
    if not args:
        print(
            "usage: furqan-lint manifest <init|verify|update> ...",
            file=sys.stderr,
        )
        return 2
    sub = args[0]
    rest = args[1:]
    if sub == "init":
        return cmd_manifest_init(rest)
    if sub == "verify":
        return cmd_manifest_verify(rest)
    if sub == "update":
        return cmd_manifest_update(rest)
    print(f"unknown manifest action: {sub}", file=sys.stderr)
    return 2


__all__ = (
    "cmd_check_gate11",
    "cmd_manifest_init",
    "cmd_manifest_update",
    "cmd_manifest_verify",
    "dispatch_manifest",
)
