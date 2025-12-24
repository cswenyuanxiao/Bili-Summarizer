"""
缓存模块 - 使用 SQLite 存储视频总结结果
避免重复分析相同视频，节省 API 费用
"""

import hashlib
import json
from datetime import datetime
from typing import Optional, Dict, Any

from .db import get_connection, using_postgres


def init_cache_db():
    """初始化缓存数据库"""
    conn = get_connection()
    cursor = conn.cursor()
    if using_postgres():
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS video_cache (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                video_id TEXT NOT NULL,
                url TEXT NOT NULL,
                mode TEXT NOT NULL,
                focus TEXT NOT NULL,
                cache_key TEXT UNIQUE NOT NULL,
                summary TEXT,
                transcript TEXT,
                mindmap TEXT,
                usage_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS video_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                url TEXT NOT NULL,
                mode TEXT NOT NULL,
                focus TEXT NOT NULL,
                cache_key TEXT UNIQUE NOT NULL,
                summary TEXT,
                transcript TEXT,
                mindmap TEXT,
                usage_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_key ON video_cache(cache_key)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_video_id ON video_cache(video_id)")
    
    conn.commit()
    conn.close()


def generate_cache_key(url: str, mode: str, focus: str) -> str:
    """生成缓存键"""
    # 提取视频 ID（BV号）
    import re
    bv_match = re.search(r'BV[a-zA-Z0-9]+', url)
    video_id = bv_match.group(0) if bv_match else url
    
    # 组合生成唯一键
    key_string = f"{video_id}:{mode}:{focus}"
    return hashlib.md5(key_string.encode()).hexdigest()


def get_cached_result(url: str, mode: str, focus: str) -> Optional[Dict[str, Any]]:
    """
    获取缓存的总结结果
    
    Returns:
        如果有缓存返回 dict，否则返回 None
    """
    cache_key = generate_cache_key(url, mode, focus)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT summary, transcript, usage_data, created_at 
        FROM video_cache 
        WHERE cache_key = ?
    """, (cache_key,))
    
    row = cursor.fetchone()
    
    if row:
        # 更新最后访问时间
        cursor.execute("""
            UPDATE video_cache 
            SET last_accessed = CURRENT_TIMESTAMP 
            WHERE cache_key = ?
        """, (cache_key,))
        conn.commit()
        conn.close()
        
        return {
            "summary": row["summary"],
            "transcript": row["transcript"],
            "usage": json.loads(row["usage_data"]) if row["usage_data"] else {},
            "cached": True,
            "cached_at": row["created_at"]
        }
    
    conn.close()
    return None


def save_to_cache(url: str, mode: str, focus: str, summary: str, transcript: str, usage: Dict) -> bool:
    """
    保存总结结果到缓存
    """
    import re
    bv_match = re.search(r'BV[a-zA-Z0-9]+', url)
    video_id = bv_match.group(0) if bv_match else "unknown"
    cache_key = generate_cache_key(url, mode, focus)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        if using_postgres():
            cursor.execute("""
                INSERT INTO video_cache 
                (video_id, url, mode, focus, cache_key, summary, transcript, usage_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (cache_key)
                DO UPDATE SET
                    summary = EXCLUDED.summary,
                    transcript = EXCLUDED.transcript,
                    usage_data = EXCLUDED.usage_data,
                    last_accessed = CURRENT_TIMESTAMP
            """, (
                video_id,
                url,
                mode,
                focus,
                cache_key,
                summary,
                transcript,
                json.dumps(usage)
            ))
        else:
            cursor.execute("""
                INSERT OR REPLACE INTO video_cache 
                (video_id, url, mode, focus, cache_key, summary, transcript, usage_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                video_id,
                url,
                mode,
                focus,
                cache_key,
                summary,
                transcript,
                json.dumps(usage)
            ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"缓存保存失败: {e}")
        conn.close()
        return False


def clear_old_cache(days: int = 30):
    """清理超过指定天数的缓存"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if using_postgres():
        cursor.execute("""
            DELETE FROM video_cache 
            WHERE last_accessed < NOW() - (%s)::interval
        """, (f"{days} days",))
    else:
        cursor.execute("""
            DELETE FROM video_cache 
            WHERE last_accessed < datetime('now', ?)
        """, (f'-{days} days',))
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    return deleted


def get_cache_stats() -> Dict[str, Any]:
    """获取缓存统计信息"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM video_cache")
    count = cursor.fetchone()["count"]
    
    cursor.execute("SELECT SUM(LENGTH(summary) + LENGTH(transcript)) as size FROM video_cache")
    size = cursor.fetchone()["size"] or 0
    
    conn.close()
    
    return {
        "total_entries": count,
        "total_size_kb": round(size / 1024, 2)
    }

