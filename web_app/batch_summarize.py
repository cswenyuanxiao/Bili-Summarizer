"""
批量总结服务
支持多视频并发处理
"""
import asyncio
import uuid
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class BatchStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"  # 部分成功
    FAILED = "failed"

@dataclass
class BatchJob:
    id: str
    user_id: str
    urls: List[str]
    mode: str
    focus: str
    status: BatchStatus = BatchStatus.PENDING
    results: Dict[str, Any] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    progress: int = 0  # 0-100

class BatchSummarizeService:
    def __init__(self, max_concurrent: int = 2):
        self.jobs: Dict[str, BatchJob] = {}
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def create_batch(
        self,
        user_id: str,
        urls: List[str],
        mode: str = "smart",
        focus: str = "default"
    ) -> str:
        """创建批量对任务"""
        if len(urls) > 20:
            raise ValueError("单个批次最多支持 20 个 URL")
        
        job_id = f"BATCH_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        job = BatchJob(
            id=job_id,
            user_id=user_id,
            urls=urls,
            mode=mode,
            focus=focus
        )
        
        self.jobs[job_id] = job
        
        # 启动异步后台处理
        asyncio.create_task(self._process_batch(job))
        
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[BatchJob]:
        """获取任务状态"""
        return self.jobs.get(job_id)
    
    async def _process_batch(self, job: BatchJob):
        """核心处理循环"""
        job.status = BatchStatus.RUNNING
        total = len(job.urls)
        completed = 0
        
        async def process_single(url: str):
            nonlocal completed
            async with self.semaphore:
                try:
                    # 调用单个总结逻辑
                    result = await self._summarize_single(url, job.mode, job.focus)
                    job.results[url] = result
                except Exception as e:
                    logger.error(f"Batch item failed: {url} - {e}")
                    job.errors[url] = str(e)
                finally:
                    completed += 1
                    job.progress = int(completed / total * 100)
        
        # 并发执行
        await asyncio.gather(*[process_single(url) for url in job.urls])
        
        # 设置完成状态
        job.completed_at = time.time()
        if len(job.results) == total:
            job.status = BatchStatus.COMPLETED
        elif len(job.results) > 0:
            job.status = BatchStatus.PARTIAL
        else:
            job.status = BatchStatus.FAILED
            
        logger.info(f"BatchJob {job.id} completed. Success: {len(job.results)}, Fail: {len(job.errors)}")

    async def _summarize_single(self, url: str, mode: str, focus: str) -> Dict[str, Any]:
        """执行单次总结的完整链路"""
        # 注意：这里我们尽量重用 main.py/queue_manager 的逻辑
        # 为了避免循环依赖和冗余代码，我们直接调用底层的实现函数
        from .downloader import download_content
        from .summarizer_gemini import summarize_content, extract_ai_transcript, upload_to_gemini
        from .cache import save_to_cache  # 添加缓存导入
        
        loop = asyncio.get_event_loop()
        
        # 1. 下载 (同步函数转异步)
        video_path, media_type, transcript = await loop.run_in_executor(
            None, download_content, url, mode
        )
        
        # 2. 上传 Gemini
        remote_file = None
        if media_type in ['video', 'audio']:
            remote_file = await loop.run_in_executor(
                None, upload_to_gemini, video_path, None
            )
        
        # 3. 总结
        summary = await loop.run_in_executor(
            None, summarize_content, video_path, media_type, None, focus, remote_file
        )
        
        # 4. 转录 (如果需要)
        if not transcript and media_type in ['audio', 'video']:
            transcript = await loop.run_in_executor(
                None, extract_ai_transcript, video_path, None, remote_file
            )
        
        # 5. 保存到缓存/历史记录（关键！）
        # 注意：summary 是元组 (summary_text, usage_dict)
        if isinstance(summary, tuple):
            summary_text, usage = summary
        else:
            summary_text = summary
            usage = None
        
        # 保存到 cache 表（会自动成为历史记录）
        save_to_cache(url, mode, focus, summary_text, transcript or '', usage)
            
        return {
            "summary": summary_text,
            "transcript": transcript,
            "url": url
        }

batch_service = BatchSummarizeService(max_concurrent=2)
