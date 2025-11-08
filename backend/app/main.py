from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.middleware import MetricsMiddleware
from app.api import auth, documents, proposals, templates, knowledge, search, metrics, websocket

# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    ),
    level=settings.LOG_LEVEL,
)
logger.add(settings.LOG_FILE, rotation="500 MB", retention="10 days", level=settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI生命周期管理"""
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    logger.info("Initializing database...")
    try:
        init_db()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
    yield
    logger.info("应用正在关闭...")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    lifespan=lifespan,
)


# 添加安全头中间件
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    return response


# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(MetricsMiddleware)


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "app_name": settings.APP_NAME, "version": settings.APP_VERSION}


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": f"欢迎使用 {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_PREFIX}/docs",
    }


# 注册路由
app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["认证"])
app.include_router(documents.router, prefix=f"{settings.API_PREFIX}/documents", tags=["文档管理"])
app.include_router(proposals.router, prefix=f"{settings.API_PREFIX}/proposals", tags=["方案生成"])
app.include_router(templates.router, prefix=f"{settings.API_PREFIX}/templates", tags=["模板管理"])
app.include_router(knowledge.router, prefix=f"{settings.API_PREFIX}/knowledge", tags=["知识库"])
app.include_router(search.router, prefix=f"{settings.API_PREFIX}/search", tags=["语义搜索"])
app.include_router(metrics.router, prefix=f"{settings.API_PREFIX}/metrics", tags=["监控"])
app.include_router(websocket.router, tags=["WebSocket"])  # WebSocket不使用prefix


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
