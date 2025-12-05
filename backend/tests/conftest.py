"""Pytest fixtures for IPAM Backend tests."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    from app.main import app
    return TestClient(app)


@pytest.fixture
def mock_netbox_client():
    """Mock NetBox client for testing."""
    with patch("app.domain.services.prefix_service.get_netbox_client") as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        yield mock_client


@pytest.fixture
def sample_prefix_data():
    """Sample prefix data for testing."""
    return {
        "prefix": "10.0.0.0/24",
        "status": "active",
        "description": "Test prefix",
        "is_pool": False,
        "tags": ["test"],
    }


@pytest.fixture
def sample_prefix_response():
    """Sample prefix response from NetBox."""
    mock = MagicMock()
    mock.id = 1
    mock.prefix = "10.0.0.0/24"
    mock.status.value = "active"
    mock.description = "Test prefix"
    mock.site = None
    mock.tenant = None
    mock.vlan = None
    mock.role = None
    mock.is_pool = False
    mock.tags = []
    mock.created = "2025-12-05T10:00:00+00:00"
    mock.last_updated = "2025-12-05T10:00:00+00:00"
    return mock
