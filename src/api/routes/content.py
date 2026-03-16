"""Content generation and management routes."""

from fastapi import APIRouter, Depends, HTTPException, Query

from src.models.content import ContentGenerate, ContentCreate, ContentResponse, ContentApprove
from src.core.database import Database
from src.agents.content_agent import ContentAgent
from src.api.dependencies import get_db, get_current_active_user

router = APIRouter()

content_agent = ContentAgent()


@router.post("/generate", response_model=ContentResponse, status_code=201)
async def generate_content(
    params: ContentGenerate,
    current_user: dict = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Generate content using the ContentAgent."""
    try:
        result = await content_agent.generate_content(
            creator_id=params.creator_id,
            content_type=params.content_type,
            topic=params.topic,
            style=params.style or "casual",
            length=params.length or "medium",
            additional_context=params.additional_context,
            db=db,
        )
        content = db.create_content(result)
        return ContentResponse(**content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{creator_id}", response_model=list[ContentResponse])
async def list_content(
    creator_id: int,
    status: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """List content for a creator."""
    try:
        contents = db.list_content(creator_id, status=status, limit=limit)
        return [ContentResponse(**c) for c in contents]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/item/{content_id}", response_model=ContentResponse)
async def get_content_item(
    content_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Get a single content item by ID."""
    content = db.get_content_by_id(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content nicht gefunden")
    return ContentResponse(**content)


@router.put("/{content_id}/approve", response_model=ContentResponse)
async def approve_content(
    content_id: int,
    approval: ContentApprove,
    current_user: dict = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Approve or reject content."""
    content = db.get_content_by_id(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content nicht gefunden")

    approved_by = current_user["id"] if approval.status == "approved" else None
    db.update_content_status(content_id, approval.status, approved_by=approved_by)

    updated = db.get_content_by_id(content_id)
    return ContentResponse(**updated)
