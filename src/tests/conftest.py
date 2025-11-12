"""Shared test fixtures and utilities."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir():
    """Get the fixtures directory path."""
    return Path(__file__).parent / "fixtures"


def load_fixture(fixtures_dir: Path, filename: str) -> dict:
    """Load a JSON fixture file."""
    with open(fixtures_dir / filename) as f:
        return json.load(f)
