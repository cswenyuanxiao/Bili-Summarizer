"""
Dashboard Router - 用户面板、订阅、额度相关端点
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Optional
import logging

from ..dependencies import get_current_user, get_optional_user, get_db
from ..credits import ensure_user_credits, get_user_credits, get_credit_history, get_daily_usage
from ..db import get_connection

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Dashboard"])


# --- 订阅检查辅助函数 ---
def fetch_subscription(user_id: str) -> dict:
    """从本地 DB 获取订阅信息"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT plan, status, current_period_end, updated_at
            FROM subscriptions WHERE user_id = ?
        """, (user_id,))
        row = cursor.fetchone()
        
        if row:
            return {
                "plan": row["plan"],
                "status": row["status"],
                "current_period_end": row["current_period_end"],
                "updated_at": row["updated_at"]
            }
        return {
            "plan": "free",
            "status": "inactive",
            "current_period_end": None,
            "updated_at": None
        }
    finally:
        conn.close()


def is_subscription_active(user_id: str) -> bool:
    """检查用户订阅是否有效"""
    subscription = fetch_subscription(user_id)
    if subscription["plan"] != "pro":
        return False
    if subscription["status"] != "active":
        return False
    return True


# --- Dashboard 端点 ---
@router.get("/dashboard")
async def get_dashboard(request: Request):
    """获取用户面板数据：积分、使用量、历史"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    credits_info = ensure_user_credits(user["user_id"])
    usage = get_daily_usage(user["user_id"])
    history = get_credit_history(user["user_id"])
    
    # 判断是否为管理员（无限额度用户）
    from ..main import is_unlimited_user
    
    return {
        "credits": credits_info["credits"],
        "total_used": credits_info["total_used"],
        "usage_history": usage,
        "credit_history": history,
        "is_admin": is_unlimited_user(user),
        "cost_per_summary": 10
    }


# --- Subscription 端点 ---
@router.get("/subscription")
async def get_subscription(user: dict = Depends(get_current_user)):
    """获取用户订阅状态"""
    subscription = fetch_subscription(user["user_id"])
    return {
        "user_id": user["user_id"],
        "plan": subscription["plan"],
        "status": subscription["status"],
        "current_period_end": subscription["current_period_end"],
        "updated_at": subscription["updated_at"]
    }
