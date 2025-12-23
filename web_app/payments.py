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


@dataclass
class PaymentInitResult:
    payment_url: Optional[str] = None
    qr_url: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None


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
    app_private_key = _normalize_pem(os.getenv("ALIPAY_PRIVATE_KEY"))
    alipay_public_key = _normalize_pem(os.getenv("ALIPAY_PUBLIC_KEY"))
    notify_url = os.getenv("ALIPAY_NOTIFY_URL")
    if not (app_id and app_private_key and alipay_public_key and notify_url):
        return None

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
    order_string = client.api_alipay_trade_page_pay(
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
