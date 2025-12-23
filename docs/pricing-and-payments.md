# 定价方案与支付实现（方案 + 技术栈）

## 用户背景与目标
- 目标用户：B 站高频学习者、内容从业者、知识型 UP 观众
- 关键诉求：稳定可用的总结能力、可控的成本、清晰的购买路径
- 商业目标：提高转化（免费 -> 付费）、降低流失（可随时补充额度）

## 定价策略（多方案）
1) 免费版
- 每日 3 次总结
- 基础响应速度
- 基础思维导图

2) 一次性额度包（按需补充）
- Starter Pack：¥19 / 30 积分
- Creator Pack：¥49 / 120 积分

3) 订阅制（Pro）
- 月付：¥9.9 / 月
- 年付：¥99 / 年（约省 2 个月）
- 订阅期内默认视为无限次总结

4) 团队/企业
- 按需定制（不在自助支付内，人工对接）

## 技术栈与系统结构
- 前端：Vue 3 + Vite + Tailwind（`PricingModal`）
- 后端：FastAPI（`/api/payments`、`/api/payments/notify/*`、`/api/subscribe`）
- 鉴权：Supabase JWT
- 账单：SQLite `billing_events`
- 支付：
  - 支付宝/微信配置检测
  - 支付订单记录 `payment_orders`
  - 回调后更新 `subscriptions` 或 `credits`

## 支付流程设计
1) 前端选择方案 + 支付方式 -> POST `/api/payments`
2) 后端生成订单 -> 返回 payment_url 或二维码信息（mock 模式会返回 mock 完成链接）
3) 支付回调 -> POST `/api/payments/notify/alipay|wechat`
4) 后端标记订单成功 + 写账单 + 更新订阅或发放积分

## 环境变量（支付）
- 支付宝：
  - `ALIPAY_APP_ID`
  - `ALIPAY_PRIVATE_KEY`
  - `ALIPAY_PUBLIC_KEY`
  - `ALIPAY_NOTIFY_URL`
  - `ALIPAY_RETURN_URL`（可选）
  - `ALIPAY_ENV`（可选：`sandbox`）
- 微信支付：
  - `WECHAT_APP_ID`
  - `WECHAT_MCH_ID`
  - `WECHAT_SERIAL_NO`
  - `WECHAT_PRIVATE_KEY`
  - `WECHAT_API_V3_KEY`
  - `WECHAT_NOTIFY_URL`
- 回调安全：
  - `PAYMENT_WEBHOOK_SECRET`（要求回调请求带 `X-Payment-Secret`）

## 开放计划（建议执行顺序）
1) 申请并完成商户入驻
- 支付宝：申请当面付/网页支付（生产与沙箱各一套）
- 微信支付：申请 Native 支付、完成 API v3 证书配置
2) 配置 Render 环境变量并上线
- 支付宝：`ALIPAY_APP_ID`、`ALIPAY_PRIVATE_KEY`、`ALIPAY_PUBLIC_KEY`、`ALIPAY_NOTIFY_URL`、`ALIPAY_RETURN_URL`
- 微信：`WECHAT_APP_ID`、`WECHAT_MCH_ID`、`WECHAT_SERIAL_NO`、`WECHAT_PRIVATE_KEY`、`WECHAT_API_V3_KEY`、`WECHAT_NOTIFY_URL`
3) 沙箱联调
- 支付宝：`ALIPAY_ENV=sandbox`，下单后回调应能自动激活订阅/发放积分
- 微信：使用 Native 扫码支付，确认回调验签与解密成功
4) 生产切换
- 关闭沙箱标志，更新为生产 App ID / Mch ID / 证书
- 观察 `payment_orders` 与 `billing_events` 的状态变化

## 计划落地备注
- 当前回调支持官方签名校验，并保留 `PAYMENT_WEBHOOK_SECRET` 作为自建网关/联调兜底。
- 微信支付回调验签依赖平台证书（服务端会自动拉取并缓存）。
