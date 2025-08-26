import enum
from sqlalchemy import (Column, String, DateTime, Enum as SQLAlchemyEnum,
                        ForeignKey, BigInteger, Text)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILURE = "failure"

class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(BigInteger, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True, nullable=False) # Celery task ID
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    document_id = Column(BigInteger, ForeignKey("documents.id"), nullable=True)
    task_type = Column(String, nullable=False)
    status = Column(SQLAlchemyEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    priority = Column(SQLAlchemyEnum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="tasks")
    document = relationship("Document", back_populates="tasks")
