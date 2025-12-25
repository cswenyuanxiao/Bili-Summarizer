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
        
        # UP 主订阅表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS up_subscriptions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                up_mid TEXT NOT NULL,
                up_name TEXT,
                up_avatar TEXT,
                notify_methods TEXT,
                last_checked_at TEXT,
                last_video_bvid TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, up_mid)
            )
        """)
        
        # 总结模板表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS summary_templates (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                prompt_template TEXT NOT NULL,
                output_format TEXT DEFAULT 'markdown',
                sections TEXT,
                is_preset BOOLEAN DEFAULT FALSE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 幂等性主键表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS idempotency_keys (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                action TEXT,
                status TEXT,
                result TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 通知队列表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notification_queue (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                type TEXT NOT NULL,
                title TEXT,
                body TEXT,
                payload TEXT,
                status TEXT DEFAULT 'pending',
                method TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                sent_at TEXT
            )
        """)
        
        
        # 账单记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS billing_events (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                amount_cents INTEGER NOT NULL DEFAULT 0,
                currency TEXT NOT NULL DEFAULT 'CNY',
                status TEXT NOT NULL DEFAULT 'pending',
                period_start TEXT,
                period_end TEXT,
                invoice_url TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 支付订单表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payment_orders (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                provider TEXT NOT NULL,
                plan TEXT NOT NULL,
                amount_cents INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                billing_id TEXT NOT NULL,
                transaction_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 邀请码表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invite_codes (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                code TEXT NOT NULL UNIQUE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 邀请兑换表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invite_redemptions (
                id TEXT PRIMARY KEY,
                invite_id TEXT NOT NULL,
                inviter_id TEXT NOT NULL,
                invitee_id TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(invitee_id)
            )
        """)
        
        # 分享链接表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS share_links (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT,
                summary TEXT NOT NULL,
                transcript TEXT,
                mindmap TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT
            )
        """)
        
        # 反馈表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedbacks (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                feedback_type TEXT NOT NULL,
                content TEXT NOT NULL,
                contact TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 浏览器推送订阅表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS push_subscriptions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                p256dh TEXT NOT NULL,
                auth TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, endpoint)
            )
        """)
        
        
        # 创建索引以优化查询性能
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_user ON api_keys(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_usage_daily_user ON usage_daily(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_billing_user ON billing_events(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_key_usage_user ON api_key_usage_daily(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_payment_user ON payment_orders(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_invite_user ON invite_codes(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_share_user ON share_links(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_user ON feedbacks(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_status ON feedbacks(status)")
        
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
