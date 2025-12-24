"""
请求限流器
使用令牌桶算法实现
"""
import time
import asyncio
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict
import logging

logger = logging.getLogger(__name__)

@dataclass
class RateLimitConfig:
    requests_per_minute: int = 15  # 每分钟最大请求数 (调整略高一点，给予用户容差)
    requests_per_hour: int = 100   # 每小时最大请求数
    burst_size: int = 5            # 突发容量

class TokenBucket:
    def __init__(self, rate: float, capacity: int):
        self.rate = rate  # 每秒添加的令牌数
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_update = now
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def time_until_available(self, tokens: int = 1) -> float:
        if self.tokens >= tokens:
            return 0
        return (tokens - self.tokens) / self.rate

class RateLimiter:
    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        self.user_buckets: Dict[str, TokenBucket] = {}
        self.global_bucket = TokenBucket(
            rate=self.config.requests_per_minute / 60,
            capacity=self.config.burst_size
        )
    
    def _get_user_bucket(self, user_id: str) -> TokenBucket:
        if user_id not in self.user_buckets:
            self.user_buckets[user_id] = TokenBucket(
                rate=self.config.requests_per_minute / 60,
                capacity=self.config.burst_size
            )
        return self.user_buckets[user_id]
    
    async def acquire(self, user_id: str) -> bool:
        """尝试获取请求配额"""
        # 检查全局限流
        if not self.global_bucket.consume():
            wait_time = self.global_bucket.time_until_available()
            logger.warning(f"Global rate limit hit, wait {wait_time:.2f}s")
            return False
        
        # 检查用户限流
        user_bucket = self._get_user_bucket(user_id)
        if not user_bucket.consume():
            wait_time = user_bucket.time_until_available()
            logger.warning(f"User {user_id} rate limit hit, wait {wait_time:.2f}s")
            return False
        
        return True
    
    def get_wait_time(self, user_id: str) -> float:
        """获取需要等待的时间"""
        global_wait = self.global_bucket.time_until_available()
        user_bucket = self._get_user_bucket(user_id)
        user_wait = user_bucket.time_until_available()
        return max(global_wait, user_wait)

# 全局限流器
rate_limiter = RateLimiter()
