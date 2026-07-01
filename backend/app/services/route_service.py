from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.models.route import Route
from app.models.attraction import Attraction
from app.models.route_attraction import RouteAttraction

class RouteService:
    @staticmethod
    def get_routes(
        db: Session,
        region: Optional[str] = None,
        keyword: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[dict]:
        """获取路线列表，包含景点数据"""
        query = db.query(Route)

        if region:
            query = query.filter(Route.region.contains(region))

        if keyword:
            query = query.filter(
                (Route.name.contains(keyword)) |
                (Route.description.contains(keyword))
            )

        routes = query.offset(skip).limit(limit).all()

        # 为每条路线加载景点数据
        result = []
        for route in routes:
            # 查询路线关联的景点
            attractions_query = (
                db.query(Attraction, RouteAttraction.order)
                .join(RouteAttraction, Attraction.id == RouteAttraction.attraction_id)
                .filter(RouteAttraction.route_id == route.id)
                .order_by(RouteAttraction.order)
                .all()
            )

            # 构造景点列表
            attractions = []
            for attr, order in attractions_query:
                attr_dict = {
                    "id": attr.id,
                    "name": attr.name,
                    "description": attr.description,
                    "address": attr.address,
                    "latitude": attr.latitude,
                    "longitude": attr.longitude,
                    "image_url": attr.image_url,
                    "order": order
                }
                attractions.append(attr_dict)

            route_dict = {
                "id": route.id,
                "name": route.name,
                "description": route.description,
                "region": route.region,
                "route_type": route.route_type,
                "cover_image": route.cover_image,
                "duration": route.duration,
                "difficulty": route.difficulty,
                "created_at": route.created_at,
                "attractions": attractions
            }
            result.append(route_dict)

        return result

    @staticmethod
    def get_route_detail(db: Session, route_id: int):
        """获取路线详情，包含景点列表"""
        route = db.query(Route).filter(Route.id == route_id).first()
        if not route:
            return None

        # 查询路线关联的景点，按顺序排序
        attractions_query = (
            db.query(Attraction, RouteAttraction.order)
            .join(RouteAttraction, Attraction.id == RouteAttraction.attraction_id)
            .filter(RouteAttraction.route_id == route_id)
            .order_by(RouteAttraction.order)
            .all()
        )

        # 构造景点列表
        attractions = []
        for attr, order in attractions_query:
            attr_dict = {
                "id": attr.id,
                "name": attr.name,
                "description": attr.description,
                "address": attr.address,
                "latitude": attr.latitude,
                "longitude": attr.longitude,
                "image_url": attr.image_url,
                "order": order
            }
            attractions.append(attr_dict)

        return {
            "id": route.id,
            "name": route.name,
            "description": route.description,
            "region": route.region,
            "route_type": route.route_type,
            "cover_image": route.cover_image,
            "duration": route.duration,
            "difficulty": route.difficulty,
            "created_at": route.created_at,
            "updated_at": route.updated_at,
            "attractions": attractions
        }

    @staticmethod
    def get_regions(db: Session):
        """获取所有区域及路线数量"""
        results = (
            db.query(Route.region, func.count(Route.id).label('count'))
            .group_by(Route.region)
            .all()
        )

        return [{"region": r.region, "count": r.count} for r in results]
