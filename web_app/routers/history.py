"""
History Router - 历史记录同步相关端点
"""
from fastapi import APIRouter, Depends, Request
from typing import List

from ..dependencies import get_current_user
from ..schemas import HistoryItem
from ..services.history_service import (
    delete_history_item as delete_history_item_service,
    get_user_history as get_user_history_service,
    sync_history as sync_history_service,
)

router = APIRouter(prefix="/api/history", tags=["History"])


@router.get("")
async def get_user_history(
    request: Request,
    user: dict = Depends(get_current_user)
):
    """获取用户的云端历史记录"""
    auth_header = request.headers.get("Authorization", "")
    user_token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    return await get_user_history_service(user["user_id"], user_token)


@router.post("")
async def sync_history(
    request: Request,
    items: List[HistoryItem],
    user: dict = Depends(get_current_user)
):
    """批量上传本地历史到云端"""
    auth_header = request.headers.get("Authorization", "")
    user_token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    return await sync_history_service(items, user["user_id"], user_token)


@router.delete("/{history_id}")
async def delete_history_item(
    history_id: str,
    request: Request,
    user: dict = Depends(get_current_user)
):
    """删除云端历史记录"""
    auth_header = request.headers.get("Authorization", "")
    user_token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    return await delete_history_item_service(history_id, user["user_id"], user_token)
