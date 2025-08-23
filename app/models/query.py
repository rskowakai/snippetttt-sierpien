from sqlalchemy import (Column, String, Boolean, ForeignKey, Text,
                        Float, Index, Enum, DateTime)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import BaseModel
from .enums import QueryType

class Query(BaseModel):
    __tablename__ = "queries"

    question = Column(Text, nullable=False)
    answer = Column(Text)
    confidence_score = Column(Float)
    processing_time = Column(Float)
    query_type = Column(Enum(QueryType))
    has_error = Column(Boolean, default=False, nullable=False)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)

    answered_at = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="queries")
    document = relationship("Document", back_populates="queries")

    __table_args__ = (
        Index('ix_queries_user_document', 'user_id', 'document_id'),
    )
