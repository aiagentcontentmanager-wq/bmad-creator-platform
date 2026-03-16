"""
Authentication & Authorization module.
Uses settings from config instead of hardcoded values.
"""

import jwt
import datetime
import logging
from typing import Dict, Any, Optional
from passlib.context import CryptContext

from src.core.config import settings
from src.core.database import Database

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        sha256_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
        return sha256_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        password = password_bytes[:72].decode("utf-8", errors="replace")
    try:
        return pwd_context.hash(password)
    except ValueError as e:
        if "password cannot be longer than 72 bytes" in str(e):
            sha256_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
            return sha256_context.hash(password)
        raise


def create_access_token(data: Dict[str, Any], expires_delta: Optional[datetime.timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + (expires_delta or datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token ist abgelaufen")
    except jwt.InvalidTokenError:
        raise ValueError("Ungültiges Token")


def authenticate_user(username: str, password: str, db: Database) -> Optional[Dict[str, Any]]:
    user = db.get_user_by_username(username)
    if not user or not verify_password(password, user["password_hash"]):
        return None
    access_token = create_access_token({"sub": user["username"], "role": user["role"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
        },
    }


def register_user(user_data: Dict[str, Any], db: Database) -> Dict[str, Any]:
    if db.get_user_by_username(user_data["username"]):
        raise ValueError("Benutzername bereits vergeben")
    if db.get_user_by_email(user_data["email"]):
        raise ValueError("E-Mail bereits vergeben")
    user_data["password_hash"] = get_password_hash(user_data["password"])
    return db.create_user(user_data)


def get_current_user(token: str, db: Database) -> Dict[str, Any]:
    payload = decode_access_token(token)
    username = payload.get("sub")
    if not username:
        raise ValueError("Ungültiges Token")
    user = db.get_user_by_username(username)
    if not user:
        raise ValueError("Benutzer nicht gefunden")
    return user


def check_user_role(user: Dict[str, Any], required_role: str) -> bool:
    return user.get("role") == required_role
