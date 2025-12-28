# === 阶段1：构建前端 ===
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci --silent
COPY frontend/ ./

# 接收构建参数（Render 会自动传入环境变量）
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY
ENV VITE_SUPABASE_URL=$VITE_SUPABASE_URL
ENV VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY

RUN npm run build

# === 阶段2：构建后端 ===
FROM python:3.10-slim

# 安装系统依赖（ffmpeg 用于 yt-dlp 处理媒体）
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY . .

# 复制前端构建产物到 frontend/dist（后端 main.py 会检测这个路径）
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# 创建视频临时存储目录
RUN mkdir -p videos

# 网络端口 (Hugging Face / Render 默认使用 7860)
EXPOSE 8000

# 启动命令 (增加 timeout 以支持长时间视频分析)
CMD ["sh", "-c", "gunicorn web_app.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --timeout 1500"]
