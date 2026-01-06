"""
History Router - 历史记录同步相关端点
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List
import os
import logging

from ..dependencies import get_current_user
from ..schemas import HistoryItem

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/history", tags=["History"])


@router.get("")
async def get_user_history(
    request: Request,
    user: dict = Depends(get_current_user)
):
    """获取用户的云端历史记录"""
    try:
        from supabase import create_client
        import httpx
        
        supabase_url = os.getenv("SUPABASE_URL")
        service_key = os.getenv("SUPABASE_SERVICE_KEY")
        anon_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or (not service_key and not anon_key):
            logger.warning("Supabase not configured, returning empty history")
            return []

        auth_header = request.headers.get("Authorization", "")
        user_token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""

        if service_key:
            supabase = create_client(supabase_url, service_key)
            response = supabase.table("summaries")\
                .select("*")\
                .eq("user_id", user["user_id"])\
                .order("created_at", desc=True)\
                .limit(50)\
                .execute()
            return response.data

        headers = {
            "apikey": anon_key,
            "Authorization": f"Bearer {user_token}",
        }
        params = {
            "select": "*",
            "user_id": f"eq.{user['user_id']}",
            "order": "created_at.desc",
            "limit": "50",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{supabase_url}/rest/v1/summaries", headers=headers, params=params)
            response.raise_for_status()
            return response.json()
    
    except Exception as e:
        logger.error(f"Get history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def sync_history(
    request: Request,
    items: List[HistoryItem],
    user: dict = Depends(get_current_user)
):
    """批量上传本地历史到云端"""
    try:
        from supabase import create_client
        import httpx
        
        supabase_url = os.getenv("SUPABASE_URL")
        service_key = os.getenv("SUPABASE_SERVICE_KEY")
        anon_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or (not service_key and not anon_key):
            return {"uploaded": 0, "total": len(items), "error": "Supabase not configured"}

        auth_header = request.headers.get("Authorization", "")
        user_token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""

        if service_key:
            supabase = create_client(supabase_url, service_key)
            uploaded = 0
            errors = []
            for item in items:
                try:
                    data = item.dict(exclude_none=True, exclude={"id"})
                    data["user_id"] = user["user_id"]
                    supabase.table("summaries").upsert(data).execute()
                    uploaded += 1
                except Exception as e:
                    logger.error(f"Sync error for {item.video_url}: {e}")
                    errors.append(str(e))
            return {
                "uploaded": uploaded,
                "total": len(items),
                "errors": errors if errors else None
            }

        headers = {
            "apikey": anon_key,
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
        }
        payload = []
        for item in items:
            data = item.dict(exclude_none=True, exclude={"id"})
            data["user_id"] = user["user_id"]
            payload.append(data)

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{supabase_url}/rest/v1/summaries", headers=headers, json=payload)
            response.raise_for_status()
            return {"uploaded": len(payload), "total": len(items), "errors": None}
    
    except Exception as e:
        logger.error(f"Batch sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{history_id}")
async def delete_history_item(
    history_id: str,
    request: Request,
    user: dict = Depends(get_current_user)
):
    """删除云端历史记录"""
    try:
        from supabase import create_client
        import httpx
        
        supabase_url = os.getenv("SUPABASE_URL")
        service_key = os.getenv("SUPABASE_SERVICE_KEY")
        anon_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or (not service_key and not anon_key):
            raise HTTPException(503, "Supabase not configured")

        auth_header = request.headers.get("Authorization", "")
        user_token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""

        if service_key:
            supabase = create_client(supabase_url, service_key)
            supabase.table("summaries")\
                .delete()\
                .eq("id", history_id)\
                .eq("user_id", user["user_id"])\
                .execute()
            return {"message": "History item deleted"}

        headers = {
            "apikey": anon_key,
            "Authorization": f"Bearer {user_token}",
        }
        params = {
            "id": f"eq.{history_id}",
            "user_id": f"eq.{user['user_id']}",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.delete(f"{supabase_url}/rest/v1/summaries", headers=headers, params=params)
            response.raise_for_status()
        
        return {"message": "History item deleted"}
    
    except Exception as e:
        logger.error(f"Delete history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
