"""
Authentication-related Pydantic schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """User login request schema."""

    email: EmailStr
    password: str = Field(..., min_length=8)


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserProfile(BaseModel):
    """User profile response schema."""

    id: str
    email: str
    first_name: str
    last_name: str
    organization: Optional[str] = None
    role: str
    created_at: datetime
    updated_at: datetime


class UserProfileUpdate(BaseModel):
    """User profile update request schema."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    organization: Optional[str] = None
