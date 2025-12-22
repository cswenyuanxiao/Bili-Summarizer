# 使用 Python 3.10 基础镜像
FROM python:3.10-slim

# 安装系统依赖，特别是 ffmpeg (yt-dlp 下载和处理媒体必需)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目所有文件
COPY . .

# 创建视频临时存储目录
RUN mkdir -p videos

# 网络端口 (Hugging Face 默认使用 7860)
EXPOSE 7860

# 启动命令 (增加 timeout 以支持长时间视频分析)
CMD ["sh", "-c", "gunicorn web_app.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:7860 --timeout 1500"]
