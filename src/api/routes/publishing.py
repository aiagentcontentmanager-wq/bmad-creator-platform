"""Publishing and scheduling routes."""

from fastapi import APIRouter, Depends, HTTPException, Query

from src.models.analytics import SchedulePost, PublishResponse
from src.core.database import Database
from src.api.dependencies import get_db, get_current_active_user

router = APIRouter()


@router.post("/schedule", response_model=PublishResponse, status_code=201)
async def schedule_post(
    schedule: SchedulePost,
    current_user: dict = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Schedule a post for publishing."""
    try:
        entry = db.create_publish_entry({
            "content_id": schedule.content_id,
            "platform": schedule.platform,
            "scheduled_at": schedule.scheduled_at,
            "status": "scheduled",
        })
        return PublishResponse(**entry)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue", response_model=list[PublishResponse])
async def get_scheduled_posts(
    status: str = Query("scheduled"),
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Get scheduled posts from the publishing queue."""
    try:
        posts = db.get_scheduled_posts(status=status, limit=limit)
        return [PublishResponse(**p) for p in posts]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{entry_id}/status", response_model=PublishResponse)
async def get_publish_status(
    entry_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Get the publish status of a scheduled entry."""
    row = db.conn.execute(
        "SELECT * FROM publish_queue WHERE id = ?", (entry_id,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Publish-Eintrag nicht gefunden")
    return PublishResponse(**dict(row))
