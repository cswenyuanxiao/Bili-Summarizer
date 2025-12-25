"""
B站API请求速率限制器
使用令牌桶算法，避免触发风控
"""
import time
import asyncio
from typing import Optional

class BilibiliRateLimiter:
    """
    令牌桶限流器
    - 每秒补充1个令牌，最多存储5个
    - 每次调用B站API消耗1个令牌
    """
    def __init__(self, rate: float = 1.0, capacity: int = 5):
        """
        Args:
            rate: 每秒产生的令牌数
            capacity: 桶的最大容量
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """
        获取一个令牌，如果没有则等待
        """
        async with self._lock:
            now = time.time()
            # 补充令牌
            elapsed = now - self.last_update
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            # 如果没有令牌，等待到下一个令牌生成
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1

# 全局限流器
bilibili_limiter = BilibiliRateLimiter(rate=0.5, capacity=3)  # 每2秒1个请求


async def call_bilibili_api_with_limit(api_func, *args, **kwargs):
    """
    包装B站API调用，自动限流
    
    使用示例:
        result = await call_bilibili_api_with_limit(get_up_latest_video, mid="123")
    """
    await bilibili_limiter.acquire()
    return await api_func(*args, **kwargs)
