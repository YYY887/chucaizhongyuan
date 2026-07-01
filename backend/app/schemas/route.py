from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.attraction import AttractionInRoute

class RouteBase(BaseModel):
    name: str
    description: Optional[str] = None
    region: str
    route_type: Optional[str] = None
    cover_image: Optional[str] = None
    duration: Optional[str] = None
    difficulty: Optional[str] = None

class RouteCreate(RouteBase):
    pass

class RouteListResponse(RouteBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class RouteDetailResponse(RouteBase):
    id: int
    attractions: List[AttractionInRoute] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RegionResponse(BaseModel):
    region: str
    count: int
