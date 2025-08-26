import uuid
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

from .models.document import DocumentStatus
from .models.task import TaskStatus

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserRead(UserBase):
    id: uuid.UUID
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Document Schemas ---
class DocumentRead(BaseModel):
    id: int
    filename: str
    status: DocumentStatus
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class DocumentUploadResponse(BaseModel):
    document: DocumentRead
    task_id: str

# --- Task Schemas ---
class TaskRead(BaseModel):
    task_id: str
    task_type: str
    status: TaskStatus
    created_at: datetime
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

# --- Search Schemas ---
class SearchQuery(BaseModel):
    query: str
    top_k: int = 5

class SearchResult(BaseModel):
    document_id: int
    content: str
    score: float
    metadata: Optional[Dict[str, Any]] = None
