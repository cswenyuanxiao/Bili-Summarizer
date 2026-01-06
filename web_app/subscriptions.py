"""
兼容层：历史导入路径保持不变。
实际实现迁移至 web_app/services/subscriptions_service.py。
"""
from .services.subscriptions_service import (  # noqa: F401
    get_all_subscriptions,
    get_up_latest_videos,
    get_user_subscriptions,
    search_up,
    subscribe_up,
    unsubscribe_up,
    update_subscription_check,
)
