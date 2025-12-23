import secrets
import hashlib
from datetime import datetime
from fastapi import Request, Header, HTTPException
from supabase import create_client
import os
import sqlite3

# Supabase 客户端（如果配置）
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

async def verify_session_token(token: str) -> dict:
    """验证 Supabase JWT Token"""
    if not supabase:
        raise HTTPException(503, "Auth service unavailable")
    
    try:
        response = supabase.auth.get_user(token)
        if not response or not response.user:
            raise HTTPException(401, "Invalid session token")
        return {"user_id": response.user.id, "email": response.user.email, "source": "session"}
    except Exception as e:
        raise HTTPException(401, f"Session verification failed: {str(e)}")

def record_api_key_usage(key_id: str, user_id: str) -> None:
    """记录 API Key 使用次数（按天汇总）"""
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO api_key_usage_daily (key_id, user_id, date, count)
            VALUES (?, ?, DATE('now'), 1)
            ON CONFLICT(key_id, date)
            DO UPDATE SET count = count + 1
        """, (key_id, user_id))
        conn.commit()
    except Exception:
        # Usage tracking should never block auth
        conn.rollback()
    finally:
        conn.close()

async def verify_api_key(api_key: str) -> dict:
    """验证 API Key 并返回用户信息"""
    if not api_key.startswith("sk-bili-"):
        raise HTTPException(401, "Invalid API key format")
    
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    # 从数据库查询
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, user_id, is_active 
            FROM api_keys 
            WHERE key_hash = ?
        """, (key_hash,))
        
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(401, "Invalid API key")
        
        key_id, user_id, is_active = row
        
        if not is_active:
            raise HTTPException(401, "API key has been revoked")
        
        # 更新最后使用时间（后台异步）
        cursor.execute("""
            UPDATE api_keys 
            SET last_used_at = ? 
            WHERE key_hash = ?
        """, (datetime.now().isoformat(), key_hash))
        conn.commit()
        
        record_api_key_usage(key_id, user_id)
        return {"user_id": user_id, "source": "api_key", "api_key_id": key_id}
    
    finally:
        conn.close()

async def get_current_user(
    request: Request,
    x_api_key: str = Header(default="")
) -> dict:
    """
    统一鉴权入口：API Key 或 Session Token 二选一
    
    优先级：
    1. x-api-key Header
    2. Authorization Bearer Token
    
    如果两者都无，返回 401
    """
    # 优先级1: API Key
    if x_api_key:
        user = await verify_api_key(x_api_key)
        from .credits import ensure_user_credits
        ensure_user_credits(user["user_id"])
        return user
    
    # 优先级2: Session Token
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        user = await verify_session_token(auth_header[7:])
        from .credits import ensure_user_credits
        ensure_user_credits(user["user_id"])
        return user
    
    # 两者都无
    raise HTTPException(401, "Missing authentication credentials (API key or session token required)")
