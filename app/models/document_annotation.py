from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .base import BaseModel

class DocumentAnnotation(BaseModel):
    __tablename__ = "document_annotations"

    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    content = Column(Text, nullable=False)
    position = Column(JSONB) # e.g., page number, bounding box

    document = relationship("Document", back_populates="annotations")
