"""
B 站收藏夹解析服务
支持解析收藏夹列表并批量总结
"""
import re
import asyncio
import logging
from typing import List, Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)

# B 站 API 基础路径
BILIBILI_API = "https://api.bilibili.com"


def parse_favorites_url(url: str) -> Optional[str]:
    """
    解析收藏夹 URL，提取 media_id (mlid)
    支持格式:
    - https://www.bilibili.com/medialist/detail/ml123456
    - https://space.bilibili.com/123456/favlist?fid=789
    """
    # 匹配 mlid
    mlid_match = re.search(r"ml(\d+)", url)
    if mlid_match:
        return mlid_match.group(1)
    
    # 匹配 fid
    fid_match = re.search(r"fid=(\d+)", url)
    if fid_match:
        return fid_match.group(1)
    
    return None


async def fetch_favorites_info(media_id: str) -> Dict[str, Any]:
    """获取收藏夹基本信息"""
    url = f"{BILIBILI_API}/x/v3/fav/folder/info"
    params = {"media_id": media_id}
    
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, params=params)
        data = response.json()
        
        if data.get("code") != 0:
            error_msg = data.get("message", "获取收藏夹信息失败")
            logger.error(f"Failed to fetch favorites info: {error_msg}")
            raise ValueError(error_msg)
        
        info = data.get("data", {})
        return {
            "title": info.get("title", "未知收藏夹"),
            "owner": info.get("upper", {}).get("name", "未知用户"),
            "media_count": info.get("media_count", 0),
            "cover": info.get("cover", "")
        }


async def fetch_favorites_videos(
    media_id: str,
    page: int = 1,
    page_size: int = 20
) -> Dict[str, Any]:
    """
    分页获取收藏夹中的视频列表
    """
    url = f"{BILIBILI_API}/x/v3/fav/resource/list"
    params = {
        "media_id": media_id,
        "pn": page,
        "ps": page_size,
        "keyword": "",
        "order": "mtime",
        "type": 0,  # 0: 全部
        "tid": 0,
        "platform": "web"
    }
    
    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        response = await client.get(url, params=params)
        data = response.json()
        
        if data.get("code") != 0:
            error_msg = data.get("message", "获取视频列表失败")
            logger.error(f"Failed to fetch favorites videos: {error_msg}")
            raise ValueError(error_msg)
        
        result = data.get("data", {})
        medias = result.get("medias") or []
        
        videos = []
        for item in medias:
            # 过滤失效视频
            if item.get("attr") == 1:
                continue
                
            videos.append({
                "bvid": item.get("bvid", ""),
                "title": item.get("title", ""),
                "cover": item.get("cover", ""),
                "duration": item.get("duration", 0),
                "url": f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                "pubtime": item.get("pubtime", 0)
            })
        
        return {
            "has_more": result.get("has_more", False),
            "total": result.get("info", {}).get("media_count", len(videos)),
            "videos": videos
        }


async def fetch_all_favorites_videos(media_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """获取收藏夹中的全部视频（带上限）"""
    all_videos = []
    page = 1
    page_size = 20
    
    while len(all_videos) < limit:
        result = await fetch_favorites_videos(media_id, page, page_size)
        videos = result.get("videos", [])
        
        if not videos:
            break
            
        all_videos.extend(videos)
        
        if not result.get("has_more") or len(all_videos) >= limit:
            break
            
        page += 1
        await asyncio.sleep(0.5)  # 避免请求过快
        
    return all_videos[:limit]
