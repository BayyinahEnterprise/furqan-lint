"""End-to-end tests for the v0.8.2 Rust additive-only diff.

Spawns the CLI via ``python -m furqan_lint.cli diff old.rs new.rs``
on the ``tests/fixtures/rust/diff/`` fixture pairs and asserts
the verdict + exit code + diagnostic prose. Mirrors the v0.8.1
test_go_diff.py shape.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DIFF_FIXTURES = REPO_ROOT / "tests" / "fixtures" / "rust" / "diff"


def _rust_extras_present() -> bool:
    return (
        importlib.util.find_spec("tree_sitter") is not None
        and importlib.util.find_spec("tree_sitter_rust") is not None
    )


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not _rust_extras_present(),
        reason="tree_sitter / tree_sitter_rust not installed; install [rust] extras",
    ),
]


def _run_diff(old: Path, new: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "furqan_lint.cli", "diff", str(old), str(new)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_rust_diff_additive_only_passes() -> None:
    """v1 -> v2_clean adds task_count and removes nothing.
    PASS with exit 0."""
    result = _run_diff(
        DIFF_FIXTURES / "lib_v1.rs",
        DIFF_FIXTURES / "lib_v2_clean.rs",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout
    assert "(additive-only)" in result.stdout


def test_rust_diff_removed_names_fire_marad() -> None:
    """v1 -> v2_failing removes Client and new_client. Exit 1
    with one diagnostic per removed name (sorted)."""
    result = _run_diff(
        DIFF_FIXTURES / "lib_v1.rs",
        DIFF_FIXTURES / "lib_v2_failing.rs",
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "MARAD" in result.stdout
    assert "'Client'" in result.stdout
    assert "'new_client'" in result.stdout
    # Sorted: 'Client' (uppercase C, ord 67) before 'new_client'
    # (lowercase n, ord 110).
    assert result.stdout.index("'Client'") < result.stdout.index("'new_client'")


def test_rust_diff_uses_rust_rename_hint() -> None:
    """Removed-name diagnostics use the Rust re-export hint
    ('pub use <new> as Name;'), not Python alias or Go var
    syntax."""
    result = _run_diff(
        DIFF_FIXTURES / "lib_v1.rs",
        DIFF_FIXTURES / "lib_v2_failing.rs",
    )
    assert result.returncode == 1
    assert "pub use <new> as Client;" in result.stdout
    assert "pub use <new> as new_client;" in result.stdout
    # Python and Go syntaxes must NOT appear.
    assert "Client = <new_name>" not in result.stdout
    assert "var Client = <new>" not in result.stdout


def test_compare_name_sets_with_rust_language_emits_rust_hint(tmp_path: Path) -> None:
    """Direct unit test for compare_name_sets with
    language='rust'. Pins the v0.8.2 contract that the Rust
    language tag dispatches to the 'pub use <new> as X;' hint
    template."""
    from furqan_lint.additive import compare_name_sets

    diagnostics = compare_name_sets(
        previous_names=frozenset({"PublicItem"}),
        current_names=frozenset(),
        filename="m.rs",
        language="rust",
    )
    assert len(diagnostics) == 1
    assert "pub use <new> as PublicItem;" in diagnostics[0].minimal_fix


def test_rust_diff_no_extras_emits_install_hint(tmp_path: Path) -> None:
    """When the [rust] extras are not installed, a Rust diff
    invocation must emit a one-line install hint to stderr and
    return exit 1 (NOT a Python traceback).

    Regression test for the v0.8.2 build-time finding: the
    initial extract_public_names lacked the v0.7.0.1 lazy-
    import probe, so missing tree_sitter / tree_sitter_rust
    surfaced as a raw ModuleNotFoundError traceback from deep
    inside parser._get_parser. The probe now lives at the
    entry of public_names.extract_public_names, mirroring the
    rust_adapter.parse_file probe added in v0.7.0.1 fix (a).
    """
    from unittest.mock import patch

    v1 = tmp_path / "v1.rs"
    v2 = tmp_path / "v2.rs"
    v1.write_text("pub fn x() {}\n")
    v2.write_text("pub fn x() {}\n")

    # Simulate missing tree_sitter / tree_sitter_rust by
    # injecting a meta_path finder that refuses both modules.
    class _Refuser:
        def find_spec(self, name: str, path: object, target: object = None) -> None:
            if name in ("tree_sitter", "tree_sitter_rust"):
                raise ImportError(f"refused: {name}")
            return None

    refuser = _Refuser()

    import sys as _sys

    with patch.dict(_sys.modules, {}, clear=False):
        # Drop any cached modules so the import fires.
        for mod in list(_sys.modules):
            if mod == "tree_sitter" or mod.startswith("tree_sitter."):
                del _sys.modules[mod]
            if mod == "tree_sitter_rust" or mod.startswith("tree_sitter_rust."):
                del _sys.modules[mod]
        original = list(_sys.meta_path)
        _sys.meta_path.insert(0, refuser)
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    (
                        "import sys\n"
                        "class R:\n"
                        "    def find_spec(self, n, p, t=None):\n"
                        "        if n in ('tree_sitter','tree_sitter_rust'):\n"
                        "            raise ImportError('refused')\n"
                        "        return None\n"
                        "sys.meta_path.insert(0, R())\n"
                        "from furqan_lint.cli import main\n"
                        f"sys.argv = ['furqan-lint','diff','{v1}','{v2}']\n"
                        "raise SystemExit(main())\n"
                    ),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        finally:
            _sys.meta_path[:] = original

    assert result.returncode == 1, (
        f"expected exit 1, got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "Rust support not installed" in result.stderr
    assert "Traceback" not in result.stderr, f"traceback in stderr:\n{result.stderr}"


def test_rust_diff_returns_exit_2_on_parse_error_old_side(tmp_path: Path) -> None:
    """v0.8.3: a parse error on the OLD side returns exit 2
    (PARSE ERROR) on stdout, not exit 1 (false MARAD).
    """
    old = tmp_path / "old.rs"
    new = tmp_path / "new.rs"
    old.write_text("pub fn ){ broken")
    new.write_text("pub fn ok() {}\n")
    result = _run_diff(old, new)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "PARSE ERROR" in result.stdout


def test_rust_diff_returns_exit_2_on_parse_error_new_side(tmp_path: Path) -> None:
    """v0.8.3 (DISCRIMINATING for the round-21 HIGH): a parse
    error on the NEW side returns exit 2, not exit 1. The
    v0.8.2 false-MARAD bug surfaced specifically on this side
    -- a well-formed old.rs with names that the broken new.rs
    couldn't produce would fire a false 'removed name' MARAD
    for every old-side name.
    """
    old = tmp_path / "old.rs"
    new = tmp_path / "new.rs"
    old.write_text("pub fn ok() {}\npub struct Server;\n")
    new.write_text("pub fn ){ broken")
    result = _run_diff(old, new)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "PARSE ERROR" in result.stdout
    # Defensive: the false-MARAD case would have surfaced as
    # exit 1 with 'ok' or 'Server' in the output. Pin the
    # absence to catch a regression.
    assert "MARAD" not in result.stdout
    assert "'ok'" not in result.stdout
    assert "'Server'" not in result.stdout


def test_rust_diff_returns_exit_2_on_parse_error_both_sides(tmp_path: Path) -> None:
    """v0.8.3: both sides broken still returns exit 2 (not
    exit 0 false PASS via empty-set diff)."""
    old = tmp_path / "old.rs"
    new = tmp_path / "new.rs"
    old.write_text("pub fn ){ broken")
    new.write_text("pub fn ){ also_broken")
    result = _run_diff(old, new)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "PARSE ERROR" in result.stdout
