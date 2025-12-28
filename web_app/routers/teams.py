"""
团队协作路由
提供团队创建、列表、详情查询功能
"""
import uuid
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import logging

from ..db import get_connection
from ..auth import verify_session_token

router = APIRouter(prefix="/api/teams", tags=["teams"])
logger = logging.getLogger(__name__)


class TeamCreate(BaseModel):
    """创建团队请求"""
    name: str
    description: str = ""


class TeamResponse(BaseModel):
    """团队列表响应"""
    id: str
    name: str
    description: str
    role: str
    owner_id: str
    created_at: str


@router.get("")
async def get_teams(request: Request) -> Dict[str, List[TeamResponse]]:
    """获取用户所属的所有团队"""
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
        # 查询用户参与的所有团队
        cursor.execute("""
            SELECT 
                t.id, t.name, t.description, t.owner_id, t.created_at,
                tm.role
            FROM teams t
            LEFT JOIN team_members tm ON t.id = tm.team_id
            WHERE t.owner_id = ? OR tm.user_id = ?
            ORDER BY t.created_at DESC
        """, (user_id, user_id))
        
        rows = cursor.fetchall()
        
        teams = []
        for row in rows:
            teams.append(TeamResponse(
                id=row["id"],
                name=row["name"],
                description=row["description"] or "",
                role=row["role"] if row["role"] else "admin",  # owner默认是admin
                owner_id=row["owner_id"],
                created_at=row["created_at"]
            ))
        
        return {"teams": teams}
        
    except Exception as e:
        logger.error(f"获取团队列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取团队列表失败")
    finally:
        conn.close()


@router.post("", status_code=201)
async def create_team(
    team: TeamCreate,
    request: Request
) -> TeamResponse:
    """创建新团队"""
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
        team_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        
        # 创建团队
        cursor.execute("""
            INSERT INTO teams (id, name, description, owner_id, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (team_id, team.name, team.description, user_id, created_at))
        
        # 将创建者添加为团队成员
        member_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO team_members (id, team_id, user_id, role, joined_at)
            VALUES (?, ?, ?, ?, ?)
        """, (member_id, team_id, user_id, "admin", created_at))
        
        conn.commit()
        
        logger.info(f"用户 {user_id} 创建团队: {team.name}")
        
        return TeamResponse(
            id=team_id,
            name=team.name,
            description=team.description,
            role="admin",
            owner_id=user_id,
            created_at=created_at
        )
        
    except Exception as e:
        logger.error(f"创建团队失败: {e}")
        conn.rollback()
        raise HTTPException(status_code=500, detail="创建团队失败")
    finally:
        conn.close()


@router.get("/{team_id}")
async def get_team_detail(
    team_id: str,
    request: Request
) -> Dict[str, Any]:
    """获取团队详情（包括成员和共享内容）"""
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
        # 验证用户是否是团队成员
        cursor.execute("""
            SELECT id FROM team_members
            WHERE team_id = ? AND user_id = ?
        """, (team_id, user_id))
        
        if not cursor.fetchone():
            # 检查是否是owner
            cursor.execute("""
                SELECT id FROM teams
                WHERE id = ? AND owner_id = ?
            """, (team_id, user_id))
            
            if not cursor.fetchone():
                raise HTTPException(status_code=403, detail="无权访问该团队")
        
        # 获取团队基本信息
        cursor.execute("""
            SELECT id, name, description, owner_id, created_at
            FROM teams
            WHERE id = ?
        """, (team_id,))
        
        team_row = cursor.fetchone()
        if not team_row:
            raise HTTPException(status_code=404, detail="团队不存在")
        
        # 获取成员列表
        cursor.execute("""
            SELECT user_id, role, joined_at
            FROM team_members
            WHERE team_id = ?
            ORDER BY joined_at ASC
        """, (team_id,))
        
        members = []
        for row in cursor.fetchall():
            members.append({
                "user_id": row["user_id"],
                "role": row["role"],
                "joined_at": row["joined_at"]
            })
        
        # 获取共享的总结列表（简化版：暂时返回空列表）
        # TODO: 实现从 summaries 表关联查询
        summaries = []
        
        # 确定当前用户角色
        user_role = "admin" if team_row["owner_id"] == user_id else "member"
        
        return {
            "id": team_row["id"],
            "name": team_row["name"],
            "description": team_row["description"] or "",
            "role": user_role,
            "owner_id": team_row["owner_id"],
            "created_at": team_row["created_at"],
            "members": members,
            "summaries": summaries
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取团队详情失败: {e}")
        raise HTTPException(status_code=500, detail="获取团队详情失败")
    finally:
        conn.close()
