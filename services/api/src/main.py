"""
Main FastAPI application module for DrugInsightAI API service.
"""

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from config import settings
from exceptions import register_exception_handlers
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from middleware.auth import AuthMiddleware
from middleware.logging import LoggingMiddleware
from routes import auth, clinical_trials, companies, drugs, health, market, users

import logging
from database import database

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    logger.info("Starting DrugInsightAI API service...")
    await database.connect()
    logger.info("Database connection established")

    yield

    # Shutdown
    logger.info("Shutting down DrugInsightAI API service...")
    await database.disconnect()
    logger.info("Database connection closed")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="DrugInsightAI API",
        description="""
        REST API service for the DrugInsightAI pharmaceutical data analysis platform.

        This API provides endpoints for:
        - Drug information and analytics
        - Clinical trial data
        - Pharmaceutical company insights
        - Market analysis
        - User management and authentication
        """,
        version="0.1.0",
        contact={
            "name": "DrugInsightAI Team",
            "email": "support@druginsightai.com",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        lifespan=lifespan,
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url="/redoc" if settings.environment != "production" else None,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add custom middleware
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(AuthMiddleware)

    # Register exception handlers
    register_exception_handlers(app)

    # Add request timing middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

    # Register routes
    app.include_router(health.router, tags=["Health"])
    app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    app.include_router(users.router, prefix="/users", tags=["Users"])
    app.include_router(drugs.router, prefix="/drugs", tags=["Drugs"])
    app.include_router(
        clinical_trials.router, prefix="/clinical-trials", tags=["Clinical Trials"]
    )
    app.include_router(companies.router, prefix="/companies", tags=["Companies"])
    app.include_router(market.router, prefix="/market", tags=["Market Analysis"])

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        log_level="info",
    )
