import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List

from ..clients.bilibili_client import get_up_latest_videos, search_up
from ..db import get_connection

logger = logging.getLogger(__name__)


def subscribe_up(
    user_id: str,
    up_mid: str,
    up_name: str,
    up_avatar: str = "",
    notify_methods: List[str] = None
) -> Dict[str, Any]:
    """订阅 UP 主"""
    sub_id = f"sub_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow().isoformat()

    conn = get_connection()
    cursor = conn.cursor()

    # 检查是否已订阅
    cursor.execute(
        "SELECT id FROM up_subscriptions WHERE user_id = ? AND up_mid = ?",
        (user_id, up_mid)
    )

    if cursor.fetchone():
        conn.close()
        raise ValueError("已订阅该 UP 主")

    cursor.execute("""
        INSERT INTO up_subscriptions 
        (id, user_id, up_mid, up_name, up_avatar, notify_methods, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        sub_id,
        user_id,
        up_mid,
        up_name,
        up_avatar,
        json.dumps(notify_methods or ["browser"]),
        now
    ))

    conn.commit()
    conn.close()

    return {
        "id": sub_id,
        "up_mid": up_mid,
        "up_name": up_name,
        "created_at": now
    }


def unsubscribe_up(user_id: str, subscription_id: str) -> bool:
    """取消订阅"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM up_subscriptions WHERE id = ? AND user_id = ?",
        (subscription_id, user_id)
    )

    conn.commit()
    affected = cursor.rowcount > 0
    conn.close()

    return affected


def get_user_subscriptions(user_id: str) -> List[Dict[str, Any]]:
    """获取用户的订阅列表"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, up_mid, up_name, up_avatar, notify_methods, last_video_bvid, created_at
        FROM up_subscriptions
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row["id"],
            "up_mid": row["up_mid"],
            "up_name": row["up_name"],
            "up_avatar": row["up_avatar"],
            "notify_methods": json.loads(row["notify_methods"]) if row["notify_methods"] else [],
            "last_video_bvid": row["last_video_bvid"],
            "created_at": row["created_at"]
        }
        for row in rows
    ]


def get_all_subscriptions() -> List[Dict[str, Any]]:
    """获取所有订阅（用于定时任务）"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, user_id, up_mid, up_name, notify_methods, last_video_bvid, last_checked_at
        FROM up_subscriptions
    """)

    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        item = dict(row)
        # 解析 notify_methods JSON
        if item.get("notify_methods"):
            try:
                item["notify_methods"] = json.loads(item["notify_methods"])
            except (json.JSONDecodeError, TypeError):
                item["notify_methods"] = ["browser"]
        else:
            item["notify_methods"] = ["browser"]
        result.append(item)

    return result


def update_subscription_check(subscription_id: str, last_video_bvid: str):
    """更新订阅的检查状态"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE up_subscriptions
        SET last_checked_at = ?, last_video_bvid = ?
        WHERE id = ?
    """, (datetime.utcnow().isoformat(), last_video_bvid, subscription_id))

    conn.commit()
    conn.close()
