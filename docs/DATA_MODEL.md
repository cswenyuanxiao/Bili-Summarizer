# 数据模型

Last updated: 2025-12-25  
Owner: Backend

## 核心表（v1.x）

### summaries
- `id` (pk)
- `user_id`
- `video_id`
- `mode`
- `focus`
- `summary`
- `transcript`
- `created_at`

### user_credits
- `user_id` (pk)
- `credits`
- `total_used`
- `updated_at`

### credit_events
- `id` (pk)
- `user_id`
- `event_type` (grant/consume)
- `cost`
- `created_at`

### payment_orders
- `id` (pk)
- `user_id`
- `plan_id`
- `provider`
- `status`
- `transaction_id`
- `created_at`

### billing_events
- `id` (pk)
- `user_id`
- `order_id`
- `amount_cents`
- `status`
- `created_at`

### subscriptions
- `user_id` (pk)
- `plan`
- `status`
- `current_period_end`
- `updated_at`

### idempotency_keys
- `key` (pk)
- `status`
- `result`
- `created_at`
- `completed_at`

---

## v2.0 新增表

### summary_templates (P2 总结模板)
- `id` (pk)
- `user_id`
- `name`
- `description`
- `prompt_template`
- `output_format`
- `sections` (JSON)
- `created_at`
- `updated_at`

### up_subscriptions (P4 UP主订阅)
- `id` (pk)
- `user_id`
- `up_mid`
- `up_name`
- `notify_methods` (JSON)
- `last_video_bvid`
- `last_checked_at`
- `created_at`

### notification_queue (P4 通知队列)
- `id` (pk)
- `user_id`
- `type` (email/browser/in_app)
- `title`
- `body`
- `status` (pending/sent/failed)
- `metadata` (JSON)
- `created_at`
- `sent_at`

### push_subscriptions (P4 浏览器推送)
- `id` (pk)
- `user_id`
- `endpoint`
- `keys` (JSON)
- `created_at`

### teams (P6 团队)
- `id` (pk)
- `name`
- `description`
- `owner_id`
- `created_at`
- `updated_at`

### team_members (P6 团队成员)
- `id` (pk)
- `team_id` (fk → teams)
- `user_id`
- `role` (owner/admin/member)
- `joined_at`

### team_summaries (P6 团队共享总结)
- `id` (pk)
- `team_id` (fk → teams)
- `shared_by`
- `title`
- `video_url`
- `video_thumbnail`
- `summary_content`
- `transcript`
- `mindmap`
- `tags`
- `shared_at`

### comments (P6 评论)
- `id` (pk)
- `team_summary_id` (fk → team_summaries)
- `user_id`
- `content`
- `parent_id` (自引用，支持嵌套回复)
- `created_at`

---

## 索引建议

### v1.x 索引
- summaries：`(user_id, video_id, mode, focus)` 组合索引
- payment_orders：`order_id` 唯一索引
- user_credits：`user_id` 主键

### v2.0 索引
- summary_templates：`(user_id)` 索引
- up_subscriptions：`(user_id, up_mid)` 唯一索引
- notification_queue：`(status, created_at)` 索引
- team_members：`(team_id, user_id)` 唯一索引
- team_summaries：`(team_id)` 索引
- comments：`(team_summary_id)` 索引

## 幂等与对账
- `payment_orders.id` 全局唯一（uuid）。
- 回调幂等键：平台交易号 + 商户订单号。

