import enum
from sqlalchemy import (Column, String, DateTime, Enum as SQLAlchemyEnum,
                        ForeignKey, BigInteger, Text, JSON)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Document(Base):
    __tablename__ = "documents"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    status = Column(SQLAlchemyEnum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    task_id = Column(String, index=True, nullable=True) # Celery task ID
    weaviate_id = Column(String, index=True, nullable=True)
    transcription = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="document")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(BigInteger, primary_key=True, index=True)
    document_id = Column(BigInteger, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(BigInteger, nullable=False)
    content = Column(Text, nullable=False)
    weaviate_chunk_id = Column(String, index=True, nullable=True)

    document = relationship("Document", back_populates="chunks")
