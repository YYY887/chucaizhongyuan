from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "出彩中原 - 河南旅游路线导航"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./app.db"

    # 高德地图配置
    AMAP_API_KEY: str = "your_amap_key_here"
    AMAP_WEB_KEY: str = "your_amap_web_key_here"

    # CORS配置（从环境变量读取时用逗号分隔的字符串）
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        """将 CORS_ORIGINS 字符串转为列表"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
