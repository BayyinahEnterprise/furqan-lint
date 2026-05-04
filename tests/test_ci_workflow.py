"""Structural tests for the CI workflow configuration.

Verify the YAML file exists, parses cleanly, and exercises the
expected matrix and quality gates. These are not integration tests
of the workflow itself; they pin the structural promise that any
reorganisation of CI must preserve.

v0.8.4 expansion (commit 7): the test matrix grew from one
``test`` job to four (``test-python-only``, ``test-rust``,
``test-go``, ``test-full``). The em-dash check moved from
per-Python-version to once-only in the lint job. The
origin-tag-presence gate landed in the lint job.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit
yaml = pytest.importorskip("yaml")


REPO_ROOT = Path(__file__).resolve().parents[1]
CI_PATH = REPO_ROOT / ".github" / "workflows" / "ci.yml"


def _load_ci() -> dict:
    assert CI_PATH.is_file(), f"{CI_PATH} does not exist"
    with CI_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_ci_workflow_exists_and_is_valid_yaml() -> None:
    data = _load_ci()
    assert isinstance(data, dict)
    assert data.get("name") == "CI"
    assert "jobs" in data
    # v0.8.4: the canonical test job is renamed to test-python-only.
    assert "test-python-only" in data["jobs"]


def test_ci_workflow_tests_python_310_through_313() -> None:
    data = _load_ci()
    matrix = data["jobs"]["test-python-only"]["strategy"]["matrix"]
    versions = matrix["python-version"]
    # Each listed version must be present. Missing one would mean
    # a Python release went untested on every PR.
    for required in ["3.10", "3.11", "3.12", "3.13"]:
        assert required in versions, f"CI matrix is missing Python {required}; covers {versions}"


def test_ci_workflow_includes_version_sync() -> None:
    """The version-sync gate is the project's only barrier against
    shipping a release where __version__ and pyproject.toml
    disagree. Removing it would let the bug back in."""
    data = _load_ci()
    steps = data["jobs"]["test-python-only"]["steps"]
    step_names = " ".join(s.get("name", "") for s in steps)
    assert "Verify version sync" in step_names


def test_ci_workflow_includes_emdash_check() -> None:
    """The em-dash policy lives in the CI workflow, not in code, so
    the regex literal must appear in the workflow YAML.

    v0.4.1 also pins the locale prefix: ``LC_ALL=C.UTF-8`` is
    required because GNU grep -P fails on some default GitHub
    runner locales when the regex contains hex-escape sequences.

    v0.8.4 (commit 7): the check moves from the per-version test
    job to the once-only lint job. The literal still scans
    src/, tests/, README.md, and now also CHANGELOG.md and
    pyproject.toml; CODE_OF_CONDUCT.md is excluded as third-party
    verbatim text.
    """
    text = CI_PATH.read_text(encoding="utf-8")
    # Must scan src/, tests/, README.md per the documented policy.
    assert "src/" in text
    assert "tests/" in text
    assert "README.md" in text
    # The regex used to detect en-dash (U+2013) and em-dash (U+2014).
    assert "x{2013}" in text or "x{2014}" in text
    # Locale prefix added in v0.4.1.
    assert "LC_ALL=C.UTF-8" in text, (
        "Em-dash check must run under LC_ALL=C.UTF-8; "
        "without the locale prefix, GNU grep -P fails on "
        "some default GitHub runner locales"
    )


# ---------------------------------------------------------------------------
# v0.8.4 commit 7: matrix expansion + em-dash extension + origin-tag pin
# ---------------------------------------------------------------------------


def test_ci_workflow_has_full_extras_matrix() -> None:
    """v0.8.4: the test matrix expands to cover the no-extras,
    [rust]-only, [go]-only, and full-extras install paths. Each
    job runs the full pytest -q suite; the per-job differentiator
    is install-set only. Tests skip themselves based on extras
    availability via the §7.11-enforced skip-guards.

    Pinning all four job names defends against the round-22
    audit-coverage gap from PR #9: a CI matrix that only ran the
    no-extras path missed adapter-test failures that the local
    audit (with extras installed) had passed."""
    data = _load_ci()
    jobs = data["jobs"]
    for required_job in ("test-python-only", "test-rust", "test-go", "test-full"):
        assert required_job in jobs, (
            f"CI is missing the {required_job!r} job; the matrix expansion "
            f"is what closes round-22 HIGH 2."
        )


def test_ci_workflow_emdash_check_extends_to_changelog_and_pyproject() -> None:
    """v0.8.4: the em-dash check extends to CHANGELOG.md and
    pyproject.toml in addition to src/ tests/ README.md. Round-22
    repo-audit MEDIUM 2 found em-dashes in CHANGELOG and pyproject
    that the previous check did not catch. The extension closes
    that gap.

    The check also excludes CODE_OF_CONDUCT.md (Contributor
    Covenant v2.1 verbatim, third-party text excluded from the
    project-authored em-dash policy).
    """
    text = CI_PATH.read_text(encoding="utf-8")
    assert "CHANGELOG.md" in text
    assert "pyproject.toml" in text
    assert "--exclude=CODE_OF_CONDUCT.md" in text


def test_ci_workflow_emdash_check_lives_in_lint_job() -> None:
    """v0.8.4: the em-dash check moves from the test job to the
    lint job (once-only instead of per-Python-version). Pinning
    the location prevents a future reorganisation from accidentally
    re-introducing the four-times-per-CI-run shape."""
    data = _load_ci()
    lint_steps = data["jobs"]["lint"]["steps"]
    lint_step_names = [s.get("name", "") for s in lint_steps]
    assert (
        "Em-dash check" in lint_step_names
    ), f"Em-dash check must run in the lint job; found steps: {lint_step_names}"
    # And NOT in the test-python-only job (avoids redundant runs).
    test_steps = data["jobs"]["test-python-only"]["steps"]
    test_step_names = [s.get("name", "") for s in test_steps]
    assert "Em-dash check" not in test_step_names, (
        f"Em-dash check must NOT run in test-python-only; " f"found steps: {test_step_names}"
    )


def test_ci_workflow_runs_origin_tag_presence_gate() -> None:
    """v0.8.4: the origin-tag-presence gate (commit 6 script) runs
    in the lint job. The gate parses CHANGELOG.md for version
    headers and queries ``git ls-remote --tags origin`` to confirm
    every CHANGELOG-listed version has a tag pushed. This catches
    the round-22 patch-audit shape where v0.7.3 and v0.8.3 had been
    released without their tags being pushed."""
    data = _load_ci()
    lint_steps = data["jobs"]["lint"]["steps"]
    lint_step_names = [s.get("name", "") for s in lint_steps]
    assert "Origin tag presence gate" in lint_step_names, (
        f"Lint job must run the origin-tag-presence gate; " f"found steps: {lint_step_names}"
    )
    # The step must invoke the script we ship in scripts/.
    runs = " ".join(s.get("run", "") for s in lint_steps)
    assert (
        "scripts/verify_origin_tags.py" in runs
    ), "Origin-tag-presence gate must invoke scripts/verify_origin_tags.py"
