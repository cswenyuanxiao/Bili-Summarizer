"""
Subscriptions Router - UP主订阅管理端点
"""
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

from ..auth import verify_session_token
from ..subscriptions import (
    search_up,
    subscribe_up,
    unsubscribe_up,
    get_user_subscriptions,
    get_up_latest_videos
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/subscriptions", tags=["Subscriptions"])


class UPSubscribeRequest(BaseModel):
    up_mid: str
    up_name: str
    up_avatar: str = ""
    notify_methods: List[str] = ["browser"]


@router.get("/search")
async def search_up_users(keyword: str):
    """搜索 UP 主"""
    if not keyword or len(keyword) < 2:
        return {"users": []}
    
    users = await search_up(keyword)
    return {"users": users}


@router.get("")
async def list_subscriptions(request: Request):
    """获取用户订阅列表"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    subscriptions = get_user_subscriptions(user["user_id"])
    return {"subscriptions": subscriptions}


@router.post("")
async def handle_up_subscribe(request: Request, body: UPSubscribeRequest):
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


@router.delete("/{subscription_id}")
async def cancel_subscription(subscription_id: str, request: Request):
    """取消订阅"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    success = unsubscribe_up(user["user_id"], subscription_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return {"status": "success"}


@router.get("/videos")
async def get_up_videos(up_mid: str, count: int = 2, request: Request = None):
    """获取UP主最新视频列表
    
    Args:
        up_mid: UP主的mid
        count: 获取视频数量,默认2个
        request: FastAPI Request对象(可选,用于验证)
    
    Returns:
        {"up_mid": "xxx", "videos": [...]}
    """
    # 可选: 验证用户登录状态
    if request:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        try:
            await verify_session_token(token)
        except HTTPException:
            pass  # 允许未登录用户查询
    
    # 获取视频列表
    videos = await get_up_latest_videos(up_mid, count)
    
    # 即使遇到风控也容错,返回空列表
    if videos is None:
        videos = []
    
    return {
        "up_mid": up_mid,
        "videos": videos
    }
