from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


def configure_app(app: FastAPI) -> None:
    """应用级配置：环境变量、CORS 与静态资源挂载。"""
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

    # 允许前端访问 videos 目录下的文件用于播放（CI 环境可能没有）
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
