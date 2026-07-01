from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from app.core.config import settings
from app.core.logger import logger
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.api import admin, attractions, config, regions, routes, visits
from app.db.init_db import init_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册异常处理器
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 注册API路由
app.include_router(routes.router, prefix=settings.API_PREFIX)
app.include_router(regions.router, prefix=settings.API_PREFIX)
app.include_router(attractions.router, prefix=settings.API_PREFIX)
app.include_router(config.router, prefix=settings.API_PREFIX)
app.include_router(visits.router, prefix=settings.API_PREFIX)
app.include_router(admin.router, prefix=settings.API_PREFIX)

# 挂载静态文件目录
static_dir = Path(__file__).parent.parent / "static"
admin_static_dir = Path(__file__).parent.parent / "admin_static"
upload_dir = Path(__file__).parent.parent / "uploads"
upload_dir.mkdir(parents=True, exist_ok=True)
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")
    app.mount("/tu", StaticFiles(directory=static_dir / "tu"), name="tu")
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")
if admin_static_dir.exists():
    admin_assets_dir = admin_static_dir / "assets"
    if admin_assets_dir.exists():
        app.mount("/admin/assets", StaticFiles(directory=admin_assets_dir), name="admin_assets")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/favicon.svg")
async def serve_favicon():
    return FileResponse(static_dir / "favicon.svg")

@app.get("/logo.png")
async def serve_logo():
    return FileResponse(static_dir / "logo.png")

@app.get("/icons.svg")
async def serve_icons():
    return FileResponse(static_dir / "icons.svg")

@app.get("/admin")
@app.get("/admin/{full_path:path}")
async def serve_admin(full_path: str = ""):
    """处理独立后台路由，返回 admin index.html"""
    index_file = admin_static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "管理后台未构建"}

# 前端路由处理 - 所有非API路径都返回index.html
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """处理前端路由，返回 index.html"""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    else:
        return {"message": f"Welcome to {settings.PROJECT_NAME}", "version": settings.VERSION}

@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info(f"{settings.PROJECT_NAME} 启动成功！")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"{settings.PROJECT_NAME} 关闭")
