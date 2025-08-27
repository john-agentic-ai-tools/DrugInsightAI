"""
Tests for health check endpoints.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest_asyncio.fixture
async def client(client):
    """Override client to not require authentication for health checks."""
    return client


class TestHealthEndpoints:
    """Test health and monitoring endpoints."""

    @pytest.mark.asyncio
    async def test_health_check_success(self, client: AsyncClient):
        """Test successful health check."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "uptime" in data
        assert "dependencies" in data

        assert data["version"] == "0.1.0"
        assert isinstance(data["uptime"], int)
        assert data["uptime"] >= 0

    @pytest.mark.asyncio
    async def test_health_check_structure(self, client: AsyncClient):
        """Test health check response structure."""
        response = await client.get("/health")
        data = response.json()

        dependencies = data["dependencies"]
        assert "database" in dependencies
        assert "redis" in dependencies
        assert "external_apis" in dependencies

        # In test environment, we expect healthy or unhealthy status
        assert data["status"] in ["healthy", "degraded", "unhealthy"]

    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, client: AsyncClient):
        """Test metrics endpoint."""
        response = await client.get("/metrics")

        assert response.status_code == 200
        data = response.json()

        assert "requests_total" in data
        assert "requests_per_minute" in data
        assert "average_response_time" in data
        assert "error_rate" in data

        # Verify data types
        assert isinstance(data["requests_total"], int)
        assert isinstance(data["requests_per_minute"], float)
        assert isinstance(data["average_response_time"], float)
        assert isinstance(data["error_rate"], float)

    @pytest.mark.asyncio
    async def test_metrics_default_values(self, client: AsyncClient):
        """Test metrics endpoint returns default values when Redis unavailable."""
        response = await client.get("/metrics")
        data = response.json()

        # With fake Redis, we expect default values
        assert data["requests_total"] >= 0
        assert data["requests_per_minute"] >= 0.0
        assert data["average_response_time"] >= 0.0
        assert data["error_rate"] >= 0.0
