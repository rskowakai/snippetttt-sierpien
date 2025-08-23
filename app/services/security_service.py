import secrets
import hmac
import hashlib
import re
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from cryptography.fernet import Fernet
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import User, Document, Query, AuditLog, Subscription

class SecurityService:
    def __init__(self):
        # In a real app, this key should be loaded securely and not generated on each run
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None

    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        # Simplified for stub
        if len(password) < settings.PASSWORD_MIN_LENGTH:
            return {"valid": False, "issues": ["Password too short"]}
        return {"valid": True, "score": 5, "issues": []}


class GDPRService:
    def __init__(self, db: Session):
        self.db = db

    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        # This is a simplified export
        return {
            "personal_info": {
                "email": user.email,
                "first_name": user.first_name,
            },
            "documents_count": user.documents.count(),
            "queries_count": user.queries.count(),
        }

    async def anonymize_user_data(self, user_id: str) -> bool:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        user.email = f"anonymous_{secrets.token_hex(8)}@deleted.local"
        user.first_name = "Anonymous"
        user.last_name = "User"
        user.hashed_password = "anonymized"
        user.is_active = False

        self.db.commit()
        return True

# Helper functions that might be used directly in endpoints/tests
security_service = SecurityService()

def get_password_hash(password: str) -> str:
    return security_service.hash_password(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return security_service.verify_password(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    return security_service.create_access_token(data, expires_delta)

def verify_token(token: str) -> Optional[str]:
    payload = security_service.verify_token(token)
    if payload:
        return payload.get("sub")
    return None
