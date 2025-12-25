"""
应用配置常量
集中管理硬编码的配置项，如管理员邮箱、定价方案等。
"""
import os
from typing import Set, Dict, Any


# 管理员邮箱列表（从环境变量加载）
ADMIN_EMAILS: Set[str] = {
    email.strip().lower()
    for email in os.getenv("ADMIN_EMAILS", "admin@bili-summarizer.com").split(",")
    if email.strip()
}


# 定价方案配置
PRICING_PLANS: Dict[str, Dict[str, Any]] = {
    "starter_pack": {
        "plan": "credits_pack",
        "type": "one_time",
        "amount_cents": 100,
        "credits": 30
    },
    "basic_monthly": {
        "plan": "subscription",
        "type": "monthly",
        "amount_cents": 1000,
        "period_days": 30,
        "credits": 100
    },
    "pro_monthly": {
        "plan": "subscription",
        "type": "monthly",
        "amount_cents": 2000,
        "period_days": 30,
        "credits": 300
    },
    "unlimited_monthly": {
        "plan": "subscription",
        "type": "monthly",
        "amount_cents": 5000,
        "period_days": 30,
        "credits": -1  # -1 表示无限
    }
}


# TTS 支持的配音列表
VOICES = [
    {"code": "zh-CN-XiaoxiaoNeural", "name": "晓晓 (女声)", "language": "zh-CN"},
    {"code": "zh-CN-YunxiNeural", "name": "云希 (男声)", "language": "zh-CN"},
    {"code": "zh-CN-XiaoyiNeural", "name": "晓伊 (女声)", "language": "zh-CN"},
    {"code": "zh-CN-YunjianNeural", "name": "云健 (男声)", "language": "zh-CN"},
]


def is_admin_user(email: str) -> bool:
    """检查用户是否为管理员"""
    return email.lower() in ADMIN_EMAILS
