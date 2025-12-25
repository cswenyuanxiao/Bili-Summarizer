"""
API Keys Router - API 密钥管理相关端点
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import secrets
import hashlib
from datetime import datetime

from ..dependencies import get_current_user
from ..db import get_connection

router = APIRouter(prefix="/api/keys", tags=["API Keys"])


class CreateKeyRequest(BaseModel):
    name: str


@router.post("")
async def create_api_key(request: CreateKeyRequest, user: dict = Depends(get_current_user)):
    """创建新的 API Key"""
    import uuid
    
    # 生成唯一的 API key
    key = f"sk-{secrets.token_urlsafe(32)}"
    key_id = str(uuid.uuid4())
    prefix = key[:12]  # 只显示前缀
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO api_keys (id, user_id, name, prefix, key_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (key_id, user["user_id"], request.name, prefix, key_hash, datetime.utcnow().isoformat()))
        conn.commit()
        
        # 只返回一次完整的 key
        return {
            "id": key_id,
            "name": request.name,
            "key": key,  # 完整密钥只返回一次
            "prefix": prefix,
            "created_at": datetime.utcnow().isoformat()
        }
    finally:
        conn.close()


@router.get("")
async def list_api_keys(user: dict = Depends(get_current_user)):
    """列出用户的所有 API Key"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, name, prefix, created_at, last_used_at, is_active
            FROM api_keys
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user["user_id"],))
        
        keys = []
        for row in cursor.fetchall():
            keys.append({
                "id": row[0],
                "name": row[1],
                "prefix": row[2],
                "created_at": row[3],
                "last_used_at": row[4],
                "is_active": bool(row[5])
            })
        
        return keys
    finally:
        conn.close()


@router.delete("/{key_id}")
async def delete_api_key(key_id: str, user: dict = Depends(get_current_user)):
    """删除指定的 API Key"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 验证所有权并删除
        cursor.execute("""
            DELETE FROM api_keys
            WHERE id = ? AND user_id = ?
        """, (key_id, user["user_id"]))
        
        if cursor.rowcount == 0:
            raise HTTPException(404, "API key not found or unauthorized")
        
        conn.commit()
        return {"message": "API key deleted successfully"}
    finally:
        conn.close()


@router.get("/usage")
async def get_api_key_usage(user: dict = Depends(get_current_user)):
    """获取API Key使用统计"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, name, prefix, last_used_at
            FROM api_keys
            WHERE user_id = ?
        """, (user["user_id"],))
        keys = cursor.fetchall()

        cursor.execute("""
            SELECT key_id, SUM(count)
            FROM api_key_usage_daily
            WHERE user_id = ?
            GROUP BY key_id
        """, (user["user_id"],))
        total_usage = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute("""
            SELECT key_id, SUM(count)
            FROM api_key_usage_daily
            WHERE user_id = ?
              AND date >= DATE('now', '-6 day')
            GROUP BY key_id
        """, (user["user_id"],))
        recent_usage = {row[0]: row[1] for row in cursor.fetchall()}

        data = []
        for row in keys:
            key_id = row[0]
            data.append({
                "id": key_id,
                "name": row[1],
                "prefix": row[2],
                "last_used_at": row[3],
                "total_uses": int(total_usage.get(key_id, 0) or 0),
                "uses_7d": int(recent_usage.get(key_id, 0) or 0)
            })
        return data
    finally:
        conn.close()
