from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.database import Base

class Banner(Base):
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False, comment="轮播图标题")
    image_url = Column(String(500), nullable=False, comment="图片URL")
    link_url = Column(String(500), comment="跳转链接")
    order = Column(Integer, default=0, comment="排序顺序")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<Banner(id={self.id}, title={self.title})>"
