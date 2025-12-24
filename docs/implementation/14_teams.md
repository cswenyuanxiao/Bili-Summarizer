# 团队协作实施计划

> 优先级: P6 | 预估工作量: 20h | 依赖: 用户系统成熟

---

## 1. 功能概述

创建团队空间，成员可共享总结、添加评论和标签，实现知识协作。

### 用户故事

1. 用户创建团队，邀请成员加入
2. 成员可将个人总结分享到团队
3. 团队成员可查看、评论共享的总结
4. 支持标签分类和搜索

### 核心功能

| 功能 | 描述 |
|------|------|
| 团队创建 | 创建团队，设置名称和头像 |
| 成员管理 | 邀请链接、角色分配（管理员/成员） |
| 总结共享 | 将个人总结分享到团队空间 |
| 评论系统 | 对共享总结添加评论 |
| 标签分类 | 自定义标签，方便归类查找 |

---

## 2. 技术方案

### 2.1 数据模型

```sql
-- 团队表
CREATE TABLE IF NOT EXISTS teams (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    avatar_url TEXT,
    owner_id TEXT NOT NULL,
    invite_code TEXT UNIQUE,          -- 邀请码
    settings TEXT,                     -- JSON 配置
    member_count INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_teams_owner ON teams(owner_id);

-- 团队成员表
CREATE TABLE IF NOT EXISTS team_members (
    id TEXT PRIMARY KEY,
    team_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT DEFAULT 'member',        -- owner / admin / member
    nickname TEXT,                      -- 团队内昵称
    joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, user_id),
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_members_team ON team_members(team_id);
CREATE INDEX IF NOT EXISTS idx_members_user ON team_members(user_id);

-- 团队共享总结表
CREATE TABLE IF NOT EXISTS team_summaries (
    id TEXT PRIMARY KEY,
    team_id TEXT NOT NULL,
    summary_id TEXT,                   -- 原始总结 ID（可选）
    shared_by TEXT NOT NULL,           -- 分享者 user_id
    title TEXT NOT NULL,
    video_url TEXT,
    video_thumbnail TEXT,
    summary_content TEXT NOT NULL,
    transcript TEXT,
    mindmap TEXT,
    tags TEXT,                         -- JSON 数组
    view_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_team_summaries_team ON team_summaries(team_id);

-- 评论表
CREATE TABLE IF NOT EXISTS comments (
    id TEXT PRIMARY KEY,
    team_summary_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    parent_id TEXT,                    -- 父评论 ID（回复）
    content TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_summary_id) REFERENCES team_summaries(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_comments_summary ON comments(team_summary_id);

-- 团队标签表
CREATE TABLE IF NOT EXISTS team_tags (
    id TEXT PRIMARY KEY,
    team_id TEXT NOT NULL,
    name TEXT NOT NULL,
    color TEXT DEFAULT '#6366f1',
    usage_count INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, name),
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
);
```

---

### 2.2 后端实现

#### 新增文件: `web_app/teams.py`

```python
"""
团队协作服务
"""
import uuid
import json
import secrets
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from .db import get_connection

logger = logging.getLogger(__name__)


# ============ 团队 CRUD ============

def create_team(
    owner_id: str,
    name: str,
    description: str = "",
    avatar_url: str = ""
) -> Dict[str, Any]:
    """创建团队"""
    team_id = f"team_{uuid.uuid4().hex[:12]}"
    invite_code = secrets.token_urlsafe(8)
    now = datetime.utcnow().isoformat()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO teams (id, name, description, avatar_url, owner_id, invite_code, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (team_id, name, description, avatar_url, owner_id, invite_code, now, now))
    
    # 自动将创建者添加为成员
    member_id = f"mem_{uuid.uuid4().hex[:12]}"
    cursor.execute("""
        INSERT INTO team_members (id, team_id, user_id, role, joined_at)
        VALUES (?, ?, ?, 'owner', ?)
    """, (member_id, team_id, owner_id, now))
    
    conn.commit()
    conn.close()
    
    return {
        "id": team_id,
        "name": name,
        "description": description,
        "avatar_url": avatar_url,
        "invite_code": invite_code,
        "role": "owner",
        "created_at": now
    }


def get_team(team_id: str) -> Optional[Dict[str, Any]]:
    """获取团队信息"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, description, avatar_url, owner_id, invite_code, 
               member_count, created_at
        FROM teams WHERE id = ?
    """, (team_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return dict(row)


def get_user_teams(user_id: str) -> List[Dict[str, Any]]:
    """获取用户加入的团队列表"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT t.id, t.name, t.description, t.avatar_url, t.member_count, 
               tm.role, tm.joined_at
        FROM teams t
        JOIN team_members tm ON t.id = tm.team_id
        WHERE tm.user_id = ?
        ORDER BY tm.joined_at DESC
    """, (user_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def update_team(
    team_id: str,
    user_id: str,
    **updates
) -> bool:
    """更新团队信息（仅 owner/admin）"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 检查权限
    cursor.execute("""
        SELECT role FROM team_members 
        WHERE team_id = ? AND user_id = ?
    """, (team_id, user_id))
    
    row = cursor.fetchone()
    if not row or row["role"] not in ["owner", "admin"]:
        conn.close()
        return False
    
    # 构建更新
    allowed_fields = ["name", "description", "avatar_url"]
    set_clauses = []
    params = []
    
    for field in allowed_fields:
        if field in updates:
            set_clauses.append(f"{field} = ?")
            params.append(updates[field])
    
    if not set_clauses:
        conn.close()
        return False
    
    set_clauses.append("updated_at = ?")
    params.append(datetime.utcnow().isoformat())
    params.append(team_id)
    
    cursor.execute(
        f"UPDATE teams SET {', '.join(set_clauses)} WHERE id = ?",
        params
    )
    
    conn.commit()
    conn.close()
    return True


def delete_team(team_id: str, user_id: str) -> bool:
    """删除团队（仅 owner）"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM teams 
        WHERE id = ? AND owner_id = ?
    """, (team_id, user_id))
    
    conn.commit()
    affected = cursor.rowcount > 0
    conn.close()
    
    return affected


# ============ 成员管理 ============

def join_team_by_code(user_id: str, invite_code: str) -> Dict[str, Any]:
    """通过邀请码加入团队"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 查找团队
    cursor.execute("SELECT id, name FROM teams WHERE invite_code = ?", (invite_code,))
    team = cursor.fetchone()
    
    if not team:
        conn.close()
        raise ValueError("邀请码无效")
    
    # 检查是否已加入
    cursor.execute("""
        SELECT id FROM team_members 
        WHERE team_id = ? AND user_id = ?
    """, (team["id"], user_id))
    
    if cursor.fetchone():
        conn.close()
        raise ValueError("你已经是该团队成员")
    
    # 加入团队
    member_id = f"mem_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow().isoformat()
    
    cursor.execute("""
        INSERT INTO team_members (id, team_id, user_id, role, joined_at)
        VALUES (?, ?, ?, 'member', ?)
    """, (member_id, team["id"], user_id, now))
    
    # 更新成员计数
    cursor.execute(
        "UPDATE teams SET member_count = member_count + 1 WHERE id = ?",
        (team["id"],)
    )
    
    conn.commit()
    conn.close()
    
    return {
        "team_id": team["id"],
        "team_name": team["name"],
        "role": "member"
    }


def get_team_members(team_id: str) -> List[Dict[str, Any]]:
    """获取团队成员列表"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT tm.id, tm.user_id, tm.role, tm.nickname, tm.joined_at
        FROM team_members tm
        WHERE tm.team_id = ?
        ORDER BY 
            CASE tm.role 
                WHEN 'owner' THEN 1 
                WHEN 'admin' THEN 2 
                ELSE 3 
            END,
            tm.joined_at
    """, (team_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def update_member_role(
    team_id: str,
    operator_id: str,
    target_user_id: str,
    new_role: str
) -> bool:
    """更新成员角色（仅 owner 可操作）"""
    if new_role not in ["admin", "member"]:
        raise ValueError("无效的角色")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 检查操作者权限
    cursor.execute("""
        SELECT role FROM team_members 
        WHERE team_id = ? AND user_id = ?
    """, (team_id, operator_id))
    
    row = cursor.fetchone()
    if not row or row["role"] != "owner":
        conn.close()
        return False
    
    # 不能修改 owner 的角色
    cursor.execute("""
        SELECT role FROM team_members 
        WHERE team_id = ? AND user_id = ?
    """, (team_id, target_user_id))
    
    target = cursor.fetchone()
    if not target or target["role"] == "owner":
        conn.close()
        return False
    
    cursor.execute("""
        UPDATE team_members SET role = ?
        WHERE team_id = ? AND user_id = ?
    """, (new_role, team_id, target_user_id))
    
    conn.commit()
    conn.close()
    return True


def remove_member(team_id: str, operator_id: str, target_user_id: str) -> bool:
    """移除成员"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 自己退出
    if operator_id == target_user_id:
        cursor.execute("""
            DELETE FROM team_members
            WHERE team_id = ? AND user_id = ? AND role != 'owner'
        """, (team_id, target_user_id))
    else:
        # 管理员移除成员
        cursor.execute("""
            SELECT role FROM team_members 
            WHERE team_id = ? AND user_id = ?
        """, (team_id, operator_id))
        
        row = cursor.fetchone()
        if not row or row["role"] not in ["owner", "admin"]:
            conn.close()
            return False
        
        cursor.execute("""
            DELETE FROM team_members
            WHERE team_id = ? AND user_id = ? AND role = 'member'
        """, (team_id, target_user_id))
    
    affected = cursor.rowcount > 0
    
    if affected:
        cursor.execute(
            "UPDATE teams SET member_count = member_count - 1 WHERE id = ?",
            (team_id,)
        )
    
    conn.commit()
    conn.close()
    return affected


# ============ 共享总结 ============

def share_summary_to_team(
    team_id: str,
    user_id: str,
    title: str,
    summary_content: str,
    video_url: str = "",
    video_thumbnail: str = "",
    transcript: str = "",
    mindmap: str = "",
    tags: List[str] = None
) -> Dict[str, Any]:
    """分享总结到团队"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 检查是否是团队成员
    cursor.execute("""
        SELECT id FROM team_members 
        WHERE team_id = ? AND user_id = ?
    """, (team_id, user_id))
    
    if not cursor.fetchone():
        conn.close()
        raise ValueError("你不是该团队成员")
    
    summary_id = f"ts_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow().isoformat()
    
    cursor.execute("""
        INSERT INTO team_summaries 
        (id, team_id, shared_by, title, video_url, video_thumbnail, 
         summary_content, transcript, mindmap, tags, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        summary_id, team_id, user_id, title, video_url, video_thumbnail,
        summary_content, transcript, mindmap, json.dumps(tags or []),
        now, now
    ))
    
    conn.commit()
    conn.close()
    
    return {
        "id": summary_id,
        "team_id": team_id,
        "title": title,
        "created_at": now
    }


def get_team_summaries(
    team_id: str,
    page: int = 1,
    page_size: int = 20,
    tag: str = None
) -> Dict[str, Any]:
    """获取团队共享的总结列表"""
    conn = get_connection()
    cursor = conn.cursor()
    
    offset = (page - 1) * page_size
    
    # 基础查询
    query = """
        SELECT id, title, video_url, video_thumbnail, shared_by, 
               tags, view_count, comment_count, created_at
        FROM team_summaries
        WHERE team_id = ?
    """
    params = [team_id]
    
    # 标签过滤
    if tag:
        query += " AND tags LIKE ?"
        params.append(f'%"{tag}"%')
    
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([page_size, offset])
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # 获取总数
    cursor.execute(
        "SELECT COUNT(*) FROM team_summaries WHERE team_id = ?",
        (team_id,)
    )
    total = cursor.fetchone()[0]
    
    conn.close()
    
    summaries = []
    for row in rows:
        r = dict(row)
        r["tags"] = json.loads(r["tags"]) if r["tags"] else []
        summaries.append(r)
    
    return {
        "summaries": summaries,
        "total": total,
        "page": page,
        "page_size": page_size
    }


def get_team_summary_detail(summary_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """获取团队总结详情"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT ts.*, t.name as team_name
        FROM team_summaries ts
        JOIN teams t ON ts.team_id = t.id
        JOIN team_members tm ON t.id = tm.team_id AND tm.user_id = ?
        WHERE ts.id = ?
    """, (user_id, summary_id))
    
    row = cursor.fetchone()
    
    if row:
        # 增加浏览量
        cursor.execute(
            "UPDATE team_summaries SET view_count = view_count + 1 WHERE id = ?",
            (summary_id,)
        )
        conn.commit()
    
    conn.close()
    
    if not row:
        return None
    
    result = dict(row)
    result["tags"] = json.loads(result["tags"]) if result["tags"] else []
    return result


# ============ 评论系统 ============

def add_comment(
    summary_id: str,
    user_id: str,
    content: str,
    parent_id: str = None
) -> Dict[str, Any]:
    """添加评论"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 检查权限（是否是团队成员）
    cursor.execute("""
        SELECT ts.team_id FROM team_summaries ts
        JOIN team_members tm ON ts.team_id = tm.team_id AND tm.user_id = ?
        WHERE ts.id = ?
    """, (user_id, summary_id))
    
    if not cursor.fetchone():
        conn.close()
        raise ValueError("无权评论")
    
    comment_id = f"cmt_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow().isoformat()
    
    cursor.execute("""
        INSERT INTO comments (id, team_summary_id, user_id, parent_id, content, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (comment_id, summary_id, user_id, parent_id, content, now))
    
    # 更新评论计数
    cursor.execute(
        "UPDATE team_summaries SET comment_count = comment_count + 1 WHERE id = ?",
        (summary_id,)
    )
    
    conn.commit()
    conn.close()
    
    return {
        "id": comment_id,
        "content": content,
        "created_at": now
    }


def get_comments(summary_id: str) -> List[Dict[str, Any]]:
    """获取总结的评论列表"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, user_id, parent_id, content, created_at
        FROM comments
        WHERE team_summary_id = ?
        ORDER BY created_at ASC
    """, (summary_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def delete_comment(comment_id: str, user_id: str) -> bool:
    """删除评论（仅评论者或管理员）"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 仅删除自己的评论
    cursor.execute("""
        DELETE FROM comments
        WHERE id = ? AND user_id = ?
    """, (comment_id, user_id))
    
    conn.commit()
    affected = cursor.rowcount > 0
    conn.close()
    
    return affected
```

#### 修改文件: `web_app/main.py`

添加团队协作 API 端点（核心端点）：

```python
# === 团队协作相关 ===
from .teams import (
    create_team, get_team, get_user_teams, update_team, delete_team,
    join_team_by_code, get_team_members, update_member_role, remove_member,
    share_summary_to_team, get_team_summaries, get_team_summary_detail,
    add_comment, get_comments, delete_comment
)

class CreateTeamRequest(BaseModel):
    name: str
    description: str = ""

class ShareToTeamRequest(BaseModel):
    team_id: str
    title: str
    summary_content: str
    video_url: str = ""
    video_thumbnail: str = ""
    transcript: str = ""
    mindmap: str = ""
    tags: List[str] = []

class CommentRequest(BaseModel):
    content: str
    parent_id: Optional[str] = None

# 团队 CRUD
@app.post("/api/teams")
async def api_create_team(request: Request, body: CreateTeamRequest):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    team = create_team(user["user_id"], body.name, body.description)
    return team

@app.get("/api/teams")
async def api_list_teams(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    teams = get_user_teams(user["user_id"])
    return {"teams": teams}

@app.get("/api/teams/{team_id}")
async def api_get_team(team_id: str, request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    team = get_team(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return team

@app.post("/api/teams/join")
async def api_join_team(request: Request, invite_code: str):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    try:
        result = join_team_by_code(user["user_id"], invite_code)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/teams/{team_id}/members")
async def api_get_members(team_id: str, request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    members = get_team_members(team_id)
    return {"members": members}

# 团队总结
@app.post("/api/teams/share")
async def api_share_to_team(request: Request, body: ShareToTeamRequest):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    try:
        result = share_summary_to_team(
            team_id=body.team_id,
            user_id=user["user_id"],
            title=body.title,
            summary_content=body.summary_content,
            video_url=body.video_url,
            video_thumbnail=body.video_thumbnail,
            transcript=body.transcript,
            mindmap=body.mindmap,
            tags=body.tags
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.get("/api/teams/{team_id}/summaries")
async def api_get_team_summaries(
    team_id: str,
    request: Request,
    page: int = 1,
    tag: str = None
):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    result = get_team_summaries(team_id, page, tag=tag)
    return result

@app.get("/api/team-summaries/{summary_id}")
async def api_get_team_summary(summary_id: str, request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    detail = get_team_summary_detail(summary_id, user["user_id"])
    if not detail:
        raise HTTPException(status_code=404, detail="Summary not found")
    
    return detail

# 评论
@app.post("/api/team-summaries/{summary_id}/comments")
async def api_add_comment(summary_id: str, request: Request, body: CommentRequest):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    try:
        comment = add_comment(summary_id, user["user_id"], body.content, body.parent_id)
        return comment
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.get("/api/team-summaries/{summary_id}/comments")
async def api_get_comments(summary_id: str, request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    await verify_session_token(token)
    
    comments = get_comments(summary_id)
    return {"comments": comments}
```

---

### 2.3 前端实现

#### 新增页面

1. `frontend/src/pages/TeamsPage.vue` - 团队列表
2. `frontend/src/pages/TeamDetailPage.vue` - 团队详情
3. `frontend/src/pages/TeamSummaryPage.vue` - 团队总结详情

#### 新增组件

1. `CreateTeamModal.vue` - 创建团队弹窗
2. `ShareToTeamModal.vue` - 分享到团队弹窗
3. `CommentList.vue` - 评论列表
4. `InviteMemberModal.vue` - 邀请成员弹窗

---

## 3. 实施步骤清单

| 序号 | 任务 | 预估时间 |
|------|------|----------|
| 1 | 数据库表创建 | 1h |
| 2 | teams.py 基础 CRUD | 3h |
| 3 | 成员管理逻辑 | 2h |
| 4 | 共享总结逻辑 | 2h |
| 5 | 评论系统 | 1.5h |
| 6 | API 端点 | 2h |
| 7 | 前端 TeamsPage | 2h |
| 8 | 前端 TeamDetailPage | 2h |
| 9 | 前端组件 | 3h |
| 10 | 测试 | 1.5h |

---

## 4. 验收标准

- [ ] 可创建团队并生成邀请链接
- [ ] 邀请码可正常加入团队
- [ ] 成员角色管理正常
- [ ] 可将总结分享到团队
- [ ] 团队总结列表正确展示
- [ ] 评论功能正常（发布/删除）
- [ ] 权限控制正确（非成员无法访问）

---

## 5. 注意事项

1. **权限隔离**: 非团队成员不能访问团队内容
2. **数据清理**: 删除团队时级联删除成员和总结
3. **性能优化**: 大团队需要分页加载成员
4. **通知集成**: 可与推送系统集成，新评论时通知
