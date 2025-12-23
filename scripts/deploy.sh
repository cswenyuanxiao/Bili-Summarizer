#!/bin/bash

# Bili-Summarizer 快速部署脚本
# 用法: ./deploy.sh [railway|render|fly]

set -e

PLATFORM=${1:-railway}

echo "🚀 开始部署 Bili-Summarizer 到 $PLATFORM..."

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "❌ 错误: 未找到 .env 文件"
    echo "请创建 .env 文件并添加 GOOGLE_API_KEY"
    exit 1
fi

# 检查 Git 仓库
if [ ! -d .git ]; then
    echo "📦 初始化 Git 仓库..."
    git init
    git add .
    git commit -m "Initial commit: Bili-Summarizer"
    echo "✅ Git 仓库初始化完成"
    echo ""
    echo "请将代码推送到 GitHub:"
    echo "  git remote add origin https://github.com/你的用户名/bili-summarizer.git"
    echo "  git push -u origin main"
    echo ""
fi

case $PLATFORM in
    railway)
        echo "📌 Railway 部署提示:"
        echo "1. 访问 https://railway.app/"
        echo "2. 连接 GitHub 仓库"
        echo "3. 添加环境变量: GOOGLE_API_KEY"
        echo "4. 自动部署完成后获取公网 URL"
        ;;
    
    render)
        echo "📌 Render 部署提示:"
        echo "1. 访问 https://render.com/"
        echo "2. New → Web Service"
        echo "3. 连接 GitHub 仓库"
        echo "4. 设置环境变量: GOOGLE_API_KEY"
        echo "5. 点击 Create Web Service"
        ;;
    
    fly)
        echo "📌 Fly.io 部署步骤:"
        
        # 检查 flyctl 是否安装
        if ! command -v fly &> /dev/null; then
            echo "安装 Fly CLI..."
            curl -L https://fly.io/install.sh | sh
            echo "请重启终端或运行: export PATH=\$HOME/.fly/bin:\$PATH"
            exit 0
        fi
        
        # 登录检查
        if ! fly auth whoami &> /dev/null; then
            echo "请先登录 Fly.io:"
            fly auth login
        fi
        
        echo "🚀 开始部署到 Fly.io..."
        
        # 读取 .env 中的 API key
        if [ -f .env ]; then
            API_KEY=$(grep GOOGLE_API_KEY .env | cut -d '=' -f2 | tr -d '"' | tr -d "'")
            if [ -n "$API_KEY" ]; then
                echo "设置环境变量..."
                fly secrets set GOOGLE_API_KEY="$API_KEY"
            fi
        fi
        
        echo "部署应用..."
        fly deploy
        
        echo ""
        echo "✅ 部署完成！"
        echo "访问应用: fly open"
        echo "查看日志: fly logs"
        echo "查看状态: fly status"
        ;;
    
    *)
        echo "❌ 未知平台: $PLATFORM"
        echo "支持的平台: railway, render, fly"
        exit 1
        ;;
esac

echo ""
echo "📖 完整部署文档: DEPLOYMENT.md"
