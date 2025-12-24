"""
任务队列管理器
使用 asyncio.Queue 实现轻量级任务队列
"""
import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Task:
    id: str
    task_type: str  # 'summarize', 'transcript', 'ppt'
    payload: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3

class TaskQueue:
    def __init__(self, max_workers: int = 3, max_queue_size: int = 100):
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self.tasks: Dict[str, Task] = {}
        self.max_workers = max_workers
        self.workers: list = []
        self.running = False
        self.handlers: Dict[str, Callable] = {}
    
    def register_handler(self, task_type: str, handler: Callable):
        """注册任务处理器"""
        self.handlers[task_type] = handler
    
    async def submit(self, task_type: str, payload: Dict[str, Any]) -> str:
        """提交任务，返回任务ID"""
        task_id = str(uuid.uuid4())
        task = Task(id=task_id, task_type=task_type, payload=payload)
        self.tasks[task_id] = task
        
        try:
            await asyncio.wait_for(
                self.queue.put(task),
                timeout=5.0
            )
            logger.info(f"Task {task_id} submitted: {task_type}")
            return task_id
        except asyncio.TimeoutError:
            task.status = TaskStatus.FAILED
            task.error = "Queue full, please try again later"
            raise Exception("Task queue is full")
    
    def get_task_status(self, task_id: str) -> Optional[Task]:
        """获取任务状态"""
        return self.tasks.get(task_id)
    
    async def _worker(self, worker_id: int):
        """工作线程"""
        logger.info(f"Worker {worker_id} started")
        while self.running:
            try:
                task = await asyncio.wait_for(
                    self.queue.get(),
                    timeout=1.0
                )
                await self._process_task(task, worker_id)
                self.queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
    
    async def _process_task(self, task: Task, worker_id: int):
        """处理单个任务"""
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        
        handler = self.handlers.get(task.task_type)
        if not handler:
            task.status = TaskStatus.FAILED
            task.error = f"Unknown task type: {task.task_type}"
            return
        
        try:
            # 执行任务处理器
            if asyncio.iscoroutinefunction(handler):
                result = await handler(task.payload)
            else:
                result = handler(task.payload)
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            logger.info(f"Task {task.id} completed by worker {worker_id}")
        except Exception as e:
            task.retry_count += 1
            if task.retry_count < task.max_retries:
                # 重新入队重试
                task.status = TaskStatus.PENDING
                await self.queue.put(task)
                logger.warning(f"Task {task.id} failed, retrying ({task.retry_count}/{task.max_retries})")
            else:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                task.completed_at = time.time()
                logger.error(f"Task {task.id} failed after {task.max_retries} retries: {e}")
    
    async def start(self):
        """启动队列处理"""
        self.running = True
        self.workers = [] # 重置 workers 列表
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(i))
            self.workers.append(worker)
        logger.info(f"TaskQueue started with {self.max_workers} workers")
    
    async def stop(self):
        """停止队列处理"""
        self.running = False
        if self.workers:
            await asyncio.gather(*self.workers, return_exceptions=True)
        logger.info("TaskQueue stopped")

# 全局队列实例
task_queue = TaskQueue(max_workers=3)
