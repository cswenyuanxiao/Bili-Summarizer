import logging
import os
from typing import List

import httpx
from fastapi import HTTPException

from ..schemas import HistoryItem

logger = logging.getLogger(__name__)


async def get_user_history(user_id: str, user_token: str) -> List[dict]:
    """获取用户的云端历史记录"""
    try:
        from supabase import create_client

        supabase_url = os.getenv("SUPABASE_URL")
        service_key = os.getenv("SUPABASE_SERVICE_KEY")
        anon_key = os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url or (not service_key and not anon_key):
            logger.warning("Supabase not configured, returning empty history")
            return []

        if service_key:
            supabase = create_client(supabase_url, service_key)
            response = (
                supabase.table("summaries")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(50)
                .execute()
            )
            return response.data

        headers = {
            "apikey": anon_key,
            "Authorization": f"Bearer {user_token}",
        }
        params = {
            "select": "*",
            "user_id": f"eq.{user_id}",
            "order": "created_at.desc",
            "limit": "50",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{supabase_url}/rest/v1/summaries",
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Get history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def sync_history(items: List[HistoryItem], user_id: str, user_token: str) -> dict:
    """批量上传本地历史到云端"""
    try:
        from supabase import create_client

        supabase_url = os.getenv("SUPABASE_URL")
        service_key = os.getenv("SUPABASE_SERVICE_KEY")
        anon_key = os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url or (not service_key and not anon_key):
            return {"uploaded": 0, "total": len(items), "error": "Supabase not configured"}

        if service_key:
            supabase = create_client(supabase_url, service_key)
            uploaded = 0
            errors = []
            for item in items:
                try:
                    data = item.dict(exclude_none=True, exclude={"id"})
                    data["user_id"] = user_id

                    # 尝试直接插入
                    # 如果数据库有唯一约束 (video_url / user_id)，重复插入会报 409 Conflict
                    # 我们在此处捕获该错误并视为成功 (幂等性)
                    supabase.table("summaries").insert(data).execute()
                    uploaded += 1
                except Exception as e:
                    error_str = str(e)
                    # 如果是 409 Conflict（重复插入），视为成功
                    if "409" in error_str or "Conflict" in error_str or "duplicate" in error_str.lower():
                        logger.info(f"Item already exists (409), counting as success: {item.video_url}")
                        uploaded += 1
                    else:
                        logger.error(f"Sync error for {item.video_url}: {e}")
                        errors.append(str(e))
            return {"uploaded": uploaded, "total": len(items), "errors": errors if errors else None}

        headers = {
            "apikey": anon_key,
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
        }
        payload = []
        for item in items:
            data = item.dict(exclude_none=True, exclude={"id"})
            data["user_id"] = user_id
            payload.append(data)

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{supabase_url}/rest/v1/summaries",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            return {"uploaded": len(payload), "total": len(items), "errors": None}
    except Exception as e:
        logger.error(f"Batch sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def delete_history_item(history_id: str, user_id: str, user_token: str) -> dict:
    """删除云端历史记录"""
    try:
        from supabase import create_client

        supabase_url = os.getenv("SUPABASE_URL")
        service_key = os.getenv("SUPABASE_SERVICE_KEY")
        anon_key = os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url or (not service_key and not anon_key):
            raise HTTPException(503, "Supabase not configured")

        if service_key:
            supabase = create_client(supabase_url, service_key)
            (
                supabase.table("summaries")
                .delete()
                .eq("id", history_id)
                .eq("user_id", user_id)
                .execute()
            )
            return {"message": "History item deleted"}

        headers = {
            "apikey": anon_key,
            "Authorization": f"Bearer {user_token}",
        }
        params = {
            "id": f"eq.{history_id}",
            "user_id": f"eq.{user_id}",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.delete(
                f"{supabase_url}/rest/v1/summaries",
                headers=headers,
                params=params,
            )
            response.raise_for_status()

        return {"message": "History item deleted"}
    except Exception as e:
        logger.error(f"Delete history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
