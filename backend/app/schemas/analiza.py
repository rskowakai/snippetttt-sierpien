from pydantic import BaseModel
from typing import Optional, List, Any

class AnalizaBase(BaseModel):
    summary: str
    internal_notes: Optional[str] = None
    attachments: Optional[List[Any]] = None

class AnalizaCreate(AnalizaBase):
    pismo_id: int

class AnalizaRead(AnalizaBase):
    id: int
    pismo_id: int
    admin_id: int

    class Config:
        from_attributes = True
