"""
Health check router - 独立于 DB 的健康检查端点
必须第一个注册，确保即使 DB 初始化失败也能响应
"""
from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Health check endpoint - no DB dependency"""
    return {"status": "ok", "service": "Bili-Summarizer"}


@router.get("/api/health")
async def api_health_check():
    """API health check endpoint"""
    return {"status": "ok", "service": "Bili-Summarizer API"}
