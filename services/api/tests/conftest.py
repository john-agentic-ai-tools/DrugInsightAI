"""
Pytest configuration and fixtures for API tests.
"""

import asyncio
import sys
from pathlib import Path

import fakeredis.aioredis
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import get_settings, Settings
from main import app
from middleware.auth import auth_service

from database import Base, database, get_db_session, get_redis_client


class TestSettings(Settings):
    """Test-specific settings."""

    environment: str = "testing"
    database_url: str = "sqlite+aiosqlite:///:memory:"
    redis_url: str = "redis://fake"
    enable_local_auth: bool = True
    enable_aws_auth: bool = False
    secret_key: str = "test-secret-key"


# Note: Using pytest-asyncio's built-in event loop instead of custom one


@pytest_asyncio.fixture(scope="function")
async def test_settings():
    """Override settings for testing."""
    original_get_settings = get_settings
    test_settings = TestSettings()

    # Override the get_settings function
    app.dependency_overrides[get_settings] = lambda: test_settings

    yield test_settings

    # Restore original settings
    if get_settings in app.dependency_overrides:
        del app.dependency_overrides[get_settings]


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Create test database."""
    # Create in-memory SQLite database for testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    async_session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Override database dependency
    async def override_get_db():
        async with async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db_session] = override_get_db

    yield async_session_factory

    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

    if get_db_session in app.dependency_overrides:
        del app.dependency_overrides[get_db_session]


@pytest_asyncio.fixture(scope="function")
async def test_redis():
    """Create fake Redis client for testing."""
    fake_redis = fakeredis.aioredis.FakeRedis()

    app.dependency_overrides[get_redis_client] = lambda: fake_redis

    yield fake_redis

    await fake_redis.aclose()

    if get_redis_client in app.dependency_overrides:
        del app.dependency_overrides[get_redis_client]


@pytest_asyncio.fixture(scope="function")
async def client(test_settings, test_db, test_redis):
    """Create test client."""
    from httpx import ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def authenticated_client(client, test_db):
    """Create authenticated test client."""
    # Create test user
    async with test_db() as session:
        from models.users import User

        test_user = User(
            email="test@example.com",
            password_hash=auth_service.get_password_hash("testpass123"),
            first_name="Test",
            last_name="User",
            role="user",
            is_active=True,
            is_verified=True,
        )
        session.add(test_user)
        await session.commit()
        await session.refresh(test_user)

        # Create access token
        token_data = {
            "sub": str(test_user.id),
            "email": test_user.email,
            "role": test_user.role,
        }
        access_token = auth_service.create_access_token(token_data)

    # Set authorization header
    client.headers.update({"Authorization": f"Bearer {access_token}"})

    yield client


@pytest.fixture
def sample_drug_data():
    """Sample drug data for testing."""
    return {
        "name": "Test Drug",
        "generic_name": "testdrug",
        "status": "approved",
        "therapeutic_area": "oncology",
        "indication": "Test indication",
        "description": "Test drug description",
    }


@pytest.fixture
def sample_company_data():
    """Sample company data for testing."""
    return {
        "name": "Test Pharmaceutical Inc.",
        "ticker": "TPHI",
        "country": "United States",
        "headquarters": "Boston, MA",
        "description": "Test pharmaceutical company",
    }
