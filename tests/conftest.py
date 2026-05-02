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
