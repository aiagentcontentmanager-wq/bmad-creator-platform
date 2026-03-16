"""Analytics & Publishing Pydantic models."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class SchedulePost(BaseModel):
    content_id: int
    platform: str = Field(..., pattern="^(instagram|twitter|telegram)$")
    scheduled_at: str


class PublishResponse(BaseModel):
    id: int
    content_id: int
    platform: str
    scheduled_at: str
    status: str
    platform_post_id: Optional[str] = None


class MetricCreate(BaseModel):
    content_id: int
    platform: str
    likes: int = 0
    comments: int = 0
    shares: int = 0
    views: int = 0


class MetricResponse(BaseModel):
    id: int
    content_id: int
    platform: str
    likes: int
    comments: int
    shares: int
    views: int
    engagement_rate: float
    collected_at: Optional[str] = None


class CreatorAnalytics(BaseModel):
    creator_id: int
    period_days: int
    total_posts: int
    total_likes: int
    total_comments: int
    total_views: int
    avg_engagement_rate: float
    top_content: List[Dict[str, Any]]


class AssistantSuggestion(BaseModel):
    creator_id: int
    fan_identifier: str
    fan_message: str
    conversation_history: Optional[List[Dict[str, str]]] = None


class AssistantSuggestionResponse(BaseModel):
    suggestion: str
    tone: str
    alternatives: List[str]
    conversation_id: int
