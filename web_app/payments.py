import base64
import json
import os
import time
import secrets
from dataclasses import dataclass
from typing import Optional, Dict, Any

import httpx
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple


@dataclass
class PaymentInitResult:
    payment_url: Optional[str] = None
    qr_url: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None


# ============ 订单状态常量 ============
class OrderStatus:
    PENDING = "pending"      # 待支付
    PAID = "paid"           # 已支付
    DELIVERED = "delivered"  # 已发货（积分/订阅已到账）
    FAILED = "failed"       # 失败
    REFUNDED = "refunded"   # 已退款
    EXPIRED = "expired"     # 已过期


def _normalize_pem(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    return value.replace("\\n", "\n").strip()


# --- Alipay ---
_ALIPAY_CLIENT = None


def _get_alipay_client():
    global _ALIPAY_CLIENT
    if _ALIPAY_CLIENT is not None:
        return _ALIPAY_CLIENT
    from alipay import AliPay

    app_id = os.getenv("ALIPAY_APP_ID")
    app_private_key_raw = _normalize_pem(os.getenv("ALIPAY_PRIVATE_KEY"))
    alipay_public_key_raw = _normalize_pem(os.getenv("ALIPAY_PUBLIC_KEY"))
    notify_url = os.getenv("ALIPAY_NOTIFY_URL")
    if not (app_id and app_private_key_raw and alipay_public_key_raw and notify_url):
        return None

    # 支付宝沙箱只提供纯 Base64 密钥字符串，需要添加 PEM 头尾
    # 自动检测并添加 PEM 格式包装
    if not app_private_key_raw.startswith("-----BEGIN"):
        # PKCS8 格式（支付宝沙箱默认）
        app_private_key = f"-----BEGIN PRIVATE KEY-----\n{app_private_key_raw}\n-----END PRIVATE KEY-----"
    else:
        app_private_key = app_private_key_raw
    
    if not alipay_public_key_raw.startswith("-----BEGIN"):
        alipay_public_key = f"-----BEGIN PUBLIC KEY-----\n{alipay_public_key_raw}\n-----END PUBLIC KEY-----"
    else:
        alipay_public_key = alipay_public_key_raw

    _ALIPAY_CLIENT = AliPay(
        appid=app_id,
        app_notify_url=notify_url,
        app_private_key_string=app_private_key,
        alipay_public_key_string=alipay_public_key,
        sign_type="RSA2",
        debug=os.getenv("ALIPAY_ENV") == "sandbox"
    )
    return _ALIPAY_CLIENT


def create_alipay_payment(order_id: str, amount_cents: int, subject: str) -> Optional[PaymentInitResult]:
    client = _get_alipay_client()
    if not client:
        return None
    total_amount = f"{amount_cents / 100:.2f}"
    # 使用手机网站支付（wap_pay）替代电脑网站支付（page_pay）
    # 沙箱环境下 wap_pay 无需企业资质，且 PC/移动端都能用
    order_string = client.api_alipay_trade_wap_pay(
        out_trade_no=order_id,
        total_amount=total_amount,
        subject=subject,
        return_url=os.getenv("ALIPAY_RETURN_URL"),
        notify_url=os.getenv("ALIPAY_NOTIFY_URL")
    )
    gateway = "https://openapi.alipaydev.com/gateway.do" if os.getenv("ALIPAY_ENV") == "sandbox" else "https://openapi.alipay.com/gateway.do"
    return PaymentInitResult(payment_url=f"{gateway}?{order_string}")


def verify_alipay_notify(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    client = _get_alipay_client()
    if not client:
        return None
    data = dict(payload)
    signature = data.pop("sign", None)
    if not signature:
        return None
    if not client.verify(data, signature):
        return None
    return data


# --- WeChat Pay v3 ---
_WECHAT_CERT_CACHE: Dict[str, Any] = {}
_WECHAT_CERT_CACHE_TS = 0


def _get_wechat_private_key():
    key = _normalize_pem(os.getenv("WECHAT_PRIVATE_KEY"))
    if not key:
        return None
    return serialization.load_pem_private_key(key.encode(), password=None)


def _wechat_sign(method: str, path: str, body: str, timestamp: str, nonce: str, private_key) -> str:
    message = f"{method}\n{path}\n{timestamp}\n{nonce}\n{body}\n"
    signature = private_key.sign(
        message.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()


def _wechat_auth_header(method: str, path: str, body: str) -> Optional[str]:
    mch_id = os.getenv("WECHAT_MCH_ID")
    serial_no = os.getenv("WECHAT_SERIAL_NO")
    private_key = _get_wechat_private_key()
    if not (mch_id and serial_no and private_key):
        return None
    timestamp = str(int(time.time()))
    nonce = secrets.token_urlsafe(16)
    signature = _wechat_sign(method, path, body, timestamp, nonce, private_key)
    return (
        f'WECHATPAY2-SHA256-RSA2048 mchid="{mch_id}",'
        f'nonce_str="{nonce}",timestamp="{timestamp}",'
        f'serial_no="{serial_no}",signature="{signature}"'
    )


async def _wechat_request(method: str, path: str, payload: Optional[Dict[str, Any]] = None) -> httpx.Response:
    body = json.dumps(payload or {}, ensure_ascii=False) if method.upper() != "GET" else ""
    auth = _wechat_auth_header(method, path, body)
    if not auth:
        raise ValueError("WeChat Pay credentials missing")
    headers = {
        "Authorization": auth,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "bili-summarizer"
    }
    url = f"https://api.mch.weixin.qq.com{path}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        return await client.request(method, url, headers=headers, content=body.encode("utf-8") if body else None)


async def create_wechat_payment(order_id: str, amount_cents: int, description: str) -> PaymentInitResult:
    app_id = os.getenv("WECHAT_APP_ID")
    notify_url = os.getenv("WECHAT_NOTIFY_URL")
    mch_id = os.getenv("WECHAT_MCH_ID")
    if not (app_id and notify_url and mch_id):
        raise ValueError("WeChat Pay credentials missing")
    payload = {
        "appid": app_id,
        "mchid": mch_id,
        "description": description,
        "out_trade_no": order_id,
        "notify_url": notify_url,
        "amount": {
            "total": amount_cents,
            "currency": "CNY"
        }
    }
    resp = await _wechat_request("POST", "/v3/pay/transactions/native", payload)
    if resp.status_code >= 400:
        raise ValueError(resp.text)
    data = resp.json()
    return PaymentInitResult(qr_url=data.get("code_url"), raw=data)


def _decrypt_wechat_resource(resource: Dict[str, Any]) -> Any:
    api_v3_key = os.getenv("WECHAT_API_V3_KEY")
    if not api_v3_key:
        raise ValueError("WECHAT_API_V3_KEY missing")
    ciphertext = resource.get("ciphertext")
    nonce = resource.get("nonce")
    associated_data = resource.get("associated_data")
    if not (ciphertext and nonce):
        raise ValueError("Invalid resource payload")
    aesgcm = AESGCM(api_v3_key.encode())
    decrypted = aesgcm.decrypt(
        nonce.encode(),
        base64.b64decode(ciphertext),
        associated_data.encode() if associated_data else None
    )
    decrypted_text = decrypted.decode()
    try:
        return json.loads(decrypted_text)
    except json.JSONDecodeError:
        return decrypted_text


async def _refresh_wechat_platform_certs() -> None:
    global _WECHAT_CERT_CACHE, _WECHAT_CERT_CACHE_TS
    resp = await _wechat_request("GET", "/v3/certificates")
    if resp.status_code >= 400:
        raise ValueError(resp.text)
    payload = resp.json()
    certs: Dict[str, serialization.PublicFormat] = {}
    for item in payload.get("data", []):
        serial = item.get("serial_no")
        resource = item.get("encrypt_certificate") or {}
        cert_data = _decrypt_wechat_resource(resource)
        cert_pem = None
        if isinstance(cert_data, dict):
            cert_pem = cert_data.get("certificates") or cert_data.get("certificate") or cert_data.get("cert")
        elif isinstance(cert_data, str):
            cert_pem = cert_data
        if not (serial and cert_pem):
            continue
        cert = x509.load_pem_x509_certificate(cert_pem.encode())
        certs[serial] = cert.public_key()
    if certs:
        _WECHAT_CERT_CACHE = certs
        _WECHAT_CERT_CACHE_TS = int(time.time())


async def verify_wechat_signature(headers: Dict[str, str], body: str) -> bool:
    signature = headers.get("Wechatpay-Signature") or headers.get("wechatpay-signature")
    timestamp = headers.get("Wechatpay-Timestamp") or headers.get("wechatpay-timestamp")
    nonce = headers.get("Wechatpay-Nonce") or headers.get("wechatpay-nonce")
    serial = headers.get("Wechatpay-Serial") or headers.get("wechatpay-serial")
    if not all([signature, timestamp, nonce, serial]):
        return False
    public_key = _WECHAT_CERT_CACHE.get(serial)
    if not public_key:
        await _refresh_wechat_platform_certs()
        public_key = _WECHAT_CERT_CACHE.get(serial)
    if not public_key:
        return False
    message = f"{timestamp}\n{nonce}\n{body}\n"
    try:
        public_key.verify(
            base64.b64decode(signature),
            message.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False


def parse_wechat_notification(payload: Dict[str, Any]) -> Dict[str, Any]:
    resource = payload.get("resource") or {}
    return _decrypt_wechat_resource(resource)


# ============ 高级订单管理 ============

def create_payment_order(
    user_id: str,
    plan_id: str,
    provider: str,  # 'alipay' | 'wechat'
    amount_cents: int,
    metadata: Optional[Dict] = None
) -> Tuple[str, str, str]:
    """
    创建支付订单
    返回: (order_id, payment_link_or_qr, billing_id)
    """
    import uuid
    import time
    from .db import get_connection
    
    order_id = f"ORD_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    billing_id = f"BIL_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 创建账单记录
    cursor.execute("""
        INSERT INTO billing_events (id, user_id, amount_cents, currency, status, created_at)
        VALUES (?, ?, ?, 'CNY', 'pending', ?)
    """, (billing_id, user_id, amount_cents, datetime.utcnow().isoformat()))
    
    # 创建支付订单
    cursor.execute("""
        INSERT INTO payment_orders (id, user_id, provider, plan, amount_cents, status, billing_id, created_at)
        VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)
    """, (order_id, user_id, provider, plan_id, amount_cents, billing_id, datetime.utcnow().isoformat()))
    
    conn.commit()
    conn.close()
    
    # 调用支付渠道创建预支付
    payment_link = ""
    if provider == 'alipay':
        res = create_alipay_payment(order_id, amount_cents, f"BiliSummarizer-{plan_id}")
        if res:
            payment_link = res.payment_url or ""
    else:
        # WeChat Pay 这里需要 async 处理，但目前的 payments.py 是混用的
        # 实际调用时建议在异步环境运行
        # 这里为了兼容性，如果是 async 我们后续在 API 调用
        payment_link = "" # 会在 API 层处理异步
    
    return order_id, payment_link, billing_id


def update_order_status(order_id: str, new_status: str, transaction_id: Optional[str] = None) -> bool:
    """更新订单状态并记录外部交易号"""
    from .db import get_connection
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE payment_orders 
        SET status = ?, updated_at = ?, transaction_id = ?
        WHERE id = ?
    """, (new_status, datetime.utcnow().isoformat(), transaction_id, order_id))
    
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    return affected > 0


def deliver_order(order_id: str) -> bool:
    """
    发货：根据订单类型发放积分或激活订阅
    """
    import logging
    from .db import get_connection
    from .credits import grant_credits
    
    logger = logging.getLogger(__name__)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 获取订单信息
    cursor.execute("""
        SELECT user_id, plan, amount_cents, status, billing_id
        FROM payment_orders WHERE id = ?
    """, (order_id,))
    
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    
    user_id, plan, amount_cents, status, billing_id = row
    
    # 检查是否已发货
    if status == OrderStatus.DELIVERED:
        logger.info(f"Order {order_id} already delivered, skipping")
        conn.close()
        return True
    
    # 根据套餐类型发货
    # 注意：这里需要从 PRICING_PLANS 获取信息，
    # 避免循环引用，我们可以直接从 main 导入或者按规范传参
    # 这里我们采用局部导入
    from .main import PRICING_PLANS
    plan_info = PRICING_PLANS.get(plan, {})
    
    if plan_info.get("type") == "one_time":
        # 积分包：发放积分
        credits_to_add = plan_info.get("credits", 0)
        grant_credits(user_id, credits_to_add, f"purchase_{order_id}")
        logger.info(f"Granted {credits_to_add} credits to user {user_id}")
    else:
        # 订阅：激活订阅
        period_days = plan_info.get("period_days", 30)
        period_end = datetime.utcnow() + timedelta(days=period_days)
        cursor.execute("""
            INSERT INTO subscriptions (user_id, plan, status, current_period_end, updated_at)
            VALUES (?, ?, 'active', ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                plan = EXCLUDED.plan,
                status = EXCLUDED.status,
                current_period_end = EXCLUDED.current_period_end,
                updated_at = EXCLUDED.updated_at
        """ if conn._is_postgres else """
            INSERT OR REPLACE INTO subscriptions (user_id, plan, status, current_period_end, updated_at)
            VALUES (?, ?, 'active', ?, ?)
        """, (user_id, plan, period_end.isoformat(), datetime.utcnow().isoformat()))
        logger.info(f"Activated subscription {plan} for user {user_id}")
    
    # 更新订单和账单状态
    cursor.execute("UPDATE payment_orders SET status = ?, updated_at = ? WHERE id = ?", 
                  (OrderStatus.DELIVERED, datetime.utcnow().isoformat(), order_id))
    cursor.execute("UPDATE billing_events SET status = 'paid', updated_at = ? WHERE id = ?", 
                  (datetime.utcnow().isoformat(), billing_id))
    
    conn.commit()
    conn.close()
    
    return True
