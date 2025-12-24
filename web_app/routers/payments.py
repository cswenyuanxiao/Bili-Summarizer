"""
Payments Router - 支付相关端点
注意：回调端点需要特殊处理（无需用户认证）
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
import json
import logging

from ..dependencies import get_current_user, get_db
from ..auth import verify_session_token
from ..db import get_connection
from ..payments import (
    create_payment_order,
    update_order_status,
    deliver_order,
    OrderStatus,
    verify_alipay_notify,
    create_wechat_payment,
    verify_wechat_signature,
    parse_wechat_notification
)
from .. import idempotency

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payments", tags=["Payments"])

# --- 定价计划 ---
PRICING_PLANS = {
    "starter_pack": {
        "plan": "credits_pack",
        "type": "one_time",
        "amount_cents": 100,
        "credits": 30
    },
    "creator_pack": {
        "plan": "credits_pack",
        "type": "one_time",
        "amount_cents": 300,
        "credits": 100
    },
    "pro_monthly": {
        "plan": "pro",
        "type": "subscription",
        "amount_cents": 2990,
        "period_days": 30
    }
}


class PaymentRequest(BaseModel):
    plan_id: str
    provider: str = "alipay"


@router.post("/create")
async def create_payment_route(
    request: Request,
    plan_id: str,
    provider: str = "alipay"
):
    """创建支付订单"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    if plan_id not in PRICING_PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    plan = PRICING_PLANS[plan_id]
    
    order_id, payment_url, billing_id = create_payment_order(
        user_id=user["user_id"],
        plan_id=plan_id,
        provider=provider,
        amount_cents=plan["amount_cents"]
    )
    
    # 特殊处理微信支付异步创建
    if provider == 'wechat':
        try:
            res = await create_wechat_payment(order_id, plan["amount_cents"], f"BiliSummarizer-{plan_id}")
            payment_url = res.qr_url or ""
        except Exception as e:
            logger.error(f"Failed to create WeChat payment: {e}")
            raise HTTPException(status_code=500, detail=f"WeChat Pay error: {str(e)}")

    return {
        "order_id": order_id,
        "payment_url": payment_url,
        "billing_id": billing_id,
        "amount_cents": plan["amount_cents"]
    }


@router.get("/status/{order_id}")
async def get_payment_status(order_id: str, request: Request):
    """查询支付状态"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT status, plan, amount_cents, created_at
        FROM payment_orders
        WHERE id = ? AND user_id = ?
    """, (order_id, user["user_id"]))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {
        "order_id": order_id,
        "status": row["status"],
        "plan": row["plan"],
        "amount_cents": row["amount_cents"],
        "created_at": row["created_at"]
    }


# --- 支付回调（无需用户认证）---

@router.post("/callback/alipay")
async def alipay_callback(request: Request):
    """支付宝异步回调"""
    form_data = await request.form()
    data = dict(form_data)
    
    # 验证签名
    verified_data = verify_alipay_notify(data)
    if not verified_data:
        logger.warning(f"Alipay callback signature verification failed")
        return "fail"
    
    trade_status = verified_data.get("trade_status")
    out_trade_no = verified_data.get("out_trade_no")
    trade_no = verified_data.get("trade_no")
    
    # 幂等性检查
    idempotency_key = idempotency.generate_idempotency_key("alipay", trade_no)
    is_new, existing_result = idempotency.check_and_lock(idempotency_key)
    
    if not is_new:
        return existing_result or "success"
    
    try:
        if trade_status in ["TRADE_SUCCESS", "TRADE_FINISHED"]:
            update_order_status(out_trade_no, OrderStatus.PAID, trade_no)
            deliver_order(out_trade_no)
            idempotency.mark_completed(idempotency_key, "success")
            return "success"
        else:
            idempotency.mark_completed(idempotency_key, "ignored")
            return "success"
    except Exception as e:
        logger.error(f"Alipay callback processing error: {e}")
        idempotency.mark_failed(idempotency_key, str(e))
        return "fail"


@router.post("/callback/wechat")
async def wechat_callback(request: Request):
    """微信支付异步回调"""
    body = await request.body()
    headers = dict(request.headers)
    
    # 验证签名
    if not await verify_wechat_signature(headers, body.decode()):
        logger.warning("WeChat callback signature verification failed")
        return {"code": "FAIL", "message": "Invalid signature"}
    
    try:
        data = json.loads(body)
        decrypted = parse_wechat_notification(data)
        
        out_trade_no = decrypted.get("out_trade_no")
        transaction_id = decrypted.get("transaction_id")
        trade_state = decrypted.get("trade_state")
        
        # 幂等性检查
        idempotency_key = idempotency.generate_idempotency_key("wechat", transaction_id)
        is_new, _ = idempotency.check_and_lock(idempotency_key)
        
        if not is_new:
            return {"code": "SUCCESS", "message": "OK"}
        
        if trade_state == "SUCCESS":
            update_order_status(out_trade_no, OrderStatus.PAID, transaction_id)
            deliver_order(out_trade_no)
            idempotency.mark_completed(idempotency_key, "success")
        else:
            idempotency.mark_completed(idempotency_key, "ignored")
            
        return {"code": "SUCCESS", "message": "OK"}
        
    except Exception as e:
        logger.error(f"WeChat callback processing error: {e}")
        return {"code": "FAIL", "message": str(e)}


@router.get("/plans")
async def get_plans():
    """获取可用的定价计划"""
    return {
        "plans": [
            {
                "plan_id": plan_id,
                "plan": plan["plan"],
                "type": plan["type"],
                "amount_cents": plan["amount_cents"],
                "period_days": plan.get("period_days"),
                "credits": plan.get("credits")
            }
            for plan_id, plan in PRICING_PLANS.items()
        ]
    }
