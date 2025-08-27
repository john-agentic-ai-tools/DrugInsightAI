"""Company information endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, Path, Query
from middleware.auth import get_current_user

router = APIRouter()


@router.get("/", tags=["Companies"])
async def list_companies(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user=Depends(get_current_user),
):
    """Get paginated list of pharmaceutical companies."""
    return {"data": [], "meta": {"page": page, "limit": limit, "total": 0, "pages": 0}}


@router.get("/{company_id}", tags=["Companies"])
async def get_company_details(
    company_id: str = Path(...), current_user=Depends(get_current_user)
):
    """Get detailed company information."""
    return {"id": company_id, "name": "Example Company"}


@router.get("/{company_id}/pipeline", tags=["Companies"])
async def get_company_pipeline(
    company_id: str = Path(...), current_user=Depends(get_current_user)
):
    """Get company drug development pipeline."""
    return {
        "company_id": company_id,
        "pipeline_summary": {"total_drugs": 0},
        "drugs": [],
    }
