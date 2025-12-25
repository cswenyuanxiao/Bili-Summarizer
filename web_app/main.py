import os
import sys
import json
import asyncio
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, Security, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Ensure local env vars (.env) are available before auth/client setup.
load_dotenv()

# Import startup initialization
from .startup import init_core_tables as startup_init_core_tables

# --- 数据模型（已迁移到 schemas/）---
from .schemas import (
    # Summarize
    SummarizeRequest,
    BatchSummarizeRequest,
    HistoryItem,
    # Chat
    ChatMessage,
    ChatRequest,
    ChatSimpleRequest,
    # Payment
    PaymentRequest,
    PlanSubscribeRequest,
    RedeemInviteRequest,
    # Share
    ShareRequest,
    ShareCardRequest,
    # Video
    VideoInfoRequest,
    PPTRequest,
    # Feedback
    FeedbackRequest,
    # V2
    FavoritesImportRequest,
    TemplateCreateRequest,
    TemplateUpdateRequest,
    TTSRequest,
    UPSubscribeRequest,
    PushSubscriptionRequest,
    CompareRequest,
    CompareDirectRequest,
    TeamCreateRequest,
    TeamShareRequest,
    CommentCreateRequest,
)

# --- web_app 内部模块导入 ---
from .downloader import download_content
from .summarizer_gemini import summarize_content, extract_ai_transcript, upload_to_gemini, delete_gemini_file
from .cache import get_cached_result, save_to_cache, get_cache_stats, init_cache_db
from .queue_manager import task_queue
from .rate_limiter import rate_limiter
from .auth import get_current_user, verify_session_token
from .credits import ensure_user_credits, get_user_credits, charge_user_credits, get_daily_usage, grant_credits, get_credit_history, init_credits_db
from .payments import (
    create_alipay_payment,
    create_wechat_payment,
    verify_alipay_notify,
    verify_wechat_signature,
    parse_wechat_notification,
    create_payment_order,
    update_order_status,
    deliver_order,
    OrderStatus
)
from .idempotency import idempotency
from .reconciliation import reconciliation
from .batch_summarize import batch_service
from .share_card import generate_share_card, get_card_image, cleanup_expired_cards
from .favorites import parse_favorites_url, fetch_favorites_info, fetch_favorites_videos, fetch_all_favorites_videos
from .templates import get_user_templates, get_template_by_id, create_template, update_template, delete_template
from .tts import generate_tts, cleanup_expired_tts, VOICES
from .subscriptions import search_up, subscribe_up, unsubscribe_up, get_user_subscriptions
from .notifications import save_push_subscription
from .scheduler import start_scheduler, stop_scheduler
from .compare import compare_summaries, get_summaries_for_compare
from .teams import (
    create_team, get_user_teams, get_team_details, 
    share_summary_to_team, add_comment, get_summary_comments
)
from .telemetry import record_failure, init_telemetry_db
from typing import List
from .db import get_connection, get_backend_info, using_postgres
from io import BytesIO
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

# 导入配置常量
from .config import ADMIN_EMAILS, PRICING_PLANS, VOICES

def is_unlimited_user(user: Optional[dict]) -> bool:
    if not user:
        return False
    email = (user.get("email") or "").lower()
    return email in ADMIN_EMAILS




# --- 初始化 ---
app = FastAPI(title="Bili-Summarizer")

# --- 注册模块化路由 (health router 必须首先注册，不依赖 DB) ---
from .routers import register_routers
register_routers(app)

# --- 数据库初始化 ---
@app.on_event("startup")
async def on_startup():
    """启动项集合"""
    async def init_db_with_retry(name: str, init_fn):
        for attempt in range(1, 6):
            try:
                if asyncio.iscoroutinefunction(init_fn):
                    await init_fn()
                else:
                    init_fn()
                logger.info(f"{name} initialized")
                return
            except Exception as exc:
                logger.warning(f"{name} init failed (attempt {attempt}/5): {exc}")
                await asyncio.sleep(min(2 ** (attempt - 1), 10))
        logger.error(f"{name} init failed after retries; service may be degraded")

    # 表初始化（允许失败并重试，避免启动崩溃）
    from .startup.db_init import init_core_tables, init_all_databases
    from .cache import init_cache_db
    from .credits import init_credits_db
    from .telemetry import init_telemetry_db

    asyncio.create_task(init_db_with_retry("Core DB", init_core_tables))
    asyncio.create_task(init_db_with_retry("Cache DB", init_cache_db))
    asyncio.create_task(init_db_with_retry("Credits DB", init_credits_db))
    asyncio.create_task(init_db_with_retry("Telemetry DB", init_telemetry_db))
    
    # 周期性清理任务
    async def schedule_cleanups():
        while True:
            await asyncio.sleep(3600)  # 每小时运行一次
            cleanup_expired_cards()
            cleanup_expired_tts()
            
    asyncio.create_task(schedule_cleanups())
    
    # 启动定时任务调度器 (P4 每日推送到订阅)
    start_scheduler()

@app.on_event("startup")
async def start_queue():
    """启动后台任务队列并注册处理器"""
    import functools
    
    async def summarize_handler(payload):
        """总结任务处理器 - 在线程池中执行同步函数"""
        loop = asyncio.get_event_loop()
        
        custom_prompt = None
        template_id = payload.get('template_id')
        if template_id:
            from .templates import get_template_by_id
            template = get_template_by_id(template_id)
            if template:
                custom_prompt = template.get('prompt_template')
        
        func = functools.partial(
            summarize_content,
            payload['file_path'],
            payload['media_type'],
            payload.get('progress_callback'),
            payload.get('focus', 'default'),
            payload.get('uploaded_file'),
            custom_prompt
        )
        return await loop.run_in_executor(None, func)
    
    task_queue.register_handler('summarize', summarize_handler)
    
    async def transcript_handler(payload):
        """转录任务处理器 - 在线程池中执行同步函数"""
        loop = asyncio.get_event_loop()
        func = functools.partial(
            extract_ai_transcript,
            payload['file_path'],
            payload.get('progress_callback'),
            payload.get('uploaded_file')
        )
        return await loop.run_in_executor(None, func)
    
    task_queue.register_handler('transcript', transcript_handler)


    await task_queue.start()

@app.on_event("shutdown")
async def shutdown_queue():
    """停止后台任务队列"""
    await task_queue.stop()

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
# 确保目录存在（CI 环境可能没有）
videos_dir = Path("videos")
videos_dir.mkdir(exist_ok=True)
app.mount("/videos", StaticFiles(directory=str(videos_dir)), name="videos")
legacy_static = Path(__file__).resolve().parent / "legacy_ui" / "static"
if legacy_static.exists():
    app.mount("/static", StaticFiles(directory=str(legacy_static)), name="static")

# TTS 静态文件支持
tts_static = Path(__file__).resolve().parent / "static" / "tts"
tts_static.mkdir(parents=True, exist_ok=True)
app.mount("/api/tts/audio", StaticFiles(directory=str(tts_static)), name="tts_audio")

# --- Frontend Static (Render) ---
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
LEGACY_INDEX = Path(__file__).resolve().parent / "legacy_ui" / "index.html"

# --- 健康检查路由 ---
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Bili-Summarizer API"}

# --- Runtime config for frontend (Render) ---
@app.get("/config.js", include_in_schema=False)
async def frontend_config():
    config = {
        "VITE_SUPABASE_URL": os.getenv("VITE_SUPABASE_URL", ""),
        "VITE_SUPABASE_ANON_KEY": os.getenv("VITE_SUPABASE_ANON_KEY", "")
    }
    payload = f"window.__APP_CONFIG__ = {json.dumps(config)};"
    return Response(content=payload, media_type="application/javascript")

# --- 核心业务路由 ---

# 模型已迁移到 schemas/summarize.py

@app.get("/summarize")
async def run_summarization(
    url: str,
    mode: str = "smart",
    focus: str = "default",
    skip_cache: bool = False,
    token: Optional[str] = None,
    template_id: Optional[str] = None
):
    safe_url = url.split("?")[0]
    logger.info(f"收到总结请求: URL={safe_url}, Mode={mode}, Focus={focus}")

    async def event_generator():
        video_path = None
        remote_file = None
        user = None
        unlimited_user = False
        credit_cost = 10
        
        try:
            if not token:
                record_failure(None, "AUTH_REQUIRED", "auth", "missing token")
                yield f"data: {json.dumps({'type': 'error', 'code': 'AUTH_REQUIRED', 'error': '请先登录再使用该功能'})}\n\n"
                return
            try:
                user = await verify_session_token(token)
                
                # 频率限制
                if user:
                    if not await rate_limiter.acquire(user["user_id"]):
                        wait_time = rate_limiter.get_wait_time(user["user_id"])
                        record_failure(user["user_id"], "RATE_LIMITED", "quota", f"wait {wait_time:.1f}s")
                        yield f"data: {json.dumps({'type': 'error', 'code': 'RATE_LIMITED', 'error': f'请求过于频繁，请等待 {wait_time:.0f} 秒后重试'})}\n\n"
                        return

                ensure_user_credits(user["user_id"])
                unlimited_user = is_unlimited_user(user) or is_subscription_active(user["user_id"])
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

            if user and not unlimited_user:
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
            async def summary_via_queue():
                task_id = await task_queue.submit('summarize', {
                    'file_path': video_path,
                    'media_type': media_type,
                    'progress_callback': progress_callback,
                    'focus': focus,
                    'uploaded_file': remote_file,
                    'template_id': template_id
                })
                # 轮询任务状态 (或者可以使用更复杂的事件通知机制)
                from .queue_manager import TaskStatus
                while True:
                    task = task_queue.get_task_status(task_id)
                    if not task: raise Exception("Task disappeared")
                    if task.status == TaskStatus.COMPLETED:
                        return task.result
                    if task.status == TaskStatus.FAILED:
                        raise Exception(task.error)
                    await asyncio.sleep(0.5)

            asyncio.create_task(task_wrapper('summary', summary_via_queue()))
            active_tasks += 1

            # Task B: Transcript (if needed)
            need_transcript = (not transcript and media_type in ['audio', 'video'])
            transcript_task_started = False
            if need_transcript:
                async def transcript_via_queue():
                    task_id = await task_queue.submit('transcript', {
                        'file_path': video_path,
                        'progress_callback': progress_callback,
                        'uploaded_file': remote_file
                    })
                    from .queue_manager import TaskStatus
                    while True:
                        task = task_queue.get_task_status(task_id)
                        if not task: raise Exception("Task disappeared")
                        if task.status == TaskStatus.COMPLETED:
                            return task.result
                        if task.status == TaskStatus.FAILED:
                            raise Exception(task.error)
                        await asyncio.sleep(0.5)

                asyncio.create_task(task_wrapper('transcript', transcript_via_queue()))
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
                 if user and not unlimited_user:
                     charge_user_credits(user["user_id"], credit_cost, metadata=json.dumps({"url": safe_url}))
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


@app.get("/api/summarize")
async def run_summarization_api(
    url: str,
    mode: str = "smart",
    focus: str = "default",
    skip_cache: bool = False,
    token: Optional[str] = None,
    template_id: Optional[str] = None
):
    return await run_summarization(url, mode, focus, skip_cache, token, template_id)


@app.get("/api/dashboard")
async def get_dashboard(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    credits = ensure_user_credits(user["user_id"])
    usage = get_daily_usage(user["user_id"])
    history = get_credit_history(user["user_id"])
    
    return {
        "credits": credits["credits"],
        "total_used": credits["total_used"],
        "usage_history": usage,
        "credit_history": history,
        "is_admin": is_unlimited_user(user),
        "cost_per_summary": 10
    }


@app.get("/api/billing/{billing_id}/invoice")
async def download_invoice(billing_id: str, user: dict = Depends(get_current_user)):
    conn = get_connection()
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
    conn = get_connection()
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


@app.post("/api/batch-summarize")
async def batch_summarize_api(request: BatchSummarizeRequest):
    return await batch_summarize(request)


# --- 缓存统计端点 ---
@app.get("/cache-stats")
async def cache_stats():
    """获取缓存统计信息"""
    stats = get_cache_stats()
    return stats


@app.get("/api/cache-stats")
async def cache_stats_api():
    return await cache_stats()


# API Keys 端点已迁移到 routers/api_keys.py


# Invite 端点已迁移到 routers/invite.py


@app.post("/api/share")
async def create_share_link(request: ShareRequest, user: dict = Depends(get_current_user)):
    share_id = secrets.token_urlsafe(10)
    conn = get_connection()
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
    conn = get_connection()
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


# Feedback 端点已迁移到 routers/feedback.py


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
# 模型已迁移到 schemas/video.py

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


@app.post("/api/video-info")
async def get_video_info_api(request: VideoInfoRequest):
    return await get_video_info(request)


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


@app.get("/api/proxy-image")
async def proxy_image_api(url: str):
    return await proxy_image(url)


# --- AI Chat / Follow-up Endpoint (Legacy) ---
# 模型已迁移到 schemas/chat.py

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

# 模型已迁移到 schemas/video.py

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


# AI Chat 端点保留在 main.py (Phase 2 跳过)
# History 端点已迁移到 routers/history.py


@app.post("/api/admin/reconciliation")
async def run_reconciliation(
    request: Request,
    auto_fix: bool = False
):
    """执行对账（仅管理员）"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    if not is_unlimited_user(user):
        raise HTTPException(status_code=403, detail="Admin only")
    
    result = reconciliation.run_full_reconciliation(auto_fix=auto_fix)
    
    return {
        "success": result.success,
        "checked_count": result.checked_count,
        "issues": result.issues,
        "fixed_count": result.fixed_count,
        "summary": result.summary
    }

# ============ 批量总结端点 ============

@app.post("/api/batch/summarize")
async def create_batch_summarize(
    request: Request,
    body: BatchSummarizeRequest
):
    """创建批量总结任务"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    # 积分校验：每个视频固定消耗 10 积分
    required_credits = len(body.urls) * 10
    credits_data = get_user_credits(user["user_id"])
    
    if not is_unlimited_user(user) and (not credits_data or credits_data["credits"] < required_credits):
        raise HTTPException(
            status_code=402,
            detail=f"余额不足。此批次需要 {required_credits} 积分，当前余额为 {credits_data['credits'] if credits_data else 0}。"
        )
    
    try:
        job_id = await batch_service.create_batch(
            user_id=user["user_id"],
            urls=body.urls,
            mode=body.mode,
            focus=body.focus
        )
        
        # 预扣积分
        if not is_unlimited_user(user):
            charge_user_credits(user["user_id"], required_credits)
            
        return {
            "job_id": job_id,
            "count": len(body.urls),
            "credits_charged": required_credits if not is_unlimited_user(user) else 0
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/batch/{job_id}")
async def get_batch_job_status(job_id: str, request: Request):
    """获取批量任务状态和结果"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    job = batch_service.get_job_status(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Batch job not found")
    
    # 权限校验
    if job.user_id != user["user_id"] and not is_unlimited_user(user):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "job_id": job.id,
        "status": job.status.value,
        "progress": job.progress,
        "total": len(job.urls),
        "completed_count": len(job.results),
        "failed_count": len(job.errors),
        "results": job.results if job.status.value in ["completed", "partial"] else {},
        "errors": job.errors,
        "created_at": job.created_at,
        "completed_at": job.completed_at
    }



# --- Frontend Static (Render) ---
# NOTE: Frontend serving code moved to end of file to avoid interfering with API routes
# if FRONTEND_DIST.exists():
#     assets_dir = FRONTEND_DIST / "assets"
#     if assets_dir.exists():
#         app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
#
#     @app.get("/", include_in_schema=False)
#     async def serve_frontend_root():
#         return FileResponse(FRONTEND_DIST / "index.html")
#
#     @app.get("/{full_path:path}", include_in_schema=False)
#     async def serve_frontend_spa(full_path: str):
#         # 不要拦截 API 路由和其他后端路由
#         if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
#             # 这些路径应该由后端处理，如果到这里说明路由不存在
#             raise HTTPException(status_code=404, detail="Not found")
#         
#         candidate = FRONTEND_DIST / full_path
#         if candidate.is_file():
#             return FileResponse(candidate)
#         return FileResponse(FRONTEND_DIST / "index.html")
# elif LEGACY_INDEX.exists():
#     @app.get("/", include_in_schema=False)
#     async def serve_legacy_root():
#         return FileResponse(LEGACY_INDEX)

# === 分享卡片相关 ===

@app.post("/api/share/card")
async def create_share_card(request: Request, body: ShareCardRequest):
    """
    生成分享卡片
    """
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    # 尝试验证用户，但如果不成功也允许（支持匿名分享）
    try:
        user = await verify_session_token(token)
    except:
        user = None
    
    # 验证模板
    if body.template not in ["default", "dark", "gradient", "minimal"]:
        raise HTTPException(status_code=400, detail="Invalid template")
    
    try:
        # 在主线程外运行耗时的渲染操作
        result = await asyncio.to_thread(
            generate_share_card,
            title=body.title,
            summary=body.summary,
            thumbnail_url=body.thumbnail_url,
            template=body.template
        )
        
        return {
            "card_id": result["card_id"],
            "image_url": result["image_url"],
            "expires_at": result["expires_at"]
        }
    except Exception as e:
        logger.error(f"Failed to generate share card: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/share/card/{card_id}.png")
async def get_share_card_image(card_id: str):
    """
    获取生成的分享卡片图片
    """
    image_path = get_card_image(card_id)
    
    if not image_path:
        raise HTTPException(status_code=404, detail="Card not found or expired")
    
    return FileResponse(
        image_path,
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=86400",
            "Content-Disposition": f"inline; filename={card_id}.png"
        }
    )

@app.on_event("startup")
async def schedule_cleanup():
    """
    启动时清理过期文件
    """
    cleanup_expired_cards()

# === 收藏夹导入相关 ===

@app.get("/api/favorites/info")
async def get_favorites_info_api(url: str):
    """获取收藏夹信息"""
    media_id = parse_favorites_url(url)
    if not media_id:
        raise HTTPException(status_code=400, detail="无效的收藏夹链接")
    
    try:
        info = await fetch_favorites_info(media_id)
        return info
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/favorites/videos")
async def get_favorites_videos_api(url: str, page: int = 1):
    """预览收藏夹视频列表"""
    media_id = parse_favorites_url(url)
    if not media_id:
        raise HTTPException(status_code=400, detail="无效的收藏夹链接")
    
    try:
        videos = await fetch_favorites_videos(media_id, page=page)
        return videos
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/favorites/import")
async def import_favorites_api(request: Request, body: FavoritesImportRequest):
    """
    导入收藏夹并开始批量总结
    """
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    media_id = parse_favorites_url(body.favorites_url)
    if not media_id:
        raise HTTPException(status_code=400, detail="无效的收藏夹链接")
    
    try:
        # 获取视频列表
        if body.selected_bvids:
            # 如果指定了某些视频
            urls = [f"https://www.bilibili.com/video/{bvid}" for bvid in body.selected_bvids]
        else:
            # 否则获取全部（按限制）
            videos = await fetch_all_favorites_videos(media_id, limit=body.limit)
            urls = [v["url"] for v in videos]
            
        if not urls:
            raise HTTPException(status_code=400, detail="没有可导入的视频")
            
        # 限制单次导入数量
        if len(urls) > 100:
            urls = urls[:100]
            
        # 计费检查
        cost_info = await get_backend_info()
        cost_per = cost_info.get("cost_per_summary", 10)
        required_credits = len(urls) * cost_per
        
        user_credits = await get_user_credits(user["user_id"])
        if user_credits < required_credits and not is_unlimited_user(user):
            raise HTTPException(status_code=402, detail=f"积分不足，需要 {required_credits}，当前 {user_credits}")
            
        # 创建批量任务
        job_id = await batch_service.create_batch(
            user_id=user["user_id"],
            urls=urls,
            mode=body.mode,
            focus=body.focus
        )
        
        # 扣除积分
        if not is_unlimited_user(user):
            await charge_user_credits(user["user_id"], required_credits, f"批量导入收藏夹任务: {job_id}")
            
        return {
            "job_id": job_id,
            "video_count": len(urls),
            "credits_charged": required_credits if not is_unlimited_user(user) else 0
        }
    except Exception as e:
        logger.error(f"Favorites import failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
# === 总结模板相关 ===

@app.get("/api/templates")
async def list_templates(request: Request):
    """获取用户可用的模板列表"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        user = await verify_session_token(token)
        user_id = user["user_id"]
    except:
        user_id = "anonymous"
    
    return get_user_templates(user_id)

@app.post("/api/templates")
async def add_template(request: Request, body: TemplateCreateRequest):
    """创建自定义模板"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    return create_template(
        user_id=user["user_id"],
        name=body.name,
        prompt_template=body.prompt_template,
        description=body.description,
        output_format=body.output_format,
        sections=body.sections
    )

@app.patch("/api/templates/{template_id}")
async def patch_template(request: Request, template_id: str, body: TemplateUpdateRequest):
    """更新自定义模板"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    success = update_template(
        template_id=template_id,
        user_id=user["user_id"],
        **body.dict(exclude_unset=True)
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Template not found or no permission")
        
    return {"status": "success"}

@app.delete("/api/templates/{template_id}")
async def remove_template(request: Request, template_id: str):
    """删除模板"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    success = delete_template(template_id, user["user_id"])
    if not success:
        raise HTTPException(status_code=404, detail="Template not found or no permission")
        
    return {"status": "success"}

# === 语音播报相关 ===

@app.get("/api/tts/voices")
async def list_voices():
    """获取支持的配音列表"""
    return VOICES

@app.post("/api/tts/generate")
async def tts_generate(request: Request, body: TTSRequest):
    """生成语音音频"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    # TTS 目前不需要强制登录，但可以记录用户行为
    try:
        user = await verify_session_token(token)
    except:
        user = None
        
    try:
        relative_path = await generate_tts(body.text, body.voice)
        # 转换为外部可访问的 URL
        audio_url = relative_path.replace("/static/tts/", "/api/tts/audio/")
        return {"audio_url": audio_url}
    except Exception as e:
        logger.error(f"TTS API failed: {e}")
        raise HTTPException(status_code=500, detail="Voice generation failed")

# === 订阅与推送相关 (P4) ===

@app.get("/api/subscriptions/search")
async def search_up_users(keyword: str):
    """搜索 UP 主"""
    if not keyword or len(keyword) < 2:
        return {"users": []}
    
    users = await search_up(keyword)
    return {"users": users}

@app.get("/api/subscriptions")
async def list_subscriptions(request: Request):
    """获取用户订阅列表"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    subscriptions = get_user_subscriptions(user["user_id"])
    return {"subscriptions": subscriptions}

@app.post("/api/subscriptions")
async def handle_up_subscribe(request: Request, body: UPSubscribeRequest):
    """订阅 UP 主"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    try:
        result = subscribe_up(
            user_id=user["user_id"],
            up_mid=body.up_mid,
            up_name=body.up_name,
            up_avatar=body.up_avatar,
            notify_methods=body.notify_methods
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/subscriptions/{subscription_id}")
async def cancel_subscription(subscription_id: str, request: Request):
    """取消订阅"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    success = unsubscribe_up(user["user_id"], subscription_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return {"message": "Unsubscribed"}

@app.post("/api/push/subscribe")
async def register_push_subscription(request: Request, body: PushSubscriptionRequest):
    """注册浏览器推送订阅"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    save_push_subscription(
        user_id=user["user_id"],
        endpoint=body.endpoint,
        p256dh=body.keys.get("p256dh", ""),
        auth=body.keys.get("auth", "")
    )
    
    return {"message": "Push subscription saved"}

@app.get("/api/push/vapid-key")
async def get_vapid_public_key():
    """获取 VAPID 公钥（用于浏览器订阅）"""
    return {"publicKey": os.getenv("VAPID_PUBLIC_KEY", "")}

# === 总结对比相关 (P5) ===

# 模型已迁移到 schemas/v2.py

@app.post("/api/compare")
async def compare_videos(request: Request, body: CompareRequest):
    """
    对比多个视频总结（使用历史记录 ID）
    """
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    
    if len(body.summary_ids) < 2:
        raise HTTPException(status_code=400, detail="至少需要 2 个视频进行对比")
    
    if len(body.summary_ids) > 4:
        raise HTTPException(status_code=400, detail="最多支持 4 个视频对比")
    
    # 获取总结内容
    summaries = get_summaries_for_compare(body.summary_ids, user["user_id"])
    
    if len(summaries) < 2:
        raise HTTPException(status_code=400, detail="找不到足够的总结内容")
    
    try:
        result = await compare_summaries(summaries, body.aspects)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Compare failed: {e}")
        raise HTTPException(status_code=500, detail="对比分析失败")

@app.post("/api/compare/direct")
async def compare_videos_direct(request: Request, body: CompareDirectRequest):
    """
    对比多个视频总结（直接传入内容）
    """
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    # 可选登录，但通常建议登录以记录额度或审计
    try:
        user = await verify_session_token(token)
    except:
        user = None
    
    if len(body.summaries) < 2:
        raise HTTPException(status_code=400, detail="至少需要 2 个视频进行对比")
    
    if len(body.summaries) > 4:
        raise HTTPException(status_code=400, detail="最多支持 4 个视频对比")
    
    try:
        result = await compare_summaries(body.summaries, body.aspects)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Compare failed: {e}")
        raise HTTPException(status_code=500, detail="对比分析失败")

# === 团队协作相关 (P6) ===

# 模型已迁移到 schemas/v2.py

@app.get("/api/teams")
async def list_teams(request: Request):
    """列出用户的团队"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    teams = get_user_teams(user["user_id"])
    return {"teams": teams}

@app.post("/api/teams")
async def handle_create_team(request: Request, body: TeamCreateRequest):
    """创建团队"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    team = create_team(body.name, user["user_id"], body.description)
    return team

@app.get("/api/teams/{team_id}")
async def fetch_team_details(team_id: str, request: Request):
    """获取团队详情"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    details = get_team_details(team_id, user["user_id"])
    if not details:
        raise HTTPException(status_code=403, detail="无权访问该团队")
    return details

@app.post("/api/teams/{team_id}/share")
async def handle_share_to_team(team_id: str, body: TeamShareRequest, request: Request):
    """分享总结到团队"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    success = share_summary_to_team(
        team_id=team_id,
        user_id=user["user_id"],
        title=body.title,
        video_url=body.video_url,
        summary_content=body.summary_content,
        video_thumbnail=body.video_thumbnail,
        transcript=body.transcript,
        mindmap=body.mindmap,
        tags=body.tags
    )
    if not success:
        raise HTTPException(status_code=400, detail="分享失败，请确认权限")
    return {"status": "success"}

@app.post("/api/teams/{team_id}/comments")
async def handle_add_comment(team_id: str, body: CommentCreateRequest, request: Request):
    """发表团队评论"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = await verify_session_token(token)
    comment = add_comment(body.team_summary_id, user["user_id"], body.content, body.parent_id)
    return comment

@app.get("/api/teams/{team_id}/summaries/{team_summary_id}/comments")
async def list_comments(team_id: str, team_summary_id: str, request: Request):
    """获取总结的所有评论"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    await verify_session_token(token)
    comments = get_summary_comments(team_summary_id)
    return {"comments": comments}


# --- SPA Serving (Must be last) ---

if FRONTEND_DIST.exists():
    # Mount /assets explicitly since index.html references /assets/...
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Exclude specific API/Docs paths to ensure 404s are returned for them
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi.json") or full_path.startswith("videos"):
            raise HTTPException(status_code=404, detail="Not Found")
        
        # Try to serve file directly (e.g. favicon.ico, robots.txt)
        target_file = FRONTEND_DIST / full_path
        if target_file.is_file():
            return FileResponse(target_file)
            
        # Fallback to index.html for known frontend routes
        index_file = FRONTEND_DIST / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        # Fallback if index.html is missing (should not happen in production)
        return JSONResponse(
            {"status": "ok", "message": "API is running, frontend not available"},
            status_code=200
        )

elif LEGACY_INDEX.exists():
    @app.get("/", include_in_schema=False)
    async def serve_legacy():
        return FileResponse(LEGACY_INDEX)
