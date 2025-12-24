"""
定时任务调度器
"""
import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .subscriptions import get_all_subscriptions, get_up_latest_video, update_subscription_check
from .notifications import queue_notification, process_notification_queue

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def check_new_videos():
    """检查订阅 UP 主的新视频"""
    logger.info("Starting new video check...")
    
    subscriptions = get_all_subscriptions()
    new_videos_count = 0
    
    for sub in subscriptions:
        try:
            latest = await get_up_latest_video(sub["up_mid"])
            
            if not latest:
                continue
            
            # 检查是否是新视频
            if sub["last_video_bvid"] != latest["bvid"]:
                logger.info(f"New video found: {latest['title']} from {sub['up_name']}")
                
                # 更新订阅状态
                update_subscription_check(sub["id"], latest["bvid"])
                
                # 如果是首次检查（last_video_bvid 为空），标记但不发送通知，避免瞬间触发一堆旧视频通知
                if sub["last_video_bvid"]:
                    # 加入通知队列
                    await queue_notification(
                        user_id=sub["user_id"],
                        notification_type="new_video",
                        title=f"{sub['up_name']} 发布了新视频",
                        body=latest["title"],
                        payload={
                            "video_url": latest["url"],
                            "video_bvid": latest["bvid"],
                            "video_title": latest["title"],
                            "video_cover": latest["cover"],
                            "up_name": sub["up_name"]
                        },
                        methods=sub.get("notify_methods", ["browser"])
                    )
                    new_videos_count += 1
            
        except Exception as e:
            logger.error(f"Error checking UP {sub['up_mid']}: {e}")
        
        # 添加间隔，避免请求过快被 B 站封锁
        await asyncio.sleep(2)
    
    logger.info(f"Video check completed. Found {new_videos_count} new videos.")


def start_scheduler():
    """启动调度器"""
    # 每小时检查一次新视频
    scheduler.add_job(
        check_new_videos,
        trigger=IntervalTrigger(hours=1),
        id="check_new_videos",
        replace_existing=True,
        next_run_time=datetime.now()
    )
    
    # 每 5 分钟处理一次通知队列
    scheduler.add_job(
        process_notification_queue,
        trigger=IntervalTrigger(minutes=5),
        id="process_notification_queue",
        replace_existing=True
    )
    
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")


def stop_scheduler():
    """停止调度器"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
