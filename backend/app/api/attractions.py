from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.attraction_service import AttractionService
from app.schemas.attraction import AttractionResponse
from app.core.response import success_response, error_response

router = APIRouter(prefix="/attractions", tags=["attractions"])

@router.get("/{attraction_id}", response_model=dict)
def get_attraction_detail(
    attraction_id: int,
    db: Session = Depends(get_db)
):
    """获取景点详情"""
    try:
        attraction = AttractionService.get_attraction_detail(db, attraction_id)
        if not attraction:
            return error_response(404, "景点不存在")

        attraction_data = AttractionResponse.model_validate(attraction).model_dump()
        return success_response(attraction_data)
    except Exception as e:
        return error_response(500, f"获取景点详情失败: {str(e)}")
