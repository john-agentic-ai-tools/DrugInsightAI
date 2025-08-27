"""User profile management endpoints."""

from fastapi import APIRouter, Depends, Request
from middleware.auth import get_current_user
from schemas.auth import UserProfile, UserProfileUpdate

router = APIRouter()


@router.get("/profile", response_model=UserProfile, tags=["Users"])
async def get_current_user_profile(current_user=Depends(get_current_user)):
    """Get current user profile."""
    return UserProfile(**current_user, id=current_user["user_id"])


@router.patch("/profile", response_model=UserProfile, tags=["Users"])
async def update_user_profile(
    profile_update: UserProfileUpdate, current_user=Depends(get_current_user)
):
    """Update user profile."""
    # Implementation would update database
    return UserProfile(**current_user, id=current_user["user_id"])
