# 稳定性优化实施计划

> 目标：提升系统稳定性和可靠性，解决队列管理、重试限流、PDF导出和思维导图渲染问题

---

## 概览

| 模块 | 优先级 | 预估工时 | 复杂度 |
|------|--------|----------|--------|
| 1. 队列/Worker架构 | P0 | 4h | 高 |
| 2. 失败重试与限流 | P0 | 2h | 中 |
| 3. PDF导出稳定 | P1 | 3h | 高 |
| 4. 思维导图稳定渲染 | P1 | 2h | 中 |

---

## 模块 1: 队列/Worker 架构

### 1.1 目标

将同步的 AI 调用改为异步队列处理，避免请求阻塞和超时。

### 1.2 技术选型

**推荐方案**：使用 Python `asyncio.Queue` + 后台 Worker（无需额外依赖）

备选方案：Redis Queue (RQ) 或 Celery（需要部署 Redis，更复杂）

### 1.3 文件变更

#### [NEW] `web_app/queue_manager.py`

```python
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
            result = await handler(task.payload)
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
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(i))
            self.workers.append(worker)
        logger.info(f"TaskQueue started with {self.max_workers} workers")
    
    async def stop(self):
        """停止队列处理"""
        self.running = False
        await asyncio.gather(*self.workers, return_exceptions=True)
        logger.info("TaskQueue stopped")

# 全局队列实例
task_queue = TaskQueue(max_workers=3)
```

#### [MODIFY] `web_app/main.py`

在 `@app.on_event("startup")` 中添加：

```python
from .queue_manager import task_queue

@app.on_event("startup")
async def startup():
    await init_database()
    
    # 启动任务队列
    async def summarize_handler(payload):
        # 实际的总结逻辑
        from .summarizer_gemini import summarize_content
        return summarize_content(
            payload['file_path'],
            payload['media_type'],
            payload.get('progress_callback'),
            payload.get('focus', 'default'),
            payload.get('uploaded_file')
        )
    
    task_queue.register_handler('summarize', summarize_handler)
    await task_queue.start()

@app.on_event("shutdown")
async def shutdown():
    await task_queue.stop()
```

#### [NEW] API 端点（可选，用于轮询任务状态）

```python
@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    task = task_queue.get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "id": task.id,
        "status": task.status.value,
        "result": task.result,
        "error": task.error,
        "created_at": task.created_at,
        "completed_at": task.completed_at
    }
```

---

## 模块 2: 失败重试与限流

### 2.1 目标

1. 统一的重试机制（指数退避）
2. 请求限流（防止 API 滥用和 Gemini 配额超限）

### 2.2 文件变更

#### [NEW] `web_app/rate_limiter.py`

```python
"""
请求限流器
使用令牌桶算法实现
"""
import time
import asyncio
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict
import logging

logger = logging.getLogger(__name__)

@dataclass
class RateLimitConfig:
    requests_per_minute: int = 10  # 每分钟最大请求数
    requests_per_hour: int = 100   # 每小时最大请求数
    burst_size: int = 5            # 突发容量

class TokenBucket:
    def __init__(self, rate: float, capacity: int):
        self.rate = rate  # 每秒添加的令牌数
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_update = now
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def time_until_available(self, tokens: int = 1) -> float:
        if self.tokens >= tokens:
            return 0
        return (tokens - self.tokens) / self.rate

class RateLimiter:
    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        self.user_buckets: Dict[str, TokenBucket] = {}
        self.global_bucket = TokenBucket(
            rate=self.config.requests_per_minute / 60,
            capacity=self.config.burst_size
        )
    
    def _get_user_bucket(self, user_id: str) -> TokenBucket:
        if user_id not in self.user_buckets:
            self.user_buckets[user_id] = TokenBucket(
                rate=self.config.requests_per_minute / 60,
                capacity=self.config.burst_size
            )
        return self.user_buckets[user_id]
    
    async def acquire(self, user_id: str) -> bool:
        """尝试获取请求配额"""
        # 检查全局限流
        if not self.global_bucket.consume():
            wait_time = self.global_bucket.time_until_available()
            logger.warning(f"Global rate limit hit, wait {wait_time:.2f}s")
            return False
        
        # 检查用户限流
        user_bucket = self._get_user_bucket(user_id)
        if not user_bucket.consume():
            wait_time = user_bucket.time_until_available()
            logger.warning(f"User {user_id} rate limit hit, wait {wait_time:.2f}s")
            return False
        
        return True
    
    def get_wait_time(self, user_id: str) -> float:
        """获取需要等待的时间"""
        global_wait = self.global_bucket.time_until_available()
        user_bucket = self._get_user_bucket(user_id)
        user_wait = user_bucket.time_until_available()
        return max(global_wait, user_wait)

# 全局限流器
rate_limiter = RateLimiter()
```

#### [NEW] `web_app/retry_utils.py`

```python
"""
重试工具
实现指数退避重试
"""
import asyncio
import functools
import random
from typing import Callable, Type, Tuple
import logging

logger = logging.getLogger(__name__)

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    指数退避重试装饰器
    
    Args:
        max_retries: 最大重试次数
        base_delay: 基础延迟（秒）
        max_delay: 最大延迟（秒）
        exponential_base: 指数基数
        jitter: 是否添加随机抖动
        retryable_exceptions: 可重试的异常类型
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.error(f"{func.__name__} failed after {max_retries + 1} attempts: {e}")
                        raise
                    
                    # 计算延迟
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    if jitter:
                        delay = delay * (0.5 + random.random())
                    
                    logger.warning(f"{func.__name__} attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s")
                    await asyncio.sleep(delay)
            
            raise last_exception
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            import time
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.error(f"{func.__name__} failed after {max_retries + 1} attempts: {e}")
                        raise
                    
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    if jitter:
                        delay = delay * (0.5 + random.random())
                    
                    logger.warning(f"{func.__name__} attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s")
                    time.sleep(delay)
            
            raise last_exception
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator
```

#### [MODIFY] `web_app/main.py` - 在 `/api/summarize` 添加限流

```python
from .rate_limiter import rate_limiter

# 在 event_generator 函数开头添加：
if user:
    if not await rate_limiter.acquire(user["user_id"]):
        wait_time = rate_limiter.get_wait_time(user["user_id"])
        yield f"data: {json.dumps({'type': 'error', 'code': 'RATE_LIMITED', 'error': f'请求过于频繁，请等待 {wait_time:.0f} 秒后重试'})}\\n\\n"
        return
```

---

## 模块 3: PDF 导出稳定

### 3.1 目标

1. 解决长文分页问题
2. 支持中文字体嵌入
3. 稳定渲染 Mermaid 图表

### 3.2 技术方案

使用 `html2pdf.js` 配合自定义配置。

### 3.3 文件变更

#### [NEW] `frontend/src/utils/pdfExporter.ts`

```typescript
/**
 * PDF 导出工具
 * 支持长文分页、中文字体、Mermaid 图表
 */
import html2pdf from 'html2pdf.js'

export interface PdfExportOptions {
  filename?: string
  pageSize?: 'a4' | 'letter' | 'legal'
  orientation?: 'portrait' | 'landscape'
  margin?: number | [number, number, number, number]
  enablePageBreaks?: boolean
  imageQuality?: number
}

const defaultOptions: PdfExportOptions = {
  filename: 'bili-summary.pdf',
  pageSize: 'a4',
  orientation: 'portrait',
  margin: 15,
  enablePageBreaks: true,
  imageQuality: 2
}

/**
 * 预处理 HTML 内容
 * - 将 Mermaid SVG 转换为图片
 * - 添加分页标记
 * - 处理中文字体
 */
async function preprocessContent(element: HTMLElement): Promise<HTMLElement> {
  const clone = element.cloneNode(true) as HTMLElement
  
  // 1. 处理 Mermaid SVG -> 转换为 PNG
  const svgs = clone.querySelectorAll('svg.mermaid')
  for (const svg of svgs) {
    try {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      if (!ctx) continue
      
      const svgData = new XMLSerializer().serializeToString(svg)
      const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
      const url = URL.createObjectURL(svgBlob)
      
      const img = new Image()
      await new Promise((resolve, reject) => {
        img.onload = resolve
        img.onerror = reject
        img.src = url
      })
      
      canvas.width = img.width * 2
      canvas.height = img.height * 2
      ctx.scale(2, 2)
      ctx.drawImage(img, 0, 0)
      
      const imgElement = document.createElement('img')
      imgElement.src = canvas.toDataURL('image/png')
      imgElement.style.maxWidth = '100%'
      imgElement.style.height = 'auto'
      
      svg.parentNode?.replaceChild(imgElement, svg)
      URL.revokeObjectURL(url)
    } catch (e) {
      console.warn('Failed to convert SVG to PNG:', e)
    }
  }
  
  // 2. 添加分页控制样式
  const style = document.createElement('style')
  style.textContent = `
    /* 中文字体支持 */
    * {
      font-family: "PingFang SC", "Microsoft YaHei", "Hiragino Sans GB", 
                   "WenQuanYi Micro Hei", sans-serif !important;
    }
    
    /* 分页控制 */
    h1, h2, h3 {
      page-break-after: avoid;
      break-after: avoid;
    }
    
    p, li {
      orphans: 3;
      widows: 3;
    }
    
    pre, code, table {
      page-break-inside: avoid;
      break-inside: avoid;
    }
    
    img {
      max-width: 100%;
      height: auto;
      page-break-inside: avoid;
    }
    
    /* 强制分页点 */
    .page-break {
      page-break-before: always;
      break-before: page;
    }
  `
  clone.prepend(style)
  
  // 3. 在大标题前添加分页
  const h2s = clone.querySelectorAll('h2')
  h2s.forEach((h2, index) => {
    if (index > 0) {
      h2.classList.add('page-break')
    }
  })
  
  return clone
}

/**
 * 导出 PDF
 */
export async function exportToPdf(
  element: HTMLElement,
  options: PdfExportOptions = {}
): Promise<void> {
  const opts = { ...defaultOptions, ...options }
  
  // 预处理内容
  const processedElement = await preprocessContent(element)
  
  // 创建临时容器
  const container = document.createElement('div')
  container.style.position = 'absolute'
  container.style.left = '-9999px'
  container.style.width = '210mm' // A4 宽度
  container.appendChild(processedElement)
  document.body.appendChild(container)
  
  try {
    const pdf = html2pdf()
      .set({
        margin: opts.margin,
        filename: opts.filename,
        image: { 
          type: 'jpeg', 
          quality: 0.98 
        },
        html2canvas: { 
          scale: opts.imageQuality,
          useCORS: true,
          letterRendering: true,
          scrollY: 0
        },
        jsPDF: { 
          unit: 'mm', 
          format: opts.pageSize, 
          orientation: opts.orientation 
        },
        pagebreak: { 
          mode: ['avoid-all', 'css', 'legacy'],
          before: '.page-break',
          avoid: ['pre', 'code', 'table', 'img', 'h1', 'h2', 'h3']
        }
      })
      .from(processedElement)
    
    await pdf.save()
  } finally {
    document.body.removeChild(container)
  }
}

/**
 * 导出带目录的 PDF
 */
export async function exportToPdfWithToc(
  element: HTMLElement,
  options: PdfExportOptions = {}
): Promise<void> {
  const clone = element.cloneNode(true) as HTMLElement
  
  // 生成目录
  const headings = clone.querySelectorAll('h1, h2, h3')
  const tocHtml = `
    <div class="toc" style="margin-bottom: 30px;">
      <h2 style="margin-bottom: 15px;">目录</h2>
      <ul style="list-style: none; padding-left: 0;">
        ${Array.from(headings).map((h, i) => {
          const level = parseInt(h.tagName[1])
          const indent = (level - 1) * 20
          return `<li style="margin-left: ${indent}px; margin-bottom: 5px;">${i + 1}. ${h.textContent}</li>`
        }).join('')}
      </ul>
    </div>
    <div class="page-break"></div>
  `
  
  clone.insertAdjacentHTML('afterbegin', tocHtml)
  
  await exportToPdf(clone, options)
}
```

#### [MODIFY] `frontend/src/components/SummaryPanel.vue`

找到导出按钮的位置，添加/修改导出函数：

```typescript
import { exportToPdf, exportToPdfWithToc } from '../utils/pdfExporter'

const handleExportPdf = async () => {
  const summaryElement = document.querySelector('.summary-content')
  if (!summaryElement) return
  
  try {
    await exportToPdf(summaryElement as HTMLElement, {
      filename: `${videoTitle || 'bili-summary'}.pdf`,
      enablePageBreaks: true
    })
  } catch (e) {
    console.error('PDF export failed:', e)
    // 显示错误提示
  }
}
```

---

## 模块 4: 思维导图/图片稳定渲染

### 4.1 目标

1. 解决 Mermaid 渲染失败问题
2. 添加渲染错误回退机制
3. 支持导出为 SVG/PNG

### 4.2 文件变更

#### [NEW] `frontend/src/utils/mermaidRenderer.ts`

```typescript
/**
 * Mermaid 稳定渲染器
 * 包含错误处理、重试和回退机制
 */
import mermaid from 'mermaid'

// 初始化配置
mermaid.initialize({
  startOnLoad: false,
  theme: 'default',
  securityLevel: 'loose',
  fontFamily: '"PingFang SC", "Microsoft YaHei", sans-serif',
  flowchart: {
    useMaxWidth: true,
    htmlLabels: true,
    curve: 'basis'
  },
  mindmap: {
    useMaxWidth: true
  }
})

export interface RenderResult {
  success: boolean
  svg?: string
  error?: string
}

/**
 * 预处理 Mermaid 代码
 * 修复常见的语法问题
 */
function preprocessCode(code: string): string {
  let processed = code.trim()
  
  // 移除可能的 markdown 代码块标记
  processed = processed.replace(/^```mermaid\n?/i, '')
  processed = processed.replace(/\n?```$/i, '')
  
  // 修复常见问题
  // 1. 中文括号转英文
  processed = processed.replace(/（/g, '(')
  processed = processed.replace(/）/g, ')')
  processed = processed.replace(/【/g, '[')
  processed = processed.replace(/】/g, ']')
  
  // 2. 转义特殊字符
  // 不在引号内的特殊字符需要处理
  const lines = processed.split('\n')
  const fixedLines = lines.map(line => {
    // 如果行包含节点定义，处理特殊字符
    if (line.includes('[') && line.includes(']')) {
      // 转义引号内的特殊字符
      line = line.replace(/\[([^\]]+)\]/g, (match, content) => {
        // 移除可能导致问题的字符
        const safeContent = content
          .replace(/"/g, "'")
          .replace(/</g, '‹')
          .replace(/>/g, '›')
        return `[${safeContent}]`
      })
    }
    return line
  })
  
  return fixedLines.join('\n')
}

/**
 * 安全渲染 Mermaid 图表
 */
export async function renderMermaid(
  code: string,
  containerId: string
): Promise<RenderResult> {
  const processedCode = preprocessCode(code)
  
  // 尝试渲染
  try {
    const result = await mermaid.render(containerId, processedCode)
    return { success: true, svg: result.svg }
  } catch (error) {
    console.warn('Mermaid render failed, trying fallback:', error)
    
    // 尝试简化图表后重新渲染
    try {
      const simplifiedCode = simplifyDiagram(processedCode)
      const result = await mermaid.render(containerId + '_fallback', simplifiedCode)
      return { success: true, svg: result.svg }
    } catch (fallbackError) {
      return {
        success: false,
        error: `渲染失败: ${(error as Error).message}`
      }
    }
  }
}

/**
 * 简化图表（移除可能导致问题的复杂部分）
 */
function simplifyDiagram(code: string): string {
  const lines = code.split('\n')
  const simplified: string[] = []
  
  for (const line of lines) {
    // 保留图表类型声明
    if (line.match(/^(graph|flowchart|mindmap|sequenceDiagram|classDiagram)/i)) {
      simplified.push(line)
      continue
    }
    
    // 简化节点名称
    let simplifiedLine = line
      .replace(/\[([^\]]{50,})\]/g, (_, content) => {
        return `[${content.substring(0, 47)}...]`
      })
    
    simplified.push(simplifiedLine)
  }
  
  return simplified.join('\n')
}

/**
 * 导出为 SVG
 */
export function exportSvg(svgContent: string, filename: string): void {
  const blob = new Blob([svgContent], { type: 'image/svg+xml' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

/**
 * 导出为 PNG
 */
export async function exportPng(
  svgContent: string,
  filename: string,
  scale: number = 2
): Promise<void> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    
    if (!ctx) {
      reject(new Error('Canvas context not available'))
      return
    }
    
    img.onload = () => {
      canvas.width = img.width * scale
      canvas.height = img.height * scale
      ctx.scale(scale, scale)
      ctx.fillStyle = 'white'
      ctx.fillRect(0, 0, canvas.width, canvas.height)
      ctx.drawImage(img, 0, 0)
      
      canvas.toBlob((blob) => {
        if (!blob) {
          reject(new Error('Failed to create blob'))
          return
        }
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = filename
        a.click()
        URL.revokeObjectURL(url)
        resolve()
      }, 'image/png')
    }
    
    img.onerror = () => reject(new Error('Failed to load SVG'))
    
    const svgBlob = new Blob([svgContent], { type: 'image/svg+xml;charset=utf-8' })
    img.src = URL.createObjectURL(svgBlob)
  })
}
```

#### [MODIFY] `frontend/src/components/MindmapPanel.vue`

```vue
<template>
  <div class="mindmap-panel">
    <!-- 工具栏 -->
    <div class="toolbar flex gap-2 mb-4">
      <button @click="handleExportSvg" class="btn btn-sm">导出 SVG</button>
      <button @click="handleExportPng" class="btn btn-sm">导出 PNG</button>
      <button v-if="renderError" @click="retryRender" class="btn btn-sm btn-primary">
        重新渲染
      </button>
    </div>
    
    <!-- 渲染区域 -->
    <div ref="containerRef" class="mermaid-container">
      <!-- 加载状态 -->
      <div v-if="isRendering" class="loading">
        <span class="animate-spin">⏳</span> 正在渲染...
      </div>
      
      <!-- 错误状态 -->
      <div v-else-if="renderError" class="error-state">
        <p class="text-red-500">{{ renderError }}</p>
        <pre class="mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto">{{ code }}</pre>
      </div>
      
      <!-- SVG 渲染结果 -->
      <div v-else v-html="svgContent" class="svg-container"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { renderMermaid, exportSvg, exportPng } from '../utils/mermaidRenderer'

const props = defineProps<{
  code: string
}>()

const containerRef = ref<HTMLElement | null>(null)
const svgContent = ref('')
const renderError = ref('')
const isRendering = ref(false)

const render = async () => {
  if (!props.code) return
  
  isRendering.value = true
  renderError.value = ''
  
  const result = await renderMermaid(props.code, 'mindmap-' + Date.now())
  
  if (result.success && result.svg) {
    svgContent.value = result.svg
  } else {
    renderError.value = result.error || '渲染失败'
  }
  
  isRendering.value = false
}

const retryRender = () => {
  render()
}

const handleExportSvg = () => {
  if (svgContent.value) {
    exportSvg(svgContent.value, 'mindmap.svg')
  }
}

const handleExportPng = async () => {
  if (svgContent.value) {
    await exportPng(svgContent.value, 'mindmap.png')
  }
}

watch(() => props.code, render, { immediate: true })
onMounted(render)
</script>
```

---

## 验证清单

### 模块 1: 队列/Worker
- [ ] 创建 `queue_manager.py`
- [ ] 在 `main.py` 中注册处理器并启动
- [ ] 测试并发请求处理
- [ ] 验证任务重试机制

### 模块 2: 限流重试
- [ ] 创建 `rate_limiter.py`
- [ ] 创建 `retry_utils.py`
- [ ] 在 `/api/summarize` 添加限流
- [ ] 测试超限返回友好错误

### 模块 3: PDF 导出
- [ ] 创建 `pdfExporter.ts`
- [ ] 在 `SummaryPanel.vue` 集成
- [ ] 测试中文渲染
- [ ] 测试长文档分页
- [ ] 测试 Mermaid 图表导出

### 模块 4: 思维导图
- [ ] 创建 `mermaidRenderer.ts`
- [ ] 更新 `MindmapPanel.vue`
- [ ] 测试错误回退
- [ ] 测试 SVG/PNG 导出

---

## 部署注意事项

1. **无需额外依赖**：所有实现使用现有依赖
2. **向后兼容**：不影响现有 API 接口
3. **渐进增强**：新功能不影响基础功能

---

## 预期收益

| 指标 | 当前 | 目标 |
|------|------|------|
| 并发处理能力 | 1 | 3-5 |
| 请求超时率 | ~10% | <2% |
| PDF 导出成功率 | ~70% | >95% |
| Mermaid 渲染成功率 | ~80% | >95% |
