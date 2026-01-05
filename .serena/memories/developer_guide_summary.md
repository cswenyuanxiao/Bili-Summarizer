# DEVELOPER_GUIDE 速记

来源：docs/DEVELOPER_GUIDE.md

## 技术栈
- 后端：FastAPI + Supabase(Postgres/Auth) + APScheduler + Gemini API
- 前端：Vue3 + TS + Pinia + Vite + Markmap
- 部署：Render(后端)/Vercel(前端)/Supabase(DB)

## 核心流程
- 总结：URL → BV → B站信息 → 下载字幕/音频 → Gemini 总结/思维导图 → 返回 → 入库
- 订阅：订阅表 → 定时任务 → 拉取新视频(WBI) → 推送

## 关键模块
- web_app/main.py：API 路由与 SSE 总结流程
- web_app/subscriptions.py：订阅服务
- web_app/wbi.py：WBI 签名
- web_app/db.py：SQLite/PG 访问
- web_app/scheduler.py：定时任务

## 数据模型（要点）
- summaries（Supabase）：summary/transcript/mindmap + 用户关联
- up_subscriptions（SQLite）：up_mid/up_name/notify_methods/last_video_bvid

## 常见问题
- -352 风控：配置 `BILIBILI_SESSDATA`
- 前端失败：检查 `frontend/vite.config.ts` 代理端口
- 定时任务：确认 `scheduler.py` 在 `main.py` 初始化