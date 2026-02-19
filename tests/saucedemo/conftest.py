"""Pytest fixtures for SauceDemo tests."""

import pytest


@pytest.fixture
def base_url() -> str:
    """Base URL for the SauceDemo application."""
    return "https://www.saucedemo.com"
