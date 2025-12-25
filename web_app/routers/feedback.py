"""
Feedback Router - 用户反馈相关端点
"""
from fastapi import APIRouter, HTTPException, Request
from typing import Optional
import uuid
import logging

from ..auth import verify_session_token
from ..schemas import FeedbackRequest
from ..db import get_connection

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])


@router.post("")
async def submit_feedback(
    request: FeedbackRequest,
    req: Request
):
    """提交用户反馈，支持匿名或登录用户"""
    # 尝试获取用户信息（可选）
    user = None
    auth_header = req.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            user = await verify_session_token(auth_header[7:])
        except:
            pass  # 忽略认证失败，允许匿名反馈
    
    # 验证类型
    if request.feedback_type not in ["bug", "feature", "other"]:
        raise HTTPException(400, "Invalid feedback type")
    
    # 验证内容长度
    if not request.content or len(request.content.strip()) == 0:
        raise HTTPException(400, "Content cannot be empty")
    
    if len(request.content) > 500:
        raise HTTPException(400, "Content too long (max 500 characters)")
    
    # 验证邮箱格式（如果提供）
    if request.contact:
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, request.contact):
            raise HTTPException(400, "Invalid email format")
    
    # 存储反馈
    feedback_id = str(uuid.uuid4())
    user_id = user["user_id"] if user else None
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO feedbacks (id, user_id, feedback_type, content, contact, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        """, (feedback_id, user_id, request.feedback_type, request.content, request.contact))
        conn.commit()
        
        logger.info(f"Feedback submitted: {feedback_id} (type={request.feedback_type}, user={user_id or 'anonymous'})")
        
        return {
            "message": "感谢您的反馈！我们会尽快处理",
            "feedback_id": feedback_id
        }
    finally:
        conn.close()
