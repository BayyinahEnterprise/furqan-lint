"""Structural tests for the GitHub Action and pre-commit hook
configuration files.

These tests verify that the YAML files exist, parse cleanly, and
have the shape downstream consumers depend on. They do NOT execute
the action or the hook - that requires GitHub's runner or a
pre-commit installation, both out of scope for unit testing.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load(rel_path: str):
    path = REPO_ROOT / rel_path
    assert path.is_file(), f"{rel_path} does not exist"
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f), path


# ---------------------------------------------------------------------------
# action.yml
# ---------------------------------------------------------------------------

def test_action_yml_exists_and_is_valid_yaml() -> None:
    data, path = _load("action.yml")
    assert isinstance(data, dict)
    assert data.get("name"), "action.yml must declare a name"
    assert data.get("description"), "action.yml must declare a description"


def test_action_yml_has_required_inputs() -> None:
    data, _ = _load("action.yml")
    inputs = data.get("inputs", {})
    assert "path" in inputs
    assert "python-version" in inputs
    # Inputs MUST be optional with sensible defaults so a user can
    # adopt the action with three lines of YAML and zero required
    # input.
    assert inputs["path"].get("required") is False
    assert inputs["python-version"].get("required") is False
    assert inputs["path"].get("default") == "."


def test_action_yml_uses_composite_runs() -> None:
    """The action is a composite of standard setup-python +
    install + run steps. Avoids needing a Docker image."""
    data, _ = _load("action.yml")
    runs = data.get("runs", {})
    assert runs.get("using") == "composite"
    steps = runs.get("steps", [])
    assert len(steps) >= 3
    # The last step must be the actual furqan-lint invocation.
    last = steps[-1]
    assert "furqan-lint check" in last.get("run", "")


def test_action_pins_furqan_lint_to_action_ref() -> None:
    """The action installs furqan-lint at ``github.action_ref`` so
    a user pinning the action to a specific tag (e.g.,
    ``uses: BayyinahEnterprise/furqan-lint@v0.4.1``) gets the
    matching code from that tag, not whatever happens to be on
    main at install time. Without this pin the action silently
    drifts: yesterday's pin runs today's main.
    """
    text = (REPO_ROOT / "action.yml").read_text(encoding="utf-8")
    assert "github.action_ref" in text, (
        "action.yml does not pin furqan-lint to action_ref; "
        "users pinning the action to a tag will silently get "
        "main-branch code"
    )


# ---------------------------------------------------------------------------
# .pre-commit-hooks.yaml
# ---------------------------------------------------------------------------

def test_pre_commit_hooks_yaml_exists_and_is_valid() -> None:
    data, _ = _load(".pre-commit-hooks.yaml")
    assert isinstance(data, list)
    assert len(data) == 1


def test_pre_commit_hooks_yaml_entry_is_furqan_lint_check() -> None:
    data, _ = _load(".pre-commit-hooks.yaml")
    hook = data[0]
    assert hook["id"] == "furqan-lint"
    assert hook["entry"] == "furqan-lint check"
    assert hook["language"] == "python"
    # Hook must scope to .py files; running on every file would be
    # noisy and slow.
    assert hook["types"] == ["python"]



def test_pre_commit_hooks_yaml_declares_furqan_dependency() -> None:
    """The pre-commit hook must declare ``furqan`` as an
    ``additional_dependency`` because pyproject.toml's
    ``furqan>=0.11.0`` constraint cannot be satisfied from PyPI
    (only 0.10.1 is available there). Without this, ``pre-commit
    install`` succeeds but the first hook run fails with an
    unresolvable resolver error. Static test, no network.
    """
    data, _ = _load(".pre-commit-hooks.yaml")
    deps = data[0].get("additional_dependencies", [])
    assert any("furqan" in d for d in deps), (
        "Pre-commit hook missing furqan in additional_dependencies; "
        "install will fail because furqan is not on PyPI"
    )


@pytest.mark.slow
@pytest.mark.network
def test_pre_commit_hook_installs_in_clean_venv(tmp_path) -> None:
    """Functional smoke test: verify the hook's declared
    dependencies actually resolve in a clean venv. Network and
    PyPI required; skip with ``pytest -m "not network"``.

    Recreates what pre-commit does internally: builds a venv,
    pip-installs the additional_dependencies plus the project,
    asserts success.
    """
    venv_dir = tmp_path / "venv"
    subprocess.run(
        [sys.executable, "-m", "venv", str(venv_dir)],
        check=True,
        timeout=60,
    )
    pip = venv_dir / "bin" / "pip"
    if not pip.exists():
        # Windows path; skip rather than misdiagnose
        pytest.skip("non-posix venv layout")
    result = subprocess.run(
        [
            str(pip),
            "install",
            "furqan @ git+https://github.com/BayyinahEnterprise/furqan-programming-language.git@v0.11.1",
            "-e",
            str(REPO_ROOT),
        ],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, (
        f"Install failed in clean venv:\n{result.stderr}"
    )
