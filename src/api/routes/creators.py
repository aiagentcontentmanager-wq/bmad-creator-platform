"""Creator CRUD routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List

from src.models.creator import CreatorCreate, CreatorUpdate, CreatorResponse, CreatorListResponse
from src.core.database import Database
from src.api.dependencies import get_db, get_current_active_user, require_role

router = APIRouter()


@router.post("/", response_model=CreatorResponse, status_code=201)
async def create_creator(
    creator_data: CreatorCreate,
    current_user: dict = Depends(require_role("manager")),
    db: Database = Depends(get_db),
):
    """Create a new creator profile. Manager or admin only."""
    try:
        data = creator_data.model_dump()
        data["user_id"] = current_user["id"]
        creator = db.create_creator(data)
        return CreatorResponse(**creator)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=CreatorListResponse)
async def list_creators(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """List all creators."""
    try:
        creators = db.list_creators(status=status, limit=limit, offset=offset)
        return CreatorListResponse(
            creators=[CreatorResponse(**c) for c in creators],
            total=len(creators),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{creator_id}", response_model=CreatorResponse)
async def get_creator(
    creator_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Database = Depends(get_db),
):
    """Get a single creator by ID."""
    creator = db.get_creator_by_id(creator_id)
    if not creator:
        raise HTTPException(status_code=404, detail="Creator nicht gefunden")
    return CreatorResponse(**creator)


@router.put("/{creator_id}", response_model=CreatorResponse)
async def update_creator(
    creator_id: int,
    creator_data: CreatorUpdate,
    current_user: dict = Depends(require_role("manager")),
    db: Database = Depends(get_db),
):
    """Update a creator profile. Manager or admin only."""
    existing = db.get_creator_by_id(creator_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Creator nicht gefunden")
    update_data = creator_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Keine Aenderungen angegeben")
    try:
        updated = db.update_creator(creator_id, update_data)
        return CreatorResponse(**updated)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
