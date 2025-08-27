"""
Tests for authentication endpoints.
"""

import sys
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import AsyncClient

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from middleware.auth import auth_service


class TestAuthenticationEndpoints:
    """Test authentication and token management endpoints."""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_db):
        """Test successful login."""
        # Create test user
        async with test_db() as session:
            from models.users import User

            test_user = User(
                email="testuser@example.com",
                password_hash=auth_service.get_password_hash("password123"),
                first_name="Test",
                last_name="User",
                role="user",
                is_active=True,
                is_verified=True,
            )
            session.add(test_user)
            await session.commit()

        # Test login
        response = await client.post(
            "/auth/login",
            json={"email": "testuser@example.com", "password": "password123"},
        )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert "expires_in" in data

        assert data["token_type"] == "bearer"
        assert isinstance(data["expires_in"], int)
        assert data["expires_in"] > 0

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient, test_db):
        """Test login with invalid credentials."""
        # Create test user
        async with test_db() as session:
            from models.users import User

            test_user = User(
                email="testuser@example.com",
                password_hash=auth_service.get_password_hash("password123"),
                first_name="Test",
                last_name="User",
                role="user",
                is_active=True,
                is_verified=True,
            )
            session.add(test_user)
            await session.commit()

        # Test login with wrong password
        response = await client.post(
            "/auth/login",
            json={"email": "testuser@example.com", "password": "wrongpassword"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert "message" in data

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user."""
        response = await client.post(
            "/auth/login",
            json={"email": "nonexistent@example.com", "password": "password123"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data

    @pytest.mark.asyncio
    async def test_login_invalid_email_format(self, client: AsyncClient):
        """Test login with invalid email format."""
        response = await client.post(
            "/auth/login", json={"email": "invalid-email", "password": "password123"}
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client: AsyncClient, test_db):
        """Test successful token refresh."""
        # Create test user and get tokens
        async with test_db() as session:
            from models.users import User

            test_user = User(
                email="testuser@example.com",
                password_hash=auth_service.get_password_hash("password123"),
                first_name="Test",
                last_name="User",
                role="user",
                is_active=True,
                is_verified=True,
            )
            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)

            # Create refresh token
            token_data = {"sub": str(test_user.id)}
            refresh_token = auth_service.create_refresh_token(token_data)

        # Test token refresh
        response = await client.post(
            "/auth/refresh", json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "token_type" in data
        assert "expires_in" in data

        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test refresh with invalid token."""
        response = await client.post(
            "/auth/refresh", json={"refresh_token": "invalid-token"}
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data

    @pytest.mark.asyncio
    async def test_refresh_token_access_token_provided(
        self, client: AsyncClient, test_db
    ):
        """Test refresh with access token instead of refresh token."""
        # Create test user and get access token
        async with test_db() as session:
            from models.users import User

            test_user = User(
                email="testuser@example.com",
                password_hash=auth_service.get_password_hash("password123"),
                first_name="Test",
                last_name="User",
                role="user",
                is_active=True,
                is_verified=True,
            )
            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)

            # Create access token (not refresh token)
            token_data = {
                "sub": str(test_user.id),
                "email": test_user.email,
                "role": test_user.role,
            }
            access_token = auth_service.create_access_token(token_data)

        # Test refresh with access token
        response = await client.post(
            "/auth/refresh", json={"refresh_token": access_token}
        )

        assert (
            response.status_code == 401
        )  # Should fail because it's not a refresh token
