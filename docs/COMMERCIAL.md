# 商业化与支付

Last updated: 2025-12-24  
Owner: Biz

## 定价（单一来源）
- Starter Pack：¥1 / 30 积分
- Pro Pack：¥3 / 120 积分
- Pro 专业版：¥29.9 / 月

## 支付流程
1) 前端 `POST /api/payments`
2) 后端创建订单并返回支付链接/二维码
3) 回调 `/api/payments/notify/*`
4) 订单完成后写入账单与订阅/积分

## 幂等与订单规则（必须）
- 订单号必须全局唯一（推荐 `uuid`）。
- 回调幂等键：平台交易号 + 商户订单号。
- 重复回调必须返回成功但不得重复加积分或升级订阅。

## 生效时点
- 以验签成功的支付成功回调为准。
- 失败/超时不发放积分。
- 退款与回滚：当前不支持（需要补充后端与账单流程）。

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

## 联调开关
- `PAYMENT_MOCK=1` 开启模拟支付
- `PAYMENT_MOCK=0` 生产默认关闭

## 注意事项
- 沙箱环境不能完全替代生产环境（支付宝/微信资质限制）。
- Render 环境变量必须在部署时设置。
