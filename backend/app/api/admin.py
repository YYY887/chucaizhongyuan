from datetime import date
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.response import success_response
from app.core.security import create_access_token, get_current_admin, get_password_hash, verify_password
from app.db.database import get_db
from app.models.attraction import Attraction
from app.models.banner import Banner
from app.models.route import Route
from app.models.route_attraction import RouteAttraction
from app.models.site_config import SiteConfig
from app.models.user import User
from app.models.visit import VisitStat
from app.schemas.admin import (
    AboutConfigRequest,
    AdminLoginRequest,
    AdminRouteResponse,
    AdminRouteUpdate,
    BannerCreate,
    BannerOrderRequest,
    BannerResponse,
    BannerUpdate,
    PointCreate,
    PointResponse,
    PointUpdate,
    RoutePointOrderRequest,
    SiteConfigRequest,
)
from app.utils.excel_import import parse_points_excel

router = APIRouter(prefix="/admin", tags=["admin"])

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
EXCEL_EXTENSIONS = {".xlsx", ".xlsm"}
MAX_UPLOAD_SIZE = 5 * 1024 * 1024


def serialize_model(model, schema):
    return schema.model_validate(model).model_dump(mode="json")


def upsert_config(db: Session, key: str, label: str, value: str) -> SiteConfig:
    config = db.query(SiteConfig).filter(SiteConfig.key == key).first()
    if not config:
        config = SiteConfig(key=key, label=label, value=value)
        db.add(config)
    else:
        config.label = label
        config.value = value
    db.commit()
    db.refresh(config)
    return config


def get_config_value(db: Session, key: str, default: str = "") -> str:
    config = db.query(SiteConfig).filter(SiteConfig.key == key).first()
    return config.value if config else default


@router.post("/auth/login", response_model=dict)
def admin_login(payload: AdminLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not user.is_admin or not user.is_active:
        raise HTTPException(status_code=401, detail="账号或密码错误")
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="账号或密码错误")

    token = create_access_token({"sub": str(user.id), "username": user.username})
    return success_response({"token": token, "username": user.username})


@router.get("/profile", response_model=dict)
def admin_profile(current_user: User = Depends(get_current_admin)):
    return success_response({"username": current_user.username, "email": current_user.email})


@router.post("/uploads", response_model=dict)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin),
):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in IMAGE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="仅支持图片文件")

    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="文件大小不能超过5MB")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{suffix}"
    target = UPLOAD_DIR / filename
    target.write_bytes(content)
    return success_response({"url": f"/uploads/{filename}"})


@router.get("/banners", response_model=dict)
def list_banners(
    keyword: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    query = db.query(Banner)
    if keyword:
        query = query.filter(Banner.title.contains(keyword))
    items = query.order_by(Banner.order.asc(), Banner.id.desc()).all()
    return success_response([serialize_model(item, BannerResponse) for item in items])


@router.post("/banners", response_model=dict)
def create_banner(
    payload: BannerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    banner = Banner(**payload.model_dump())
    db.add(banner)
    db.commit()
    db.refresh(banner)
    return success_response(serialize_model(banner, BannerResponse), "轮播图已创建")


@router.put("/banners/reorder", response_model=dict)
def update_banner_order(
    payload: BannerOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    banners = db.query(Banner).all()
    banner_map = {banner.id: banner for banner in banners}
    if len(payload.items) != len(banners):
        raise HTTPException(status_code=400, detail="轮播图数量不一致，请刷新后重试")

    seen = set()
    for item in payload.items:
        if item.id in seen or item.id not in banner_map:
            raise HTTPException(status_code=400, detail="轮播图排序数据不合法")
        seen.add(item.id)
        banner_map[item.id].order = item.order

    db.commit()
    return success_response(message="轮播图排序已保存")


@router.put("/banners/{banner_id}", response_model=dict)
def update_banner(
    banner_id: int,
    payload: BannerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=404, detail="轮播图不存在")
    for key, value in payload.model_dump().items():
        setattr(banner, key, value)
    db.commit()
    db.refresh(banner)
    return success_response(serialize_model(banner, BannerResponse), "轮播图已更新")


@router.delete("/banners/{banner_id}", response_model=dict)
def delete_banner(
    banner_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=404, detail="轮播图不存在")
    db.delete(banner)
    db.commit()
    return success_response(message="轮播图已删除")


@router.get("/points", response_model=dict)
def list_points(
    keyword: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    query = db.query(Attraction)
    if keyword:
        query = query.filter(
            (Attraction.name.contains(keyword)) |
            (Attraction.address.contains(keyword)) |
            (Attraction.tags.contains(keyword))
        )
    total = query.count()
    items = query.order_by(Attraction.id.desc()).offset(skip).limit(limit).all()
    return success_response({
        "total": total,
        "items": [serialize_model(item, PointResponse) for item in items],
    })


@router.get("/points/{point_id}", response_model=dict)
def get_point_detail(
    point_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    point = db.query(Attraction).filter(Attraction.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="节点不存在")
    return success_response(serialize_model(point, PointResponse))


@router.post("/points", response_model=dict)
def create_point(
    payload: PointCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    point = Attraction(**payload.model_dump())
    db.add(point)
    db.commit()
    db.refresh(point)
    return success_response(serialize_model(point, PointResponse), "节点已创建")


@router.put("/points/{point_id}", response_model=dict)
def update_point(
    point_id: int,
    payload: PointUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    point = db.query(Attraction).filter(Attraction.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="节点不存在")
    for key, value in payload.model_dump().items():
        setattr(point, key, value)
    db.commit()
    db.refresh(point)
    return success_response(serialize_model(point, PointResponse), "节点已更新")


@router.delete("/points/{point_id}", response_model=dict)
def delete_point(
    point_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    point = db.query(Attraction).filter(Attraction.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="节点不存在")
    db.delete(point)
    db.commit()
    return success_response(message="节点已删除")


@router.get("/routes", response_model=dict)
def list_admin_routes(
    keyword: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    query = db.query(Route)
    if keyword:
        query = query.filter(
            (Route.name.contains(keyword)) |
            (Route.region.contains(keyword)) |
            (Route.route_type.contains(keyword))
        )
    items = query.order_by(Route.id.desc()).all()
    return success_response([serialize_model(item, AdminRouteResponse) for item in items])


@router.put("/routes/{route_id}", response_model=dict)
def update_admin_route(
    route_id: int,
    payload: AdminRouteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="路线不存在")
    for key, value in payload.model_dump().items():
        setattr(route, key, value)
    db.commit()
    db.refresh(route)
    return success_response(serialize_model(route, AdminRouteResponse), "路线已更新")


@router.get("/routes/{route_id}/points", response_model=dict)
def list_route_points(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="路线不存在")
    rows = (
        db.query(Attraction, RouteAttraction.order)
        .join(RouteAttraction, Attraction.id == RouteAttraction.attraction_id)
        .filter(RouteAttraction.route_id == route_id)
        .order_by(RouteAttraction.order.asc(), Attraction.id.asc())
        .all()
    )
    return success_response([
        {
            **serialize_model(point, PointResponse),
            "order": order,
        }
        for point, order in rows
    ])


@router.put("/routes/{route_id}/points/order", response_model=dict)
def update_route_point_order(
    route_id: int,
    payload: RoutePointOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="路线不存在")

    relations = db.query(RouteAttraction).filter(RouteAttraction.route_id == route_id).all()
    relation_map = {relation.attraction_id: relation for relation in relations}
    if len(payload.items) != len(relations):
        raise HTTPException(status_code=400, detail="节点数量不一致，请刷新后重试")

    seen = set()
    for item in payload.items:
        if item.attraction_id in seen or item.attraction_id not in relation_map:
            raise HTTPException(status_code=400, detail="节点排序数据不合法")
        seen.add(item.attraction_id)
        relation_map[item.attraction_id].order = item.order

    db.commit()
    return success_response(message="路线节点顺序已保存")


@router.post("/points/import", response_model=dict)
async def import_points(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in EXCEL_EXTENSIONS:
        raise HTTPException(status_code=400, detail="仅支持 .xlsx 或 .xlsm 文件")

    rows = parse_points_excel(await file.read())
    created = 0
    skipped = 0
    errors: list[str] = []

    for index, row in enumerate(rows, start=2):
        try:
            name = str(row.get("name") or "").strip()
            latitude = float(row.get("latitude"))
            longitude = float(row.get("longitude"))
            if not name:
                raise ValueError("名称不能为空")
            if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
                raise ValueError("经纬度超出范围")
            exists = db.query(Attraction).filter(Attraction.name == name).first()
            if exists:
                skipped += 1
                continue
            point = Attraction(
                name=name,
                description=str(row.get("description") or ""),
                address=str(row.get("address") or ""),
                latitude=latitude,
                longitude=longitude,
                image_url=str(row.get("image_url") or ""),
                tags=str(row.get("tags") or ""),
            )
            db.add(point)
            created += 1
        except Exception as exc:
            skipped += 1
            errors.append(f"第{index}行：{exc}")

    db.commit()
    return success_response({
        "total": len(rows),
        "created": created,
        "skipped": skipped,
        "errors": errors[:20],
    }, "导入完成")


@router.get("/about", response_model=dict)
def get_about(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    return success_response({
        "title": get_config_value(db, "about_title", "关于我们"),
        "content": get_config_value(db, "about_content", ""),
        "contact": get_config_value(db, "about_contact", ""),
    })


@router.put("/about", response_model=dict)
def update_about(
    payload: AboutConfigRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    upsert_config(db, "about_title", "关于我们标题", payload.title)
    upsert_config(db, "about_content", "关于我们内容", payload.content)
    upsert_config(db, "about_contact", "联系方式", payload.contact or "")
    return success_response(payload.model_dump(), "关于我们已更新")


@router.get("/site-config", response_model=dict)
def get_site_config(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    return success_response({
        "site_name": get_config_value(db, "site_name", "出彩中原"),
        "site_subtitle": get_config_value(db, "site_subtitle", "河南旅游路线导航平台"),
        "site_logo": get_config_value(db, "site_logo", "/logo.png"),
    })


@router.put("/site-config", response_model=dict)
def update_site_config(
    payload: SiteConfigRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    upsert_config(db, "site_name", "站点名称", payload.site_name)
    upsert_config(db, "site_subtitle", "站点副标题", payload.site_subtitle or "")
    upsert_config(db, "site_logo", "站点 Logo", payload.site_logo or "")
    return success_response(payload.model_dump(), "站点配置已更新")


@router.get("/visits", response_model=dict)
def list_visits(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    items = (
        db.query(VisitStat)
        .order_by(VisitStat.visit_date.desc(), VisitStat.path.asc())
        .limit(days * 20)
        .all()
    )
    today = date.today()
    total_count = db.query(func.coalesce(func.sum(VisitStat.count), 0)).scalar()
    today_count = (
        db.query(func.coalesce(func.sum(VisitStat.count), 0))
        .filter(VisitStat.visit_date == today)
        .scalar()
    )
    return success_response({
        "total": int(total_count or 0),
        "today": int(today_count or 0),
        "items": [
            {
                "visit_date": item.visit_date.isoformat(),
                "path": item.path,
                "ip_address": item.ip_address,
                "location": item.location,
                "count": item.count,
            }
            for item in items
        ],
    })


def ensure_default_admin(db: Session):
    admin = db.query(User).filter(User.username == "admin").first()
    if admin:
        admin.is_admin = True
        admin.is_active = True
        db.commit()
        return
    admin = User(
        username="admin",
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        is_admin=True,
        is_active=True,
    )
    db.add(admin)
    db.commit()
