from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Index, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .base import BaseModel
from .enums import AuditAction

class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(Enum(AuditAction), nullable=False)
    resource_type = Column(String(50))  # document, query, user, etc.
    resource_id = Column(String(255))
    details = Column(JSONB, default={})
    ip_address = Column(String(45))  # IPv6 support
    user_agent = Column(String(500))
    success = Column(Boolean, default=True)
    error_message = Column(Text)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    # Indexes
    __table_args__ = (
        Index('ix_audit_logs_user_action', 'user_id', 'action'),
        Index('ix_audit_logs_timestamp', 'created_at'),
        Index('ix_audit_logs_resource', 'resource_type', 'resource_id'),
    )
