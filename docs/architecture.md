# 系统架构

## 组件关系
```
Browser -> Vue SPA -> FastAPI
FastAPI -> yt-dlp / Gemini / DB / 本地视频
```

## 核心流程（总结）
1) 前端发起 `GET /api/summarize`（SSE）。
2) 后端检查缓存（命中直接返回）。
3) 缓存未命中：下载字幕/视频 -> Gemini 分析 -> 回传 summary/transcript。
4) 结果写入数据库与历史。

## Auth 与鉴权
- 优先 x-api-key，其次 Bearer token（Supabase）。
- Supabase 未配置时，登录入口降级但 UI 仍可运行。

## 数据与存储
- 生产推荐：PostgreSQL（`DATABASE_URL`）。
- 开发可用：SQLite（本地）。
- 重要表：`summaries`、`user_credits`、`credit_events`、`payment_orders`、`billing_events`。

## 部署拓扑
- 本地开发：Vite 5173 -> FastAPI 7860。
- 生产部署：FastAPI 服务 + 前端 `dist` 静态文件。

## 已知边界
- Render 免费实例无持久化磁盘。
- 支付平台资质未完成时，生产支付不可用。
