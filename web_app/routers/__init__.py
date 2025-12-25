"""
Routers registry - 集中管理所有 API 路由
"""
from fastapi import FastAPI

from .health import router as health_router
from .dashboard import router as dashboard_router
from .share import router as share_router
from .templates import router as templates_router
from .payments import router as payments_router
from .api_keys import router as api_keys_router
from .invite import router as invite_router
from .history import router as history_router
from .feedback import router as feedback_router
from .subscriptions import router as subscriptions_router
from .trending import router as trending_router
from .favorites import router as favorites_router


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
    
    # API Keys router - API 密钥管理
    app.include_router(api_keys_router)
    
    # Invite router - 邀请码
    app.include_router(invite_router)
    
    # History router - 历史同步
    app.include_router(history_router)
    
    # Feedback router - 用户反馈
    app.include_router(feedback_router)
    
    # Subscriptions router - UP主订阅
    app.include_router(subscriptions_router)
    
    # Trending router - 热门视频推荐
    app.include_router(trending_router)
    
    # Favorites router - 收藏夹
    app.include_router(favorites_router)

