"""
Share Router - 分享卡片生成相关端点
"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
import logging

from ..auth import verify_session_token
from ..share_card import generate_share_card, get_card_image

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/share", tags=["Share"])


class ShareCardRequest(BaseModel):
    title: str
    summary: str
    thumbnail_url: Optional[str] = None
    template: str = "default"


@router.post("/card")
async def create_share_card(request: Request, body: ShareCardRequest):
    """生成分享卡片"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    # 尝试验证用户，但如果不成功也允许（支持匿名分享）
    try:
        user = await verify_session_token(token)
    except:
        user = None
    
    # 验证模板
    if body.template not in ["default", "dark", "gradient", "minimal"]:
        raise HTTPException(status_code=400, detail="Invalid template")
    
    try:
        # 在线程池中运行耗时的渲染操作
        result = await asyncio.to_thread(
            generate_share_card,
            title=body.title,
            summary=body.summary,
            thumbnail_url=body.thumbnail_url,
            template=body.template
        )
        
        return {
            "card_id": result["card_id"],
            "image_url": result["image_url"],
            "expires_at": result["expires_at"]
        }
    except Exception as e:
        logger.error(f"Failed to generate share card: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/card/{card_id}.png")
async def get_share_card_image(card_id: str):
    """获取生成的分享卡片图片"""
    image_path = get_card_image(card_id)
    
    if not image_path:
        raise HTTPException(status_code=404, detail="Card not found or expired")
    
    return FileResponse(
        image_path,
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=86400",
            "Content-Disposition": f"inline; filename={card_id}.png"
        }
    )
