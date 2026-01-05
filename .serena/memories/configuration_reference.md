# CONFIGURATION 速记

来源：docs/CONFIGURATION.md

## 基础配置
- `GOOGLE_API_KEY`（必填）
- `DATABASE_URL`（生产推荐）
- `SUPABASE_URL` / `SUPABASE_ANON_KEY` / `SUPABASE_SERVICE_KEY`

## 运行时开关
- `DEBUG_API`：开启 `/api/debug/*`
- `PAYMENT_MOCK`：模拟支付回调

## 连接池
- `PG_POOL_MIN` / `PG_POOL_MAX`

## 支付
- 支付宝：`ALIPAY_*`
- 微信：`WECHAT_*`
- 回调安全：`PAYMENT_WEBHOOK_SECRET`

## v2.0 新增
- 浏览器推送：`VAPID_PUBLIC_KEY` / `VAPID_PRIVATE_KEY` / `ADMIN_EMAILS`
- 邮件通知：`SMTP_*`

## 推荐值
- 开发：`PAYMENT_MOCK=1`，`DEBUG_API=1`
- 生产：`PAYMENT_MOCK=0`，`DEBUG_API=0`