from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BannerBase(BaseModel):
    title: str = Field(..., max_length=100, description="轮播图标题")
    image_url: str = Field(..., max_length=500, description="图片URL")
    link_url: Optional[str] = Field(None, max_length=500, description="跳转链接")
    order: int = Field(default=0, description="排序顺序")
    is_active: bool = Field(default=True, description="是否启用")

class BannerCreate(BannerBase):
    pass

class BannerUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = Field(None, max_length=500)
    link_url: Optional[str] = Field(None, max_length=500)
    order: Optional[int] = None
    is_active: Optional[bool] = None

class BannerResponse(BannerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
