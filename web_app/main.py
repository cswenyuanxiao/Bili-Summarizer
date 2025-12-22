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
                    video_path, media_type, transcript = await loop.run_in_executor(None, download_content, request.url, request.mode, progress_callback)
                    if media_type == 'subtitle':
                         progress_callback("Processing subtitles...")
                    
                    summary, usage = await loop.run_in_executor(None, summarize_content, video_path, media_type, progress_callback, request.focus)
                    return summary, usage, transcript
                except Exception as e:
                    logger.error(f"处理任务时发生错误: {str(e)}")
                    raise e

            task = asyncio.create_task(run_tasks())

            while not task.done():
                try:
                    # 将超时缩短，并增加心跳机制，防止 SSE 连接因长时间无数据而断开
                    status = await asyncio.wait_for(queue.get(), timeout=5.0)
                    yield f"data: {json.dumps({'status': status})}\n\n"
                except asyncio.TimeoutError:
                    # 发送心跳/中间状态，保持连接活跃
                    yield f"data: {json.dumps({'status': 'AI is still thinking... please wait'})}\n\n"
                    continue

            summary, usage, transcript = await task
            logger.info(f"总结成功: {request.url}")
            yield f"data: {json.dumps({'status': 'complete', 'summary': summary, 'transcript': transcript, 'credits': 999, 'usage': usage})}\n\n"

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


# --- AI Chat / Follow-up Endpoint ---
class ChatRequest(BaseModel):
    question: str
    context: str  # The summary text to use as context

@app.post("/chat")
async def chat_with_ai(request: ChatRequest):
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

