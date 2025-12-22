import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# --- web_app 内部模块导入 ---
from .downloader import download_content
from .summarizer_gemini import summarize_content

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

# --- 静态文件与模板 ---
app.mount("/static", StaticFiles(directory="web_app/static"), name="static")
templates = Jinja2Templates(directory="web_app/templates")

# --- 核心业务路由 ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

class SummarizeRequest(BaseModel):
    url: str
    mode: str = "smart" # "smart" or "video"
    focus: str = "default" # "default", "study", "gossip", "business"

@app.post("/summarize")
async def run_summarization(request: SummarizeRequest):
    logger.info(f"收到总结请求: URL={request.url}, Mode={request.mode}, Focus={request.focus}")

    async def event_generator():
        video_path = None
        try:
            loop = asyncio.get_event_loop()
            queue = asyncio.Queue()

            def progress_callback(status):
                loop.call_soon_threadsafe(queue.put_nowait, status)

            async def run_tasks():
                nonlocal video_path
                try:
                    video_path, media_type = await loop.run_in_executor(None, download_content, request.url, request.mode, progress_callback)
                    if media_type == 'subtitle':
                         progress_callback("Processing subtitles...")
                    
                    summary, usage = await loop.run_in_executor(None, summarize_content, video_path, media_type, progress_callback, request.focus)
                    return summary, usage
                except Exception as e:
                    logger.error(f"处理任务时发生错误: {str(e)}")
                    raise e

            task = asyncio.create_task(run_tasks())

            while not task.done():
                try:
                    status = await asyncio.wait_for(queue.get(), timeout=0.1)
                    yield f"data: {json.dumps({'status': status})}\n\n"
                except asyncio.TimeoutError:
                    continue

            summary, usage = await task
            logger.info(f"总结成功: {request.url}")
            yield f"data: {json.dumps({'status': 'complete', 'summary': summary, 'credits': 999, 'usage': usage})}\n\n"

        except Exception as e:
            logger.error(f"流式响应异常: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            import shutil
            # 强力清理 videos 目录
            videos_dir = "videos"
            if os.path.exists(videos_dir):
                for filename in os.listdir(videos_dir):
                    if filename == '.gitkeep': continue
                    file_path = os.path.join(videos_dir, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                            logger.info(f"已删除文件: {file_path}")
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                            logger.info(f"已删除目录: {file_path}")
                    except Exception as e:
                        logger.error(f"删除失败 {file_path}: {e}")

    return StreamingResponse(event_generator(), media_type="text/event-stream")
