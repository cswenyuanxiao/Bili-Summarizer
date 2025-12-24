# 系统架构

Last updated: 2025-12-24  
Owner: Backend

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

## 错误路径与降级
- Gemini 超时/失败：返回 `error` 事件（`UPSTREAM_FAILED`），前端结束加载。
- yt-dlp 无字幕：回退到视频转录（若失败则返回 `error`）。
- SSE 断连：前端进入错误态并提示重试。

## 缓存策略
- Key 建议包含：`video_id + mode + focus + language + model_version`。
- 缓存命中不扣分（见 `docs/API_CONTRACT.md`）。

## Auth 与鉴权
- 优先 `x-api-key`，其次 `Authorization: Bearer`（Supabase）。
- 两者同时存在时以 `x-api-key` 为准。
- `x-api-key` 仅允许访问 API 能力；账单/订阅等需 Bearer。
- 401：未携带凭证或无效；403：凭证有效但权限不足。

## 数据与存储
- 生产推荐：PostgreSQL（`DATABASE_URL`）。
- 开发可用：SQLite（本地）。
- 重要表：`summaries`、`user_credits`、`credit_events`、`payment_orders`、`billing_events`。

最低字段建议（示例）：
- `summaries(user_id, video_id, mode, focus, summary, transcript, created_at)`
- `user_credits(user_id, credits, total_used, updated_at)`
- `payment_orders(id, user_id, plan_id, status, provider, created_at)`

## 部署拓扑
- 本地开发：Vite 5173 -> FastAPI 7860。
- 生产部署：FastAPI 服务 + 前端 `dist` 静态文件。

## 资源消耗与限流（建议）
- 限制并发：按用户或 API Key 限制同时进行的总结任务数。
- 长视频限制：可设置最大时长或大小阈值。
- 扣分时机：总结成功（`summary_complete`）后扣分，失败不扣分。

## 已知边界
- Render 免费实例无持久化磁盘。
- 支付平台资质未完成时，生产支付不可用。
