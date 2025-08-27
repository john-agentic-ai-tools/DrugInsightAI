"""
Health check and monitoring endpoints.
"""

import time
from datetime import datetime
from typing import Any, Dict

import redis.asyncio as redis
from config import settings
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from database import check_database_health, check_redis_health, get_redis_client

router = APIRouter()


class HealthStatus(BaseModel):
    """Health status response model."""

    status: str
    timestamp: datetime
    version: str
    uptime: int
    dependencies: Dict[str, str]


class ApiMetrics(BaseModel):
    """API metrics response model."""

    requests_total: int
    requests_per_minute: float
    average_response_time: float
    error_rate: float


# Store start time for uptime calculation
START_TIME = time.time()


@router.get("/health", response_model=HealthStatus, tags=["Health"])
async def get_health_status():
    """
    Health check endpoint that returns the current status of the API service.
    """
    # Check dependencies
    db_healthy = await check_database_health()
    redis_healthy = await check_redis_health()

    # Determine overall status
    if db_healthy and redis_healthy:
        status = "healthy"
    elif db_healthy or redis_healthy:
        status = "degraded"
    else:
        status = "unhealthy"

    return HealthStatus(
        status=status,
        timestamp=datetime.utcnow(),
        version="0.1.0",
        uptime=int(time.time() - START_TIME),
        dependencies={
            "database": "healthy" if db_healthy else "unhealthy",
            "redis": "healthy" if redis_healthy else "unhealthy",
            "external_apis": "unknown",  # Would check external APIs in production
        },
    )


@router.get("/metrics", response_model=ApiMetrics, tags=["Health"])
async def get_metrics(redis_client: redis.Redis = Depends(get_redis_client)):
    """
    Get current API performance and usage metrics.
    """
    try:
        # Get metrics from Redis (these would be updated by middleware)
        requests_total = await redis_client.get("metrics:requests_total") or 0
        requests_per_minute = (
            await redis_client.get("metrics:requests_per_minute") or 0.0
        )
        average_response_time = (
            await redis_client.get("metrics:avg_response_time") or 0.0
        )
        error_rate = await redis_client.get("metrics:error_rate") or 0.0

        return ApiMetrics(
            requests_total=int(requests_total),
            requests_per_minute=float(requests_per_minute),
            average_response_time=float(average_response_time),
            error_rate=float(error_rate),
        )
    except Exception:
        # Return default values if Redis is unavailable
        return ApiMetrics(
            requests_total=0,
            requests_per_minute=0.0,
            average_response_time=0.0,
            error_rate=0.0,
        )
