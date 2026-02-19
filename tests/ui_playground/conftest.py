"""Pytest fixtures for UI Playground tests."""

import pytest


@pytest.fixture
def base_url() -> str:
    """Base URL for the UI Playground application."""
    return "http://uitestingplayground.com"
