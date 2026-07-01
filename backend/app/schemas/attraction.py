from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AttractionBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: float
    longitude: float
    image_url: Optional[str] = None
    tags: Optional[str] = None

class AttractionCreate(AttractionBase):
    pass

class AttractionResponse(AttractionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AttractionInRoute(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: float
    longitude: float
    image_url: Optional[str] = None
    order: int

    class Config:
        from_attributes = True
