"""Tests for IP Prefix API endpoints."""

import pytest
from unittest.mock import patch, MagicMock


class TestHealthCheck:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test that health check returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestPrefixList:
    """Tests for listing prefixes."""

    def test_list_prefixes_empty(self, client, mock_netbox_client):
        """Test listing prefixes when none exist."""
        mock_netbox_client.list_prefixes.return_value = []

        response = client.get("/api/v1/prefixes/")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_prefixes_with_data(
        self, client, mock_netbox_client, sample_prefix_response
    ):
        """Test listing prefixes with existing data."""
        mock_netbox_client.list_prefixes.return_value = [sample_prefix_response]

        response = client.get("/api/v1/prefixes/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["prefix"] == "10.0.0.0/24"

    def test_list_prefixes_with_filters(self, client, mock_netbox_client):
        """Test listing prefixes with query parameters."""
        mock_netbox_client.list_prefixes.return_value = []

        response = client.get("/api/v1/prefixes/?site_id=1&status=active")
        assert response.status_code == 200
        mock_netbox_client.list_prefixes.assert_called_once()


class TestPrefixCreate:
    """Tests for creating prefixes."""

    def test_create_prefix_success(
        self, client, mock_netbox_client, sample_prefix_data, sample_prefix_response
    ):
        """Test successful prefix creation."""
        mock_netbox_client.create_prefix.return_value = sample_prefix_response

        response = client.post("/api/v1/prefixes/", json=sample_prefix_data)
        assert response.status_code == 201
        data = response.json()
        assert data["prefix"] == "10.0.0.0/24"
        assert data["id"] == 1

    def test_create_prefix_invalid_cidr(self, client):
        """Test prefix creation with invalid CIDR."""
        invalid_data = {
            "prefix": "invalid-cidr",
            "status": "active",
        }

        response = client.post("/api/v1/prefixes/", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_create_prefix_invalid_status(self, client):
        """Test prefix creation with invalid status."""
        invalid_data = {
            "prefix": "10.0.0.0/24",
            "status": "invalid-status",
        }

        response = client.post("/api/v1/prefixes/", json=invalid_data)
        assert response.status_code == 422


class TestPrefixGet:
    """Tests for getting a single prefix."""

    def test_get_prefix_success(
        self, client, mock_netbox_client, sample_prefix_response
    ):
        """Test getting an existing prefix."""
        mock_netbox_client.get_prefix.return_value = sample_prefix_response

        response = client.get("/api/v1/prefixes/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["prefix"] == "10.0.0.0/24"

    def test_get_prefix_not_found(self, client, mock_netbox_client):
        """Test getting a non-existent prefix."""
        mock_netbox_client.get_prefix.return_value = None

        response = client.get("/api/v1/prefixes/999")
        assert response.status_code == 404


class TestPrefixDelete:
    """Tests for deleting prefixes."""

    def test_delete_prefix_success(self, client, mock_netbox_client):
        """Test successful prefix deletion."""
        mock_netbox_client.delete_prefix.return_value = True

        response = client.delete("/api/v1/prefixes/1")
        assert response.status_code == 204

    def test_delete_prefix_not_found(self, client, mock_netbox_client):
        """Test deleting a non-existent prefix."""
        mock_netbox_client.delete_prefix.return_value = False

        response = client.delete("/api/v1/prefixes/999")
        assert response.status_code == 404
