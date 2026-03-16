"""Analytics routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any

from src.models.analytics import MetricCreate, MetricResponse, CreatorAnalytics
from src.core.database import Database
from src.api.dependencies import get_db, get_current_active_user

router = APIRouter()


@router.post("/metrics", response_model=MetricResponse, status_code=201)
async def record_metrics(
    metric: MetricCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Record metrics for content."""
    try:
        result = db.create_metric(metric.model_dump())
        return MetricResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/creator/{creator_id}", response_model=CreatorAnalytics)
async def get_creator_analytics(
    creator_id: int,
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Get aggregated analytics for a creator."""
    try:
        metrics = db.get_metrics_for_creator(creator_id, days=days)

        if not metrics:
            return CreatorAnalytics(
                creator_id=creator_id,
                period_days=days,
                total_posts=0,
                total_likes=0,
                total_comments=0,
                total_views=0,
                avg_engagement_rate=0.0,
                top_content=[],
            )

        total_posts = len(metrics)
        total_likes = sum(m.get("likes", 0) for m in metrics)
        total_comments = sum(m.get("comments", 0) for m in metrics)
        total_views = sum(m.get("views", 0) for m in metrics)
        avg_engagement = sum(m.get("engagement_rate", 0) for m in metrics) / total_posts if total_posts > 0 else 0.0

        # Top content by views
        sorted_metrics = sorted(metrics, key=lambda m: m.get("views", 0), reverse=True)
        top_content = [
            {"content_id": m["content_id"], "views": m["views"], "likes": m["likes"]}
            for m in sorted_metrics[:5]
        ]

        return CreatorAnalytics(
            creator_id=creator_id,
            period_days=days,
            total_posts=total_posts,
            total_likes=total_likes,
            total_comments=total_comments,
            total_views=total_views,
            avg_engagement_rate=round(avg_engagement, 4),
            top_content=top_content,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
