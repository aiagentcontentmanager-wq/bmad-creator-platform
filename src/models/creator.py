"""Creator Pydantic models."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class CreatorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    platform: Optional[str] = None
    persona: Optional[Dict[str, Any]] = None
    language: str = Field(default="en", max_length=5)
    consent: bool = False


class CreatorUpdate(BaseModel):
    name: Optional[str] = None
    platform: Optional[str] = None
    persona: Optional[Dict[str, Any]] = None
    language: Optional[str] = None
    status: Optional[str] = None


class CreatorResponse(BaseModel):
    id: int
    user_id: int
    name: str
    platform: Optional[str] = None
    persona: Optional[Dict[str, Any]] = None
    language: str = "en"
    consent: bool = False
    status: str = "active"
    created_at: Optional[str] = None


class CreatorListResponse(BaseModel):
    creators: List[CreatorResponse]
    total: int
