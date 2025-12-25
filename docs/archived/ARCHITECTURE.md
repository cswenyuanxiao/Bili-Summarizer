# 系统架构

Last updated: 2025-12-25  
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
- 重要表：`summaries`、`user_credits`、`credit_events`、`payment_orders`、`billing_events`、`idempotency_keys`、`subscriptions`。

最低字段建议（示例）：
- `summaries(user_id, video_id, mode, focus, summary, transcript, created_at)`
- `user_credits(user_id, credits, total_used, updated_at)`
- `payment_orders(id, user_id, plan_id, status, provider, transaction_id, billing_id, created_at)`
- `idempotency_keys(key, status, result, created_at, completed_at)`

## 部署拓扑
- 本地开发：Vite 5173 -> FastAPI 7860。
- 生产部署：FastAPI 服务 + 前端 `dist` 静态文件。

## 资源消耗与限流
- 限制并发：按用户或 API Key 限制同时进行的总结任务数。
- 长视频限制：可设置最大时长或大小阈值。
- 扣分时机：总结成功（`summary_complete`）后扣分，失败不扣分。
- 限流机制：令牌桶算法，全局 + 用户级别双层限流。

## 支付与订单架构 (v1.2 新增)

### 支付全链路
```
用户下单 -> 创建 payment_order + billing_event
         -> 调用支付宝/微信 SDK 获取支付链接
         -> 用户完成支付
         -> 异步回调 -> 幂等键检查 -> 发货（积分/订阅）
         -> 更新订单状态为 delivered
```

### 幂等性保障
- 使用 `idempotency_keys` 表防止重复回调。
- 回调处理前先 check_and_lock，成功后 mark_completed。
- 失败时删除幂等键，允许重试。

### 对账服务
- 检测已支付但未发货订单（PAID_NOT_DELIVERED）。
- 检测账单与订单状态不匹配（BILLING_MISMATCH）。
- 自动过期超时待支付订单（1 小时）。
- 管理员可触发 `/api/admin/reconciliation?auto_fix=true`。

## 批量总结架构 (v1.2 新增)
```
POST /api/batch/summarize { urls: [...] }
  -> 积分预扣（每个视频 10 积分）
  -> 创建 BatchJob，返回 job_id
  -> 后台 asyncio.gather 并发处理（Semaphore 控制）
  -> GET /api/batch/{job_id} 查询进度与结果
```

## v2.0 新增模块

### 分享卡片 (P0)
- `share_card.py`：Pillow 渲染，4 种模板
- 文件 24h 过期自动清理

### 收藏夹导入 (P1)
- `favorites.py`：解析 B 站收藏夹 URL
- 批量创建总结任务

### 总结模板 (P2)
- `templates.py`：预设模板 + 用户自定义
- `summary_templates` 表存储

### 语音播报 (P3)
- `tts.py`：Edge TTS 集成
- 支持 6 种中文语音

### 每日推送 (P4)
- `subscriptions.py`：UP 主订阅管理
- `notifications.py`：邮件 + 浏览器推送
- `scheduler.py`：APScheduler 定时检查

### 总结对比 (P5)
- `compare.py`：2-4 视频 AI 对比分析
- 差异点、共识点、结论生成

### 团队协作 (P6)
- `teams.py`：团队 CRUD + 成员管理
- 内容共享到团队
- 评论系统（支持嵌套回复）

## 已知边界
- Render 免费实例无持久化磁盘。
- 支付平台资质未完成时，生产支付不可用。
- 批量任务状态仅在内存中，服务重启后丢失（可扩展为持久化）。
- 浏览器推送需配置 VAPID 密钥。
- 团队功能需登录用户使用。

