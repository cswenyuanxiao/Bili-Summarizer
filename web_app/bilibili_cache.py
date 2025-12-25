"""
B站视频缓存管理
避免重复请求同一个UP主的视频列表
"""
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import json

@dataclass
class CacheEntry:
    """缓存条目"""
    data: Any
    timestamp: float
    ttl: int  # 存活时间（秒）
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        return time.time() - self.timestamp > self.ttl


class BilibiliVideoCache:
    """
    UP主视频列表缓存
    - 成功获取的数据缓存1小时
    - 失败的请求缓存5分钟（避免重复失败）
    """
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
    
    def get(self, mid: str) -> Optional[List[Dict[str, Any]]]:
        """
        获取缓存的视频列表
        
        Args:
            mid: UP主ID
            
        Returns:
            视频列表，如果未命中或过期则返回None
        """
        entry = self._cache.get(mid)
        if entry and not entry.is_expired():
            return entry.data
        elif entry and entry.is_expired():
            # 清理过期条目
            del self._cache[mid]
        return None
    
    def set_success(self, mid: str, videos: List[Dict[str, Any]]) -> None:
        """
        缓存成功获取的视频列表
        
        Args:
            mid: UP主ID
            videos: 视频列表
        """
        self._cache[mid] = CacheEntry(
            data=videos,
            timestamp=time.time(),
            ttl=3600  # 1小时
        )
    
    def set_failure(self, mid: str) -> None:
        """
        缓存失败的请求（避免短时间内重复请求）
        
        Args:
            mid: UP主ID
        """
        self._cache[mid] = CacheEntry(
            data=[],
            timestamp=time.time(),
            ttl=300  # 5分钟
        )
    
    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
    
    def remove(self, mid: str) -> None:
        """删除特定UP主的缓存"""
        if mid in self._cache:
            del self._cache[mid]


# 全局缓存实例
video_cache = BilibiliVideoCache()
