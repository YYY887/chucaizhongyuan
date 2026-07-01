from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.services.route_service import RouteService
from app.schemas.route import RouteListResponse, RouteDetailResponse, RegionResponse
from app.core.response import success_response, error_response

router = APIRouter(prefix="/routes", tags=["routes"])

@router.get("", response_model=dict)
def get_routes(
    region: Optional[str] = Query(None, description="区域筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=100, description="返回数量"),
    db: Session = Depends(get_db)
):
    """获取路线列表，包含景点数据"""
    try:
        routes = RouteService.get_routes(db, region, keyword, skip, limit)
        # 直接返回service的数据，不经过schema验证（因为service已经返回dict格式，包含attractions）
        return success_response(routes)
    except Exception as e:
        return error_response(500, f"获取路线列表失败: {str(e)}")

@router.get("/{route_id}", response_model=dict)
def get_route_detail(
    route_id: int,
    db: Session = Depends(get_db)
):
    """获取路线详情"""
    try:
        route = RouteService.get_route_detail(db, route_id)
        if not route:
            return error_response(404, "路线不存在")
        return success_response(route)
    except Exception as e:
        return error_response(500, f"获取路线详情失败: {str(e)}")
