"""Content Pydantic models."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ContentGenerate(BaseModel):
    creator_id: int
    content_type: str = Field(..., pattern="^(caption|post|story|bio|message_template)$")
    topic: Optional[str] = None
    style: Optional[str] = Field(default="casual", pattern="^(casual|professional|playful|flirty|informative)$")
    length: Optional[str] = Field(default="medium", pattern="^(short|medium|long)$")
    additional_context: Optional[str] = None


class ContentCreate(BaseModel):
    creator_id: int
    content_type: str
    title: Optional[str] = None
    body: Optional[str] = None
    media_url: Optional[str] = None
    persona_tags: List[str] = []


class ContentResponse(BaseModel):
    id: int
    creator_id: int
    content_type: str
    title: Optional[str] = None
    body: Optional[str] = None
    media_url: Optional[str] = None
    persona_tags: List[str] = []
    status: str = "draft"
    approved_by: Optional[int] = None
    created_at: Optional[str] = None


class ContentApprove(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected)$")
    notes: Optional[str] = None


class ContentVariant(BaseModel):
    variant_id: int
    body: str
    style: str
    word_count: int
