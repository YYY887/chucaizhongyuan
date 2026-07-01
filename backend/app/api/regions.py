from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.route_service import RouteService
from app.core.response import success_response, error_response

router = APIRouter(prefix="/regions", tags=["regions"])

@router.get("", response_model=dict)
def get_regions(db: Session = Depends(get_db)):
    """获取区域列表"""
    try:
        regions = RouteService.get_regions(db)
        return success_response(regions)
    except Exception as e:
        return error_response(500, f"获取区域列表失败: {str(e)}")
