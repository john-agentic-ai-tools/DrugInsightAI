"""
Database configuration and connection management.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

import redis.asyncio as redis
from config import get_database_url, settings
from sqlalchemy import create_engine, event, pool
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

import logging

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self):
        self.engine = None
        self.async_session_factory = None
        self.redis_client = None
        self._database_url = get_database_url()

    async def connect(self):
        """Initialize database and Redis connections."""
        try:
            # Create async database engine
            # Convert postgresql:// to postgresql+asyncpg:// for async support
            async_url = self._database_url.replace(
                "postgresql://", "postgresql+asyncpg://"
            )

            self.engine = create_async_engine(
                async_url,
                pool_size=settings.database_pool_size,
                max_overflow=settings.database_max_overflow,
                pool_pre_ping=settings.database_pool_pre_ping,
                echo=settings.debug,
            )

            # Create session factory
            self.async_session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

            # Test database connection
            async with self.engine.begin() as conn:
                await conn.execute("SELECT 1")

            logger.info("Database connection established successfully")

            # Initialize Redis connection
            self.redis_client = redis.from_url(
                settings.redis_url,
                max_connections=settings.redis_max_connections,
                decode_responses=True,
            )

            # Test Redis connection
            await self.redis_client.ping()
            logger.info("Redis connection established successfully")

        except Exception as e:
            logger.error(f"Failed to connect to database or Redis: {e}")
            raise

    async def disconnect(self):
        """Close database and Redis connections."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connection closed")

        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session context manager."""
        if not self.async_session_factory:
            raise RuntimeError("Database not connected. Call connect() first.")

        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def get_redis(self) -> redis.Redis:
        """Get Redis client."""
        if not self.redis_client:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self.redis_client


# Global database manager instance
database = DatabaseManager()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session in FastAPI routes."""
    async with database.get_session() as session:
        yield session


async def get_redis_client() -> redis.Redis:
    """Dependency to get Redis client in FastAPI routes."""
    return await database.get_redis()


# Health check functions
async def check_database_health() -> bool:
    """Check if database is accessible."""
    try:
        if not database.engine:
            return False

        async with database.engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def check_redis_health() -> bool:
    """Check if Redis is accessible."""
    try:
        if not database.redis_client:
            return False

        await database.redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return False
