from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class OpcjaBase(BaseModel):
    description: str
    price: Decimal

class OpcjaCreate(OpcjaBase):
    analiza_id: int

class OpcjaRead(OpcjaBase):
    id: int
    analiza_id: int
    is_purchased: bool

    class Config:
        from_attributes = True
