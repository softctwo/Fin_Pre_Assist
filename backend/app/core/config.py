from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """应用配置"""

    # 应用基础配置
    APP_NAME: str = "金融售前方案辅助系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 数据库配置
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/fin_pre_assist"
    DATABASE_ECHO: bool = False

    # 向量数据库配置
    CHROMA_PERSIST_DIRECTORY: str = "./storage/chroma"

    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # AI模型配置
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"

    TONGYI_API_KEY: str = ""

    WENXIN_API_KEY: str = ""
    WENXIN_SECRET_KEY: str = ""

    AI_PROVIDER: str = "openai"  # openai/tongyi/wenxin/local

    # 文件存储配置
    UPLOAD_DIR: str = "./storage/documents"
    EXPORT_DIR: str = "./storage/exports"
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB

    # CORS配置
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"

    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建配置实例
settings = Settings()

# 确保必要的目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.EXPORT_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
