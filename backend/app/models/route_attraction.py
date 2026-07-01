from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class RouteAttraction(Base):
    __tablename__ = "route_attractions"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False, comment="路线ID")
    attraction_id = Column(Integer, ForeignKey("attractions.id"), nullable=False, comment="景点ID")
    order = Column(Integer, nullable=False, comment="景点顺序")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    def __repr__(self):
        return f"<RouteAttraction(route_id={self.route_id}, attraction_id={self.attraction_id}, order={self.order})>"
