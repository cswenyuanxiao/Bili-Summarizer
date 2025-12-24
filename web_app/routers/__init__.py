"""
Routers registry - 集中管理所有 API 路由
"""
from fastapi import FastAPI

from .health import router as health_router
from .dashboard import router as dashboard_router
from .share import router as share_router
from .templates import router as templates_router
from .payments import router as payments_router


def register_routers(app: FastAPI):
    """注册所有路由到 FastAPI 应用"""
    # Health router 必须第一个注册，确保健康检查不依赖其他模块
    app.include_router(health_router)
    
    # Dashboard router - 用户面板、订阅
    app.include_router(dashboard_router)
    
    # Share router - 分享卡片
    app.include_router(share_router)
    
    # Templates router - 总结模板
    app.include_router(templates_router)
    
    # Payments router - 支付相关
    app.include_router(payments_router)
