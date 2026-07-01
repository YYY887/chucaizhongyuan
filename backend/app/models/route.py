from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func
from app.db.database import Base

class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="路线名称")
    description = Column(Text, comment="路线描述")
    region = Column(String(50), nullable=False, comment="所属区域")
    route_type = Column(String(50), comment="路线类型（历史文化/自然风光等）")
    cover_image = Column(String(255), comment="封面图片URL")
    duration = Column(String(50), comment="建议游玩时长")
    difficulty = Column(String(20), comment="难度等级（简单/中等/困难）")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<Route(id={self.id}, name={self.name})>"
