from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.response import success_response
from app.db.database import get_db
from app.models.banner import Banner
from app.models.site_config import SiteConfig

router = APIRouter(prefix="/config", tags=["config"])

@router.get("/map", response_model=dict)
def get_map_config():
    """获取地图配置"""
    return success_response({
        "amap_web_key": settings.AMAP_WEB_KEY
    })


@router.get("/banners", response_model=dict)
def get_public_banners(db: Session = Depends(get_db)):
    banners = (
        db.query(Banner)
        .filter(Banner.is_active == True)
        .order_by(Banner.order.asc(), Banner.id.desc())
        .all()
    )
    return success_response([
        {
            "id": item.id,
            "title": item.title,
            "image_url": item.image_url,
            "link_url": item.link_url,
            "order": item.order,
            "description": item.link_url or "",
        }
        for item in banners
    ])


@router.get("/site", response_model=dict)
def get_public_site_config(db: Session = Depends(get_db)):
    configs = db.query(SiteConfig).filter(SiteConfig.key.in_([
        "site_name",
        "site_subtitle",
        "site_logo",
    ])).all()
    config_map = {item.key: item.value for item in configs}
    return success_response({
        "site_name": config_map.get("site_name", "出彩中原"),
        "site_subtitle": config_map.get("site_subtitle", "河南旅游路线导航平台"),
        "site_logo": config_map.get("site_logo", "/logo.png"),
    })


@router.get("/about", response_model=dict)
def get_public_about(db: Session = Depends(get_db)):
    configs = db.query(SiteConfig).filter(SiteConfig.key.in_([
        "about_title",
        "about_content",
        "about_contact",
    ])).all()
    config_map = {item.key: item.value for item in configs}
    return success_response({
        "title": config_map.get("about_title", "关于我们"),
        "content": config_map.get("about_content", ""),
        "contact": config_map.get("about_contact", ""),
    })
