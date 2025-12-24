# 对话关键背景（持续维护）

本文档用于记录近期对话中的关键决策与实现状态，帮助后续 Agent 快速上手。

## 一、部署与持久化
- Render 免费实例文件系统是临时的，**SQLite 会在每次部署后丢失数据**。
- 已迁移到 **Supabase PostgreSQL**：通过 `DATABASE_URL` 自动切换到 Postgres。
- 后端统一连接层在 `web_app/db.py`：
  - `get_connection()` 根据 `DATABASE_URL` 选择 Postgres/SQLite。
  - 使用 `psycopg2.pool.SimpleConnectionPool` 做连接池。
  - 自动替换 SQL 占位符 `?` → `%s`。
- 重要环境变量：
  - `DATABASE_URL`：Supabase 连接字符串（建议用 pooler 6543）。
  - `PG_POOL_MIN` / `PG_POOL_MAX`：连接池大小。

## 二、调试接口与支付开关
- 调试接口已加开关：`DEBUG_API=1` 才能访问 `/api/debug/*`，默认关闭。
- `PAYMENT_MOCK` 默认关闭（`0`）；开启用于本地/联调测试。

## 三、前端结构调整（路由化）
- 前端改为 **独立路由页面**（`vue-router`），主入口为 `frontend/src/AppShell.vue`。
- 页面路径：
  - `/` 首页
  - `/product` 产品
  - `/pricing` 方案
  - `/docs` 使用文档
  - `/dashboard` 仪表盘
  - `/billing` 账单
  - `/invite` 邀请好友
  - `/developer` 开发者 API
- 需要依赖：`vue-router@4`。若出现 `Failed to resolve import "vue-router"`，需在 `frontend/` 执行 `npm install`。

## 四、商业化与价格
- 价格已统一：
  - Starter Pack：30 积分 ¥1
  - Pro Pack：120 积分 ¥3
  - Pro 专业版：¥29.9 / 月
- 价格配置在 `web_app/main.py` 的 `PRICING_PLANS`。
- 前端展示在 `frontend/src/components/PricingModal.vue` 与 `frontend/src/pages/PricingPage.vue`。

## 五、UI 统一
- 新增统一页面布局与动效：
  - `page-hero`, `page-card`, `page-hero__cloud`, `wiggle-soft` 等样式在 `frontend/src/style.css`。
  - 各路由页面已统一应用。

## 六、已知风险与注意事项
- 如果 Render 无法联网安装依赖，前端会报 `vue-router` 未找到，需要在本机安装后再部署。
- Supabase 侧若手动创建表导致结构不一致，`subscriptions` 表已做字段补齐逻辑（`web_app/main.py`），但依然建议避免手动建错表结构。
- 支付宝/微信支付仍需要平台侧配置与资质，沙箱限制无法完全通过代码绕开。
