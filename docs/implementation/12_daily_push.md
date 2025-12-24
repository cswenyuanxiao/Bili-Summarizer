# 每日总结推送实施计划

> 优先级: P4 | 预估工作量: 14h | 依赖: APScheduler, 邮件/推送服务

---

## 1. 功能概述

用户订阅 UP 主，系统每日自动检测新视频并推送总结通知。

### 用户故事

1. 用户在「订阅管理」页面搜索并订阅 UP 主
2. 设置通知方式（邮件/浏览器推送）
3. 系统定时检测订阅 UP 主的新视频
4. 发现新视频后自动总结并推送通知
5. 用户可在通知中直接查看总结

---

## 2. 技术方案

### 2.1 数据模型

```sql
-- UP 主订阅表
CREATE TABLE IF NOT EXISTS up_subscriptions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    up_mid TEXT NOT NULL,           -- UP 主 ID
    up_name TEXT,                   -- UP 主昵称
    up_avatar TEXT,                 -- UP 主头像
    notify_methods TEXT,            -- JSON: ["email", "browser"]
    last_checked_at TEXT,           -- 上次检查时间
    last_video_bvid TEXT,           -- 上次检查到的最新视频
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, up_mid)
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON up_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_up ON up_subscriptions(up_mid);

-- 通知队列表
CREATE TABLE IF NOT EXISTS notification_queue (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    type TEXT NOT NULL,             -- new_video / summary_ready
    title TEXT,
    body TEXT,
    payload TEXT,                   -- JSON 附加数据
    status TEXT DEFAULT 'pending',  -- pending / sent / failed
    method TEXT,                    -- email / browser / wechat
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    sent_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_notifications_status ON notification_queue(status);

-- 浏览器推送订阅表
CREATE TABLE IF NOT EXISTS push_subscriptions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    p256dh TEXT NOT NULL,
    auth TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, endpoint)
);
```

---

### 2.2 后端实现

#### 安装依赖

```bash
# 添加到 requirements.txt
APScheduler>=3.10.0
pywebpush>=1.14.0

# 安装
pip install APScheduler pywebpush
```

#### 新增文件: `web_app/subscriptions.py`

```python
"""
UP 主订阅管理服务
"""
import uuid
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import httpx
import logging

from .db import get_connection

logger = logging.getLogger(__name__)

BILIBILI_API = "https://api.bilibili.com"


async def search_up(keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
    """搜索 UP 主"""
    url = f"{BILIBILI_API}/x/web-interface/search/type"
    params = {
        "keyword": keyword,
        "search_type": "bili_user",
        "page": 1,
        "page_size": limit
    }
    
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, params=params)
        data = response.json()
        
        if data.get("code") != 0:
            return []
        
        results = []
        for item in data.get("data", {}).get("result", []):
            results.append({
                "mid": str(item.get("mid")),
                "name": item.get("uname", ""),
                "avatar": item.get("upic", ""),
                "fans": item.get("fans", 0),
                "videos": item.get("videos", 0),
                "sign": item.get("usign", "")
            })
        
        return results


async def get_up_latest_video(mid: str) -> Optional[Dict[str, Any]]:
    """获取 UP 主最新视频"""
    url = f"{BILIBILI_API}/x/space/wbi/arc/search"
    params = {
        "mid": mid,
        "pn": 1,
        "ps": 1,
        "order": "pubdate"
    }
    
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, params=params)
        data = response.json()
        
        if data.get("code") != 0:
            return None
        
        videos = data.get("data", {}).get("list", {}).get("vlist", [])
        if not videos:
            return None
        
        v = videos[0]
        return {
            "bvid": v.get("bvid", ""),
            "title": v.get("title", ""),
            "cover": v.get("pic", ""),
            "duration": v.get("length", ""),
            "created": v.get("created", 0),
            "url": f"https://www.bilibili.com/video/{v.get('bvid', '')}"
        }


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
    
    return [dict(row) for row in rows]


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
```

#### 新增文件: `web_app/scheduler.py`

```python
"""
定时任务调度器
"""
import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .subscriptions import get_all_subscriptions, get_up_latest_video, update_subscription_check
from .notifications import queue_notification

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def check_new_videos():
    """检查订阅 UP 主的新视频"""
    logger.info("Starting new video check...")
    
    subscriptions = get_all_subscriptions()
    new_videos_count = 0
    
    for sub in subscriptions:
        try:
            latest = await get_up_latest_video(sub["up_mid"])
            
            if not latest:
                continue
            
            # 检查是否是新视频
            if sub["last_video_bvid"] != latest["bvid"]:
                logger.info(f"New video found: {latest['title']} from {sub['up_name']}")
                
                # 更新订阅状态
                update_subscription_check(sub["id"], latest["bvid"])
                
                # 如果是首次检查（last_video_bvid 为空），不发送通知
                if sub["last_video_bvid"]:
                    # 加入通知队列
                    await queue_notification(
                        user_id=sub["user_id"],
                        notification_type="new_video",
                        title=f"{sub['up_name']} 发布了新视频",
                        body=latest["title"],
                        payload={
                            "video_url": latest["url"],
                            "video_bvid": latest["bvid"],
                            "video_title": latest["title"],
                            "video_cover": latest["cover"],
                            "up_name": sub["up_name"]
                        },
                        methods=sub.get("notify_methods", ["browser"])
                    )
                    new_videos_count += 1
                    
        except Exception as e:
            logger.error(f"Error checking UP {sub['up_mid']}: {e}")
        
        # 添加间隔，避免请求过快
        await asyncio.sleep(1)
    
    logger.info(f"Video check completed. Found {new_videos_count} new videos.")


def start_scheduler():
    """启动调度器"""
    # 每小时检查一次新视频
    scheduler.add_job(
        check_new_videos,
        trigger=IntervalTrigger(hours=1),
        id="check_new_videos",
        replace_existing=True,
        next_run_time=datetime.now()  # 立即执行一次
    )
    
    scheduler.start()
    logger.info("Scheduler started")


def stop_scheduler():
    """停止调度器"""
    scheduler.shutdown()
    logger.info("Scheduler stopped")
```

#### 新增文件: `web_app/notifications.py`

```python
"""
通知服务
支持邮件和浏览器推送
"""
import uuid
import json
import os
from datetime import datetime
from typing import List, Dict, Any
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
    # 获取用户邮箱
    from .auth import get_user_email
    email = get_user_email(user_id)
    
    if not email:
        logger.warning(f"User {user_id} has no email")
        return
    
    # 使用邮件服务发送
    # 这里可以集成 SendGrid / Resend / SMTP
    logger.info(f"Sending email to {email}: {title}")
    
    # TODO: 实现邮件发送逻辑


async def send_browser_push(
    user_id: str,
    title: str,
    body: str,
    payload: Dict[str, Any]
):
    """发送浏览器推送"""
    from pywebpush import webpush, WebPushException
    
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
            logger.error(f"Push failed: {e}")


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
    
    # 使用 upsert
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
```

#### 修改文件: `web_app/main.py`

添加订阅和推送 API：

```python
# === 订阅与推送相关 ===
from .subscriptions import (
    search_up,
    subscribe_up,
    unsubscribe_up,
    get_user_subscriptions
)
from .notifications import save_push_subscription
from .scheduler import start_scheduler, stop_scheduler

# 启动时启动调度器
@app.on_event("startup")
async def start_jobs():
    start_scheduler()

@app.on_event("shutdown")
async def stop_jobs():
    stop_scheduler()

class SubscribeRequest(BaseModel):
    up_mid: str
    up_name: str
    up_avatar: str = ""
    notify_methods: List[str] = ["browser"]

class PushSubscriptionRequest(BaseModel):
    endpoint: str
    keys: Dict[str, str]

@app.get("/api/subscriptions/search")
async def search_up_users(keyword: str):
    """搜索 UP 主"""
    if not keyword or len(keyword) < 2:
        return {"users": []}
    
    users = await search_up(keyword)
    return {"users": users}

@app.get("/api/subscriptions")
async def list_subscriptions(request: Request):
    """获取用户订阅列表"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    subscriptions = get_user_subscriptions(user["user_id"])
    return {"subscriptions": subscriptions}

@app.post("/api/subscriptions")
async def create_subscription(request: Request, body: SubscribeRequest):
    """订阅 UP 主"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    try:
        result = subscribe_up(
            user_id=user["user_id"],
            up_mid=body.up_mid,
            up_name=body.up_name,
            up_avatar=body.up_avatar,
            notify_methods=body.notify_methods
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/subscriptions/{subscription_id}")
async def cancel_subscription(subscription_id: str, request: Request):
    """取消订阅"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    success = unsubscribe_up(user["user_id"], subscription_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return {"message": "Unsubscribed"}

@app.post("/api/push/subscribe")
async def register_push_subscription(request: Request, body: PushSubscriptionRequest):
    """注册浏览器推送订阅"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    save_push_subscription(
        user_id=user["user_id"],
        endpoint=body.endpoint,
        p256dh=body.keys.get("p256dh", ""),
        auth=body.keys.get("auth", "")
    )
    
    return {"message": "Push subscription saved"}

@app.get("/api/push/vapid-key")
async def get_vapid_public_key():
    """获取 VAPID 公钥（用于浏览器订阅）"""
    return {"publicKey": os.getenv("VAPID_PUBLIC_KEY", "")}
```

---

### 2.3 前端实现

#### 新增文件: `frontend/src/pages/SubscriptionsPage.vue`

完整的订阅管理页面，包含搜索、订阅列表、通知设置。

#### 新增文件: `frontend/src/utils/push.ts`

浏览器推送订阅工具函数。

---

## 3. 环境变量

```bash
# VAPID 密钥生成
npx web-push generate-vapid-keys

# 添加到 .env
VAPID_PUBLIC_KEY=xxx
VAPID_PRIVATE_KEY=xxx
```

---

## 4. 实施步骤清单

| 序号 | 任务 | 预估时间 |
|------|------|----------|
| 1 | 数据库表创建 | 30min |
| 2 | subscriptions.py | 2h |
| 3 | scheduler.py | 1.5h |
| 4 | notifications.py | 2.5h |
| 5 | API 端点 | 1.5h |
| 6 | 前端订阅页面 | 3h |
| 7 | 浏览器推送集成 | 2h |
| 8 | 测试 | 1h |

---

## 5. 验收标准

- [ ] 可搜索并订阅 UP 主
- [ ] 订阅列表正确显示
- [ ] 定时任务每小时执行
- [ ] 新视频触发通知
- [ ] 浏览器推送正常送达
- [ ] 可取消订阅
