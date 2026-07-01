from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class AdminLoginRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class AdminLoginResponse(BaseModel):
    token: str
    username: str


class BannerBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    image_url: str = Field(..., min_length=1, max_length=500)
    link_url: Optional[str] = Field(None, max_length=500)
    order: int = Field(0, ge=0)
    is_active: bool = True


class BannerCreate(BannerBase):
    pass


class BannerUpdate(BannerBase):
    pass


class BannerResponse(BannerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PointBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    address: Optional[str] = Field(None, max_length=255)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    image_url: Optional[str] = Field(None, max_length=255)
    tags: Optional[str] = Field(None, max_length=255)

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, value: Optional[str]) -> Optional[str]:
        if not value:
            return value
        return ",".join([item.strip() for item in value.split(",") if item.strip()])


class PointCreate(PointBase):
    pass


class PointUpdate(PointBase):
    pass


class PointResponse(PointBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminRouteUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    region: str = Field(..., min_length=1, max_length=50)
    route_type: Optional[str] = Field(None, max_length=50)
    cover_image: Optional[str] = Field(None, max_length=255)
    duration: Optional[str] = Field(None, max_length=50)
    difficulty: Optional[str] = Field(None, max_length=20)


class AdminRouteResponse(AdminRouteUpdate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoutePointOrderItem(BaseModel):
    attraction_id: int
    order: int = Field(..., ge=1)


class RoutePointOrderRequest(BaseModel):
    items: list[RoutePointOrderItem]


class BannerOrderItem(BaseModel):
    id: int
    order: int = Field(..., ge=0)


class BannerOrderRequest(BaseModel):
    items: list[BannerOrderItem]


class AboutConfigRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    content: str = Field(..., min_length=1)
    contact: Optional[str] = Field("", max_length=500)
    footer_summary: Optional[str] = Field("", max_length=1000)
    footer_copyright: Optional[str] = Field("", max_length=255)
    footer_record: Optional[str] = Field("", max_length=255)


class AboutConfigResponse(AboutConfigRequest):
    pass


class SiteConfigRequest(BaseModel):
    site_name: str = Field(..., min_length=1, max_length=80)
    site_subtitle: Optional[str] = Field("", max_length=120)
    site_logo: Optional[str] = Field("", max_length=500)


class SiteConfigResponse(SiteConfigRequest):
    pass


class VisitTrackRequest(BaseModel):
    path: str = Field("/", max_length=255)


class VisitSummaryResponse(BaseModel):
    total: int
    today: int
    items: list[dict]


class ImportResult(BaseModel):
    total: int
    created: int
    skipped: int
    errors: list[str]


class VisitItem(BaseModel):
    visit_date: date
    path: str
    count: int
