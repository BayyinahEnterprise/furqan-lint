"""Go adapter parser tests (v0.8.0 Phase 1).

3 unit tests covering the contract between Python and the goast
binary: well-formed source returns valid JSON, malformed source
raises GoParseError with the binary's stderr, pathological input
times out into a GoParseError rather than a process hang.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def _go_extras_present() -> bool:
    """True iff the bundled goast binary is present and executable."""
    spec = importlib.util.find_spec("furqan_lint.go_adapter")
    if spec is None or spec.origin is None:
        return False
    pkg_root = Path(spec.origin).parent
    binary = pkg_root / "bin" / "goast"
    return binary.is_file() and os.access(binary, os.X_OK)


_REASON = "goast binary not built; install [go] extras"
pytestmark_go = pytest.mark.skipif(not _go_extras_present(), reason=_REASON)


@pytestmark_go
def test_go_parser_returns_valid_json(tmp_path: Path) -> None:
    """Well-formed Go source produces valid JSON with the expected
    top-level keys."""
    from furqan_lint.go_adapter import parse_file

    source = tmp_path / "config.go"
    source.write_text(
        "package config\n\n"
        "func LoadConfig(path string) (string, error) {\n"
        "    return path, nil\n"
        "}\n"
    )
    data = parse_file(source)
    assert data["package"] == "config"
    assert "LoadConfig" in data["public_names"]
    assert len(data["functions"]) == 1
    fn = data["functions"][0]
    assert fn["name"] == "LoadConfig"
    assert fn["return_type_names"] == ["string", "error"]


@pytestmark_go
def test_go_parser_handles_parse_error(tmp_path: Path) -> None:
    """Malformed Go source raises GoParseError with the binary's
    stderr message. CLI converts to exit code 2."""
    from furqan_lint.go_adapter import GoParseError, parse_file

    source = tmp_path / "broken.go"
    # Missing closing brace; go/parser rejects this.
    source.write_text("package broken\n\nfunc f() {\n")
    with pytest.raises(GoParseError) as excinfo:
        parse_file(source)
    # The binary's stderr typically includes "expected '}'" or
    # similar; we check for the file path or a syntax-error keyword
    # to verify the message wraps the actual parser output.
    msg = str(excinfo.value)
    assert "broken.go" in msg or "expected" in msg.lower()


@pytestmark_go
def test_go_parser_timeout_on_pathological_input(tmp_path: Path) -> None:
    """The parser timeout wraps subprocess.TimeoutExpired in a
    GoParseError so callers see a clean exception, not a hang.

    We can't easily construct input that hangs go/parser without
    OS-level resource manipulation; this test verifies the timeout
    wrapper is in place by patching subprocess.run to raise the
    timeout directly.
    """
    from unittest.mock import patch

    from furqan_lint.go_adapter import GoParseError, parse_file

    source = tmp_path / "smoke.go"
    source.write_text("package smoke\nfunc f() {}\n")

    import subprocess

    with patch(
        "furqan_lint.go_adapter.parser.subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="goast", timeout=10),
    ):
        with pytest.raises(GoParseError) as excinfo:
            parse_file(source)
        assert "timed out" in str(excinfo.value)
