# API 契约（对外/前端对接）

Last updated: 2025-12-25  
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
- `RATE_LIMITED`（v1.2 新增）

## 计费语义（单一口径）
- 扣分发生在 `summary_complete` 成功时。
- 缓存命中不扣分。
- 失败/中断不扣分。

## 主要接口

### Dashboard
`GET /api/dashboard`
- 返回：`credits`, `total_used`, `cost_per_summary`, `usage_history`, `is_admin`

### Payments (v1.2 更新)
`POST /api/payments/create?plan_id=...&provider=...`
- 返回：`{ order_id, payment_url, billing_id, amount_cents }`

`GET /api/payments/status/{order_id}`
- 返回：`{ order_id, status, plan, amount_cents, created_at }`

### Payment Callbacks (内部)
`POST /api/payments/callback/alipay` - 支付宝异步回调
`POST /api/payments/callback/wechat` - 微信支付异步回调

### Batch Summarize (v1.2 新增)
`POST /api/batch/summarize`
- 请求：`{ urls: string[], mode?: string, focus?: string }`
- 返回：`{ job_id, count, credits_charged }`
- 限制：单批次最多 20 个 URL

`GET /api/batch/{job_id}`
- 返回：`{ job_id, status, progress, total, completed_count, failed_count, results, errors, created_at, completed_at }`
- status 枚举：`pending | running | completed | partial | failed`

### Admin Reconciliation (v1.2 新增)
`POST /api/admin/reconciliation?auto_fix=false`
- 权限：仅管理员
- 返回：`{ success, checked_count, issues, fixed_count, summary }`

### History
`GET /api/history` / `POST /api/history` / `DELETE /api/history/{id}`

### API Keys
`GET /api/keys` / `POST /api/keys` / `DELETE /api/keys/{id}`

### Share
`POST /api/share` / `GET /share/{id}`

---

## v2.0 新增接口

### Share Card (P0)
`POST /api/share/card`
- 请求：`{ video_title, video_url, summary_points, template, overlay_text? }`
- 返回：`{ card_url }`

`GET /api/share/card/{filename}`
- 返回：图片文件

### Favorites (P1)
`GET /api/favorites/parse?url=...`
- 返回：`{ fid, title, videos: [...] }`

`POST /api/favorites/import`
- 请求：`{ fid, video_ids: [...], template_id?, credits_estimated }`
- 返回：`{ job_id, count, credits_charged }`

### Templates (P2)
`GET /api/templates`
- 返回：模板列表（预设 + 用户自定义）

`POST /api/templates`
- 请求：`{ name, description, prompt_template, output_format, sections }`
- 返回：创建的模板

`PATCH /api/templates/{id}`
- 更新模板

`DELETE /api/templates/{id}`
- 删除模板

### TTS (P3)
`GET /api/tts/voices`
- 返回：可用语音列表

`POST /api/tts/generate`
- 请求：`{ text, voice? }`
- 返回：`{ audio_url, voice, duration }`

### Subscriptions (P4)
`GET /api/subscription`
- 返回：用户订阅的 UP 主列表

`POST /api/subscription`
- 请求：`{ up_mid, up_name, notify_methods }`

`DELETE /api/subscription/{id}`

### Push Notifications (P4)
`POST /api/push/subscribe`
- 请求：`{ endpoint, keys }`

`POST /api/push/unsubscribe`

`GET /api/notifications`
- 返回：通知列表

`PATCH /api/notifications/{id}/read`

### Compare (P5)
`POST /api/compare`
- 请求：`{ summary_ids: string[] }`
- 返回：AI 对比分析结果

`POST /api/compare/direct`
- 请求：`{ summaries: [{ title, summary, video_url }] }`
- 返回：AI 对比分析结果

### Teams (P6)
`GET /api/teams`
- 返回：用户的团队列表

`POST /api/teams`
- 请求：`{ name, description? }`
- 返回：创建的团队

`GET /api/teams/{id}`
- 返回：团队详情（成员 + 共享总结）

`POST /api/teams/{id}/share`
- 请求：`{ title, video_url, summary_content, video_thumbnail?, transcript?, mindmap?, tags? }`

`POST /api/teams/{id}/comments`
- 请求：`{ team_summary_id, content, parent_id? }`

`GET /api/teams/{id}/summaries/{team_summary_id}/comments`
- 返回：评论列表

---

## 错误响应格式
```json
{
  "detail": "错误描述"
}
```

HTTP 状态码：
- `400` - 请求参数错误
- `401` - 未认证
- `402` - 余额不足
- `403` - 权限不足
- `404` - 资源不存在
- `429` - 请求过于频繁（限流）
- `500` - 服务器错误

