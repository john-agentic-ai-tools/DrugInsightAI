"""
Authentication endpoints.
"""

from datetime import timedelta

from exceptions import AuthenticationError
from fastapi import APIRouter, Depends, HTTPException, status
from middleware.auth import auth_service, AuthenticationService
from schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db_session

router = APIRouter()


@router.post("/login", response_model=TokenResponse, tags=["Authentication"])
async def login_user(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db_session),
    auth: AuthenticationService = Depends(lambda: auth_service),
):
    """
    Authenticate user and return access token.
    """
    # Authenticate user
    user_data = await auth.authenticate_user(login_data.email, login_data.password)
    if not user_data:
        raise AuthenticationError("Invalid email or password")

    # Create tokens
    token_data = {
        "sub": user_data["user_id"],
        "email": user_data["email"],
        "role": user_data["role"],
    }

    access_token = auth.create_access_token(token_data)
    refresh_token = auth.create_refresh_token({"sub": user_data["user_id"]})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=60 * 30,  # 30 minutes
    )


@router.post("/refresh", response_model=TokenResponse, tags=["Authentication"])
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    auth: AuthenticationService = Depends(lambda: auth_service),
):
    """
    Get a new access token using refresh token.
    """
    # Verify refresh token
    payload = await auth.verify_token(refresh_request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise AuthenticationError("Invalid or expired refresh token")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid refresh token payload")

    # Create new access token
    token_data = {
        "sub": user_id,
        "email": payload.get("email"),
        "role": payload.get("role"),
    }

    access_token = auth.create_access_token(token_data)

    return TokenResponse(access_token=access_token, expires_in=60 * 30)  # 30 minutes
