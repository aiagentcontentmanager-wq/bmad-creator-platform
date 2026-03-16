"""Finance Pydantic models."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class RevenueCreate(BaseModel):
    creator_id: int
    source: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    currency: str = Field(default="EUR", max_length=3)
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    notes: Optional[str] = None


class RevenueResponse(BaseModel):
    id: int
    creator_id: int
    source: str
    amount: float
    currency: str
    created_at: Optional[str] = None


class PayoutRequest(BaseModel):
    creator_id: int
    amount: float = Field(..., gt=0)
    notes: Optional[str] = None


class PayoutResponse(BaseModel):
    id: int
    creator_id: int
    amount: float
    commission: float
    net_amount: float
    status: str
    requested_at: Optional[str] = None


class BalanceResponse(BaseModel):
    creator_id: int
    total_revenue: float
    total_paid_out: float
    pending_payouts: float
    available_balance: float


class CommissionConfig(BaseModel):
    commission_rate: float = Field(..., ge=0.0, le=1.0)
