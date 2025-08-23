import hashlib
from typing import Optional

from sqlalchemy import (Column, Integer, String, DateTime, Boolean, ForeignKey,
                        Text, Float, Index, Enum)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB

from .base import BaseModel
from .enums import DocumentType, DocumentStatus

class Document(BaseModel):
    __tablename__ = "documents"

    # File info
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(100), nullable=False)
    document_type = Column(Enum(DocumentType), nullable=False)
    file_hash = Column(String(64), nullable=False)  # SHA-256 hash

    # Processing status
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADED, nullable=False)
    processing_progress = Column(Integer, default=0)
    processing_error = Column(Text)

    # Content
    extracted_text = Column(Text)
    summary = Column(Text)
    key_topics = Column(ARRAY(String))
    legal_entities = Column(JSONB)  # Extracted legal entities
    metadata = Column(JSONB, default={})

    # AI processing
    chunk_count = Column(Integer, default=0)
    embedding_model = Column(String(100))
    language_detected = Column(String(10))
    confidence_score = Column(Float)

    # Vector DB
    weaviate_id = Column(String(255), unique=True)
    vector_status = Column(String(50), default="pending")

    # Legal classification
    document_category = Column(String(100))  # contract, law, regulation, etc.
    jurisdiction = Column(String(100))
    legal_area = Column(ARRAY(String))  # civil, criminal, administrative, etc.

    # Relationships
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="documents")
    queries = relationship("Query", back_populates="document", lazy="dynamic")
    annotations = relationship("DocumentAnnotation", back_populates="document")

    # Timestamps
    processed_at = Column(DateTime(timezone=True))
    last_accessed_at = Column(DateTime(timezone=True))

    # Indexes
    __table_args__ = (
        Index('ix_documents_owner_status', 'owner_id', 'status'),
        Index('ix_documents_type_category', 'document_type', 'document_category'),
        Index('ix_documents_hash', 'file_hash'),
        Index('ix_documents_weaviate', 'weaviate_id'),
    )

    def generate_file_hash(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    @property
    def is_processed(self) -> bool:
        return self.status == DocumentStatus.PROCESSED

    @property
    def processing_time_seconds(self) -> Optional[int]:
        if self.processed_at and self.created_at:
            return int((self.processed_at - self.created_at).total_seconds())
        return None
