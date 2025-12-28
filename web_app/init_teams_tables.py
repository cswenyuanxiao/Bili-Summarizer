"""
团队协作数据表初始化脚本
在应用启动时自动创建 teams 相关表
"""
import logging
from .db import get_connection, using_postgres

logger = logging.getLogger(__name__)


def init_teams_tables():
    """初始化团队协作相关表"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        if using_postgres():
            # PostgreSQL schema
            # 1. teams 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teams (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name TEXT NOT NULL,
                    description TEXT,
                    owner_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # 2. team_members 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS team_members (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    team_id UUID NOT NULL,
                    user_id TEXT NOT NULL,
                    role TEXT DEFAULT 'member',
                    joined_at TIMESTAMP DEFAULT NOW(),
                    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
                    UNIQUE(team_id, user_id)
                )
            """)
            
            # 3. team_shares 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS team_shares (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    team_id UUID NOT NULL,
                    summary_id TEXT NOT NULL,
                    shared_by TEXT NOT NULL,
                    shared_at TIMESTAMP DEFAULT NOW(),
                    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
                )
            """)
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_teams_owner ON teams(owner_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_team_members_user ON team_members(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_team_members_team ON team_members(team_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_team_shares_team ON team_shares(team_id)")
            
        else:
            # SQLite schema
            # 1. teams 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teams (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    owner_id TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            # 2. team_members 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS team_members (
                    id TEXT PRIMARY KEY,
                    team_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    role TEXT DEFAULT 'member',
                    joined_at TEXT NOT NULL,
                    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
                    UNIQUE(team_id, user_id)
                )
            """)
            
            # 3. team_shares 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS team_shares (
                    id TEXT PRIMARY KEY,
                    team_id TEXT NOT NULL,
                    summary_id TEXT NOT NULL,
                    shared_by TEXT NOT NULL,
                    shared_at TEXT NOT NULL,
                    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
                )
            """)
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_teams_owner ON teams(owner_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_team_members_user ON team_members(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_team_members_team ON team_members(team_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_team_shares_team ON team_shares(team_id)")
        
        conn.commit()
        logger.info("✅ Teams tables initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize teams tables: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()
