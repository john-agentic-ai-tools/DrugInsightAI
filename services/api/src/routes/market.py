"""Market analysis endpoints."""

from fastapi import APIRouter, Depends, Query
from middleware.auth import get_current_user

router = APIRouter()


@router.get("/therapeutic-areas", tags=["Market Analysis"])
async def get_therapeutic_areas_market(current_user=Depends(get_current_user)):
    """Get market analysis data for therapeutic areas."""
    return {"data": []}


@router.get("/trends", tags=["Market Analysis"])
async def get_market_trends(
    time_period: str = Query("1y"), current_user=Depends(get_current_user)
):
    """Get current pharmaceutical market trends."""
    return {"period": time_period, "trends": [], "overall_growth": 0.0}
