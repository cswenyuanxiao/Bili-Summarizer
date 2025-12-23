import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Security, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

# --- web_app 内部模块导入 ---
from .downloader import download_content
from .summarizer_gemini import summarize_content, extract_ai_transcript, upload_to_gemini, delete_gemini_file
from .cache import get_cached_result, save_to_cache, get_cache_stats
from typing import List

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
    skip_cache: bool = False
):
    logger.info(f"收到总结请求: URL={url}, Mode={mode}, Focus={focus}")

    async def event_generator():
        video_path = None
        remote_file = None
        
        try:
            # 检查缓存
            if not skip_cache:
                cached = get_cached_result(url, mode, focus)
                if cached:
                    logger.info(f"命中缓存: {url}")
                    yield f"data: {json.dumps({'status': 'Found in cache! Loading...'})}\n\n"
                    # Emit all events for cached content
                    yield f"data: {json.dumps({'type': 'transcript_complete', 'data': cached['transcript']})}\n\n"
                    yield f"data: {json.dumps({'type': 'summary_complete', 'data': cached['summary'], 'usage': cached['usage'], 'cached': True})}\n\n"
                     # Finally emit completion
                    yield f"data: {json.dumps({'status': 'complete'})}\n\n"
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
                    await queue.put({'type': f'{name}_complete', 'data': result})
                except Exception as e:
                    logger.error(f"Task {name} failed: {e}")
                    await queue.put({'type': 'error', 'data': str(e)})

            # 1. Download Content
            # ... (download logic) ...
            try:
                video_path, media_type, transcript = await loop.run_in_executor(None, download_content, url, mode, progress_callback)
                
                # Immediately notify frontend about video
                video_filename = os.path.basename(video_path) if video_path else None
                await queue.put({'type': 'video_downloaded', 'data': {'filename': video_filename}})
                
                # If transcript exists from download (e.g. subtitles), emit it now
                if transcript:
                     await queue.put({'type': 'transcript_complete', 'data': transcript})

            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
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
            need_transcript = (not transcript and remote_file is not None)
            if need_transcript:
                 transcript_coro = loop.run_in_executor(
                    None,
                    extract_ai_transcript,
                    video_path,
                    progress_callback,
                    remote_file
                )
                 asyncio.create_task(task_wrapper('transcript', transcript_coro))
                 active_tasks += 1

            if active_tasks > 0:
                 logger.info(f"🚀 Started {active_tasks} parallel AI tasks...")

            # 4. Event Loop: Consume queue until all tasks done
            final_summary = None
            final_transcript = transcript
            final_usage = None

            completed_tasks = 0
            while completed_tasks < active_tasks:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=300.0)
                    msg_type = event.get('type')
                    data = event.get('data')

                    if msg_type == 'status':
                         yield f"data: {json.dumps({'status': data})}\n\n"
                    elif msg_type == 'video_downloaded':
                         yield f"data: {json.dumps({'type': 'video_downloaded', 'video_file': data['filename']})}\n\n"
                    elif msg_type == 'transcript_complete':
                         final_transcript = data
                         yield f"data: {json.dumps({'type': 'transcript_complete', 'transcript': final_transcript})}\n\n"
                         completed_tasks += 1
                    elif msg_type == 'summary_complete':
                         final_summary, final_usage = data
                         yield f"data: {json.dumps({'type': 'summary_complete', 'summary': final_summary, 'usage': final_usage})}\n\n"
                         completed_tasks += 1
                    elif msg_type == 'error':
                         yield f"data: {json.dumps({'error': data})}\n\n"
                         completed_tasks += 1
                except asyncio.TimeoutError:
                     yield f"data: {json.dumps({'status': 'AI analysis is taking longer than expected...'})}\n\n"
            
            if final_summary:
                 save_to_cache(url, mode, focus, final_summary, final_transcript, final_usage)
                 yield f"data: {json.dumps({'status': 'complete'})}\n\n"

        except Exception as e:
            logger.error(f"流式响应异常: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
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


# --- API Key Management (TEMPORARILY DISABLED DUE TO IMPORT ISSUES) ---
# class CreateKeyRequest(BaseModel):
#     name: str
# 
# @app.post("/api/keys")
# async def create_api_key(request: CreateKeyRequest, user=Depends(get_current_user)):
#     ...
# 
# @app.get("/api/keys")
# async def list_api_keys(user=Depends(get_current_user)):
#     ...
# 
# @app.delete("/api/keys/{key_id}")
# async def delete_api_key(key_id: str, user=Depends(get_current_user)):
#     ...
# 
# @app.get("/api/v1/user")
# async def get_user_info_api(api_user=Depends(get_user_by_api_key)):
#     ...


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
