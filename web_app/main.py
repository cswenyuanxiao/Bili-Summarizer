import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, Security, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional

# --- 数据模型 ---
class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str

class ChatRequest(BaseModel):
    summary: str
    transcript: Optional[str] = ""
    question: str
    history: List[ChatMessage] = []

class HistoryItem(BaseModel):
    id: Optional[str] = None
    video_url: str
    video_title: Optional[str] = None
    video_thumbnail: Optional[str] = None
    mode: str
    focus: str
    summary: str
    transcript: Optional[str] = None
    mindmap: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

# --- web_app 内部模块导入 ---
from .downloader import download_content
from .summarizer_gemini import summarize_content, extract_ai_transcript, upload_to_gemini, delete_gemini_file
from .cache import get_cached_result, save_to_cache, get_cache_stats
from .auth import get_current_user, verify_session_token
from .credits import ensure_user_credits, get_user_credits, charge_user_credits, get_daily_usage, grant_first_summary_bonus
from .telemetry import record_failure
from typing import List
import sqlite3
import secrets
import hashlib

# --- 配置日志 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# --- 初始化 ---
app = FastAPI(title="Bili-Summarizer")

# --- 数据库初始化 ---
@app.on_event("startup")
async def init_database():
    """初始化 API Key 和配额管理表"""
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    
    # 创建 API Keys 表
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
    
    # 创建使用配额表
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

    # API Key 使用统计（按天）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_key_usage_daily (
            key_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            date TEXT NOT NULL,
            count INTEGER DEFAULT 0,
            PRIMARY KEY (key_id, date)
        )
    """)

    # 支付订单
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payment_orders (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            plan TEXT NOT NULL,
            amount_cents INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            billing_id TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 邀请码
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invite_codes (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

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

    # 分享链接
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
    
    # 创建索引
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_api_keys_user 
        ON api_keys(user_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_api_keys_hash 
        ON api_keys(key_hash)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_usage_daily_user 
        ON usage_daily(user_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_billing_user 
        ON billing_events(user_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_api_key_usage_user 
        ON api_key_usage_daily(user_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_payment_user 
        ON payment_orders(user_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_invite_user 
        ON invite_codes(user_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_share_user 
        ON share_links(user_id)
    """)
    
    conn.commit()
    conn.close()
    logger.info("Database tables initialized successfully")

# --- CORS 配置（允许 Vue 前端访问）---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite 开发服务器
        "http://localhost:3000",  # 备用端口
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 静态文件（仅保留 videos 用于视频播放）---
# 允许前端访问 videos 目录下的文件用于播放
app.mount("/videos", StaticFiles(directory="videos"), name="videos")
legacy_static = Path(__file__).resolve().parent / "legacy_ui" / "static"
if legacy_static.exists():
    app.mount("/static", StaticFiles(directory=str(legacy_static)), name="static")

# --- Frontend Static (Render) ---
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
LEGACY_INDEX = Path(__file__).resolve().parent / "legacy_ui" / "index.html"

# --- 健康检查路由 ---
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Bili-Summarizer API"}

# --- 核心业务路由 ---

class SummarizeRequest(BaseModel):
    url: str
    mode: str = "smart" # "smart" or "video"
    focus: str = "default" # "default", "study", "gossip", "business"
    skip_cache: bool = False  # 是否跳过缓存

class BatchSummarizeRequest(BaseModel):
    urls: List[str]
    mode: str = "smart"
    focus: str = "default"

@app.get("/summarize")
async def run_summarization(
    url: str,
    mode: str = "smart",
    focus: str = "default",
    skip_cache: bool = False,
    token: Optional[str] = None
):
    safe_url = url.split("?")[0]
    logger.info(f"收到总结请求: URL={safe_url}, Mode={mode}, Focus={focus}")

    async def event_generator():
        video_path = None
        remote_file = None
        user = None
        credit_cost = 10
        
        try:
            if token:
                try:
                    user = await verify_session_token(token)
                    ensure_user_credits(user["user_id"])
                except HTTPException as e:
                    record_failure(None, "AUTH_INVALID", "auth", str(e.detail))
                    yield f"data: {json.dumps({'type': 'error', 'code': 'AUTH_INVALID', 'error': e.detail})}\n\n"
                    return

            # 检查缓存
            if not skip_cache:
                cached = get_cached_result(url, mode, focus)
                if cached:
                    logger.info(f"命中缓存: {url}")
                    yield f"data: {json.dumps({'type': 'status', 'status': 'Found in cache! Loading...'})}\n\n"
                    # Emit all events for cached content using the same payload shape as live SSE
                    yield f"data: {json.dumps({'type': 'transcript_complete', 'transcript': cached['transcript']})}\n\n"
                    yield f"data: {json.dumps({'type': 'summary_complete', 'summary': cached['summary'], 'usage': cached['usage'], 'cached': True})}\n\n"
                    # Finally emit completion
                    yield f"data: {json.dumps({'type': 'status', 'status': 'complete'})}\n\n"
                    return

            if user:
                credits = get_user_credits(user["user_id"])
                if not credits or credits["credits"] < credit_cost:
                    record_failure(user["user_id"], "CREDITS_EXCEEDED", "quota", "insufficient credits")
                    yield f"data: {json.dumps({'type': 'error', 'code': 'CREDITS_EXCEEDED', 'error': '积分不足，请升级或稍后再试'})}\n\n"
                    return
            
            loop = asyncio.get_event_loop()
            queue = asyncio.Queue()

            def progress_callback(status):
                loop.call_soon_threadsafe(queue.put_nowait, {'type': 'status', 'data': status})

            # Task wrapper to send results to queue
            async def task_wrapper(name, coro):
                try:
                    # coro is a Future (from run_in_executor) or a coroutine
                    result = await coro
                    if name == "transcript" and not result:
                        await queue.put({'type': 'transcript_failed', 'data': 'empty transcript', 'source': name})
                        return
                    await queue.put({'type': f'{name}_complete', 'data': result, 'source': name})
                except Exception as e:
                    logger.error(f"Task {name} failed: {e}")
                    if name == "transcript":
                        await queue.put({'type': 'transcript_failed', 'data': str(e), 'source': name})
                        return
                    await queue.put({'type': 'error', 'data': str(e), 'source': name})

            def extract_transcript_with_retry():
                transcript_text = extract_ai_transcript(video_path, progress_callback, remote_file)
                if transcript_text:
                    return transcript_text
                progress_callback("Transcript empty, retrying...")
                return extract_ai_transcript(video_path, progress_callback, remote_file)

            # 1. Download Content
            # ... (download logic) ...
            try:
                video_path, media_type, transcript = await loop.run_in_executor(None, download_content, url, mode, progress_callback)
                
                # Immediately notify frontend about video
                video_filename = os.path.basename(video_path) if video_path else None
                await queue.put({'type': 'video_downloaded', 'data': {'filename': video_filename}})
                
                # If transcript exists from download (e.g. subtitles), emit it now
                if transcript:
                    await queue.put({'type': 'transcript_complete', 'data': transcript, 'source': 'subtitle'})

            except Exception as e:
                record_failure(user["user_id"] if user else None, "DOWNLOAD_FAILED", "download", str(e))
                yield f"data: {json.dumps({'type': 'error', 'code': 'DOWNLOAD_FAILED', 'error': str(e)})}\n\n"
                return

            # 2. Upload to Gemini (if needed)
            if media_type in ['video', 'audio']:
                 remote_file = await loop.run_in_executor(None, upload_to_gemini, video_path, progress_callback)

            # 3. Start Parallel Tasks
            active_tasks = 0

            # Task A: Summary
            summary_coro = loop.run_in_executor(
                None,
                summarize_content,
                video_path,
                media_type,
                progress_callback,
                focus,
                remote_file
            )
            asyncio.create_task(task_wrapper('summary', summary_coro))
            active_tasks += 1

            # Task B: Transcript (if needed)
            need_transcript = (not transcript and media_type in ['audio', 'video'])
            transcript_task_started = False
            if need_transcript:
                 transcript_coro = loop.run_in_executor(None, extract_transcript_with_retry)
                 asyncio.create_task(task_wrapper('transcript', transcript_coro))
                 active_tasks += 1
                 transcript_task_started = True

            if active_tasks > 0:
                 logger.info(f"🚀 Started {active_tasks} parallel AI tasks...")

            # 4. Event Loop: Consume queue until all tasks done
            final_summary = None
            final_transcript = transcript or ''
            final_usage = None

            completed_tasks = 0
            while completed_tasks < active_tasks:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=300.0)
                    msg_type = event.get('type')
                    data = event.get('data')

                    if msg_type == 'status':
                         yield f"data: {json.dumps({'type': 'status', 'status': data})}\n\n"
                    elif msg_type == 'video_downloaded':
                         yield f"data: {json.dumps({'type': 'video_downloaded', 'video_file': data['filename']})}\n\n"
                    elif msg_type == 'transcript_complete':
                         final_transcript = data or ''
                         yield f"data: {json.dumps({'type': 'transcript_complete', 'transcript': final_transcript})}\n\n"
                         if transcript_task_started and event.get('source') == 'transcript':
                             completed_tasks += 1
                    elif msg_type == 'summary_complete':
                         final_summary, final_usage = data
                         yield f"data: {json.dumps({'type': 'summary_complete', 'summary': final_summary, 'usage': final_usage})}\n\n"
                         completed_tasks += 1
                    elif msg_type == 'transcript_failed':
                         record_failure(user["user_id"] if user else None, "TRANSCRIPT_FAILED", "transcript", str(data))
                         yield f"data: {json.dumps({'type': 'status', 'status': '转录生成失败，已跳过'})}\n\n"
                         if transcript_task_started:
                             completed_tasks += 1
                    elif msg_type == 'error':
                         record_failure(user["user_id"] if user else None, "SUMMARY_FAILED", "summary", str(data))
                         yield f"data: {json.dumps({'type': 'error', 'code': 'SUMMARY_FAILED', 'error': data})}\n\n"
                         completed_tasks += 1
                except asyncio.TimeoutError:
                     yield f"data: {json.dumps({'type': 'status', 'status': 'AI analysis is taking longer than expected...'})}\n\n"
            
            if final_summary:
                 if user:
                     if charge_user_credits(user["user_id"], credit_cost):
                         grant_first_summary_bonus(user["user_id"])
                 save_to_cache(url, mode, focus, final_summary, final_transcript or '', final_usage)
                 yield f"data: {json.dumps({'type': 'status', 'status': 'complete'})}\n\n"

        except Exception as e:
            logger.error(f"流式响应异常: {str(e)}")
            record_failure(user["user_id"] if user else None, "INTERNAL_ERROR", "sse", str(e))
            yield f"data: {json.dumps({'type': 'error', 'code': 'INTERNAL_ERROR', 'error': str(e)})}\n\n"
        finally:
            if remote_file:
                 # Start cleanup in executor, but don't wrap in create_task since it returns a future
                 loop.run_in_executor(None, delete_gemini_file, remote_file)
            
            # Clean up local video after 1 hour (same logic as before)
            videos_dir = "videos"
            if os.path.exists(videos_dir):
                import time
                current_time = time.time()
                for filename in os.listdir(videos_dir):
                    if filename == '.gitkeep': continue
                    file_path = os.path.join(videos_dir, filename)
                    try:
                        if os.path.isfile(file_path):
                            file_age = current_time - os.path.getmtime(file_path)
                            if file_age > 3600:
                                os.remove(file_path)
                    except Exception:
                        pass
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/dashboard")
async def get_dashboard(user: dict = Depends(get_current_user)):
    credits = get_user_credits(user["user_id"]) or ensure_user_credits(user["user_id"])
    usage = get_daily_usage(user["user_id"], 14)
    daily_usage = [
        {"day": day, "count": usage[day]}
        for day in sorted(usage.keys())
    ]
    return {
        "user_id": user["user_id"],
        "email": user.get("email"),
        "credits": credits["credits"],
        "total_used": credits["total_used"],
        "cost_per_summary": 10,
        "daily_usage": daily_usage
    }


def fetch_subscription(user_id: str) -> dict:
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT plan, status, current_period_end, updated_at
            FROM subscriptions
            WHERE user_id = ?
        """, (user_id,))
        row = cursor.fetchone()
        if not row:
            return {
                "plan": "free",
                "status": "inactive",
                "current_period_end": None,
                "updated_at": None
            }
        return {
            "plan": row[0],
            "status": row[1],
            "current_period_end": row[2],
            "updated_at": row[3]
        }
    finally:
        conn.close()


@app.get("/api/subscription")
async def get_subscription(user: dict = Depends(get_current_user)):
    subscription = fetch_subscription(user["user_id"])
    return {
        "user_id": user["user_id"],
        "plan": subscription["plan"],
        "status": subscription["status"],
        "current_period_end": subscription["current_period_end"],
        "updated_at": subscription["updated_at"]
    }


class SubscribeRequest(BaseModel):
    plan_id: str


class PaymentRequest(BaseModel):
    plan_id: str
    provider: str


class RedeemInviteRequest(BaseModel):
    code: str


class ShareRequest(BaseModel):
    title: Optional[str] = None
    summary: str
    transcript: Optional[str] = None
    mindmap: Optional[str] = None


@app.post("/api/subscribe")
async def create_subscription(request: SubscribeRequest, user: dict = Depends(get_current_user)):
    plan_map = {
        "pro_monthly": {
            "plan": "pro",
            "amount_cents": 990,
            "period_days": 30
        }
    }
    if request.plan_id not in plan_map:
        raise HTTPException(400, "Invalid plan")

    plan = plan_map[request.plan_id]
    period_end = (datetime.utcnow() + timedelta(days=plan["period_days"])).isoformat()
    invoice_id = secrets.token_urlsafe(12)
    invoice_url = f"/api/billing/{invoice_id}/invoice"

    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO subscriptions (user_id, plan, status, current_period_end, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id)
            DO UPDATE SET
              plan = excluded.plan,
              status = excluded.status,
              current_period_end = excluded.current_period_end,
              updated_at = CURRENT_TIMESTAMP
        """, (user["user_id"], plan["plan"], "active", period_end))

        cursor.execute("""
            INSERT INTO billing_events (id, user_id, amount_cents, currency, status, period_start, period_end, invoice_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            invoice_id,
            user["user_id"],
            plan["amount_cents"],
            "CNY",
            "paid",
            datetime.utcnow().isoformat(),
            period_end,
            invoice_url
        ))

        conn.commit()
    finally:
        conn.close()

    return {
        "user_id": user["user_id"],
        "plan": plan["plan"],
        "status": "active",
        "current_period_end": period_end,
        "invoice_url": invoice_url
    }


def is_alipay_configured() -> bool:
    return all([
        os.getenv("ALIPAY_APP_ID"),
        os.getenv("ALIPAY_PRIVATE_KEY"),
        os.getenv("ALIPAY_PUBLIC_KEY"),
        os.getenv("ALIPAY_NOTIFY_URL")
    ])


def is_wechat_configured() -> bool:
    return all([
        os.getenv("WECHAT_APP_ID"),
        os.getenv("WECHAT_MCH_ID"),
        os.getenv("WECHAT_SERIAL_NO"),
        os.getenv("WECHAT_PRIVATE_KEY"),
        os.getenv("WECHAT_API_V3_KEY"),
        os.getenv("WECHAT_NOTIFY_URL")
    ])


def create_payment_order(user_id: str, plan: dict, provider: str) -> dict:
    order_id = secrets.token_urlsafe(16)
    billing_id = secrets.token_urlsafe(12)
    invoice_url = f"/api/billing/{billing_id}/invoice"
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO billing_events (id, user_id, amount_cents, currency, status, period_start, period_end, invoice_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            billing_id,
            user_id,
            plan["amount_cents"],
            "CNY",
            "pending",
            datetime.utcnow().isoformat(),
            (datetime.utcnow() + timedelta(days=plan["period_days"])).isoformat(),
            invoice_url
        ))

        cursor.execute("""
            INSERT INTO payment_orders (id, user_id, provider, plan, amount_cents, status, billing_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            order_id,
            user_id,
            provider,
            plan["plan"],
            plan["amount_cents"],
            "pending",
            billing_id
        ))
        conn.commit()
        return {
            "order_id": order_id,
            "billing_id": billing_id,
            "invoice_url": invoice_url
        }
    finally:
        conn.close()


def mark_payment_paid(order_id: str) -> dict:
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT user_id, plan, billing_id FROM payment_orders WHERE id = ?
        """, (order_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(404, "Payment order not found")
        user_id, plan, billing_id = row

        period_end = (datetime.utcnow() + timedelta(days=30)).isoformat()
        cursor.execute("""
            UPDATE payment_orders
            SET status = 'paid', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (order_id,))

        cursor.execute("""
            UPDATE billing_events
            SET status = 'paid'
            WHERE id = ?
        """, (billing_id,))

        cursor.execute("""
            INSERT INTO subscriptions (user_id, plan, status, current_period_end, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id)
            DO UPDATE SET
              plan = excluded.plan,
              status = excluded.status,
              current_period_end = excluded.current_period_end,
              updated_at = CURRENT_TIMESTAMP
        """, (user_id, plan, "active", period_end))
        conn.commit()
        return {"user_id": user_id, "plan": plan, "current_period_end": period_end}
    finally:
        conn.close()


@app.post("/api/payments")
async def create_payment(request: PaymentRequest, user: dict = Depends(get_current_user)):
    plan_map = {
        "pro_monthly": {
            "plan": "pro",
            "amount_cents": 990,
            "period_days": 30
        }
    }
    if request.plan_id not in plan_map:
        raise HTTPException(400, "Invalid plan")
    provider = request.provider.lower()
    if provider not in ("alipay", "wechat"):
        raise HTTPException(400, "Invalid provider")

    if provider == "alipay" and not is_alipay_configured():
        raise HTTPException(501, "Alipay is not configured")
    if provider == "wechat" and not is_wechat_configured():
        raise HTTPException(501, "WeChat Pay is not configured")

    plan = plan_map[request.plan_id]
    order = create_payment_order(user["user_id"], plan, provider)
    payment_url = None
    qr_url = None

    if os.getenv("PAYMENT_MOCK") == "1":
        payment_url = f"/api/payments/mock-complete?order_id={order['order_id']}"

    return {
        "order_id": order["order_id"],
        "provider": provider,
        "plan": plan["plan"],
        "amount_cents": plan["amount_cents"],
        "payment_url": payment_url,
        "qr_url": qr_url
    }


@app.post("/api/payments/mock-complete")
async def mock_payment_complete(order_id: str):
    if os.getenv("PAYMENT_MOCK") != "1":
        raise HTTPException(403, "Mock payment disabled")
    return mark_payment_paid(order_id)


@app.get("/api/billing/{billing_id}/invoice")
async def download_invoice(billing_id: str, user: dict = Depends(get_current_user)):
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, amount_cents, currency, status, period_start, period_end, created_at
            FROM billing_events
            WHERE id = ? AND user_id = ?
        """, (billing_id, user["user_id"]))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(404, "Invoice not found")
        if row[3] != "paid":
            raise HTTPException(400, "Invoice is not paid yet")
        invoice_path = Path("invoices")
        invoice_path.mkdir(exist_ok=True)
        file_path = invoice_path / f"{billing_id}.pdf"
        if not file_path.exists():
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            c = canvas.Canvas(str(file_path), pagesize=A4)
            width, height = A4
            c.setFont("Helvetica-Bold", 16)
            c.drawString(40, height - 60, "Bili-Summarizer 发票")
            c.setFont("Helvetica", 11)
            c.drawString(40, height - 100, f"账单编号: {billing_id}")
            c.drawString(40, height - 120, f"金额: ¥{row[1] / 100:.2f} {row[2]}")
            c.drawString(40, height - 140, f"周期: {row[4]} - {row[5]}")
            c.drawString(40, height - 160, f"开票时间: {row[6]}")
            c.drawString(40, height - 200, "感谢使用 Bili-Summarizer")
            c.showPage()
            c.save()
        return FileResponse(str(file_path), media_type="application/pdf", filename=f"invoice-{billing_id}.pdf")
    finally:
        conn.close()


@app.get("/api/billing")
async def get_billing_history(user: dict = Depends(get_current_user)):
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, amount_cents, currency, status, period_start, period_end, invoice_url, created_at
            FROM billing_events
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user["user_id"],))
        rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "amount_cents": row[1],
                "currency": row[2],
                "status": row[3],
                "period_start": row[4],
                "period_end": row[5],
                "invoice_url": row[6],
                "created_at": row[7]
            }
            for row in rows
        ]
    finally:
        conn.close()


# --- 批量处理端点 ---
@app.post("/batch-summarize")
async def batch_summarize(request: BatchSummarizeRequest):
    """批量处理多个视频URL，返回处理状态"""
    results = []
    
    for url in request.urls:
        # 检查缓存
        cached = get_cached_result(url, request.mode, request.focus)
        if cached:
            results.append({
                "url": url,
                "status": "cached",
                "summary": cached["summary"][:200] + "..." if len(cached["summary"]) > 200 else cached["summary"],
                "cached": True
            })
        else:
            results.append({
                "url": url,
                "status": "pending",
                "cached": False
            })
    
    return {
        "total": len(request.urls),
        "cached_count": sum(1 for r in results if r.get("cached")),
        "pending_count": sum(1 for r in results if not r.get("cached")),
        "results": results
    }


# --- 缓存统计端点 ---
@app.get("/cache-stats")
async def cache_stats():
    """获取缓存统计信息"""
    stats = get_cache_stats()
    return stats


# --- API Key Management ---
class CreateKeyRequest(BaseModel):
    name: str

@app.post("/api/keys")
async def create_api_key(request: CreateKeyRequest, user: dict = Depends(get_current_user)):
    """创建新的 API Key"""
    # 生成密钥
    raw_key = f"sk-bili-{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    prefix = raw_key[:15] + "..."
    key_id = secrets.token_urlsafe(16)
    
    # 存储到数据库
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO api_keys (id, user_id, name, prefix, key_hash)
            VALUES (?, ?, ?, ?, ?)
        """, (key_id, user["user_id"], request.name, prefix, key_hash))
        
        conn.commit()
        
        return {
            "id": key_id,
            "name": request.name,
            "key": raw_key,  # ⚠️ 仅返回一次
            "prefix": prefix,
            "created_at": datetime.now().isoformat()
        }
    finally:
        conn.close()

@app.get("/api/keys")
async def list_api_keys(user: dict = Depends(get_current_user)):
    """列出用户的所有 API Key"""
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, name, prefix, created_at, last_used_at, is_active
            FROM api_keys
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user["user_id"],))
        
        keys = []
        for row in cursor.fetchall():
            keys.append({
                "id": row[0],
                "name": row[1],
                "prefix": row[2],
                "created_at": row[3],
                "last_used_at": row[4],
                "is_active": bool(row[5])
            })
        
        return keys
    finally:
        conn.close()

@app.delete("/api/keys/{key_id}")
async def delete_api_key(key_id: str, user: dict = Depends(get_current_user)):
    """删除指定的 API Key"""
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    
    try:
        # 验证所有权并删除
        cursor.execute("""
            DELETE FROM api_keys
            WHERE id = ? AND user_id = ?
        """, (key_id, user["user_id"]))
        
        if cursor.rowcount == 0:
            raise HTTPException(404, "API key not found or unauthorized")
        
        conn.commit()
        return {"message": "API key deleted successfully"}
    finally:
        conn.close()


@app.get("/api/keys/usage")
async def get_api_key_usage(user: dict = Depends(get_current_user)):
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, name, prefix, last_used_at
            FROM api_keys
            WHERE user_id = ?
        """, (user["user_id"],))
        keys = cursor.fetchall()

        cursor.execute("""
            SELECT key_id, SUM(count)
            FROM api_key_usage_daily
            WHERE user_id = ?
            GROUP BY key_id
        """, (user["user_id"],))
        total_usage = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute("""
            SELECT key_id, SUM(count)
            FROM api_key_usage_daily
            WHERE user_id = ?
              AND date >= DATE('now', '-6 day')
            GROUP BY key_id
        """, (user["user_id"],))
        recent_usage = {row[0]: row[1] for row in cursor.fetchall()}

        data = []
        for row in keys:
            key_id = row[0]
            data.append({
                "id": key_id,
                "name": row[1],
                "prefix": row[2],
                "last_used_at": row[3],
                "total_uses": int(total_usage.get(key_id, 0) or 0),
                "uses_7d": int(recent_usage.get(key_id, 0) or 0)
            })
        return data
    finally:
        conn.close()


@app.get("/api/invites")
async def get_invite_info(user: dict = Depends(get_current_user)):
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, code, created_at
            FROM invite_codes
            WHERE user_id = ?
        """, (user["user_id"],))
        row = cursor.fetchone()
        cursor.execute("""
            SELECT COUNT(*)
            FROM invite_redemptions
            WHERE inviter_id = ?
        """, (user["user_id"],))
        total = cursor.fetchone()[0]
        return {
            "code": row[1] if row else None,
            "created_at": row[2] if row else None,
            "total_redeemed": total
        }
    finally:
        conn.close()


@app.post("/api/invites")
async def create_invite_code(user: dict = Depends(get_current_user)):
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT code FROM invite_codes WHERE user_id = ?
        """, (user["user_id"],))
        existing = cursor.fetchone()
        if existing:
            return {"code": existing[0]}
        invite_id = secrets.token_urlsafe(10)
        code = secrets.token_urlsafe(6)
        cursor.execute("""
            INSERT INTO invite_codes (id, user_id, code)
            VALUES (?, ?, ?)
        """, (invite_id, user["user_id"], code))
        conn.commit()
        return {"code": code}
    finally:
        conn.close()


@app.post("/api/invites/redeem")
async def redeem_invite(request: RedeemInviteRequest, user: dict = Depends(get_current_user)):
    invite_code = request.code.strip()
    if not invite_code:
        raise HTTPException(400, "Invalid code")
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, user_id FROM invite_codes WHERE code = ?
        """, (invite_code,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(404, "Invite code not found")
        invite_id, inviter_id = row
        if inviter_id == user["user_id"]:
            raise HTTPException(400, "Cannot redeem your own code")
        cursor.execute("""
            SELECT 1 FROM invite_redemptions WHERE invitee_id = ?
        """, (user["user_id"],))
        if cursor.fetchone():
            raise HTTPException(400, "Invite already redeemed")
        ensure_user_credits(inviter_id)
        ensure_user_credits(user["user_id"])
        redemption_id = secrets.token_urlsafe(12)
        cursor.execute("""
            INSERT INTO invite_redemptions (id, invite_id, inviter_id, invitee_id)
            VALUES (?, ?, ?, ?)
        """, (redemption_id, invite_id, inviter_id, user["user_id"]))
        # Reward both sides
        cursor.execute("""
            UPDATE user_credits
            SET credits = credits + 10,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (inviter_id,))
        cursor.execute("""
            UPDATE user_credits
            SET credits = credits + 10,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (user["user_id"],))
        cursor.execute("""
            INSERT INTO credit_events (user_id, event_type, cost)
            VALUES (?, ?, ?)
        """, (inviter_id, "invite_reward", 0))
        cursor.execute("""
            INSERT INTO credit_events (user_id, event_type, cost)
            VALUES (?, ?, ?)
        """, (user["user_id"], "invite_redeem", 0))
        conn.commit()
        return {"message": "Redeemed", "reward": 10}
    finally:
        conn.close()


@app.post("/api/share")
async def create_share_link(request: ShareRequest, user: dict = Depends(get_current_user)):
    share_id = secrets.token_urlsafe(10)
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO share_links (id, user_id, title, summary, transcript, mindmap)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (share_id, user["user_id"], request.title, request.summary, request.transcript, request.mindmap))
        conn.commit()
        return {
            "share_id": share_id,
            "share_url": f"/share/{share_id}"
        }
    finally:
        conn.close()


@app.get("/api/share/{share_id}")
async def get_share_link(share_id: str):
    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT title, summary, transcript, mindmap, created_at
            FROM share_links
            WHERE id = ?
        """, (share_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(404, "Share link not found")
        return {
            "title": row[0],
            "summary": row[1],
            "transcript": row[2],
            "mindmap": row[3],
            "created_at": row[4]
        }
    finally:
        conn.close()


@app.get("/share/{share_id}")
async def render_share_link(share_id: str):
    data = await get_share_link(share_id)
    import html as html_lib
    title = html_lib.escape(data.get("title") or "分享内容")
    summary = html_lib.escape(data.get("summary") or "")
    transcript = html_lib.escape(data.get("transcript") or "")
    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{title}</title>
        <style>
          body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 24px; background: #f9fafb; color: #111827; }}
          .card {{ max-width: 820px; margin: 0 auto; background: white; padding: 24px; border-radius: 16px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08); }}
          h1 {{ font-size: 22px; margin-bottom: 12px; }}
          pre {{ white-space: pre-wrap; word-break: break-word; font-size: 14px; line-height: 1.7; background: #f3f4f6; padding: 16px; border-radius: 12px; }}
          .section {{ margin-top: 20px; }}
          .label {{ font-size: 12px; text-transform: uppercase; letter-spacing: 0.2em; color: #6b7280; }}
        </style>
      </head>
      <body>
        <div class="card">
          <div class="label">Bili-Summarizer 分享</div>
          <h1>{title}</h1>
          <div class="section">
            <div class="label">总结</div>
            <pre>{summary}</pre>
          </div>
          <div class="section">
            <div class="label">转录</div>
            <pre>{transcript or '暂无转录'}</pre>
          </div>
        </div>
      </body>
    </html>
    """
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html)



# --- Video Info Endpoint ---
class VideoInfoRequest(BaseModel):
    url: str

@app.post("/video-info")
async def get_video_info(request: VideoInfoRequest):
    """Fetch video metadata (title, thumbnail) from Bilibili."""
    import re
    import yt_dlp
    
    try:
        # Extract video info without downloading
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=False)
            
            # Get thumbnail URL and convert to proxy URL
            thumbnail_url = info.get("thumbnail", "")
            if thumbnail_url:
                # Encode the URL for proxy
                import urllib.parse
                encoded_url = urllib.parse.quote(thumbnail_url, safe='')
                thumbnail_url = f"/proxy-image?url={encoded_url}"
            
            return {
                "title": info.get("title", "未知标题"),
                "thumbnail": thumbnail_url,
                "duration": info.get("duration", 0),
                "uploader": info.get("uploader", "未知作者"),
                "view_count": info.get("view_count", 0),
            }
    except Exception as e:
        logger.error(f"获取视频信息失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# --- Image Proxy Endpoint (Bypass Bilibili Referer Check) ---
@app.get("/proxy-image")
async def proxy_image(url: str):
    """Proxy image requests to bypass Bilibili's Referer protection."""
    import httpx
    import urllib.parse
    
    try:
        decoded_url = urllib.parse.unquote(url)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                decoded_url,
                headers={
                    "Referer": "https://www.bilibili.com/",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                },
                follow_redirects=True,
                timeout=10.0
            )
            
            if response.status_code == 200:
                from fastapi.responses import Response
                content_type = response.headers.get("content-type", "image/jpeg")
                return Response(
                    content=response.content,
                    media_type=content_type,
                    headers={"Cache-Control": "public, max-age=86400"}  # Cache for 1 day
                )
            else:
                raise HTTPException(status_code=response.status_code, detail="Image fetch failed")
    except Exception as e:
        logger.error(f"图片代理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- AI Chat / Follow-up Endpoint (Legacy) ---
class ChatSimpleRequest(BaseModel):
    question: str
    context: str  # The summary text to use as context

@app.post("/chat")
async def chat_with_ai(request: ChatSimpleRequest):
    """Answer follow-up questions based on the video summary context."""
    import google.generativeai as genai
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API Key not configured")
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")
        
        prompt = f"""你是一个视频内容助手。用户已经观看了一个视频，以下是该视频的总结内容：

---
{request.context}
---

现在用户有一个问题，请基于上述视频内容回答。如果问题超出了视频范围，请礼貌地说明。

用户问题: {request.question}

请用简洁、友好的中文回答："""
        
        response = model.generate_content(prompt, request_options={"timeout": 60})
        
        if not response.parts:
            raise HTTPException(status_code=500, detail="AI 未能生成回复")
        
        return {
            "answer": response.text,
            "usage": {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
            }
        }
    except Exception as e:
        logger.error(f"AI Chat 失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- PPT Generation Endpoint ---
from .ppt_generator import PPTGenerator
from .summarizer_gemini import generate_ppt_structure
from urllib.parse import quote

class PPTRequest(BaseModel):
    summary: str

@app.post("/generate-ppt")
async def generate_ppt_endpoint(request: PPTRequest):
    """
    Generate a PPT file from the summary content.
    """
    logger.info("Generating PPT...")
    try:
        # 1. Use AI to structure the JSON
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        ppt_json = await loop.run_in_executor(None, generate_ppt_structure, request.summary)
        
        logger.info("PPT Structure Generated successfully.")

        # 2. Generate PPT bytes
        generator = PPTGenerator()
        ppt_file = await loop.run_in_executor(None, generator.generate_from_json, ppt_json)
        
        # 3. Return as downloadable file
        filename = f"bili-ppt-{int(datetime.now().timestamp())}.pptx"
        
        # Configure headers for file download
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
        
        return StreamingResponse(
            ppt_file, 
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers=headers
        )
        
    except Exception as e:
        logger.error(f"PPT generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- AI Chat Endpoint ---
@app.post("/api/chat")
async def chat_with_ai(request: ChatRequest):
    """基于视频内容的 AI 追问"""
    try:
        # 构建上下文
        context = f"""你是一个视频内容分析专家。用户正在基于以下视频信息提问：

【视频总结】
{request.summary}

【转录内容（节选）】
{request.transcript[:5000] if request.transcript else '（无转录内容）'}

请基于以上内容回答用户的问题。如果问题涉及视频中没有提到的内容,请明确说明。保持回答简洁准确。"""

        # 组装消息
        messages = [
            {"role": "user", "parts": [context]},
            {"role": "model", "parts": ["我已了解视频内容，请问有什么问题？"]},
        ]
        
        for msg in request.history:
            messages.append({
                "role": "user" if msg.role == "user" else "model",
                "parts": [msg.content]
            })
        
        messages.append({"role": "user", "parts": [request.question]})
        
        async def event_stream():
            try:
                import google.generativeai as genai
                model = genai.GenerativeModel("models/gemini-2.0-flash-exp")
                
                response = model.generate_content(
                    messages,
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 2048,
                    },
                    stream=True
                )
                
                for chunk in response:
                    if chunk.text:
                        yield f"data: {json.dumps({'content': chunk.text}, ensure_ascii=False)}\n\n"
                
                yield f"data: {json.dumps({'done': True})}\n\n"
                
            except Exception as e:
                logger.error(f"Chat error: {e}")
                yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
    
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# --- History Sync API ---
@app.get("/api/history")
async def get_user_history(user: dict = Depends(get_current_user)):
    """获取用户的云端历史记录"""
    try:
        from supabase import create_client
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            logger.warning("Supabase not configured, returning empty history")
            return []
        
        supabase = create_client(supabase_url, supabase_key)
        
        response = supabase.table("summaries")\
            .select("*")\
            .eq("user_id", user["user_id"])\
            .order("created_at", desc=True)\
            .limit(50)\
            .execute()
        
        return response.data
    
    except Exception as e:
        logger.error(f"Get history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/history")
async def sync_history(
    items: List[HistoryItem],
    user: dict = Depends(get_current_user)
):
    """批量上传本地历史到云端"""
    try:
        from supabase import create_client
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            return {"uploaded": 0, "total": len(items), "error": "Supabase not configured"}
        
        supabase = create_client(supabase_url, supabase_key)
        
        uploaded = 0
        errors = []
        
        for item in items:
            try:
                data = item.dict(exclude_none=True, exclude={"id"})
                data["user_id"] = user["user_id"]
                
                supabase.table("summaries").upsert(data).execute()
                uploaded += 1
            except Exception as e:
                logger.error(f"Sync error for {item.video_url}: {e}")
                errors.append(str(e))
        
        return {
            "uploaded": uploaded,
            "total": len(items),
            "errors": errors if errors else None
        }
    
    except Exception as e:
        logger.error(f"Batch sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/history/{history_id}")
async def delete_history_item(
    history_id: str,
    user: dict = Depends(get_current_user)
):
    """删除云端历史记录"""
    try:
        from supabase import create_client
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            raise HTTPException(503, "Supabase not configured")
        
        supabase = create_client(supabase_url, supabase_key)
        
        response = supabase.table("summaries")\
            .delete()\
            .eq("id", history_id)\
            .eq("user_id", user["user_id"])\
            .execute()
        
        return {"message": "History item deleted"}
    
    except Exception as e:
        logger.error(f"Delete history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Frontend Static (Render) ---
if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/", include_in_schema=False)
    async def serve_frontend_root():
        return FileResponse(FRONTEND_DIST / "index.html")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend_spa(full_path: str):
        candidate = FRONTEND_DIST / full_path
        if candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(FRONTEND_DIST / "index.html")
elif LEGACY_INDEX.exists():
    @app.get("/", include_in_schema=False)
    async def serve_legacy_root():
        return FileResponse(LEGACY_INDEX)
