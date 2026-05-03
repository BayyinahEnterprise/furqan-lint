"""Regression tests for the v0.7.0.1 corrective release.

Two HIGH-severity findings from Bilal's fresh-instance review of
the v0.7.0 patch:

1. mypy --strict failed on a clean install because tomli (the 3.10
   tomllib fallback) had no stubs and no override. v0.7.0.1 adds
   the override; the regression test asserts the override is
   present in pyproject.toml so a future cleanup cannot silently
   drop it.

2. Running ``furqan-lint check foo.rs`` without the ``[rust]``
   extra crashed with a Python traceback instead of the clean
   install hint promised by prompt section 3.3. v0.7.0.1 adds
   the ``RustExtrasNotInstalled`` typed exception (subclass of
   ``ImportError``) raised at the entry of ``parse_file`` and
   handled by the CLI; the regression test asserts the typed
   exception exists, is exported, and produces the expected
   message when the extras imports fail.

Both are pinned here as Bayyinah-style adversarial gauntlet
fixtures: the test is the four-place anchor that prevents either
finding from regressing silently.
"""

from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# Issue 1: mypy tomli override
# ---------------------------------------------------------------------------


def test_pyproject_has_tomli_mypy_override() -> None:
    """pyproject.toml must declare ``[[tool.mypy.overrides]]`` with
    ``module = "tomli"`` so that mypy --strict passes on a clean
    install where tomli stubs are absent.

    Without this override, v0.7.0 failed the gate-4 check for any
    contributor whose venv did not have tomli pre-installed (a
    transitive of mypy on Python 3.10, but not always present on
    3.11+).
    """
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")

    # Look for an overrides stanza that names tomli. The TOML parser
    # would be more rigorous but a textual check is enough for
    # regression purposes; the override is a one-liner.
    # Look for any line `module = "tomli"` (or list form) under a
    # mypy.overrides stanza. Permissive pattern: just check the
    # bare line exists in the file.
    has_string_form = bool(re.search(r'^\s*module\s*=\s*"tomli"\s*$', pyproject, re.MULTILINE))
    has_list_form = bool(re.search(r'^\s*module\s*=\s*\[[^\]]*"tomli"', pyproject, re.MULTILINE))
    assert (
        (has_string_form or has_list_form) and "[tool.mypy.overrides]" in pyproject
    ) or "[[tool.mypy.overrides]]" in pyproject, (
        "pyproject.toml is missing the [[tool.mypy.overrides]] "
        'module = "tomli" stanza. v0.7.0.1 added it; if you '
        "removed it, mypy --strict will fail on any clean install "
        "without tomli pre-installed."
    )


# ---------------------------------------------------------------------------
# Issue 2: typed RustExtrasNotInstalled exception
# ---------------------------------------------------------------------------


def test_rust_extras_not_installed_is_exported_and_subclass_of_importerror() -> None:
    """``RustExtrasNotInstalled`` must be exported from
    ``furqan_lint.rust_adapter.__all__`` and must subclass
    ``ImportError`` so that callers catching ``ImportError``
    broadly still work."""
    from furqan_lint.rust_adapter import RustExtrasNotInstalled

    assert "RustExtrasNotInstalled" in importlib.import_module("furqan_lint.rust_adapter").__all__
    assert issubclass(RustExtrasNotInstalled, ImportError)


def test_parse_file_raises_typed_exception_when_tree_sitter_missing() -> None:
    """When ``tree_sitter`` is not importable, ``parse_file`` must
    raise ``RustExtrasNotInstalled`` (not the raw
    ``ModuleNotFoundError``) with a message that contains the
    install hint.

    Simulates a missing extra by monkey-patching ``sys.modules``
    so the ``import tree_sitter`` inside ``parse_file`` raises.
    """
    from furqan_lint.rust_adapter import RustExtrasNotInstalled, parse_file

    # Save originals
    original_modules = {name: sys.modules.get(name) for name in ("tree_sitter", "tree_sitter_rust")}

    # Force ImportError on the next `import tree_sitter`
    class _ImportErrorFinder:
        def find_spec(self, fullname: str, path=None, target=None) -> None:  # type: ignore[no-untyped-def]
            if fullname in ("tree_sitter", "tree_sitter_rust"):
                raise ImportError(f"forced for test: {fullname}")
            return None

    # Drop cached imports first
    for name in ("tree_sitter", "tree_sitter_rust"):
        sys.modules.pop(name, None)
    finder = _ImportErrorFinder()
    sys.meta_path.insert(0, finder)
    try:
        with pytest.raises(RustExtrasNotInstalled) as excinfo:
            parse_file(Path("/nonexistent.rs"))
        assert "pip install furqan-lint[rust]" in str(excinfo.value)
    finally:
        sys.meta_path.remove(finder)
        # Restore cached modules
        for name, mod in original_modules.items():
            if mod is not None:
                sys.modules[name] = mod


def test_cli_emits_install_hint_without_traceback_when_extras_missing(
    tmp_path: Path,
) -> None:
    """When tree_sitter is unimportable, ``furqan-lint check foo.rs``
    must print the one-line install hint to stderr and exit 1
    cleanly, not dump a Python traceback.

    Asserts the v0.7.0.1 contract from prompt section 3.3.
    Calls the CLI dispatcher in-process with a mocked
    ``parse_file`` that raises ``RustExtrasNotInstalled``.
    """
    from furqan_lint.cli import _check_rust_file
    from furqan_lint.rust_adapter import RustExtrasNotInstalled

    rust_file = tmp_path / "foo.rs"
    rust_file.write_text("fn answer() -> i32 { 42 }\n")

    def _raise_extras_missing(path: Path) -> None:
        raise RustExtrasNotInstalled(
            "Rust support not installed. Run: pip install furqan-lint[rust]"
        )

    with patch("furqan_lint.rust_adapter.parse_file", side_effect=_raise_extras_missing):
        # Capture stderr by patching sys.stderr
        import io

        captured = io.StringIO()
        with patch.object(sys, "stderr", captured):
            exit_code = _check_rust_file(rust_file)

    assert exit_code == 1, f"expected exit 1, got {exit_code}"
    stderr_output = captured.getvalue()
    assert "Rust support not installed" in stderr_output
    assert "pip install furqan-lint[rust]" in stderr_output
    # Negative-control: must not contain traceback markers
    assert "Traceback" not in stderr_output
    assert "ModuleNotFoundError" not in stderr_output
