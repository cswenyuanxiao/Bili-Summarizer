# API 契约（对外/前端对接）

Last updated: 2025-12-24  
Owner: Backend

## 兼容性原则
- 字段只增不删，事件只增不改语义。
- 破坏性变更必须记录在 `docs/CHANGELOG.md`。

## 鉴权优先级
1) `x-api-key`  
2) `Authorization: Bearer <token>`

同时存在时：以 `x-api-key` 为准。  
401：未携带或无效；403：权限不足（如用 API Key 访问账单）。

## SSE 总结
`GET /api/summarize?url=...&mode=...&focus=...`

事件类型：
- `status`：`{ stage, message }`
- `transcript_complete`：`{ transcript, videoFile, usage }`
- `summary_complete`：`{ summary, mindmap, usage }`
- `error`：`{ code, message, retryable }`

错误码（最小集）：
- `AUTH_REQUIRED`
- `AUTH_INVALID`
- `CREDITS_EXCEEDED`
- `UPSTREAM_FAILED`

## 计费语义（单一口径）
- 扣分发生在 `summary_complete` 成功时。
- 缓存命中不扣分。
- 失败/中断不扣分。

## 主要接口
### Dashboard
`GET /api/dashboard`
- 返回：`credits`, `total_used`, `cost_per_summary`, `daily_usage`

### Payments
`POST /api/payments`
- 请求：`{ plan_id, provider }`
- 返回：`payment_url` 或 `qr_url`

`GET /api/payments/status?order_id=...`
- 返回：`{ status }`

### History
`GET /api/history` / `POST /api/history` / `DELETE /api/history`

### API Keys
`GET /api/keys` / `POST /api/keys` / `DELETE /api/keys/{id}`

### Share
`POST /api/share` / `GET /share/{id}`
