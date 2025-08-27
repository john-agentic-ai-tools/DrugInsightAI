"""Clinical trials endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, Path, Query
from middleware.auth import get_current_user

router = APIRouter()


@router.get("/", tags=["Clinical Trials"])
async def list_clinical_trials(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    drug_id: Optional[str] = Query(None),
    phase: Optional[str] = Query(None),
    current_user=Depends(get_current_user),
):
    """Get paginated list of clinical trials."""
    return {"data": [], "meta": {"page": page, "limit": limit, "total": 0, "pages": 0}}


@router.get("/{trial_id}", tags=["Clinical Trials"])
async def get_clinical_trial_details(
    trial_id: str = Path(...), current_user=Depends(get_current_user)
):
    """Get detailed clinical trial information."""
    return {"id": trial_id, "title": "Example Trial"}
