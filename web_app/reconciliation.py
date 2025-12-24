"""
对账服务
检查订单、账单、积分之间的一致性
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ReconciliationResult:
    success: bool
    checked_count: int
    issues: List[Dict[str, Any]]
    fixed_count: int
    summary: str

class ReconciliationService:
    """对账服务"""
    
    def run_full_reconciliation(self, auto_fix: bool = False) -> ReconciliationResult:
        """执行完整对账"""
        issues = []
        fixed_count = 0
        
        # 1. 检查已支付但未发货的订单
        unpaid_orders = self._check_paid_not_delivered()
        issues.extend(unpaid_orders)
        
        # 2. 检查账单与订单状态不匹配
        billing_mismatches = self._check_billing_order_mismatch()
        issues.extend(billing_mismatches)
        
        # 3. 检查过期未支付订单
        expired_results = self._expire_old_pending_orders()
        issues.extend(expired_results)
        
        if auto_fix:
            fixed_count = self._auto_fix_issues(issues)
        
        return ReconciliationResult(
            success=len(issues) == 0,
            checked_count=self._get_total_order_count(),
            issues=issues,
            fixed_count=fixed_count,
            summary=self._generate_summary(issues, fixed_count)
        )
    
    def _check_paid_not_delivered(self) -> List[Dict]:
        """检查已支付但未发货的订单"""
        from .db import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # 查找 paid 状态但未变成 delivered 的订单（排除最近 2 分钟内的订单以防竞争条件）
        threshold = (datetime.utcnow() - timedelta(minutes=2)).isoformat()
        
        cursor.execute("""
            SELECT id, user_id, plan, amount_cents, updated_at
            FROM payment_orders
            WHERE status = 'paid' AND updated_at < ?
        """, (threshold,))
        
        rows = cursor.fetchall()
        conn.close()
        
        issues = []
        for row in rows:
            issues.append({
                "type": "PAID_NOT_DELIVERED",
                "severity": "high",
                "order_id": row["id"],
                "user_id": row["user_id"],
                "plan": row["plan"],
                "amount_cents": row["amount_cents"],
                "suggestion": "尝试重新执行 deliver_order"
            })
        
        return issues
    
    def _check_billing_order_mismatch(self) -> List[Dict]:
        """检查账单与订单状态不匹配"""
        from .db import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # 订单已发货但关联的账单事件状态不是已支付
        cursor.execute("""
            SELECT p.id, p.billing_id, p.status as order_status, b.status as billing_status
            FROM payment_orders p
            JOIN billing_events b ON p.billing_id = b.id
            WHERE p.status = 'delivered' AND b.status != 'paid'
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        issues = []
        for row in rows:
            issues.append({
                "type": "BILLING_MISMATCH",
                "severity": "medium",
                "order_id": row["id"],
                "billing_id": row["billing_id"],
                "order_status": row["order_status"],
                "billing_status": row["billing_status"],
                "suggestion": "更新账单状态为 paid"
            })
        
        return issues
    
    def _expire_old_pending_orders(self) -> List[Dict]:
        """标记过期旧的待支付订单"""
        from .db import get_connection
        from .payments import OrderStatus
        
        # 超过 1 小时未支付的订单标记为过期
        threshold = (datetime.utcnow() - timedelta(hours=1)).isoformat()
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE payment_orders
            SET status = ?, updated_at = ?
            WHERE status = ? AND created_at < ?
        """, (OrderStatus.EXPIRED, datetime.utcnow().isoformat(), OrderStatus.PENDING, threshold))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        if affected > 0:
            return [{
                "type": "EXPIRED_ORDERS",
                "severity": "info",
                "count": affected,
                "suggestion": "已自动过期旧订单"
            }]
        return []
    
    def _auto_fix_issues(self, issues: List[Dict]) -> int:
        """选择性地自动修复问题"""
        from .payments import deliver_order
        from .db import get_connection
        
        fixed = 0
        for issue in issues:
            try:
                if issue["type"] == "PAID_NOT_DELIVERED":
                    if deliver_order(issue["order_id"]):
                        fixed += 1
                elif issue["type"] == "BILLING_MISMATCH":
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE billing_events SET status = 'paid' WHERE id = ?", (issue["billing_id"],))
                    conn.commit()
                    conn.close()
                    fixed += 1
            except Exception as e:
                logger.error(f"Failed to auto-fix {issue['type']} for {issue.get('order_id')}: {e}")
                
        return fixed
    
    def _get_total_order_count(self) -> int:
        from .db import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM payment_orders")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def _generate_summary(self, issues: List[Dict], fixed: int) -> str:
        if not issues:
            return "全量对账完成，系统一致性良好。"
        
        high = sum(1 for i in issues if i.get("severity") == "high")
        return f"发现 {len(issues)} 个问题（高危: {high}），已修复 {fixed} 个。"

reconciliation = ReconciliationService()
