"""Drug information endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, Path, Query
from middleware.auth import get_current_user

router = APIRouter()


@router.get("/", tags=["Drugs"])
async def list_drugs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    therapeutic_area: Optional[str] = Query(None),
    current_user=Depends(get_current_user),
):
    """Get paginated list of drugs with optional filtering."""
    # Implementation would query database
    return {"data": [], "meta": {"page": page, "limit": limit, "total": 0, "pages": 0}}


@router.get("/{drug_id}", tags=["Drugs"])
async def get_drug_details(
    drug_id: str = Path(...), current_user=Depends(get_current_user)
):
    """Get detailed information about a specific drug."""
    # Implementation would query database
    return {"id": drug_id, "name": "Example Drug"}


@router.get("/{drug_id}/analytics", tags=["Drugs"])
async def get_drug_analytics(
    drug_id: str = Path(...),
    time_period: str = Query("6m"),
    current_user=Depends(get_current_user),
):
    """Get analytical insights and metrics for a drug."""
    return {"drug_id": drug_id, "analytics": {}}


@router.get("/{drug_id}/adverse-events", tags=["Drugs"])
async def get_drug_adverse_events(
    drug_id: str = Path(...),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    current_user=Depends(get_current_user),
):
    """Get adverse event data for a drug."""
    return {"data": [], "meta": {"page": page, "limit": limit, "total": 0, "pages": 0}}


@router.get("/new", tags=["Drugs"])
async def get_new_drugs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    days_back: int = Query(30, ge=1, le=365),
    current_user=Depends(get_current_user),
):
    """Get recently added drug entries."""
    return {"data": [], "meta": {"page": page, "limit": limit, "total": 0, "pages": 0}}
