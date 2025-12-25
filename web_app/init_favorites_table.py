"""
收藏夹数据表初始化脚本
在应用启动时自动创建 favorites 表
"""
import logging
from .db import get_connection, using_postgres

logger = logging.getLogger(__name__)


def init_favorites_table():
    """初始化收藏夹表"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        if using_postgres():
            # PostgreSQL schema
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS favorites (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id TEXT NOT NULL,
                    bvid TEXT NOT NULL,
                    title TEXT,
                    cover TEXT,
                    summary TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(user_id, bvid)
                )
            """)
            
            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_favorites_user_id 
                ON favorites(user_id)
            """)
            
        else:
            # SQLite schema
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS favorites (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    bvid TEXT NOT NULL,
                    title TEXT,
                    cover TEXT,
                    summary TEXT,
                    created_at TEXT NOT NULL,
                    UNIQUE(user_id, bvid)
                )
            """)
            
            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_favorites_user_id 
                ON favorites(user_id)
            """)
        
        conn.commit()
        logger.info("✅ Favorites table initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize favorites table: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()
