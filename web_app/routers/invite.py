"""
Invite Router - 邀请码管理相关端点
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import uuid
import secrets

from ..dependencies import get_current_user
from ..db import get_connection
from ..credits import grant_credits

router = APIRouter(prefix="/api/invites", tags=["Invites"])


class RedeemInviteRequest(BaseModel):
    code: str


@router.get("")
async def get_invite_info(user: dict = Depends(get_current_user)):
    """获取用户的邀请码信息"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, code, created_at
            FROM invite_codes
            WHERE user_id = ?
        """, (user["user_id"],))
        row = cursor.fetchone()
        
        cursor.execute("""
            SELECT COUNT(*)
            FROM invite_redemptions
            WHERE inviter_id = ?
        """, (user["user_id"],))
        total = cursor.fetchone()[0]
        
        if row:
            return {
                "code": row[1],
                "created_at": row[2],
                "total_redemptions": total or 0
            }
        else:
            return {
                "code": None,
                "created_at": None,
                "total_redemptions": 0
            }
    finally:
        conn.close()


@router.post("")
async def create_invite_code(user: dict = Depends(get_current_user)):
    """创建邀请码"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id FROM invite_codes WHERE user_id = ?
        """, (user["user_id"],))
        existing = cursor.fetchone()
        
        if existing:
            raise HTTPException(400, "User already has an invite code")
        
        invite_id = str(uuid.uuid4())
        code = secrets.token_urlsafe(8)
        
        cursor.execute("""
            INSERT INTO invite_codes (id, user_id, code)
            VALUES (?, ?, ?)
        """, (invite_id, user["user_id"], code))
        
        conn.commit()
        return {"code": code}
    finally:
        conn.close()


@router.post("/redeem")
async def redeem_invite(request: RedeemInviteRequest, user: dict = Depends(get_current_user)):
    """兑换邀请码"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, user_id
            FROM invite_codes
            WHERE code = ?
        """, (request.code,))
        invite = cursor.fetchone()
        
        if not invite:
            raise HTTPException(404, "Invalid invite code")
        
        invite_id, inviter_id = invite[0], invite[1]
        
        if inviter_id == user["user_id"]:
            raise HTTPException(400, "Cannot redeem your own invite code")
        
        cursor.execute("""
            SELECT id FROM invite_redemptions WHERE invitee_id = ?
        """, (user["user_id"],))
        if cursor.fetchone():
            raise HTTPException(400, "You have already redeemed an invite code")
        
        redemption_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO invite_redemptions (id, invite_id, inviter_id, invitee_id)
            VALUES (?, ?, ?, ?)
        """, (redemption_id, invite_id, inviter_id, user["user_id"]))
        
        conn.commit()
        
        # 奖励积分
        grant_credits(inviter_id, 50, "邀请新用户")
        grant_credits(user["user_id"], 50, "使用邀请码")
        
        return {
            "message": "邀请码兑换成功！双方各获得 50 积分",
            "credits_earned": 50
        }
    finally:
        conn.close()
