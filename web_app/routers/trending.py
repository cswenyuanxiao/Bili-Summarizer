"""
Trending Router - B站热门视频推荐
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import httpx
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trending", tags=["Trending"])


@router.get("/videos")
async def get_trending_videos(limit: int = 20):
    """获取B站热门视频列表
    
    Args:
        limit: 返回视频数量，默认20个
    
    Returns:
        {"videos": [...]}
    """
    try:
        # B站热门视频API
        url = "https://api.bilibili.com/x/web-interface/popular"
        params = {"ps": min(limit, 50), "pn": 1}
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Referer": "https://www.bilibili.com"
        }
        
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params=params, headers=headers)
            data = response.json()
            
            if data.get("code") != 0:
                logger.error(f"Get trending failed: {data.get('message')}")
                return {"videos": []}
            
            raw_videos = data.get("data", {}).get("list", [])
            
            # 转换为统一格式
            videos = []
            for v in raw_videos:
                videos.append({
                    "bvid": v.get("bvid", ""),
                    "title": v.get("title", ""),
                    "cover": v.get("pic", ""),
                    "duration": format_duration(v.get("duration", 0)),
                    "view": v.get("stat", {}).get("view", 0),
                    "like": v.get("stat", {}).get("like", 0),
                    "danmaku": v.get("stat", {}).get("danmaku", 0),
                    "url": f"https://www.bilibili.com/video/{v.get('bvid', '')}",
                    "owner": {
                        "name": v.get("owner", {}).get("name", ""),
                        "mid": v.get("owner", {}).get("mid", ""),
                        "face": v.get("owner", {}).get("face", "")
                    },
                    "pubdate": v.get("pubdate", 0),
                    "desc": v.get("desc", "")[:100]  # 简介截取100字
                })
            
            return {"videos": videos}
            
    except Exception as e:
        logger.error(f"Get trending exception: {e}")
        return {"videos": []}


def format_duration(seconds: int) -> str:
    """格式化时长为 mm:ss"""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"
