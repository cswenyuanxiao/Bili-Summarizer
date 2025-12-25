"""
收藏夹管理路由
提供收藏的增删查功能
"""
import uuid
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import logging

from ..db import get_connection
from ..auth import verify_session_token

router = APIRouter(prefix="/api/favorites", tags=["favorites"])
logger = logging.getLogger(__name__)


class FavoriteCreate(BaseModel):
    """添加收藏请求"""
    bvid: str
    title: str
    cover: str
    summary: str = ""


class FavoriteResponse(BaseModel):
    """收藏项响应"""
    id: str
    bvid: str
    title: str
    cover: str
    summary: str
    created_at: str


@router.get("")
async def get_favorites(request: Request) -> Dict[str, List[FavoriteResponse]]:
    """获取用户的所有收藏"""
    # 验证用户身份
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        user_info = await verify_session_token(token)
        user_id = user_info.get("user_id")
    except HTTPException:
        raise HTTPException(status_code=401, detail="未登录或token无效")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, bvid, title, cover, summary, created_at
            FROM favorites
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        
        rows = cursor.fetchall()
        
        favorites = []
        for row in rows:
            favorites.append(FavoriteResponse(
                id=row["id"],
                bvid=row["bvid"],
                title=row["title"],
                cover=row["cover"],
                summary=row["summary"] or "",
                created_at=row["created_at"]
            ))
        
        return {"favorites": favorites}
        
    except Exception as e:
        logger.error(f"获取收藏列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取收藏列表失败")
    finally:
        conn.close()


@router.post("", status_code=201)
async def add_favorite(
    favorite: FavoriteCreate,
    request: Request
) -> Dict[str, Any]:
    """添加收藏"""
    # 验证用户身份
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        user_info = await verify_session_token(token)
        user_id = user_info.get("user_id")
    except HTTPException:
        raise HTTPException(status_code=401, detail="未登录或token无效")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 检查是否已收藏
        cursor.execute("""
            SELECT id FROM favorites
            WHERE user_id = ? AND bvid = ?
        """, (user_id, favorite.bvid))
        
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="该视频已在收藏中")
        
        # 添加收藏
        favorite_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        
        cursor.execute("""
            INSERT INTO favorites (id, user_id, bvid, title, cover, summary, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            favorite_id,
            user_id,
            favorite.bvid,
            favorite.title,
            favorite.cover,
            favorite.summary,
            created_at
        ))
        
        conn.commit()
        
        logger.info(f"用户 {user_id} 添加收藏: {favorite.bvid}")
        
        return {
            "id": favorite_id,
            "message": "收藏成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加收藏失败: {e}")
        conn.rollback()
        raise HTTPException(status_code=500, detail="添加收藏失败")
    finally:
        conn.close()


@router.delete("/{favorite_id}")
async def delete_favorite(
    favorite_id: str,
    request: Request
) -> Dict[str, str]:
    """删除收藏"""
    # 验证用户身份
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        user_info = await verify_session_token(token)
        user_id = user_info.get("user_id")
    except HTTPException:
        raise HTTPException(status_code=401, detail="未登录或token无效")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 验证收藏是否属于该用户
        cursor.execute("""
            SELECT id FROM favorites
            WHERE id = ? AND user_id = ?
        """, (favorite_id, user_id))
        
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="收藏不存在或无权限删除")
        
        # 删除收藏
        cursor.execute("""
            DELETE FROM favorites
            WHERE id = ? AND user_id = ?
        """, (favorite_id, user_id))
        
        conn.commit()
        
        logger.info(f"用户 {user_id} 删除收藏: {favorite_id}")
        
        return {"message": "删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除收藏失败: {e}")
        conn.rollback()
        raise HTTPException(status_code=500, detail="删除收藏失败")
    finally:
        conn.close()
