import asyncio
import logging
from fastapi import FastAPI

from .queue_manager import task_queue
from .scheduler import start_scheduler
from .share_card import cleanup_expired_cards
from .tts import cleanup_expired_tts
from .summarizer_gemini import summarize_content, extract_ai_transcript

logger = logging.getLogger(__name__)


def register_lifecycle_events(app: FastAPI) -> None:
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

        async def run_blocking_init(name: str, init_fn):
            try:
                await asyncio.to_thread(init_fn)
                logger.info(f"{name} initialized")
            except Exception as exc:
                logger.error(f"{name} init failed: {exc}")

        async def delayed_start_scheduler():
            await asyncio.sleep(0.1)
            start_scheduler()

        async def delayed_register_legacy_routes():
            await asyncio.sleep(0.2)
            from .routers import include_legacy_routes
            include_legacy_routes(app)

        # 周期性清理任务
        async def schedule_cleanups():
            while True:
                await asyncio.sleep(3600)  # 每小时运行一次
                cleanup_expired_cards()
                cleanup_expired_tts()

        asyncio.create_task(schedule_cleanups())

        # 初始化收藏夹表
        try:
            from .init_favorites_table import init_favorites_table
            asyncio.create_task(run_blocking_init("Favorites table", init_favorites_table))
        except Exception as e:
            logger.error(f"Failed to initialize favorites table: {e}")

        # 初始化团队协作表
        try:
            from .init_teams_tables import init_teams_tables
            asyncio.create_task(run_blocking_init("Teams tables", init_teams_tables))
        except Exception as e:
            logger.error(f"Failed to initialize teams tables: {e}")

        # 启动定时任务调度器 (P4 每日推送到订阅)
        asyncio.create_task(delayed_start_scheduler())
        asyncio.create_task(delayed_register_legacy_routes())

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
                custom_prompt,
                payload.get('output_language', 'zh'),
                payload.get('enable_cot', False)
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

    @app.on_event("startup")
    async def schedule_cleanup():
        """启动时清理过期文件"""
        await asyncio.to_thread(cleanup_expired_cards)

    @app.on_event("shutdown")
    async def shutdown_queue():
        """停止后台任务队列"""
        await task_queue.stop()
