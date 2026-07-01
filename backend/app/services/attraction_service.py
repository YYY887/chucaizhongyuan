from sqlalchemy.orm import Session
from app.models.attraction import Attraction

class AttractionService:
    @staticmethod
    def get_attraction_detail(db: Session, attraction_id: int):
        """获取景点详情"""
        return db.query(Attraction).filter(Attraction.id == attraction_id).first()
