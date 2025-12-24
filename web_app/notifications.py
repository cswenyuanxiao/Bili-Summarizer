"""
通知服务
支持邮件和浏览器推送
"""
import uuid
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from .db import get_connection

logger = logging.getLogger(__name__)

# VAPID 密钥（浏览器推送需要）
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "")
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "")
VAPID_CLAIMS = {"sub": "mailto:admin@bili-summarizer.com"}


async def queue_notification(
    user_id: str,
    notification_type: str,
    title: str,
    body: str,
    payload: Dict[str, Any] = None,
    methods: List[str] = None
):
    """将通知加入队列"""
    conn = get_connection()
    cursor = conn.cursor()
    
    for method in (methods or ["browser"]):
        notification_id = f"ntf_{uuid.uuid4().hex[:12]}"
        
        cursor.execute("""
            INSERT INTO notification_queue 
            (id, user_id, type, title, body, payload, method, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?)
        """, (
            notification_id,
            user_id,
            notification_type,
            title,
            body,
            json.dumps(payload or {}),
            method,
            datetime.utcnow().isoformat()
        ))
    
    conn.commit()
    conn.close()


async def process_notification_queue():
    """处理通知队列"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, user_id, type, title, body, payload, method
        FROM notification_queue
        WHERE status = 'pending'
        ORDER BY created_at
        LIMIT 100
    """)
    
    notifications = cursor.fetchall()
    conn.close()
    
    for ntf in notifications:
        try:
            if ntf["method"] == "email":
                await send_email_notification(
                    user_id=ntf["user_id"],
                    title=ntf["title"],
                    body=ntf["body"],
                    payload=json.loads(ntf["payload"])
                )
            elif ntf["method"] == "browser":
                await send_browser_push(
                    user_id=ntf["user_id"],
                    title=ntf["title"],
                    body=ntf["body"],
                    payload=json.loads(ntf["payload"])
                )
            
            # 标记为已发送
            mark_notification_sent(ntf["id"])
            
        except Exception as e:
            logger.error(f"Failed to send notification {ntf['id']}: {e}")
            mark_notification_failed(ntf["id"])


async def send_email_notification(
    user_id: str,
    title: str,
    body: str,
    payload: Dict[str, Any]
):
    """发送邮件通知"""
    # 计划集成 Resend 或 SendGrid
    logger.info(f"Email mock: to user {user_id}, title: {title}")


async def send_browser_push(
    user_id: str,
    title: str,
    body: str,
    payload: Dict[str, Any]
):
    """发送浏览器推送"""
    from pywebpush import webpush, WebPushException
    
    if not VAPID_PRIVATE_KEY:
        logger.warning("VAPID_PRIVATE_KEY is missing, skip browser push")
        return

    # 获取用户的推送订阅
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT endpoint, p256dh, auth FROM push_subscriptions WHERE user_id = ?",
        (user_id,)
    )
    
    subscriptions = cursor.fetchall()
    conn.close()
    
    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub["endpoint"],
                    "keys": {
                        "p256dh": sub["p256dh"],
                        "auth": sub["auth"]
                    }
                },
                data=json.dumps({
                    "title": title,
                    "body": body,
                    **payload
                }),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims=VAPID_CLAIMS
            )
            logger.info(f"Push sent to user {user_id}")
        except WebPushException as e:
            logger.error(f"Push failed for endpoint {sub['endpoint']}: {e}")
            # 如果是 410 Gone，可以考虑删除订阅
            if "Gone" in str(e):
                delete_push_subscription(sub["endpoint"])


def mark_notification_sent(notification_id: str):
    """标记通知为已发送"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE notification_queue SET status = 'sent', sent_at = ? WHERE id = ?",
        (datetime.utcnow().isoformat(), notification_id)
    )
    conn.commit()
    conn.close()


def mark_notification_failed(notification_id: str):
    """标记通知为发送失败"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE notification_queue SET status = 'failed' WHERE id = ?",
        (notification_id,)
    )
    conn.commit()
    conn.close()


def save_push_subscription(
    user_id: str,
    endpoint: str,
    p256dh: str,
    auth: str
):
    """保存浏览器推送订阅"""
    sub_id = f"push_{uuid.uuid4().hex[:12]}"
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO push_subscriptions (id, user_id, endpoint, p256dh, auth, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, endpoint) DO UPDATE SET
            p256dh = EXCLUDED.p256dh,
            auth = EXCLUDED.auth
    """, (
        sub_id,
        user_id,
        endpoint,
        p256dh,
        auth,
        datetime.utcnow().isoformat()
    ))
    
    conn.commit()
    conn.close()


def delete_push_subscription(endpoint: str):
    """删除推送订阅"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM push_subscriptions WHERE endpoint = ?", (endpoint,))
    conn.commit()
    conn.close()
