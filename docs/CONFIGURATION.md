# 配置参考（单一来源）

Last updated: 2025-12-25  
Owner: Ops

以下为全局配置的单一事实来源，其他文档仅引用本文件。

## 基础配置
- `GOOGLE_API_KEY`（必填）：Gemini 调用密钥。
- `DATABASE_URL`（推荐）：外部 Postgres 连接字符串（生产建议）。
- `SUPABASE_URL`、`SUPABASE_ANON_KEY`（可选）：登录与云端历史。
- `SUPABASE_SERVICE_KEY`（可选）：后端服务客户端密钥。

## 运行时开关
- `DEBUG_API`：`0`（默认）/ `1`（开启调试接口）
  - 影响：开启 `/api/debug/*` 诊断接口。
- `PAYMENT_MOCK`：`0`（默认）/ `1`（开启模拟支付）
  - 影响：支付流程走 mock 回调。

## 数据库连接池
- `PG_POOL_MIN`：默认 `1`
- `PG_POOL_MAX`：默认 `5`

## 支付环境变量
支付宝：
- `ALIPAY_APP_ID`
- `ALIPAY_PRIVATE_KEY`
- `ALIPAY_PUBLIC_KEY`
- `ALIPAY_NOTIFY_URL`
- `ALIPAY_RETURN_URL`（可选）
- `ALIPAY_ENV`（可选：`sandbox`）

微信：
- `WECHAT_APP_ID`
- `WECHAT_MCH_ID`
- `WECHAT_SERIAL_NO`
- `WECHAT_PRIVATE_KEY`
- `WECHAT_API_V3_KEY`
- `WECHAT_NOTIFY_URL`

回调安全：
- `PAYMENT_WEBHOOK_SECRET`

## v2.0 新增变量

### 浏览器推送 (P4)
- `VAPID_PUBLIC_KEY`：Web Push 公钥
- `VAPID_PRIVATE_KEY`：Web Push 私钥
- `ADMIN_EMAILS`：管理员邮箱列表（逗号分隔）

### 邮件通知 (P4)
- `SMTP_HOST`：邮件服务器
- `SMTP_PORT`：端口（默认 587）
- `SMTP_USER`：用户名
- `SMTP_PASS`：密码
- `SMTP_FROM`：发件人地址

## 推荐值（开发/生产）
- 开发：`DATABASE_URL` 可省略（SQLite），`PAYMENT_MOCK=1`，`DEBUG_API=1`
- 生产：`DATABASE_URL` 必配（Postgres），`PAYMENT_MOCK=0`，`DEBUG_API=0`
- v2.0：需配置 `VAPID_*` 以启用浏览器推送

