from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
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


def register_spa_routes(app: FastAPI) -> None:
    """SPA 资源路由，必须在 API 路由注册之后调用。"""
    frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
    legacy_index = Path(__file__).resolve().parent / "legacy_ui" / "index.html"

    if frontend_dist.exists():
        assets_dir = frontend_dist / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_spa(full_path: str):
            if (
                full_path.startswith("api/")
                or full_path.startswith("docs")
                or full_path.startswith("openapi.json")
                or full_path.startswith("videos")
            ):
                raise HTTPException(status_code=404, detail="Not Found")

            target_file = frontend_dist / full_path
            if target_file.is_file():
                return FileResponse(target_file)

            index_file = frontend_dist / "index.html"
            if index_file.exists():
                return FileResponse(index_file)
            return JSONResponse(
                {"status": "ok", "message": "API is running, frontend not available"},
                status_code=200,
            )
    elif legacy_index.exists():
        @app.get("/", include_in_schema=False)
        async def serve_legacy():
            return FileResponse(legacy_index)
