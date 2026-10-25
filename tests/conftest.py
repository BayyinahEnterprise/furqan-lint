"""Test fixtures shared across the suite."""

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES


@pytest.fixture
def clean_dir() -> Path:
    return FIXTURES / "clean"


@pytest.fixture
def failing_dir() -> Path:
    return FIXTURES / "failing"


# ---------------------------------------------------------------------------
# v1.0.1 audit F-02 follow-up: inline specimens must be compilable.
#
# ``ast.parse`` accepts some code that ``compile`` rejects (``return``
# inside ``except*``, ``return`` at module level). A verdict on code
# that cannot run is not evidence about code that can. Every inline
# source string a test hands to ``translate_source`` is compiled
# first; a test that needs uncompilable input must say so by calling
# ``furqan_lint.adapter._translate_source_unchecked``.
# ---------------------------------------------------------------------------

import warnings  # noqa: E402

import furqan_lint.adapter as _adapter  # noqa: E402

_adapter._translate_source_unchecked = _adapter.translate_source  # type: ignore[attr-defined]


def _translate_source_compiled(source: str, filename: str = "<string>"):  # type: ignore[no-untyped-def]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        compile(source, filename, "exec")
    return _adapter._translate_source_unchecked(source, filename)  # type: ignore[attr-defined]


_adapter.translate_source = _translate_source_compiled  # type: ignore[assignment]
