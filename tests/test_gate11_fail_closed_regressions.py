"""Gate 11 fail-closed regression cases, using isolated mocked signature verification."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from furqan_lint.gate11 import GATE11_BUNDLE_SUFFIX
from furqan_lint.gate11 import cli as gate_cli
from furqan_lint.gate11 import verification as gate_verification


def _opts(**changes: object) -> dict[str, object]:
    defaults: dict[str, object] = {
        "trust_config_path": None,
        "force_refresh": False,
        "expected_identity": "https://example.invalid/workflow",
        "expected_issuer": "https://token.actions.githubusercontent.com",
        "allow_any_identity": False,
    }
    defaults.update(changes)
    return defaults


def _bundle(tmp_path: Path, filename: str) -> Path:
    path = tmp_path / f"{filename}{GATE11_BUNDLE_SUFFIX}"
    path.write_text("mock bundle", encoding="utf-8")
    return path


def _mock_verifier(monkeypatch: pytest.MonkeyPatch, recorded_path: str) -> list[Any]:
    calls: list[Any] = []
    manifest = SimpleNamespace(module_identity={"module_path": recorded_path})
    monkeypatch.setattr(
        gate_cli.Bundle,
        "read",
        staticmethod(lambda _path: SimpleNamespace(manifest=manifest)),
    )

    def fake_verify(_manifest: Any, args: Any) -> Any:
        calls.append(args)
        return SimpleNamespace(signed_by="fixture-identity", advisories=[])

    monkeypatch.setattr(gate_verification, "verify", fake_verify)
    return calls


@pytest.mark.parametrize("extension", ["py", "rs", "go", "onnx"])
def test_gate11_bundle_resolves_exact_source_extension(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, extension: str
) -> None:
    filename = f"module.{extension}"
    source = tmp_path / filename
    source.write_bytes(b"fixture")
    _bundle(tmp_path, filename)
    calls = _mock_verifier(monkeypatch, "nonexistent-module")
    assert gate_cli.cmd_check_gate11(tmp_path, _opts()) == 0
    assert len(calls) == 1, "reported success without invoking signature verifier"
    assert calls[0].module_path == source


def test_gate11_relative_path_does_not_depend_on_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    source = project / "module.py"
    source.write_text("def f():\n    return 1\n", encoding="utf-8")
    _bundle(project, "module.py")
    calls = _mock_verifier(monkeypatch, "module.py")
    monkeypatch.chdir(tmp_path)
    assert gate_cli.cmd_check_gate11(project, _opts()) == 0
    assert len(calls) == 1
    assert calls[0].module_path == source


def test_gate11_orphaned_bundle_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _bundle(tmp_path, "missing.py")
    calls = _mock_verifier(monkeypatch, "also-missing.py")
    assert gate_cli.cmd_check_gate11(tmp_path, _opts()) == 1
    assert calls == []
    assert "GATE11-FAIL" in capsys.readouterr().err


def test_gate11_force_refresh_propagates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "module.py"
    source.write_text("def f():\n    return 1\n", encoding="utf-8")
    _bundle(tmp_path, "module.py")
    calls = _mock_verifier(monkeypatch, "also-missing.py")
    assert gate_cli.cmd_check_gate11(tmp_path, _opts(force_refresh=True)) == 0
    assert len(calls) == 1
    assert calls[0].force_refresh is True
