"""Pytest fixtures for OathNet SDK tests."""

import os

import pytest

from oathnet import OathNetClient


@pytest.fixture
def api_key() -> str:
    """Get API key from environment variable.

    Set the OATHNET_API_KEY environment variable before running tests:
        export OATHNET_API_KEY="your-api-key"
        pytest tests/ -v
    """
    key = os.environ.get("OATHNET_API_KEY")
    if not key:
        pytest.skip("OATHNET_API_KEY environment variable required for integration tests")
    return key


@pytest.fixture
def client(api_key: str) -> OathNetClient:
    """Create OathNet client for testing."""
    return OathNetClient(api_key)
