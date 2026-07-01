from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class Attraction(Base):
    __tablename__ = "attractions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="景点名称")
    description = Column(Text, comment="景点描述")
    address = Column(String(255), comment="详细地址")
    latitude = Column(Float, nullable=False, comment="纬度")
    longitude = Column(Float, nullable=False, comment="经度")
    image_url = Column(String(255), comment="景点图片URL")
    tags = Column(String(255), comment="标签（逗号分隔）")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<Attraction(id={self.id}, name={self.name})>"
