from app.db.database import engine, Base
from app.models.route import Route
from app.models.attraction import Attraction
from app.models.route_attraction import RouteAttraction
from app.models.user import User
from app.models.banner import Banner
from app.models.site_config import SiteConfig
from app.models.visit import VisitStat
from app.api.admin import ensure_default_admin
from app.db.database import SessionLocal
from sqlalchemy import inspect, text


def migrate_existing_sqlite():
    """补齐旧 SQLite 表缺失字段，避免 create_all 无法变更已有表结构。"""
    inspector = inspect(engine)
    if "users" in inspector.get_table_names():
        user_columns = {column["name"] for column in inspector.get_columns("users")}
        with engine.begin() as conn:
            if "is_admin" not in user_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0"))
            if "is_active" not in user_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1"))
    if "visit_stats" in inspector.get_table_names():
        visit_columns = {column["name"] for column in inspector.get_columns("visit_stats")}
        with engine.begin() as conn:
            if "ip_address" not in visit_columns:
                conn.execute(text("ALTER TABLE visit_stats ADD COLUMN ip_address VARCHAR(64) NOT NULL DEFAULT 'unknown'"))
            if "location" not in visit_columns:
                conn.execute(text("ALTER TABLE visit_stats ADD COLUMN location VARCHAR(255) NOT NULL DEFAULT '未知'"))

def init_db():
    """创建所有数据表"""
    Base.metadata.create_all(bind=engine)
    migrate_existing_sqlite()
    db = SessionLocal()
    try:
        ensure_default_admin(db)
        seed_site_configs(db)
    finally:
        db.close()
    print("数据库表创建成功！")


def seed_site_configs(db: SessionLocal):
    defaults = {
        "site_name": ("站点名称", "出彩中原"),
        "site_subtitle": ("站点副标题", "河南旅游路线导航平台"),
        "site_logo": ("站点 Logo", "/logo.png"),
    }
    existing_keys = {item.key for item in db.query(SiteConfig).filter(SiteConfig.key.in_(defaults.keys())).all()}
    changed = False
    for key, (label, value) in defaults.items():
        if key in existing_keys:
            continue
        db.add(SiteConfig(key=key, label=label, value=value))
        changed = True
    if changed:
        db.commit()

if __name__ == "__main__":
    init_db()
