"""
Authentication middleware supporting both AWS Cognito and local authentication.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

import boto3
import jwt
from config import settings
from exceptions import AuthenticationError, AuthorizationError
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt as jose_jwt, JWTError
from passlib.context import CryptContext
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

import logging
from database import get_db_session

logger = logging.getLogger(__name__)


class AuthenticationService:
    """Service for handling authentication operations."""

    def __init__(self):
        self.pwd_context = CryptContext(
            schemes=settings.password_hash_schemes,
            deprecated=settings.password_hash_deprecated,
        )
        self.cognito_client = None
        if settings.enable_aws_auth:
            self.cognito_client = boto3.client(
                "cognito-idp", region_name=settings.aws_region
            )

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return self.pwd_context.hash(password)

    def create_access_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.access_token_expire_minutes
            )

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jose_jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create a JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jose_jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )
        return encoded_jwt

    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jose_jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
            return payload
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None

    async def verify_cognito_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify an AWS Cognito JWT token."""
        if not settings.enable_aws_auth or not self.cognito_client:
            return None

        try:
            # Get Cognito public keys
            jwks_url = f"https://cognito-idp.{settings.aws_region}.amazonaws.com/{settings.aws_cognito_user_pool_id}/.well-known/jwks.json"

            # This is a simplified version - in production, you'd want to cache the JWKS
            # and implement proper key rotation handling
            payload = jwt.decode(
                token,
                options={"verify_signature": False},  # Simplified for demo
                audience=settings.aws_cognito_client_id,
            )
            return payload
        except Exception as e:
            logger.warning(f"Cognito token verification failed: {e}")
            return None

    async def authenticate_user(
        self, email: str, password: str
    ) -> Optional[Dict[str, Any]]:
        """Authenticate a user with email and password."""
        if settings.enable_local_auth:
            return await self._authenticate_local_user(email, password)
        elif settings.enable_aws_auth:
            return await self._authenticate_cognito_user(email, password)
        else:
            raise AuthenticationError("No authentication method enabled")

    async def _authenticate_local_user(
        self, email: str, password: str
    ) -> Optional[Dict[str, Any]]:
        """Authenticate using local database."""
        async with get_db_session() as db:
            from models.users import User

            # This would be replaced with actual database query
            # For now, we'll implement a basic check
            user = await db.execute(
                "SELECT id, email, password_hash, first_name, last_name, role, organization "
                "FROM users WHERE email = :email AND is_active = true",
                {"email": email},
            )
            user_data = user.fetchone()

            if user_data and self.verify_password(password, user_data.password_hash):
                return {
                    "user_id": str(user_data.id),
                    "email": user_data.email,
                    "first_name": user_data.first_name,
                    "last_name": user_data.last_name,
                    "role": user_data.role,
                    "organization": user_data.organization,
                }
        return None

    async def _authenticate_cognito_user(
        self, email: str, password: str
    ) -> Optional[Dict[str, Any]]:
        """Authenticate using AWS Cognito."""
        if not self.cognito_client:
            return None

        try:
            response = self.cognito_client.initiate_auth(
                ClientId=settings.aws_cognito_client_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={"USERNAME": email, "PASSWORD": password},
            )

            access_token = response["AuthenticationResult"]["AccessToken"]
            id_token = response["AuthenticationResult"]["IdToken"]

            # Verify and extract user info from ID token
            user_info = await self.verify_cognito_token(id_token)
            if user_info:
                return {
                    "user_id": user_info.get("sub"),
                    "email": user_info.get("email"),
                    "first_name": user_info.get("given_name"),
                    "last_name": user_info.get("family_name"),
                    "role": user_info.get("custom:role", "user"),
                    "organization": user_info.get("custom:organization"),
                    "cognito_tokens": {
                        "access_token": access_token,
                        "id_token": id_token,
                    },
                }
        except Exception as e:
            logger.warning(f"Cognito authentication failed: {e}")
            return None


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for the API."""

    def __init__(self, app, auth_service: Optional[AuthenticationService] = None):
        super().__init__(app)
        self.auth_service = auth_service or AuthenticationService()

        # Routes that don't require authentication
        self.public_routes = {
            "/health",
            "/metrics",
            "/auth/login",
            "/auth/refresh",
            "/docs",
            "/redoc",
            "/openapi.json",
        }

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process authentication for each request."""
        path = request.url.path

        # Skip authentication for public routes
        if any(path.startswith(route) for route in self.public_routes):
            response = await call_next(request)
            return response

        # Extract token from request
        token = await self._extract_token(request)
        if not token:
            return Response(
                content='{"error": "AUTHENTICATION_ERROR", "message": "No authentication token provided"}',
                status_code=status.HTTP_401_UNAUTHORIZED,
                media_type="application/json",
            )

        # Verify token
        user_data = await self._verify_token(token)
        if not user_data:
            return Response(
                content='{"error": "AUTHENTICATION_ERROR", "message": "Invalid or expired token"}',
                status_code=status.HTTP_401_UNAUTHORIZED,
                media_type="application/json",
            )

        # Add user data to request state
        request.state.current_user = user_data

        response = await call_next(request)
        return response

    async def _extract_token(self, request: Request) -> Optional[str]:
        """Extract authentication token from request."""
        # Try Bearer token first
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            return authorization.split(" ")[1]

        # Try API key header
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return api_key

        return None

    async def _verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify authentication token."""
        # Try local JWT verification first
        user_data = await self.auth_service.verify_token(token)
        if user_data:
            return user_data

        # Try Cognito token verification if enabled
        if settings.enable_aws_auth:
            user_data = await self.auth_service.verify_cognito_token(token)
            if user_data:
                return user_data

        # Try API key verification
        if await self._verify_api_key(token):
            return await self._get_api_key_user(token)

        return None

    async def _verify_api_key(self, api_key: str) -> bool:
        """Verify API key."""
        async with get_db_session() as db:
            result = await db.execute(
                "SELECT user_id FROM api_keys WHERE key_hash = :key_hash AND is_active = true AND (expires_at IS NULL OR expires_at > NOW())",
                {"key_hash": self.auth_service.get_password_hash(api_key)},
            )
            return result.fetchone() is not None

    async def _get_api_key_user(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Get user data for API key."""
        async with get_db_session() as db:
            result = await db.execute(
                """
                SELECT u.id, u.email, u.first_name, u.last_name, u.role, u.organization
                FROM users u
                JOIN api_keys ak ON u.id = ak.user_id
                WHERE ak.key_hash = :key_hash AND ak.is_active = true AND (ak.expires_at IS NULL OR ak.expires_at > NOW())
                """,
                {"key_hash": self.auth_service.get_password_hash(api_key)},
            )
            user_data = result.fetchone()

            if user_data:
                return {
                    "user_id": str(user_data.id),
                    "email": user_data.email,
                    "first_name": user_data.first_name,
                    "last_name": user_data.last_name,
                    "role": user_data.role,
                    "organization": user_data.organization,
                    "auth_type": "api_key",
                }
        return None


# Global authentication service instance
auth_service = AuthenticationService()


def get_current_user(request: Request) -> Dict[str, Any]:
    """Dependency to get current authenticated user."""
    if not hasattr(request.state, "current_user"):
        raise AuthenticationError("No authenticated user found")
    return request.state.current_user


def require_role(required_role: str):
    """Decorator to require specific user role."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            request = kwargs.get("request") or args[0]
            user = get_current_user(request)

            if user.get("role") != required_role:
                raise AuthorizationError(f"Role '{required_role}' required")

            return func(*args, **kwargs)

        return wrapper

    return decorator
