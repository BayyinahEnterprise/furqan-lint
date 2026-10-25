"""Phase G12.0 (al-Basirah / v1.0.0) T05 tests for verify-self subcommand.

Exercises gate11/cli.py cmd_manifest_verify_self handler + the
dispatch_manifest wiring for the new ``manifest verify-self``
subcommand.

Per F-NA-4 v1.4 absorption: this NEW file contributes +5 tests
per T05 working hypothesis.
"""

# ruff: noqa: E402

from __future__ import annotations

import inspect

import pytest

pytest.importorskip("rfc8785")

from furqan_lint.gate11.cli import (
    cmd_manifest_verify_self,
    dispatch_manifest,
)


def test_verify_self_subcommand_routed_by_dispatch_manifest() -> None:
    """T05 closure: dispatch_manifest routes 'verify-self'
    subcommand to cmd_manifest_verify_self handler. Mirror of
    the existing init/verify/update dispatch pattern.

    Substrate-of-record: read dispatch_manifest source to confirm
    the 'verify-self' string-match branch is present (avoids
    needing to actually exercise the network-dependent flow)."""
    source = inspect.getsource(dispatch_manifest)
    assert '"verify-self"' in source, (
        "T05 substrate-of-record violation: dispatch_manifest " "missing 'verify-self' branch"
    )
    assert "cmd_manifest_verify_self" in source, (
        "T05 substrate-of-record violation: dispatch_manifest does "
        "not call cmd_manifest_verify_self"
    )


def test_verify_self_handler_routes_through_verify_bundle_dispatch() -> None:
    """T05 closure: cmd_manifest_verify_self routes through
    verification.verify (which contains the function-local
    _LANGUAGE_DISPATCH per al-Mursalat T04 + an-Naziat F-NA-3
    closure). Mirror of test_module_level_verify_dispatches_python_to_facade
    structural pattern.

    Structural-honesty test: read cmd_manifest_verify_self source
    and assert it invokes verification.verify (which then
    dispatches to _verify_python because manifest.module_identity
    ['language'] == 'python' for self-manifests)."""
    source = inspect.getsource(cmd_manifest_verify_self)
    assert "from furqan_lint.gate11 import verification" in source, (
        "T05 substrate-of-record violation: cmd_manifest_verify_self "
        "does not import verification module"
    )
    assert "_verification.verify(_manifest, _namespace)" in source, (
        "T05 substrate-of-record violation: cmd_manifest_verify_self "
        "does not invoke verification.verify; dispatch consolidation "
        "via function-local _LANGUAGE_DISPATCH regression"
    )


def test_verify_self_default_uses_installed_version() -> None:
    """T05 closure: without --version, the subcommand uses the
    installed furqan-lint version (via importlib.metadata).
    Structural-honesty test: read handler source and confirm
    importlib.metadata.version lookup is present."""
    source = inspect.getsource(cmd_manifest_verify_self)
    assert "importlib.metadata" in source or "_md.version" in source, (
        "T05 substrate-of-record violation: cmd_manifest_verify_self "
        "does not use importlib.metadata to look up installed "
        "version"
    )
    assert '_md.version("furqan-lint")' in source, (
        "T05 substrate-of-record violation: installed-version "
        "lookup does not name furqan-lint package"
    )


def test_verify_self_manifest_not_found_raises_casm_v_072(monkeypatch, capsys) -> None:
    """T05 closure + §5.1 step 4 failure mode #2 closure (manifest-
    not-found): when the convention-based URL returns 404 / network
    error, cmd_manifest_verify_self exits 1 with CASM-V-072
    sub-condition (a) named in the error message.

    Per F-BA-substrate-conflict-1 v1.0.0 closure: substrate-actual
    code is CASM-V-072 (NOT prompt-cited 040 which is in-use at
    v0.10.0+ baseline)."""
    import urllib.error
    import urllib.request

    def _raise_404(*args, **kwargs):
        raise urllib.error.HTTPError(
            url="http://test",
            code=404,
            msg="Not Found",
            hdrs={},  # type: ignore[arg-type]
            fp=None,
        )

    monkeypatch.setattr(urllib.request, "urlretrieve", _raise_404)

    exit_code = cmd_manifest_verify_self(["--version", "1.0.0"])
    captured = capsys.readouterr()
    assert exit_code == 1, "T05 closure: manifest-not-found should exit 1; got " f"{exit_code}"
    assert "CASM-V-072" in captured.err, (
        f"T05 substrate-actual violation: expected CASM-V-072 in "
        f"stderr; got {captured.err[:200]!r}"
    )
    assert "manifest-not-found" in captured.err, (
        "T05 sub-condition naming violation: stderr does not name " "the sub-condition explicitly"
    )


def test_verify_self_explicit_version_overrides_installed(monkeypatch, tmp_path) -> None:
    """T05 closure: with --version 0.14.0, the subcommand uses
    that specific version's convention-based URL (not the
    installed version). Structural-honesty test: capture the
    URL the handler attempts to download via monkeypatched
    urlretrieve."""
    import urllib.request

    captured_urls: list[str] = []

    def _capture_url(url, local_path):
        captured_urls.append(url)
        Path(local_path).write_bytes(b"")
        raise OSError("test stub: not really downloading")

    from pathlib import Path

    monkeypatch.setattr(urllib.request, "urlretrieve", _capture_url)

    # Exit code is irrelevant; we capture which URL was attempted:
    cmd_manifest_verify_self(["--version", "0.14.0"])

    # The first URL attempted should be the manifest JSON at
    # v0.14.0 (NOT the installed version):
    assert any("v0.14.0" in url for url in captured_urls), (
        f"T05 substrate-of-record violation: --version 0.14.0 did "
        f"not produce v0.14.0 URL; attempted URLs: {captured_urls!r}"
    )
    assert any(
        "self_manifest.json" in url for url in captured_urls
    ), "T05 closure: should attempt to download self_manifest.json"
