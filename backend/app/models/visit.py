from sqlalchemy import Column, Date, DateTime, Integer, String
from sqlalchemy.sql import func
from app.db.database import Base


class VisitStat(Base):
    __tablename__ = "visit_stats"

    id = Column(Integer, primary_key=True, index=True)
    visit_date = Column(Date, nullable=False, index=True, comment="访问日期")
    path = Column(String(255), nullable=False, default="/", comment="访问路径")
    ip_address = Column(String(64), nullable=False, default="unknown", index=True, comment="访问 IP")
    location = Column(String(255), nullable=False, default="未知", comment="大致归属地")
    count = Column(Integer, nullable=False, default=0, comment="访问次数")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
