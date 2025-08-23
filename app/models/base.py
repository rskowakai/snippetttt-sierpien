from sqlalchemy import Column, DateTime, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class BaseModel(Base):
    """Base model with common fields"""
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)

    def soft_delete(self):
        self.is_deleted = True
        self.updated_at = datetime.utcnow()
