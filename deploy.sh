#!/bin/bash
# One-click deployment script

# 1. Pull latest code
echo "📦 Pulling latest code..."
git pull origin master

# 2. Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found! Copying from .env.example..."
    cp .env.example .env
    echo "❗ Please edit .env with your real API keys before continuing."
    exit 1
fi

# 3. Create database file if not exists (to avoid binding directory as file)
if [ ! -f summarizer.db ]; then
    touch summarizer.db
fi

# 4. Build and start containers
echo "🚀 Building and starting container..."
docker-compose up -d --build

# 5. Clean up unused images
docker image prune -f

echo "✅ Bili-Summarizer is successfully deployed!"
echo "🌍 Access it at: http://localhost:7860"
