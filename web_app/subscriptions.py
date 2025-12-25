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
    url = f"https://api.bilibili.com/x/web-interface/search/type"
    params = {
        "keyword": keyword,
        "search_type": "bili_user",
        "page": 1,
        "page_size": limit
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://search.bilibili.com/",
        "Cookie": "buvid3=infoc;"  # 尝试简单的 buvid3
    }
    
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(url, params=params, headers=headers)
            data = response.json()
            
            if data.get("code") != 0:
                logger.error(f"Search UP failed: {data.get('message')}")
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
        except Exception as e:
            logger.error(f"Search UP exception: {e}")
            return []


from .wbi import sign_wbi, parse_wbi_keys

async def get_up_latest_video(
    mid: str, 
    client: Optional[httpx.AsyncClient] = None, 
    wbi_keys: Optional[tuple[str, str]] = None
) -> Optional[Dict[str, Any]]:
    """获取 UP 主最新视频 (支持 WBI 签名)"""
    
    should_close = False
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://space.bilibili.com/"
    }

    if not client:
        client = httpx.AsyncClient(headers=headers, timeout=10)
        should_close = True
    
    try:
        # 如果没有 key 或 是新创建的 client (没有 cookie)，都需要请求 nav
        # 注意：WBI 接口强依赖 /nav 接口种下的 buvid3/buvid4 cookie
        if not wbi_keys or should_close:
            try:
                nav_resp = await client.get("https://api.bilibili.com/x/web-interface/nav")
                nav_data = nav_resp.json()
                if not wbi_keys:
                    wbi_keys = parse_wbi_keys(nav_data)
            except Exception as e:
                logger.error(f"Failed to fetch nav info: {e}")
                return None

        if not wbi_keys or not wbi_keys[0]:
            logger.error("Failed to parse WBI keys")
            return None

        img_key, sub_key = wbi_keys
        
        # 构造 WBI 请求
        url = f"https://api.bilibili.com/x/space/wbi/arc/search"
        params = {
            "mid": mid,
            "pn": 1,
            "ps": 1,
            "order": "pubdate"
        }
        
        signed_params = sign_wbi(params, img_key, sub_key)
        
        response = await client.get(url, params=signed_params)
        data = response.json()
        
        if data.get("code") != 0:
            logger.error(f"Get UP latest video failed (mid={mid}): {data.get('message', '')} code={data.get('code')}")
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
    except Exception as e:
        logger.error(f"Get UP latest video exception: {e}")
        return None
    finally:
        if should_close:
            await client.aclose()


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
