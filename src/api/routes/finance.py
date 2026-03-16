"""Revenue and Payout routes."""

from fastapi import APIRouter, Depends, HTTPException

from src.models.finance import (
    RevenueCreate,
    RevenueResponse,
    PayoutRequest,
    PayoutResponse,
    BalanceResponse,
)
from src.core.database import Database
from src.api.dependencies import get_db, get_current_active_user, require_role

router = APIRouter()


@router.post("/revenue", response_model=RevenueResponse, status_code=201)
async def record_revenue(
    revenue: RevenueCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Record a revenue entry for a creator."""
    try:
        result = db.create_revenue(revenue.model_dump())
        return RevenueResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/balance/{creator_id}", response_model=BalanceResponse)
async def get_creator_balance(
    creator_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Get the financial balance for a creator."""
    try:
        balance = db.get_creator_balance(creator_id)
        return BalanceResponse(**balance)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payout", response_model=PayoutResponse, status_code=201)
async def request_payout(
    payout: PayoutRequest,
    current_user: dict = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Request a payout for a creator."""
    try:
        result = db.create_payout(payout.model_dump())
        return PayoutResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/payout/{payout_id}/approve", response_model=PayoutResponse)
async def approve_payout(
    payout_id: int,
    current_user: dict = Depends(require_role("manager")),
    db: Database = Depends(get_db),
):
    """Approve a payout. Manager or admin only."""
    try:
        result = db.approve_payout(payout_id, approved_by=current_user["id"])
        return PayoutResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
