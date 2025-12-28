"""
团队协作服务
"""
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from .db import get_connection

logger = logging.getLogger(__name__)

# --- 团队管理 ---

def create_team(name: str, owner_id: str, description: str = "") -> Dict[str, Any]:
    """创建新团队"""
    conn = get_connection()
    cursor = conn.cursor()
    team_id = str(uuid.uuid4())
    
    try:
        # 1. 创建团队
        cursor.execute("""
            INSERT INTO teams (id, name, description, owner_id, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (team_id, name, description, owner_id, datetime.utcnow().isoformat()))
        
        # 2. 将创建者设为管理员成员
        cursor.execute("""
            INSERT INTO team_members (id, team_id, user_id, role, joined_at)
            VALUES (?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), team_id, owner_id, 'admin', datetime.utcnow().isoformat()))
        
        conn.commit()
        return {"id": team_id, "name": name, "owner_id": owner_id}
    except Exception as e:
        conn.rollback()
        logger.error(f"Create team failed: {e}")
        raise
    finally:
        conn.close()

def get_user_teams(user_id: str) -> List[Dict[str, Any]]:
    """获取用户参与的所有团队"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT t.*, tm.role, tm.joined_at
        FROM teams t
        JOIN team_members tm ON t.id = tm.team_id
        WHERE tm.user_id = ?
        ORDER BY t.created_at DESC
    """, (user_id,))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_team_details(team_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """获取团队详情（成员和总结）"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. 检查权限
    cursor.execute("SELECT role FROM team_members WHERE team_id = ? AND user_id = ?", (team_id, user_id))
    member_row = cursor.fetchone()
    if not member_row:
        conn.close()
        return None
    
    # 2. 团队基本信息
    cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
    team_row = cursor.fetchone()
    if not team_row:
        conn.close()
        return None
    team = dict(team_row)
    
    # 3. 成员列表
    cursor.execute("""
        SELECT user_id, role, joined_at
        FROM team_members
        WHERE team_id = ?
    """, (team_id,))
    team['members'] = [dict(r) for r in cursor.fetchall()]
    
    # 4. 共享总结列表 - 直接从 team_summaries 读取
    cursor.execute("""
        SELECT id, title, video_url, video_thumbnail, summary_content as summary, 
               shared_by, tags, view_count, created_at as shared_at
        FROM team_summaries
        WHERE team_id = ?
        ORDER BY created_at DESC
    """, (team_id,))
    summaries = [dict(r) for r in cursor.fetchall()]
    
    # 5. 为每个总结添加评论计数
    for summary in summaries:
        cursor.execute("""
            SELECT COUNT(*) as count FROM comments
            WHERE team_summary_id = ?
        """, (summary['id'],))
        count_row = cursor.fetchone()
        summary['comment_count'] = count_row['count'] if count_row else 0
    
    team['summaries'] = summaries
    
    conn.close()
    return team


# --- 成员管理 ---

def invite_to_team(team_id: str, inviter_id: str, invitee_email: str) -> Dict[str, Any]:
    """邀请成员（简化版：直接添加，实际应发邀请函）"""
    # 这里的简化逻辑假设系统能根据 email 找到 user_id
    # 在真实 Supabase 环境中，通常通过邀请链接/邮件处理
    return {"message": "邀请已发送（模拟）"}

def add_member_to_team(team_id: str, user_id: str, role: str = 'member') -> bool:
    """直接添加成员"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO team_members (id, team_id, user_id, role, joined_at)
            VALUES (?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), team_id, user_id, role, datetime.utcnow().isoformat()))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Add member failed: {e}")
        return False
    finally:
        conn.close()

# --- 内容共享 ---

def share_summary_to_team(
    team_id: str, 
    user_id: str, 
    title: str,
    video_url: str,
    summary_content: str,
    video_thumbnail: str = "",
    transcript: str = "",
    mindmap: str = "",
    tags: str = ""
) -> bool:
    """将总结分享到团队"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. 检查用户是否在团队中
    cursor.execute("SELECT 1 FROM team_members WHERE team_id = ? AND user_id = ?", (team_id, user_id))
    if not cursor.fetchone():
        conn.close()
        return False
    
    try:
        cursor.execute("""
            INSERT INTO team_summaries 
            (id, team_id, shared_by, title, video_url, video_thumbnail, summary_content, transcript, mindmap, tags, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()), team_id, user_id, title, video_url, 
            video_thumbnail, summary_content, transcript, mindmap, tags, 
            datetime.utcnow().isoformat()
        ))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Share summary failed: {e}")
        return False
    finally:
        conn.close()


# --- 评论系统 ---

def add_comment(team_summary_id: str, user_id: str, content: str, parent_id: str = None) -> Dict[str, Any]:
    """发表评论"""
    conn = get_connection()
    cursor = conn.cursor()
    comment_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    try:
        cursor.execute("""
            INSERT INTO comments (id, team_summary_id, user_id, content, parent_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (comment_id, team_summary_id, user_id, content, parent_id, now))
        conn.commit()
        return {"id": comment_id, "content": content, "created_at": now}
    except Exception as e:
        logger.error(f"Add comment failed: {e}")
        raise
    finally:
        conn.close()

def get_summary_comments(team_summary_id: str) -> List[Dict[str, Any]]:
    """获取某条共享总结的评论"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM comments
        WHERE team_summary_id = ?
        ORDER BY created_at ASC
    """, (team_summary_id,))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

