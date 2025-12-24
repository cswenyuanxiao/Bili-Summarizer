from web_app.db import get_connection

def init_v2_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. 总结模板表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS summary_templates (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            prompt_template TEXT NOT NULL,
            output_format TEXT DEFAULT 'markdown',
            sections TEXT, -- JSON list
            is_preset BOOLEAN DEFAULT FALSE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. 幂等性主键表 (v1.2 遗漏或需确认)
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

    # 3. UP 主订阅表 (P4)
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

    # 4. 通知队列表 (P4)
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

    # 5. 浏览器推送订阅表 (P4)
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

    # 6. 团队协作相关表 (P6)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            avatar_url TEXT,
            owner_id TEXT NOT NULL,
            invite_code TEXT UNIQUE,
            settings TEXT,
            member_count INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS team_members (
            id TEXT PRIMARY KEY,
            team_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            role TEXT DEFAULT 'member',
            nickname TEXT,
            joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(team_id, user_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS team_summaries (
            id TEXT PRIMARY KEY,
            team_id TEXT NOT NULL,
            shared_by TEXT NOT NULL,
            title TEXT NOT NULL,
            video_url TEXT,
            video_thumbnail TEXT,
            summary_content TEXT NOT NULL,
            transcript TEXT,
            mindmap TEXT,
            tags TEXT,
            view_count INTEGER DEFAULT 0,
            comment_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id TEXT PRIMARY KEY,
            team_summary_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            parent_id TEXT,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("V2 Tables initialized successfully.")

if __name__ == "__main__":
    init_v2_tables()
