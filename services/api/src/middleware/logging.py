"""
Logging middleware for request/response tracking.
"""

import time
import uuid
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

import logging

logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""

    def __init__(self, app, logger_name: str = "api"):
        super().__init__(app)
        self.logger = logging.getLogger(logger_name)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response information."""
        # Generate request ID for tracing
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Extract client information
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Log request start
        start_time = time.time()
        self.logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_ip": client_ip,
                "user_agent": user_agent,
                "headers": dict(request.headers),
            },
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Log successful response
            self.logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time": process_time,
                    "response_headers": dict(response.headers),
                },
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Calculate processing time for failed requests
            process_time = time.time() - start_time

            # Log error
            self.logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "process_time": process_time,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )

            raise
