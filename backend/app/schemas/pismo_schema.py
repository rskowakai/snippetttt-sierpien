from pydantic import BaseModel
from typing import Optional
from app.models.pismo import PismoStatus

class PismoBase(BaseModel):
    title: str
    content: str
    user_comments: Optional[str] = None

class PismoCreate(PismoBase):
    pass

class PismoUpdate(BaseModel):
    status: Optional[PismoStatus] = None
    user_comments: Optional[str] = None


class PismoRead(PismoBase):
    id: int
    owner_id: int
    status: PismoStatus

    class Config:
        from_attributes = True
