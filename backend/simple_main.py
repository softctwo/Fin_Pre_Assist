#!/usr/bin/env python3
"""
简化版后端启动文件，用于快速启动测试
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 创建FastAPI应用
app = FastAPI(
    title="金融售前方案辅助系统",
    version="1.0.0",
    debug=True,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "app_name": "金融售前方案辅助系统", "version": "1.0.0"}

# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": f"欢迎使用 金融售前方案辅助系统",
        "version": "1.0.0",
        "docs": "/api/v1/docs",
    }

# 基础API路由
@app.get("/api/v1/test")
async def test_api():
    """测试API接口"""
    return {"status": "ok", "message": "API运行正常"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("simple_main:app", host="0.0.0.0", port=8001, reload=True)