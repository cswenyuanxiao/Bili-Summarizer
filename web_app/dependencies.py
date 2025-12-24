"""
Dependencies - FastAPI 依赖注入模块
统一管理认证、数据库连接等共享依赖
"""
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from .auth import verify_session_token
from .db import get_connection

logger = logging.getLogger(__name__)

# HTTP Bearer 安全方案
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> dict:
    """
    获取当前已认证用户（必须登录）
    用法: user: dict = Depends(get_current_user)
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        user = await verify_session_token(credentials.credentials)
        return user
    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    获取当前用户（可选，未登录返回 None）
    用法: user: Optional[dict] = Depends(get_optional_user)
    """
    if not credentials:
        return None
    
    try:
        return await verify_session_token(credentials.credentials)
    except:
        return None


def get_db():
    """
    获取数据库连接（生成器模式，自动关闭）
    用法: db = Depends(get_db)
    """
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


class RateLimitDep:
    """
    速率限制依赖
    用法: _: None = Depends(RateLimitDep(requests_per_minute=10))
    """
    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute
    
    async def __call__(
        self,
        request: Request,
        user: Optional[dict] = Depends(get_optional_user)
    ):
        # 简化实现 - 实际应使用 redis 或内存缓存
        # 这里仅作为依赖注入模式示例
        pass


# 常用依赖组合
async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """要求管理员权限"""
    from .main import is_unlimited_user
    if not is_unlimited_user(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
