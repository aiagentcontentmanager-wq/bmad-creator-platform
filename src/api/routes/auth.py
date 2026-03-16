"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.models.user import UserRegister, UserLogin, UserResponse, TokenResponse
from src.core.database import Database
from src.core.auth import authenticate_user, register_user
from src.api.dependencies import get_db, get_current_active_user

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserRegister, db: Database = Depends(get_db)):
    """Register a new user."""
    try:
        user = register_user(user_data.model_dump(), db)
        return UserResponse(**user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/token", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Database = Depends(get_db)):
    """Login and obtain an access token."""
    result = authenticate_user(form_data.username, form_data.password, db)
    if not result:
        raise HTTPException(
            status_code=401,
            detail="Ungueltiger Benutzername oder Passwort",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(**result)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_active_user)):
    """Get current user info."""
    return UserResponse(**current_user)
