# DEPLOYMENT 速记

来源：docs/DEPLOYMENT.md

## 快速部署
- 本地：后端 uvicorn 8000 + 前端 Vite 5173
- Render 后端 + Vercel 前端
- Docker：Dockerfile.backend + docker-compose(.dev)

## 必需环境变量（核心）
- GOOGLE_API_KEY
- SUPABASE_URL / SUPABASE_ANON_KEY
- JWT_SECRET_KEY
- BILIBILI_SESSDATA（强烈推荐）

## 认证流程（与代码一致）
- 优先 x-api-key；否则 Bearer Token

## 安全建议
- .env 不入库、定期轮换、生产 HTTPS、启用 RLS、限制 CORS

## 故障排查要点
- 后端启动失败：确认 Python 版本与依赖
- 前端 API 失败：检查后端运行/代理/控制台
- Supabase 401：确认 session token 与 env
- -352：补 SESSDATA + 看 app.log
- 定时任务：确认 scheduler 启动

## 监控与健康检查
- /health 端点用于 Render 健康检查

## 备份
- Supabase 日备份；本地 SQLite 复制 + cron