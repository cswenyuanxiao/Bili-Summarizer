# 数据模型

Last updated: 2025-12-24  
Owner: Backend

## 核心表（最低字段）

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

## 索引建议
- summaries：`(user_id, video_id, mode, focus)` 组合索引
- payment_orders：`order_id` 唯一索引
- user_credits：`user_id` 主键

## 幂等与对账
- `payment_orders.id` 全局唯一（uuid）。
- 回调幂等键：平台交易号 + 商户订单号。
