"""
Startup module - 处理应用启动时的初始化逻辑
所有初始化都是异步的，不阻塞 Worker 启动
"""
import asyncio
import logging
from typing import Callable

logger = logging.getLogger(__name__)


async def init_with_retry(name: str, init_fn: Callable, max_attempts: int = 5):
    """带重试的初始化函数，失败不会阻止服务启动"""
    for attempt in range(1, max_attempts + 1):
        try:
            init_fn()
            logger.info(f"{name} initialized successfully")
            return True
        except Exception as exc:
            logger.warning(f"{name} init failed (attempt {attempt}/{max_attempts}): {exc}")
            await asyncio.sleep(min(2 ** (attempt - 1), 10))
    
    logger.error(f"{name} init failed after {max_attempts} retries; service may be degraded")
    return False


async def init_all_databases():
    """初始化所有数据库，使用后台任务不阻塞启动"""
    from ..cache import init_cache_db
    from ..credits import init_credits_db
    from ..telemetry import init_telemetry_db
    
    # 并行初始化各数据库
    results = await asyncio.gather(
        init_with_retry("Cache DB", init_cache_db),
        init_with_retry("Credits DB", init_credits_db),
        init_with_retry("Telemetry DB", init_telemetry_db),
        return_exceptions=True
    )
    
    success_count = sum(1 for r in results if r is True)
    logger.info(f"Database initialization: {success_count}/{len(results)} succeeded")


async def init_core_tables():
    """初始化核心业务表"""
    from ..db import get_connection
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # API Keys 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                prefix TEXT NOT NULL,
                key_hash TEXT NOT NULL UNIQUE,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_used_at TEXT
            )
        """)
        
        # API Key 使用统计
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_key_usage_daily (
                key_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                date TEXT NOT NULL,
                count INTEGER DEFAULT 0,
                PRIMARY KEY (key_id, date)
            )
        """)
        
        # 使用配额表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_daily (
                user_id TEXT NOT NULL,
                date TEXT NOT NULL,
                count INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, date)
            )
        """)
        
        # 订阅状态表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                user_id TEXT PRIMARY KEY,
                plan TEXT NOT NULL DEFAULT 'free',
                status TEXT NOT NULL DEFAULT 'inactive',
                current_period_end TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Core tables initialized")
    except Exception as e:
        logger.error(f"Failed to initialize core tables: {e}")


async def startup_background_tasks():
    """启动后台任务（在 DB 初始化完成后）"""
    from ..scheduler import start_scheduler
    
    try:
        start_scheduler()
        logger.info("Background scheduler started")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
