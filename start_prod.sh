#!/bin/bash

# Bili-Summarizer 生产环境启动脚本

# 1. 确保安装了必要的生产级服务器
pip install gunicorn uvicorn

# 2. 检查 .env 文件
if [ ! -f .env ]; then
    echo "错误: 未找到 .env 文件！请先配置 GOOGLE_API_KEY。"
    exit 1
fi

# 3. 启动应用
# 使用 gunicorn 配合 uvicorn worker 提供更好的并发能力和稳定性
# -w 4: 启动 4 个工作进程
# -k uvicorn.workers.UvicornWorker: 使用异步 worker
# --bind 0.0.0.0:8000: 绑定到所有接口，方便外部访问
echo "正在启动生产环境服务器 (Port: 8000)..."
gunicorn web_app.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 600
