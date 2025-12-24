"""
幂等性处理
防止重复回调导致重复发货
"""
import hashlib
from typing import Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class IdempotencyManager:
    """
    幂等性管理器
    使用数据库记录已处理的回调，防止重复处理
    """
    
    @staticmethod
    def generate_idempotency_key(provider: str, transaction_id: str) -> str:
        """生成幂等键"""
        raw = f"{provider}:{transaction_id}"
        return hashlib.sha256(raw.encode()).hexdigest()
    
    @staticmethod
    def check_and_lock(idempotency_key: str) -> Tuple[bool, Optional[str]]:
        """
        检查是否已处理过该回调
        返回: (is_new, existing_result)
        - (True, None): 新回调，已锁定
        - (False, result): 已处理过，返回之前的结果
        """
        from .db import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # 检查是否存在
        cursor.execute("""
            SELECT result, status FROM idempotency_keys WHERE key = ?
        """, (idempotency_key,))
        
        row = cursor.fetchone()
        
        if row:
            conn.close()
            # 如果状态还是 processing，说明另一个请求正在处理中
            # 这里简单返回 False，上层通常会稍后重试
            return False, row["result"] if row["status"] == "completed" else None
        
        # 尝试插入（加锁）
        try:
            cursor.execute("""
                INSERT INTO idempotency_keys (key, status, created_at)
                VALUES (?, 'processing', ?)
            """, (idempotency_key, datetime.utcnow().isoformat()))
            conn.commit()
            conn.close()
            return True, None
        except Exception as e:
            # 并发插入冲突，说明另一个进程正在处理
            if conn: conn.close()
            logger.warning(f"Idempotency conflict for key {idempotency_key}: {e}")
            return False, None
    
    @staticmethod
    def mark_completed(idempotency_key: str, result: str):
        """标记为已完成"""
        from .db import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE idempotency_keys 
            SET status = 'completed', result = ?, completed_at = ?
            WHERE key = ?
        """, (result, datetime.utcnow().isoformat(), idempotency_key))
        conn.commit()
        conn.close()
    
    @staticmethod
    def mark_failed(idempotency_key: str, error: str):
        """标记为失败（允许后续重试，删除记录或标记为 failed）"""
        from .db import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        # 这里我们选择删除记录，以便允许重试
        cursor.execute("DELETE FROM idempotency_keys WHERE key = ?", (idempotency_key,))
        conn.commit()
        conn.close()

idempotency = IdempotencyManager()
