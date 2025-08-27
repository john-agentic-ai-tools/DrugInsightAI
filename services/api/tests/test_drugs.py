"""
Tests for drug information endpoints.
"""

import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient


class TestDrugEndpoints:
    """Test drug information and analytics endpoints."""

    @pytest.mark.asyncio
    async def test_list_drugs_default_params(self, authenticated_client: AsyncClient):
        """Test listing drugs with default parameters."""
        response = await authenticated_client.get("/drugs/")

        assert response.status_code == 200
        data = response.json()

        assert "data" in data
        assert "meta" in data
        assert isinstance(data["data"], list)

        meta = data["meta"]
        assert "page" in meta
        assert "limit" in meta
        assert "total" in meta
        assert "pages" in meta

        assert meta["page"] == 1
        assert meta["limit"] == 20

    @pytest.mark.asyncio
    async def test_list_drugs_custom_pagination(
        self, authenticated_client: AsyncClient
    ):
        """Test listing drugs with custom pagination."""
        response = await authenticated_client.get("/drugs/?page=2&limit=10")

        assert response.status_code == 200
        data = response.json()

        meta = data["meta"]
        assert meta["page"] == 2
        assert meta["limit"] == 10

    @pytest.mark.asyncio
    async def test_list_drugs_with_search(self, authenticated_client: AsyncClient):
        """Test listing drugs with search parameter."""
        response = await authenticated_client.get("/drugs/?search=cancer")

        assert response.status_code == 200
        data = response.json()

        assert "data" in data
        assert "meta" in data

    @pytest.mark.asyncio
    async def test_list_drugs_with_therapeutic_area(
        self, authenticated_client: AsyncClient
    ):
        """Test listing drugs filtered by therapeutic area."""
        response = await authenticated_client.get("/drugs/?therapeutic_area=oncology")

        assert response.status_code == 200
        data = response.json()

        assert "data" in data
        assert "meta" in data

    @pytest.mark.asyncio
    async def test_list_drugs_invalid_page(self, authenticated_client: AsyncClient):
        """Test listing drugs with invalid page parameter."""
        response = await authenticated_client.get("/drugs/?page=0")

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_list_drugs_invalid_limit(self, authenticated_client: AsyncClient):
        """Test listing drugs with invalid limit parameter."""
        response = await authenticated_client.get("/drugs/?limit=101")  # Exceeds max

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_drug_details_success(self, authenticated_client: AsyncClient):
        """Test getting drug details with valid ID."""
        drug_id = str(uuid.uuid4())
        response = await authenticated_client.get(f"/drugs/{drug_id}")

        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert "name" in data
        assert data["id"] == drug_id

    @pytest.mark.asyncio
    async def test_get_drug_details_invalid_uuid(
        self, authenticated_client: AsyncClient
    ):
        """Test getting drug details with invalid UUID format."""
        response = await authenticated_client.get("/drugs/invalid-uuid")

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_drug_analytics_default(self, authenticated_client: AsyncClient):
        """Test getting drug analytics with default parameters."""
        drug_id = str(uuid.uuid4())
        response = await authenticated_client.get(f"/drugs/{drug_id}/analytics")

        assert response.status_code == 200
        data = response.json()

        assert "drug_id" in data
        assert "analytics" in data
        assert data["drug_id"] == drug_id

    @pytest.mark.asyncio
    async def test_get_drug_analytics_custom_period(
        self, authenticated_client: AsyncClient
    ):
        """Test getting drug analytics with custom time period."""
        drug_id = str(uuid.uuid4())
        response = await authenticated_client.get(
            f"/drugs/{drug_id}/analytics?time_period=1y"
        )

        assert response.status_code == 200
        data = response.json()

        assert "drug_id" in data
        assert "analytics" in data

    @pytest.mark.asyncio
    async def test_get_drug_adverse_events_default(
        self, authenticated_client: AsyncClient
    ):
        """Test getting adverse events with default parameters."""
        drug_id = str(uuid.uuid4())
        response = await authenticated_client.get(f"/drugs/{drug_id}/adverse-events")

        assert response.status_code == 200
        data = response.json()

        assert "data" in data
        assert "meta" in data

        meta = data["meta"]
        assert meta["page"] == 1
        assert meta["limit"] == 50

    @pytest.mark.asyncio
    async def test_get_drug_adverse_events_custom_pagination(
        self, authenticated_client: AsyncClient
    ):
        """Test getting adverse events with custom pagination."""
        drug_id = str(uuid.uuid4())
        response = await authenticated_client.get(
            f"/drugs/{drug_id}/adverse-events?page=2&limit=100"
        )

        assert response.status_code == 200
        data = response.json()

        meta = data["meta"]
        assert meta["page"] == 2
        assert meta["limit"] == 100

    @pytest.mark.asyncio
    async def test_get_new_drugs_default(self, authenticated_client: AsyncClient):
        """Test getting new drugs with default parameters."""
        response = await authenticated_client.get("/drugs/new")

        assert response.status_code == 200
        data = response.json()

        assert "data" in data
        assert "meta" in data

        meta = data["meta"]
        assert meta["page"] == 1
        assert meta["limit"] == 20

    @pytest.mark.asyncio
    async def test_get_new_drugs_custom_params(self, authenticated_client: AsyncClient):
        """Test getting new drugs with custom parameters."""
        response = await authenticated_client.get("/drugs/new?days_back=7&limit=10")

        assert response.status_code == 200
        data = response.json()

        assert "data" in data
        assert "meta" in data

    @pytest.mark.asyncio
    async def test_get_new_drugs_invalid_days_back(
        self, authenticated_client: AsyncClient
    ):
        """Test getting new drugs with invalid days_back parameter."""
        response = await authenticated_client.get("/drugs/new?days_back=0")

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_all_drug_endpoints_require_auth(self, client: AsyncClient):
        """Test that all drug endpoints require authentication."""
        endpoints = [
            "/drugs/",
            f"/drugs/{uuid.uuid4()}",
            f"/drugs/{uuid.uuid4()}/analytics",
            f"/drugs/{uuid.uuid4()}/adverse-events",
            "/drugs/new",
        ]

        for endpoint in endpoints:
            response = await client.get(endpoint)
            assert (
                response.status_code == 401
            ), f"Endpoint {endpoint} should require authentication"
