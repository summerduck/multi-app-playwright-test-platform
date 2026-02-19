"""Pytest fixtures for The Internet tests."""

import pytest


@pytest.fixture
def base_url() -> str:
    """Base URL for The Internet application."""
    return "https://the-internet.herokuapp.com"
