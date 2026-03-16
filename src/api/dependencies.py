"""FastAPI dependency injection."""

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from src.core.database import Database
from src.core.auth import get_current_user, check_user_role

db = Database()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_db() -> Database:
    return db


async def get_current_active_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        return get_current_user(token, db)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


def require_role(role: str):
    async def role_checker(current_user: dict = Depends(get_current_active_user)):
        if not check_user_role(current_user, role) and not check_user_role(current_user, "admin"):
            raise HTTPException(status_code=403, detail="Keine Berechtigung")
        return current_user
    return role_checker
