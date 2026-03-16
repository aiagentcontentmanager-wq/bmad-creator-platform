#!/usr/bin/env python3
"""
Authentifizierungsmodul für das BMAD-System

Dieses Modul bietet Funktionen für die Authentifizierung und Autorisierung
von Benutzern, einschließlich JWT-Token-Verwaltung.
"""

import jwt
import datetime
import logging
from typing import Dict, Any, Optional
from passlib.context import CryptContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT-Konfiguration
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Passwort-Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Überprüft, ob ein Passwort mit einem Hash übereinstimmt."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Falls der Hash nicht mit bcrypt kompatibel ist, versuche sha256
        sha256_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
        return sha256_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Erstellt einen Hash für ein Passwort."""
    # Kürze das Passwort auf 72 Bytes, um das bcrypt-Limit einzuhalten
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password = password_bytes[:72].decode('utf-8', errors='replace')
    # Verwende sha256 als Fallback, falls bcrypt Probleme macht
    try:
        return pwd_context.hash(password)
    except ValueError as e:
        if "password cannot be longer than 72 bytes" in str(e):
            # Falls das Problem weiterhin besteht, verwende sha256
            sha256_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
            return sha256_context.hash(password)
        raise


def create_access_token(data: Dict[str, Any], expires_delta: Optional[datetime.timedelta] = None) -> str:
    """Erstellt ein JWT-Zugriffstoken."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """Dekodiert ein JWT-Zugriffstoken."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.error("Token ist abgelaufen")
        raise ValueError("Token ist abgelaufen")
    except jwt.InvalidTokenError:
        logger.error("Ungültiges Token")
        raise ValueError("Ungültiges Token")


def authenticate_user(username: str, password: str, db) -> Optional[Dict[str, Any]]:
    """Authentifiziert einen Benutzer und gibt ein Token zurück."""
    try:
        user = db.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user["password_hash"]):
            return None
        access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"], "role": user["role"]},
            expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"]
            }
        }
    except Exception as e:
        logger.error(f"Fehler bei der Authentifizierung: {e}")
        raise ValueError(f"Fehler bei der Authentifizierung: {e}")


def register_user(user_data: Dict[str, Any], db) -> Dict[str, Any]:
    """Registriert einen neuen Benutzer."""
    try:
        # Überprüfe, ob der Benutzer bereits existiert
        try:
            existing_user = db.get_user_by_username(user_data["username"])
            if existing_user:
                raise ValueError("Benutzername bereits vergeben")
        except ValueError:
            pass
        
        try:
            existing_email = db.get_user_by_email(user_data["email"])
            if existing_email:
                raise ValueError("E-Mail bereits vergeben")
        except ValueError:
            pass
        
        # Hash das Passwort
        hashed_password = get_password_hash(user_data["password"])
        
        # Erstelle den Benutzer
        user_data["password_hash"] = hashed_password
        user = db.create_user(user_data)
        
        return user
    except Exception as e:
        logger.error(f"Fehler bei der Registrierung: {e}")
        raise ValueError(f"Fehler bei der Registrierung: {e}")


def get_current_user(token: str, db) -> Dict[str, Any]:
    """Gibt den aktuellen Benutzer basierend auf dem Token zurück."""
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        if username is None:
            raise ValueError("Ungültiges Token")
        user = db.get_user_by_username(username)
        if user is None:
            raise ValueError("Benutzer nicht gefunden")
        return user
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des aktuellen Benutzers: {e}")
        raise ValueError(f"Fehler beim Abrufen des aktuellen Benutzers: {e}")


def check_user_role(user: Dict[str, Any], required_role: str) -> bool:
    """Überprüft, ob ein Benutzer eine bestimmte Rolle hat."""
    return user["role"] == required_role