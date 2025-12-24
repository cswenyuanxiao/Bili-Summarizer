import asyncio
import os
import uuid
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# 音频缓存目录
TTS_CACHE_DIR = Path(__file__).resolve().parent / "static" / "tts"
TTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# 默认配音
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"

# 支持的中文配音列表
VOICES = [
    {"id": "zh-CN-XiaoxiaoNeural", "name": "晓晓 (女)", "desc": "活泼、多才多艺"},
    {"id": "zh-CN-YunxiNeural", "name": "云希 (男)", "desc": "阳光、自然"},
    {"id": "zh-CN-YunjianNeural", "name": "云健 (男)", "desc": "沉稳、商务"},
    {"id": "zh-CN-XiaoyiNeural", "name": "晓伊 (女)", "desc": "温柔、感性"},
    {"id": "zh-HK-HiuGaaiNeural", "name": "晓佳 (粤语)", "desc": "自然粤语"},
    {"id": "zh-TW-HsiaoChenNeural", "name": "晓臻 (台普)", "desc": "亲切台普"},
]

async def generate_tts(text: str, voice: str = DEFAULT_VOICE) -> str:
    """
    生成音频文件并返回相对路径
    """
    if not text:
        raise ValueError("Text cannot be empty")
        
    # 为长文本做简单的截断或分段
    if len(text) > 5000:
        text = text[:5000] # 截断前 5000 字
        
    # 生成唯一文件名
    file_id = str(uuid.uuid4())
    filename = f"{file_id}.mp3"
    filepath = TTS_CACHE_DIR / filename
    
    try:
        # Lazy import to prevent module-level failure if package is missing
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(filepath))
        
        logger.info(f"TTS generated: {filename}")
        return f"/static/tts/{filename}"
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        raise e

def cleanup_expired_tts(max_age_hours: int = 24):
    """
    清理超过 24 小时的临时音频文件
    """
    try:
        import time
        now = time.time()
        for f in TTS_CACHE_DIR.glob("*.mp3"):
            if now - f.stat().st_mtime > max_age_hours * 3600:
                f.unlink()
                logger.info(f"Cleaned up expired TTS file: {f.name}")
    except Exception as e:
        logger.error(f"TTS cleanup failed: {e}")
