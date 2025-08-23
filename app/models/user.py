from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Index
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, timedelta

from .base import BaseModel
from .enums import UserRole

class User(BaseModel):
    __tablename__ = "users"

    # Basic info
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)

    # Status
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Security
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    password_reset_token = Column(String(255))
    password_reset_expires = Column(DateTime(timezone=True))
    email_verification_token = Column(String(255))

    # Preferences
    language = Column(String(10), default="pl")
    timezone = Column(String(50), default="Europe/Warsaw")
    notification_preferences = Column(JSONB, default={})

    # Usage tracking
    last_login_at = Column(DateTime(timezone=True))
    login_count = Column(Integer, default=0)

    # Relationships
    documents = relationship("Document", back_populates="owner", lazy="dynamic")
    queries = relationship("Query", back_populates="user", lazy="dynamic")
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="user", lazy="dynamic")

    # Indexes
    __table_args__ = (
        Index('ix_users_email_active', 'email', 'is_active'),
        Index('ix_users_verification', 'email_verification_token'),
        Index('ix_users_password_reset', 'password_reset_token'),
    )

    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_locked(self) -> bool:
        return self.locked_until and self.locked_until > datetime.utcnow()

    def lock_account(self, duration_minutes: int = 15):
        self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.failed_login_attempts = 0

    def unlock_account(self):
        self.locked_until = None
        self.failed_login_attempts = 0

    @validates('email')
    def validate_email(self, key, email):
        if '@' not in email:
            raise ValueError("Invalid email address")
        return email.lower()
