"""
Routers registry - 集中管理所有 API 路由
"""
from fastapi import FastAPI

from .health import router as health_router


def register_routers(app: FastAPI):
    """注册所有路由到 FastAPI 应用"""
    # Health router 必须第一个注册，确保健康检查不依赖其他模块
    app.include_router(health_router)
    
    # 后续可以添加更多路由:
    # app.include_router(summarize_router, prefix="/api")
    # app.include_router(dashboard_router, prefix="/api")
    # app.include_router(history_router, prefix="/api")
